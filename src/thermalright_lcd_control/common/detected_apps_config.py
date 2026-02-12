# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Configuration loader for detected applications.
Reads the detected_apps.json file created by the Windows installer.
"""

import json
from pathlib import Path
from typing import Optional, Dict
from thermalright_lcd_control.common.platform_utils import is_windows, get_data_dir


class DetectedAppsConfig:
    """
    Loads and provides access to detected application paths.
    """
    
    def __init__(self):
        """Initialize and load detected applications configuration"""
        self.istripper_path: Optional[str] = None
        self.vlc_path: Optional[str] = None
        self.detection_date: Optional[str] = None
        
        self._load_config()
    
    def _get_config_file_path(self) -> Path:
        """Get the path to the detected_apps.json configuration file"""
        if is_windows():
            # Use Windows-specific location
            import os
            localappdata = os.environ.get('LOCALAPPDATA', '')
            if localappdata:
                return Path(localappdata) / 'thermalright-lcd-control' / 'detected_apps.json'
        
        # Fallback to data directory
        data_dir = get_data_dir()
        return Path(data_dir) / 'detected_apps.json'
    
    def _load_config(self):
        """Load configuration from JSON file"""
        config_file = self._get_config_file_path()
        
        if not config_file.exists():
            return
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self.istripper_path = config.get('istripper_path')
            self.vlc_path = config.get('vlc_path')
            self.detection_date = config.get('detection_date')
            
            # Validate paths still exist
            if self.istripper_path and not Path(self.istripper_path).exists():
                self.istripper_path = None
            
            if self.vlc_path and not Path(self.vlc_path).exists():
                self.vlc_path = None
                
        except (json.JSONDecodeError, IOError):
            # If config file is invalid, just use defaults
            pass
    
    def has_istripper(self) -> bool:
        """Check if iStripper was detected and is still available"""
        return self.istripper_path is not None and Path(self.istripper_path).exists()
    
    def has_vlc(self) -> bool:
        """Check if VLC was detected and is still available"""
        return self.vlc_path is not None and Path(self.vlc_path).exists()
    
    def get_istripper_path(self) -> Optional[str]:
        """Get iStripper executable path"""
        return self.istripper_path if self.has_istripper() else None
    
    def get_vlc_path(self) -> Optional[str]:
        """Get VLC executable path"""
        return self.vlc_path if self.has_vlc() else None
    
    def get_all_detected_apps(self) -> Dict[str, Optional[str]]:
        """
        Get all detected applications.
        
        Returns:
            Dictionary mapping app names to paths (None if not detected/available)
        """
        return {
            'istripper': self.get_istripper_path(),
            'vlc': self.get_vlc_path()
        }


# Global singleton instance
_detected_apps_config: Optional[DetectedAppsConfig] = None


def get_detected_apps_config() -> DetectedAppsConfig:
    """
    Get the global DetectedAppsConfig instance.
    
    Returns:
        DetectedAppsConfig instance
    """
    global _detected_apps_config
    if _detected_apps_config is None:
        _detected_apps_config = DetectedAppsConfig()
    return _detected_apps_config
