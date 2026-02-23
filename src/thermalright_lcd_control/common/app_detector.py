# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Application detector for Windows to find installed applications like iStripper and VLC.
Searches common installation directories and Windows registry.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
from thermalright_lcd_control.common.platform_utils import is_windows


class AppDetector:
    """
    Detects installed applications on Windows by searching:
    - Program Files directories and subdirectories
    - Windows Registry
    - Common installation paths
    """
    
    # Common executable names for each application
    APP_EXECUTABLES = {
        'istripper': ['iStripper.exe', 'vghd.exe'],
        'vlc': ['vlc.exe']
    }
    
    # Common installation subdirectories
    COMMON_SUBDIRS = {
        'istripper': ['iStripper', 'Totem Entertainment', 'VirtuaGirl HD'],
        'vlc': ['VLC', 'VideoLAN\\VLC']
    }
    
    def __init__(self):
        """Initialize application detector"""
        if not is_windows():
            raise RuntimeError("AppDetector is only supported on Windows")
    
    def get_all_drives(self) -> List[Path]:
        """
        Get all available fixed drives on Windows.
        
        Returns:
            List of Path objects for drive roots
        """
        import string
        drives = []
        
        for letter in string.ascii_uppercase:
            drive = Path(f'{letter}:/')
            if drive.exists():
                try:
                    # Check if it's a fixed drive (not CD/DVD or network)
                    import ctypes
                    drive_type = ctypes.windll.kernel32.GetDriveTypeW(str(drive))
                    # 3 = DRIVE_FIXED (local hard disk)
                    if drive_type == 3:
                        drives.append(drive)
                except:
                    # If we can't determine type, include it anyway
                    drives.append(drive)
        
        return drives
    
    def get_program_files_dirs(self, include_all_drives: bool = False) -> List[Path]:
        """
        Get all Program Files directories to search.
        
        Args:
            include_all_drives: If True, search Program Files on all drives
        
        Returns:
            List of Path objects for Program Files directories
        """
        dirs = []
        
        if include_all_drives:
            # Search all fixed drives
            for drive in self.get_all_drives():
                # Add Program Files variants for each drive
                dirs.extend([
                    drive / 'Program Files',
                    drive / 'Program Files (x86)',
                    drive / 'Games',
                    drive  # Root of drive for direct installations
                ])
        else:
            # Standard Program Files directories on C: drive only
            program_files = os.environ.get('ProgramFiles')
            if program_files:
                dirs.append(Path(program_files))
            
            # Program Files (x86) for 32-bit apps on 64-bit Windows
            program_files_x86 = os.environ.get('ProgramFiles(x86)')
            if program_files_x86:
                dirs.append(Path(program_files_x86))
            
            # Fallback to common paths if environment variables not set
            if not dirs:
                dirs.extend([
                    Path('C:\\Program Files'),
                    Path('C:\\Program Files (x86)')
                ])
        
        return [d for d in dirs if d.exists()]
    
    def search_directory_recursive(self, base_dir: Path, executable_names: List[str], 
                                   max_depth: int = 3) -> Optional[Path]:
        """
        Recursively search a directory for an executable.
        
        Args:
            base_dir: Base directory to start search
            executable_names: List of executable names to search for
            max_depth: Maximum depth to search (default 3 levels)
            
        Returns:
            Path to executable if found, None otherwise
        """
        def search_recursive(current_dir: Path, depth: int) -> Optional[Path]:
            if depth > max_depth:
                return None
            
            try:
                # Check if any executable exists in current directory
                for exe_name in executable_names:
                    exe_path = current_dir / exe_name
                    if exe_path.exists() and exe_path.is_file():
                        return exe_path
                
                # Search subdirectories
                if depth < max_depth:
                    for item in current_dir.iterdir():
                        if item.is_dir():
                            result = search_recursive(item, depth + 1)
                            if result:
                                return result
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
            
            return None
        
        return search_recursive(base_dir, 0)
    
    def check_registry(self, app_name: str) -> Optional[Path]:
        """
        Check Windows registry for application installation path.
        
        Args:
            app_name: Application name ('istripper' or 'vlc')
            
        Returns:
            Path to executable if found in registry, None otherwise
        """
        import winreg
        # Registry keys to check
        registry_keys = [
            # Current user installations
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
            # System-wide installations
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        
        app_name_lower = app_name.lower()
        
        for hkey, key_path in registry_keys:
            try:
                with winreg.OpenKey(hkey, key_path) as key:
                    # Enumerate all subkeys
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            i += 1
                            
                            # Check if subkey name contains app name
                            if app_name_lower in subkey_name.lower():
                                try:
                                    with winreg.OpenKey(key, subkey_name) as subkey:
                                        # Try to get InstallLocation
                                        install_location, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                        if install_location:
                                            install_path = Path(install_location)
                                            if install_path.exists():
                                                # Look for executable in install location
                                                exe_names = self.APP_EXECUTABLES.get(app_name_lower, [])
                                                for exe_name in exe_names:
                                                    exe_path = install_path / exe_name
                                                    if exe_path.exists():
                                                        return exe_path
                                except (OSError, FileNotFoundError):
                                    continue
                        except OSError:
                            break
            except (OSError, PermissionError):
                continue
        
        return None
    
    def find_application(self, app_name: str, search_all_drives: bool = False) -> Optional[Path]:
        """
        Find an application by searching all common locations.
        
        Args:
            app_name: Application name ('istripper' or 'vlc')
            search_all_drives: If True, search all fixed drives (slower but more thorough)
            
        Returns:
            Path to executable if found, None otherwise
        """
        app_name_lower = app_name.lower()
        
        # First, check registry
        registry_path = self.check_registry(app_name_lower)
        if registry_path:
            return registry_path
        
        # Get executable names and common subdirs for this app
        exe_names = self.APP_EXECUTABLES.get(app_name_lower, [])
        if not exe_names:
            return None
        
        common_subdirs = self.COMMON_SUBDIRS.get(app_name_lower, [])
        
        # Search Program Files directories
        program_files_dirs = self.get_program_files_dirs(include_all_drives=search_all_drives)
        
        for base_dir in program_files_dirs:
            # First check common subdirectories (faster)
            for subdir in common_subdirs:
                search_dir = base_dir / subdir
                if search_dir.exists():
                    for exe_name in exe_names:
                        exe_path = search_dir / exe_name
                        if exe_path.exists() and exe_path.is_file():
                            return exe_path
            
            # If not found in common subdirs, do recursive search
            # Only do recursive search on C: drive to avoid long delays
            if not search_all_drives or base_dir.drive == 'C:':
                result = self.search_directory_recursive(base_dir, exe_names)
                if result:
                    return result
        
        return None
    
    def detect_all_applications(self, search_all_drives: bool = False) -> Dict[str, Optional[Path]]:
        """
        Detect all supported applications.
        
        Args:
            search_all_drives: If True, search all fixed drives for iStripper
        
        Returns:
            Dictionary mapping application names to their paths (or None if not found)
        """
        results = {}
        
        for app_name in self.APP_EXECUTABLES.keys():
            # Only search all drives for iStripper
            should_search_all = search_all_drives and app_name == 'istripper'
            results[app_name] = self.find_application(app_name, search_all_drives=should_search_all)
        
        return results


def detect_applications(search_all_drives: bool = False) -> Dict[str, Optional[str]]:
    """
    Convenience function to detect all applications and return paths as strings.
    
    Args:
        search_all_drives: If True, search all fixed drives for iStripper
    
    Returns:
        Dictionary mapping application names to their path strings (or None if not found)
    """
    if not is_windows():
        return {}
    
    detector = AppDetector()
    results = detector.detect_all_applications(search_all_drives=search_all_drives)
    
    # Convert Path objects to strings
    return {app: str(path) if path else None for app, path in results.items()}


def find_istripper_path() -> Optional[str]:
    """
    Find the iStripper executable path.

    Returns:
        Path to iStripper executable as string, or None if not found
    """
    apps = detect_applications()
    return apps.get('istripper')


def detect_istripper_content_directory(istripper_path: Optional[str] = None) -> Optional[str]:
    """
    Detect iStripper content directory containing model shows/data.
    
    Args:
        istripper_path: Path to iStripper executable (will auto-detect if not provided)
    
    Returns:
        Path to content directory as string, or None if not found
    """
    if not is_windows():
        return None
    
    # If no path provided, detect it first
    if not istripper_path:
        apps = detect_applications()
        istripper_path = apps.get('istripper')
        
        if not istripper_path:
            return None
    
    # Use IStripperManager for content directory detection
    try:
        from thermalright_lcd_control.integrations.istripper_manager import IStripperManager
        manager = IStripperManager()
        manager.installation_path = Path(istripper_path)
        
        content_dir = manager.detect_content_directory()
        return str(content_dir) if content_dir else None
        
    except Exception:
        # Fallback to simple detection
        install_dir = Path(istripper_path).parent
        
        # Common content directory names
        for dir_name in ['DATA', 'data', 'Models', 'models', 'Shows', 'shows']:
            content_path = install_dir / dir_name
            if content_path.exists() and content_path.is_dir():
                # Verify it contains subdirectories (models)
                try:
                    subdirs = [d for d in content_path.iterdir() if d.is_dir()]
                    if subdirs:
                        return str(content_path)
                except Exception:
                    pass
        
        return None
