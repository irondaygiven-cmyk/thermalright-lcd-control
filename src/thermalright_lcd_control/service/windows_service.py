# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Windows Service Implementation for Thermalright LCD Control

This module provides Windows service functionality using pywin32.
The service runs in the background and automatically starts at system boot.
"""

import os
import sys
import time
import threading
from pathlib import Path

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

from thermalright_lcd_control.common.logging_config import get_service_logger
from thermalright_lcd_control.common.platform_utils import get_data_dir


class ThermalrightLCDService:
    """
    Windows Service for Thermalright LCD Control
    
    Manages the device controller as a Windows background service with:
    - Automatic startup at system boot
    - Graceful shutdown handling
    - Automatic restart on failure
    - Windows Event Viewer logging
    """
    
    _svc_name_ = "ThermalrightLCDControl"
    _svc_display_name_ = "Thermalright LCD Control Service"
    _svc_description_ = "Controls Thermalright LCD display with real-time metrics and media playback"
    
    def __init__(self, args=None):
        """Initialize the service"""
        if not HAS_WIN32:
            raise RuntimeError(
                "pywin32 is required for Windows service functionality.\n"
                "Install with: pip install pywin32"
            )
        
        self.logger = get_service_logger()
        self.stop_event = None
        self.is_running = False
        self.service_thread = None
        
        # Initialize win32 service
        if args:
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)
    
    def SvcStop(self):
        """Handle service stop request"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # Signal the service to stop
        self.is_running = False
        if self.stop_event:
            win32event.SetEvent(self.stop_event)
        
        self.logger.info("Service stopped")
    
    def SvcDoRun(self):
        """Main service execution"""
        self.logger.info("Service starting...")
        
        try:
            # Log to Windows Event Viewer
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.is_running = True
            
            # Start the device controller in a separate thread
            self.service_thread = threading.Thread(target=self._run_device_controller)
            self.service_thread.daemon = True
            self.service_thread.start()
            
            # Wait for stop signal
            if self.stop_event:
                win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            
            # Wait for service thread to finish
            if self.service_thread and self.service_thread.is_alive():
                self.service_thread.join(timeout=10)
            
            self.logger.info("Service execution completed")
            
        except Exception as e:
            self.logger.error(f"Service error: {e}", exc_info=True)
            servicemanager.LogErrorMsg(f"Service error: {e}")
            raise
    
    def _run_device_controller(self):
        """Run the device controller in service mode"""
        try:
            from thermalright_lcd_control.device_controller import run_service
            
            # Get config directory
            config_dir = os.path.join(get_data_dir(), 'resources', 'config')
            
            # Ensure config directory exists
            os.makedirs(config_dir, exist_ok=True)
            
            self.logger.info(f"Starting device controller with config: {config_dir}")
            
            # Run the service
            run_service(config_dir)
            
        except KeyboardInterrupt:
            self.logger.info("Device controller stopped by signal")
        except Exception as e:
            self.logger.error(f"Device controller error: {e}", exc_info=True)
            servicemanager.LogErrorMsg(f"Device controller error: {e}")
            
            # Request service restart on error
            self.SvcStop()
    
    @classmethod
    def install_service(cls):
        """Install the Windows service"""
        if not HAS_WIN32:
            raise RuntimeError("pywin32 is required for service installation")
        
        try:
            # Use win32serviceutil to install
            sys.argv = [
                sys.argv[0],
                '--startup=auto',
                'install'
            ]
            win32serviceutil.HandleCommandLine(cls)
            print(f"✓ Service '{cls._svc_display_name_}' installed successfully")
            print("  Use 'net start ThermalrightLCDControl' to start the service")
            return True
            
        except Exception as e:
            print(f"✗ Failed to install service: {e}")
            return False
    
    @classmethod
    def uninstall_service(cls):
        """Uninstall the Windows service"""
        if not HAS_WIN32:
            raise RuntimeError("pywin32 is required for service uninstallation")
        
        try:
            # Stop the service first if running
            try:
                win32serviceutil.StopService(cls._svc_name_)
                print(f"✓ Service stopped")
                time.sleep(2)
            except Exception:
                pass  # Service might not be running
            
            # Uninstall the service
            sys.argv = [sys.argv[0], 'remove']
            win32serviceutil.HandleCommandLine(cls)
            print(f"✓ Service '{cls._svc_display_name_}' uninstalled successfully")
            return True
            
        except Exception as e:
            print(f"✗ Failed to uninstall service: {e}")
            return False
    
    @classmethod
    def start_service(cls):
        """Start the Windows service"""
        if not HAS_WIN32:
            raise RuntimeError("pywin32 is required")
        
        try:
            win32serviceutil.StartService(cls._svc_name_)
            print(f"✓ Service '{cls._svc_display_name_}' started")
            return True
        except Exception as e:
            print(f"✗ Failed to start service: {e}")
            return False
    
    @classmethod
    def stop_service(cls):
        """Stop the Windows service"""
        if not HAS_WIN32:
            raise RuntimeError("pywin32 is required")
        
        try:
            win32serviceutil.StopService(cls._svc_name_)
            print(f"✓ Service '{cls._svc_display_name_}' stopped")
            return True
        except Exception as e:
            print(f"✗ Failed to stop service: {e}")
            return False
    
    @classmethod
    def get_service_status(cls):
        """Get the current service status"""
        if not HAS_WIN32:
            return "pywin32 not available"
        
        try:
            status = win32serviceutil.QueryServiceStatus(cls._svc_name_)
            status_map = {
                win32service.SERVICE_STOPPED: "Stopped",
                win32service.SERVICE_START_PENDING: "Starting",
                win32service.SERVICE_STOP_PENDING: "Stopping",
                win32service.SERVICE_RUNNING: "Running",
                win32service.SERVICE_CONTINUE_PENDING: "Resuming",
                win32service.SERVICE_PAUSE_PENDING: "Pausing",
                win32service.SERVICE_PAUSED: "Paused"
            }
            return status_map.get(status[1], "Unknown")
        except Exception as e:
            return f"Not installed or error: {e}"


def main():
    """Main entry point for service operations"""
    if len(sys.argv) == 1:
        # No arguments - try to start as service
        if HAS_WIN32:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(ThermalrightLCDService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            print("Error: pywin32 is not installed")
            print("Install with: pip install pywin32")
            sys.exit(1)
    else:
        # Handle command line arguments
        if HAS_WIN32:
            win32serviceutil.HandleCommandLine(ThermalrightLCDService)
        else:
            print("Error: pywin32 is not installed")
            print("Install with: pip install pywin32")
            sys.exit(1)


if __name__ == '__main__':
    main()
