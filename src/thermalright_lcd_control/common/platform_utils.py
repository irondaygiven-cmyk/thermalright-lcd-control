# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""Platform detection and utilities for cross-platform support"""

import platform
import sys
from enum import Enum


class PlatformType(Enum):
    """Supported platform types"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"


def get_platform() -> PlatformType:
    """
    Detect the current operating system platform
    
    Returns:
        PlatformType: The detected platform type
    """
    system = platform.system().lower()
    
    if system == "windows":
        return PlatformType.WINDOWS
    elif system == "linux":
        return PlatformType.LINUX
    elif system == "darwin":
        return PlatformType.MACOS
    else:
        return PlatformType.UNKNOWN


def is_windows() -> bool:
    """Check if running on Windows"""
    return get_platform() == PlatformType.WINDOWS


def is_linux() -> bool:
    """Check if running on Linux"""
    return get_platform() == PlatformType.LINUX


def is_macos() -> bool:
    """Check if running on macOS"""
    return get_platform() == PlatformType.MACOS


def get_config_dir() -> str:
    """
    Get platform-specific configuration directory
    
    Returns:
        str: Path to configuration directory
    """
    if is_windows():
        import os
        return os.path.join(os.environ.get('APPDATA', ''), 'thermalright-lcd-control')
    elif is_linux():
        import os
        home = os.path.expanduser('~')
        return os.path.join(home, '.config', 'thermalright-lcd-control')
    elif is_macos():
        import os
        home = os.path.expanduser('~')
        return os.path.join(home, 'Library', 'Application Support', 'thermalright-lcd-control')
    else:
        return '.'


def get_data_dir() -> str:
    """
    Get platform-specific data directory
    
    Returns:
        str: Path to data directory
    """
    if is_windows():
        import os
        return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'thermalright-lcd-control')
    elif is_linux():
        import os
        home = os.path.expanduser('~')
        return os.path.join(home, '.local', 'share', 'thermalright-lcd-control')
    elif is_macos():
        import os
        home = os.path.expanduser('~')
        return os.path.join(home, 'Library', 'Application Support', 'thermalright-lcd-control')
    else:
        return '.'


def get_log_dir() -> str:
    """
    Get platform-specific log directory
    
    Returns:
        str: Path to log directory
    """
    if is_windows():
        import os
        return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'thermalright-lcd-control', 'logs')
    elif is_linux():
        # For Linux, use /var/log if running as service (root), otherwise use user dir
        import os
        try:
            if os.geteuid() == 0:  # Running as root
                return '/var/log'
        except AttributeError:
            # geteuid not available on Windows
            pass
        home = os.path.expanduser('~')
        return os.path.join(home, '.local', 'share', 'thermalright-lcd-control', 'logs')
    elif is_macos():
        import os
        home = os.path.expanduser('~')
        return os.path.join(home, 'Library', 'Logs', 'thermalright-lcd-control')
    else:
        return '.'
