# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Windows Service Manager for Thermalright LCD Control

Provides a simple interface for managing the Windows service
without requiring direct win32 API knowledge.
"""

import sys
from pathlib import Path

from thermalright_lcd_control.common.platform_utils import is_windows
from thermalright_lcd_control.common.logging_config import get_service_logger


class WindowsServiceManager:
    """Manager for Windows service operations"""
    
    def __init__(self):
        self.logger = get_service_logger()
        
        if not is_windows():
            raise RuntimeError("Windows service manager can only be used on Windows")
        
        try:
            from thermalright_lcd_control.service.windows_service import ThermalrightLCDService
            self.service_class = ThermalrightLCDService
        except ImportError as e:
            raise RuntimeError(
                f"Failed to import Windows service: {e}\n"
                "Install pywin32 with: pip install pywin32"
            )
    
    def install(self):
        """Install the Windows service"""
        print("Installing Thermalright LCD Control Service...")
        print("This requires Administrator privileges.\n")
        
        try:
            result = self.service_class.install_service()
            if result:
                print("\nService installed successfully!")
                print("\nNext steps:")
                print("  1. Start the service: net start ThermalrightLCDControl")
                print("  2. Or use the system tray icon to control the service")
                print("  3. Check service status: sc query ThermalrightLCDControl")
            return result
        except Exception as e:
            print(f"\nError during installation: {e}")
            print("\nTroubleshooting:")
            print("  - Make sure you're running as Administrator")
            print("  - Check that pywin32 is installed: pip install pywin32")
            print("  - Run: python -m win32serviceutil install")
            return False
    
    def uninstall(self):
        """Uninstall the Windows service"""
        print("Uninstalling Thermalright LCD Control Service...")
        print("This requires Administrator privileges.\n")
        
        try:
            result = self.service_class.uninstall_service()
            if result:
                print("\nService uninstalled successfully!")
            return result
        except Exception as e:
            print(f"\nError during uninstallation: {e}")
            print("\nTroubleshooting:")
            print("  - Make sure you're running as Administrator")
            print("  - Try: sc delete ThermalrightLCDControl")
            return False
    
    def start(self):
        """Start the Windows service"""
        print("Starting Thermalright LCD Control Service...")
        
        try:
            result = self.service_class.start_service()
            if result:
                print("\nService is now running!")
                print("Monitor logs in Windows Event Viewer under 'Application'")
            return result
        except Exception as e:
            print(f"\nError starting service: {e}")
            print("\nTroubleshooting:")
            print("  - Check service status: sc query ThermalrightLCDControl")
            print("  - View logs: eventvwr.msc")
            return False
    
    def stop(self):
        """Stop the Windows service"""
        print("Stopping Thermalright LCD Control Service...")
        
        try:
            result = self.service_class.stop_service()
            if result:
                print("\nService stopped successfully!")
            return result
        except Exception as e:
            print(f"\nError stopping service: {e}")
            return False
    
    def restart(self):
        """Restart the Windows service"""
        print("Restarting Thermalright LCD Control Service...")
        
        self.stop()
        import time
        time.sleep(2)
        return self.start()
    
    def status(self):
        """Get service status"""
        try:
            status = self.service_class.get_service_status()
            print(f"Service Status: {status}")
            return status
        except Exception as e:
            print(f"Error getting status: {e}")
            return None


def main():
    """Command-line interface for service management"""
    if not is_windows():
        print("Error: This tool only works on Windows")
        sys.exit(1)
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage Thermalright LCD Control Windows Service"
    )
    parser.add_argument(
        'command',
        choices=['install', 'uninstall', 'start', 'stop', 'restart', 'status'],
        help="Service command to execute"
    )
    
    args = parser.parse_args()
    
    try:
        manager = WindowsServiceManager()
        
        if args.command == 'install':
            manager.install()
        elif args.command == 'uninstall':
            manager.uninstall()
        elif args.command == 'start':
            manager.start()
        elif args.command == 'stop':
            manager.stop()
        elif args.command == 'restart':
            manager.restart()
        elif args.command == 'status':
            manager.status()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
