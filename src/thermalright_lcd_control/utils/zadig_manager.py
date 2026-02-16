# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Zadig USB Driver Manager for Windows 11

Integrates with Zadig tool for USB HID driver installation.
Provides automatic driver detection and installation wizard.
"""

import subprocess
import urllib.request
from pathlib import Path
from typing import Optional, Dict, List
import json

from thermalright_lcd_control.common.platform_utils import is_windows
from thermalright_lcd_control.common.logging_config import get_gui_logger


class ZadigManager:
    """
    Manages Zadig tool for USB driver installation
    
    Zadig is a USB driver installation tool that can install:
    - WinUSB
    - libusb-win32
    - libusbK
    
    For Thermalright devices, WinUSB is recommended.
    """
    
    ZADIG_DOWNLOAD_URL = "https://github.com/pbatard/zadig/releases/latest/download/zadig.exe"
    ZADIG_FILENAME = "zadig.exe"
    
    # Supported Thermalright devices
    SUPPORTED_DEVICES = [
        {'vid': 0x0416, 'pid': 0x5302, 'name': 'Thermalright LCD 320x240'},
        {'vid': 0x0418, 'pid': 0x5304, 'name': 'Thermalright LCD 480x480'},
        {'vid': 0x87AD, 'pid': 0x70DB, 'name': 'ChiZhu Tech USBDISPLAY'},
    ]
    
    def __init__(self, zadig_path: Optional[Path] = None):
        """
        Initialize Zadig manager
        
        Args:
            zadig_path: Path to zadig.exe. If None, uses default download location.
        """
        self.logger = get_gui_logger()
        
        if not is_windows():
            raise RuntimeError("Zadig manager only works on Windows")
        
        if zadig_path is None:
            # Use AppData\Local\thermalright-lcd-control
            from thermalright_lcd_control.common.platform_utils import get_data_dir
            data_dir = Path(get_data_dir())
            self.zadig_path = data_dir / self.ZADIG_FILENAME
        else:
            self.zadig_path = Path(zadig_path)
    
    def is_zadig_available(self) -> bool:
        """Check if Zadig is downloaded and available"""
        return self.zadig_path.exists()
    
    def download_zadig(self, progress_callback=None) -> bool:
        """
        Download Zadig from official GitHub releases
        
        Args:
            progress_callback: Optional callback function for download progress
            
        Returns:
            True if download successful
        """
        try:
            self.logger.info(f"Downloading Zadig from {self.ZADIG_DOWNLOAD_URL}")
            
            # Create directory if needed
            self.zadig_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with progress
            def reporthook(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    progress = min(100, (downloaded * 100) // total_size)
                    progress_callback(progress)
            
            urllib.request.urlretrieve(
                self.ZADIG_DOWNLOAD_URL,
                self.zadig_path,
                reporthook=reporthook
            )
            
            if self.zadig_path.exists():
                self.logger.info(f"Zadig downloaded to {self.zadig_path}")
                return True
            else:
                self.logger.error("Zadig download failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error downloading Zadig: {e}")
            return False
    
    def detect_thermalright_devices(self) -> List[Dict]:
        """
        Detect Thermalright USB devices
        
        Returns:
            List of detected devices with their info
        """
        detected = []
        
        try:
            import usb.core
            
            for device_info in self.SUPPORTED_DEVICES:
                dev = usb.core.find(
                    idVendor=device_info['vid'],
                    idProduct=device_info['pid']
                )
                
                if dev:
                    status = self.check_device_driver_status(device_info['vid'], device_info['pid'])
                    detected.append({
                        **device_info,
                        'detected': True,
                        'driver_status': status
                    })
                    self.logger.info(f"Found device: {device_info['name']} (VID:{device_info['vid']:04x} PID:{device_info['pid']:04x})")
        
        except ImportError:
            self.logger.warning("pyusb not available for device detection")
        except Exception as e:
            self.logger.error(f"Error detecting devices: {e}")
        
        return detected
    
    def check_device_driver_status(self, vid: int, pid: int) -> Dict:
        """
        Check the driver status for a USB device
        
        Args:
            vid: Vendor ID
            pid: Product ID
            
        Returns:
            Dict with driver status information
        """
        try:
            import usb.core
            
            dev = usb.core.find(idVendor=vid, idProduct=pid)
            
            if not dev:
                return {'status': 'not_found', 'message': 'Device not connected'}
            
            # Try to access the device
            try:
                # Check if we can access device configuration
                config = dev.get_active_configuration()
                
                return {
                    'status': 'accessible',
                    'message': 'Device accessible',
                    'driver': 'WinUSB or compatible'
                }
                
            except usb.core.USBError as e:
                if 'Access denied' in str(e) or 'Access is denied' in str(e):
                    return {
                        'status': 'access_denied',
                        'message': 'Driver missing or incompatible',
                        'error': str(e),
                        'recommendation': 'Install WinUSB driver using Zadig'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Device communication error',
                        'error': str(e)
                    }
        
        except Exception as e:
            self.logger.error(f"Error checking driver status: {e}")
            return {
                'status': 'unknown',
                'message': 'Could not determine driver status',
                'error': str(e)
            }
    
    def launch_zadig_for_device(self, vid: int, pid: int) -> bool:
        """
        Launch Zadig with instructions to install driver for specific device
        
        Args:
            vid: Vendor ID
            pid: Product ID
            
        Returns:
            True if Zadig launched successfully
        """
        if not self.is_zadig_available():
            self.logger.error("Zadig not available. Download it first.")
            return False
        
        try:
            # Launch Zadig
            # Note: Zadig doesn't support command-line device selection,
            # so we just launch it and provide instructions
            self.logger.info("Launching Zadig...")
            
            subprocess.Popen([str(self.zadig_path)])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error launching Zadig: {e}")
            return False
    
    def get_installation_instructions(self, vid: int, pid: int) -> Dict:
        """
        Get step-by-step instructions for installing driver with Zadig
        
        Args:
            vid: Vendor ID
            pid: Product ID
            
        Returns:
            Dict with installation instructions
        """
        # Find device info
        device_info = None
        for dev in self.SUPPORTED_DEVICES:
            if dev['vid'] == vid and dev['pid'] == pid:
                device_info = dev
                break
        
        if not device_info:
            device_name = f"Device {vid:04x}:{pid:04x}"
        else:
            device_name = device_info['name']
        
        return {
            'device': device_name,
            'vid': f"{vid:04x}",
            'pid': f"{pid:04x}",
            'driver': 'WinUSB',
            'steps': [
                {
                    'number': 1,
                    'title': 'Launch Zadig',
                    'description': 'Open Zadig.exe (will be launched automatically)',
                    'image_hint': 'zadig_main_window.png'
                },
                {
                    'number': 2,
                    'title': 'Enable "List All Devices"',
                    'description': 'Click Options → List All Devices',
                    'image_hint': 'zadig_options_menu.png'
                },
                {
                    'number': 3,
                    'title': 'Select Your Device',
                    'description': f'In the dropdown, find and select your device:\n'
                                 f'Look for "{device_name}" or "USB ID {vid:04x}:{pid:04x}"',
                    'image_hint': 'zadig_device_selection.png'
                },
                {
                    'number': 4,
                    'title': 'Select WinUSB Driver',
                    'description': 'In the driver selection (middle), choose "WinUSB"',
                    'note': 'If another driver is already installed, you can replace it',
                    'image_hint': 'zadig_driver_selection.png'
                },
                {
                    'number': 5,
                    'title': 'Install Driver',
                    'description': 'Click "Install Driver" or "Replace Driver" button',
                    'warning': 'This may take a minute. Do not disconnect the device.',
                    'image_hint': 'zadig_install_button.png'
                },
                {
                    'number': 6,
                    'title': 'Verify Installation',
                    'description': 'Wait for "Driver installed successfully" message',
                    'action': 'After installation, restart Thermalright LCD Control',
                    'image_hint': 'zadig_success.png'
                }
            ],
            'notes': [
                'Administrator privileges required',
                'Keep the device connected during installation',
                'If installation fails, try a different USB port',
                'Some antivirus software may interfere - temporarily disable if needed'
            ],
            'troubleshooting': {
                'device_not_listed': 'Try enabling "List All Devices" in Options menu',
                'installation_failed': 'Run Zadig as Administrator and try again',
                'driver_conflict': 'Use "Replace Driver" option to replace existing driver',
                'access_denied': 'Close any applications that might be using the device'
            }
        }
    
    def create_driver_installation_script(self) -> Path:
        """
        Create a helper script for automated driver installation
        
        Returns:
            Path to the created script
        """
        script_path = self.zadig_path.parent / "install_usb_driver.txt"
        
        instructions = []
        for device in self.SUPPORTED_DEVICES:
            inst = self.get_installation_instructions(device['vid'], device['pid'])
            instructions.append({
                'device': inst['device'],
                'vid_pid': f"{device['vid']:04x}:{device['pid']:04x}",
                'steps': [step['description'] for step in inst['steps']]
            })
        
        # Write to file
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("Thermalright LCD Control - USB Driver Installation Guide\n")
            f.write("=" * 60 + "\n\n")
            
            for inst in instructions:
                f.write(f"Device: {inst['device']} ({inst['vid_pid']})\n")
                f.write("-" * 60 + "\n")
                for i, step in enumerate(inst['steps'], 1):
                    f.write(f"{i}. {step}\n")
                f.write("\n")
        
        self.logger.info(f"Created driver installation guide: {script_path}")
        return script_path


def main():
    """Test Zadig manager"""
    manager = ZadigManager()
    
    print("=" * 60)
    print("Zadig USB Driver Manager")
    print("=" * 60)
    print()
    
    print("Zadig Status:")
    if manager.is_zadig_available():
        print(f"  ✓ Available at {manager.zadig_path}")
    else:
        print(f"  ✗ Not found at {manager.zadig_path}")
        print()
        response = input("  Download Zadig now? (y/n): ")
        if response.lower() == 'y':
            print("  Downloading...")
            if manager.download_zadig():
                print("  ✓ Download successful")
            else:
                print("  ✗ Download failed")
    
    print()
    print("Detecting Thermalright Devices:")
    devices = manager.detect_thermalright_devices()
    
    if devices:
        for device in devices:
            print(f"  ✓ {device['name']}")
            print(f"    VID:PID = {device['vid']:04x}:{device['pid']:04x}")
            status = device.get('driver_status', {})
            print(f"    Status: {status.get('message', 'Unknown')}")
            if status.get('recommendation'):
                print(f"    → {status['recommendation']}")
    else:
        print("  ✗ No devices detected")
        print("  Make sure your Thermalright device is connected")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
