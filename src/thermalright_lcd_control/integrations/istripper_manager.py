# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
iStripper Integration Manager

Enhanced iStripper detection and management features:
- Registry-based detection (Windows)
- Process monitoring
- Auto-reconnect on restart
- Configuration management
"""

import os
import time
import psutil
import threading
from pathlib import Path
from typing import Optional, Callable

from thermalright_lcd_control.common.platform_utils import is_windows
from thermalright_lcd_control.common.logging_config import get_service_logger


class IStripperManager:
    """
    Manages iStripper integration and monitoring
    
    Features:
    - Detect iStripper installation path
    - Monitor iStripper process status
    - Auto-start/stop window capture
    - Detect iStripper version
    - Support portable installations
    """
    
    def __init__(self):
        self.logger = get_service_logger()
        self.installation_path: Optional[Path] = None
        self.executable_name: Optional[str] = None
        self.content_directory: Optional[Path] = None  # Directory containing model shows/data
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.should_monitor = False
        
        # Callbacks
        self.on_started_callback: Optional[Callable] = None
        self.on_stopped_callback: Optional[Callable] = None
    
    def detect_installation(self, use_cache: bool = True) -> Optional[Path]:
        """
        Detect iStripper installation path
        
        Uses multiple detection methods:
        1. Windows Registry (fastest)
        2. Cached detection result
        3. Common installation locations
        4. Full drive search (slowest)
        
        Args:
            use_cache: Use cached path if available
        
        Returns:
            Path to iStripper executable or None
        """
        # Check cache first
        if use_cache and self.installation_path:
            if self.installation_path.exists():
                return self.installation_path
        
        # Try registry detection (Windows only)
        if is_windows():
            path = self._detect_from_registry()
            if path:
                self.installation_path = path
                return path
        
        # Try common locations
        path = self._detect_from_common_locations()
        if path:
            self.installation_path = path
            return path
        
        # Full search as fallback (can be slow)
        path = self._detect_from_full_search()
        if path:
            self.installation_path = path
            return path
        
        self.logger.warning("iStripper installation not found")
        return None
    
    def _detect_from_registry(self) -> Optional[Path]:
        """Detect iStripper from Windows Registry"""
        if not is_windows():
            return None
        
        try:
            import winreg
            
            # Try common registry locations
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Totem Entertainment\iStripper"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Totem Entertainment\iStripper"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Totem Entertainment\iStripper"),
            ]
            
            for hkey, subkey in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                        
                        # Check for executables
                        for exe_name in ["iStripper.exe", "vghd.exe"]:
                            exe_path = Path(install_path) / exe_name
                            if exe_path.exists():
                                self.executable_name = exe_name
                                self.logger.info(f"iStripper found via Registry: {exe_path}")
                                return exe_path
                                
                except FileNotFoundError:
                    continue
                except Exception as e:
                    self.logger.debug(f"Registry check failed: {e}")
                    continue
                    
        except ImportError:
            self.logger.debug("winreg not available")
        except Exception as e:
            self.logger.debug(f"Registry detection error: {e}")
        
        return None
    
    def _detect_from_common_locations(self) -> Optional[Path]:
        """Check common installation locations"""
        common_paths = []
        
        if is_windows():
            # Windows common locations
            drives = ['C:', 'D:', 'E:']
            base_folders = [
                'Program Files',
                'Program Files (x86)',
                'Games',
            ]
            app_folders = [
                'iStripper',
                'Totem Entertainment/iStripper',
                'VirtuaGirl HD',
            ]
            
            for drive in drives:
                for base in base_folders:
                    for app in app_folders:
                        common_paths.append(Path(drive) / base / app)
        else:
            # Linux common locations (if running via Wine)
            home = Path.home()
            common_paths.extend([
                home / '.wine' / 'drive_c' / 'Program Files' / 'iStripper',
                home / '.wine' / 'drive_c' / 'Program Files (x86)' / 'iStripper',
            ])
        
        # Check each common path
        for path in common_paths:
            if not path.exists():
                continue
            
            # Check for executables
            for exe_name in ["iStripper.exe", "vghd.exe"]:
                exe_path = path / exe_name
                if exe_path.exists():
                    self.executable_name = exe_name
                    self.logger.info(f"iStripper found in common location: {exe_path}")
                    return exe_path
        
        return None
    
    def _detect_from_full_search(self) -> Optional[Path]:
        """Full search of all drives (slow, last resort)"""
        # This is the existing logic from app_detector.py
        # Only use if quick methods fail
        try:
            from thermalright_lcd_control.common.app_detector import find_istripper_path
            path_str = find_istripper_path()
            if path_str:
                self.installation_path = Path(path_str)
                # Detect executable name
                if 'vghd.exe' in path_str:
                    self.executable_name = 'vghd.exe'
                else:
                    self.executable_name = 'iStripper.exe'
                return self.installation_path
        except Exception as e:
            self.logger.debug(f"Full search failed: {e}")
        
        return None
    
    def is_process_running(self) -> bool:
        """Check if iStripper process is running"""
        try:
            process_names = ["iStripper.exe", "vghd.exe", "iStripper", "vghd"]
            
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] in process_names:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking iStripper process: {e}")
            return False
    
    def start_monitoring(self, on_started: Callable = None, on_stopped: Callable = None):
        """
        Start monitoring iStripper process
        
        Args:
            on_started: Callback when iStripper starts
            on_stopped: Callback when iStripper stops
        """
        if self.should_monitor:
            self.logger.warning("Monitoring already active")
            return
        
        self.on_started_callback = on_started
        self.on_stopped_callback = on_stopped
        self.should_monitor = True
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("iStripper monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring iStripper process"""
        self.should_monitor = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("iStripper monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        last_state = self.is_process_running()
        
        while self.should_monitor:
            try:
                current_state = self.is_process_running()
                
                # State changed - iStripper started
                if current_state and not last_state:
                    self.is_running = True
                    self.logger.info("iStripper started")
                    if self.on_started_callback:
                        try:
                            self.on_started_callback()
                        except Exception as e:
                            self.logger.error(f"Error in started callback: {e}")
                
                # State changed - iStripper stopped
                elif not current_state and last_state:
                    self.is_running = False
                    self.logger.info("iStripper stopped")
                    if self.on_stopped_callback:
                        try:
                            self.on_stopped_callback()
                        except Exception as e:
                            self.logger.error(f"Error in stopped callback: {e}")
                
                last_state = current_state
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def detect_content_directory(self, installation_path: Optional[Path] = None) -> Optional[Path]:
        """
        Detect iStripper content directory containing model shows/data
        
        Args:
            installation_path: Path to iStripper installation (uses self.installation_path if not provided)
        
        Returns:
            Path to content directory or None if not found
        """
        # Use provided path or cached installation path
        if installation_path is None:
            installation_path = self.installation_path
        
        if not installation_path or not installation_path.exists():
            self.logger.warning("No valid iStripper installation path provided")
            return None
        
        # Get the installation directory (where the exe is located)
        install_dir = installation_path.parent
        
        # Common content directory names
        content_dir_names = [
            'DATA',      # Standard iStripper data folder
            'data',      # Lowercase variant
            'Models',    # Alternative folder name
            'models',    # Lowercase variant
            'Shows',     # Another possible name
            'shows',     # Lowercase variant
        ]
        
        # Check in installation directory
        for dir_name in content_dir_names:
            content_path = install_dir / dir_name
            if content_path.exists() and content_path.is_dir():
                # Verify it contains model content (check for subdirectories)
                try:
                    # Model folders typically have names like "0001", "0002", etc.
                    subdirs = [d for d in content_path.iterdir() if d.is_dir()]
                    if subdirs:
                        self.content_directory = content_path
                        self.logger.info(f"iStripper content directory found: {content_path}")
                        return content_path
                except Exception as e:
                    self.logger.debug(f"Error checking {content_path}: {e}")
        
        # Try Registry for custom data path (Windows only)
        if is_windows():
            registry_path = self._detect_content_from_registry()
            if registry_path:
                self.content_directory = registry_path
                return registry_path
        
        # Check parent directory (sometimes DATA is at same level as installation folder)
        parent_dir = install_dir.parent
        for dir_name in content_dir_names:
            content_path = parent_dir / dir_name
            if content_path.exists() and content_path.is_dir():
                try:
                    subdirs = [d for d in content_path.iterdir() if d.is_dir()]
                    if subdirs:
                        self.content_directory = content_path
                        self.logger.info(f"iStripper content directory found: {content_path}")
                        return content_path
                except Exception as e:
                    self.logger.debug(f"Error checking {content_path}: {e}")
        
        self.logger.warning("iStripper content directory not found")
        return None
    
    def _detect_content_from_registry(self) -> Optional[Path]:
        """Try to detect content directory from Windows Registry"""
        if not is_windows():
            return None
        
        try:
            import winreg
            
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Totem Entertainment\iStripper"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Totem Entertainment\iStripper"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Totem Entertainment\iStripper"),
            ]
            
            for hkey, subkey in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        # Try to get data path
                        try:
                            data_path = winreg.QueryValueEx(key, "DataPath")[0]
                            data_dir = Path(data_path)
                            if data_dir.exists() and data_dir.is_dir():
                                self.logger.info(f"Content directory from Registry: {data_dir}")
                                return data_dir
                        except FileNotFoundError:
                            pass
                        
                        # Try to derive from install path
                        try:
                            install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                            for subdir in ['DATA', 'data', 'Models', 'models']:
                                data_dir = Path(install_path) / subdir
                                if data_dir.exists() and data_dir.is_dir():
                                    return data_dir
                        except FileNotFoundError:
                            pass
                            
                except FileNotFoundError:
                    continue
                except Exception as e:
                    self.logger.debug(f"Registry check error: {e}")
                    continue
                    
        except ImportError:
            pass
        except Exception as e:
            self.logger.debug(f"Registry detection error: {e}")
        
        return None
    
    def get_content_directory(self, auto_detect: bool = True) -> Optional[Path]:
        """
        Get the iStripper content directory
        
        Args:
            auto_detect: If True, attempt detection if not already cached
        
        Returns:
            Path to content directory or None
        """
        if self.content_directory and self.content_directory.exists():
            return self.content_directory
        
        if auto_detect:
            return self.detect_content_directory()
        
        return None
    
    def list_model_directories(self) -> list:
        """
        List all model directories in the content folder
        
        Returns:
            List of Path objects for each model directory
        """
        content_dir = self.get_content_directory()
        if not content_dir:
            return []
        
        try:
            model_dirs = []
            for item in content_dir.iterdir():
                if item.is_dir():
                    model_dirs.append(item)
            
            # Sort by name (usually numeric IDs like "0001", "0002")
            model_dirs.sort(key=lambda x: x.name)
            return model_dirs
            
        except Exception as e:
            self.logger.error(f"Error listing model directories: {e}")
            return []
    
    def get_model_media_files(self, model_dir: Path, extensions: list = None) -> list:
        """
        Get media files from a model directory
        
        Args:
            model_dir: Path to model directory
            extensions: List of file extensions to include (e.g., ['.mp4', '.jpg'])
                       If None, includes common video and image formats
        
        Returns:
            List of Path objects for media files
        """
        if extensions is None:
            extensions = ['.mp4', '.avi', '.mkv', '.mov', '.jpg', '.jpeg', '.png', '.gif']
        
        if not model_dir.exists() or not model_dir.is_dir():
            return []
        
        try:
            media_files = []
            for item in model_dir.rglob('*'):
                if item.is_file() and item.suffix.lower() in extensions:
                    media_files.append(item)
            
            # Sort by name
            media_files.sort(key=lambda x: x.name)
            return media_files
            
        except Exception as e:
            self.logger.error(f"Error listing media files in {model_dir}: {e}")
            return []
    
    def get_all_model_media(self, extensions: list = None, limit: int = None) -> dict:
        """
        Get all model media files organized by model
        
        Args:
            extensions: List of file extensions to include
            limit: Maximum number of models to process (None for all)
        
        Returns:
            Dictionary mapping model directory names to lists of media file paths
        """
        model_dirs = self.list_model_directories()
        
        if limit:
            model_dirs = model_dirs[:limit]
        
        result = {}
        for model_dir in model_dirs:
            media_files = self.get_model_media_files(model_dir, extensions)
            if media_files:
                result[model_dir.name] = media_files
        
        return result
    
    def get_window_title(self) -> str:
        """
        Get the window title for window capture
        
        Returns:
            Window title string
        """
        # iStripper typically uses "iStripper" as window title
        # but older versions might use "VirtuaGirl HD"
        return "iStripper"
    
    def get_config_dict(self) -> dict:
        """
        Generate configuration dictionary for iStripper window capture
        
        Returns:
            dict: Configuration for window capture
        """
        return {
            'display': {
                'background': {
                    'type': 'window_capture',
                    'path': '',
                },
                'window_title': self.get_window_title(),
                'capture_fps': 30,
                'scale_factor': 1.5,
                'rotation': 0,
            }
        }


def main():
    """Test iStripper detection and monitoring"""
    import sys
    
    print("iStripper Detection Test")
    print("=" * 50)
    print()
    
    manager = IStripperManager()
    
    # Test detection
    print("1. Detecting iStripper installation...")
    path = manager.detect_installation(use_cache=False)
    
    if path:
        print(f"   ✓ Found: {path}")
        print(f"   Executable: {manager.executable_name}")
    else:
        print("   ✗ Not found")
        sys.exit(1)
    
    print()
    
    # Test content directory detection
    print("2. Detecting content directory...")
    content_dir = manager.detect_content_directory()
    
    if content_dir:
        print(f"   ✓ Found: {content_dir}")
        
        # List model directories
        print()
        print("3. Listing model directories...")
        model_dirs = manager.list_model_directories()
        print(f"   Found {len(model_dirs)} model(s)")
        
        if model_dirs:
            print(f"   First few models:")
            for model_dir in model_dirs[:5]:
                print(f"     - {model_dir.name}")
            
            # Show media files for first model
            print()
            print(f"4. Media files in first model ({model_dirs[0].name})...")
            media_files = manager.get_model_media_files(model_dirs[0])
            print(f"   Found {len(media_files)} file(s)")
            for media_file in media_files[:5]:
                print(f"     - {media_file.name}")
    else:
        print("   ✗ Not found")
        print("   Note: This is expected if no models are installed")
    
    print()
    
    # Test process detection
    print("5. Checking if iStripper is running...")
    running = manager.is_process_running()
    print(f"   Status: {'Running' if running else 'Not running'}")
    
    print()
    print("=" * 50)


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
