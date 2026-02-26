# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
System Checker for Thermalright LCD Control

Performs comprehensive system diagnostics to identify potential issues:
- Python version verification
- Dependency checks
- USB device detection
- GPU driver detection
- Window capture dependencies
- iStripper installation
- Service status (Windows)
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

from thermalright_lcd_control.common.platform_utils import is_windows, is_linux
from thermalright_lcd_control.common.logging_config import get_gui_logger


class DiagnosticCheck:
    """Represents a single diagnostic check result"""
    
    def __init__(self, name: str, passed: bool, message: str, fix_hint: str = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.fix_hint = fix_hint
    
    def __repr__(self):
        status = "✓" if self.passed else "✗"
        return f"{status} {self.name}: {self.message}"


class SystemChecker:
    """
    Comprehensive system diagnostics checker
    
    Checks all requirements and provides actionable feedback for issues.
    """
    
    def __init__(self):
        self.logger = get_gui_logger()
        self.checks: List[DiagnosticCheck] = []
    
    def run_all_checks(self) -> List[DiagnosticCheck]:
        """Run all diagnostic checks"""
        self.checks = []
        
        # Core checks
        self.check_python_version()
        self.check_dependencies()
        
        # Platform-specific checks
        if is_windows():
            self.check_windows_specific()
            self.check_video_codecs()  # Windows 11 codec check
        elif is_linux():
            self.check_linux_specific()
        
        # Device and GPU checks
        self.check_usb_device()
        self.check_gpu_support()
        
        # Optional feature checks
        self.check_window_capture()
        self.check_istripper()
        
        return self.checks
    
    def check_python_version(self):
        """Check Python version (3.10+ required)"""
        version = sys.version_info
        required = (3, 10)
        
        if version >= required:
            self.checks.append(DiagnosticCheck(
                "Python Version",
                True,
                f"Python {version.major}.{version.minor}.{version.micro} (required: {required[0]}.{required[1]}+)"
            ))
        else:
            self.checks.append(DiagnosticCheck(
                "Python Version",
                False,
                f"Python {version.major}.{version.minor}.{version.micro} is too old",
                f"Install Python {required[0]}.{required[1]} or higher from python.org"
            ))
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        # List of (import_name, pip_package_name) tuples
        required_packages = [
            ('PySide6', 'PySide6'),
            ('psutil', 'psutil'),
            ('cv2', 'opencv-python'),
            ('usb', 'pyusb'),
            ('PIL', 'pillow'),
            ('yaml', 'pyyaml'),
        ]
        
        # Each entry is (display_label, pip_name)
        missing: list[tuple[str, str]] = []
        for import_name, package_name in required_packages:
            try:
                __import__(import_name)
            except ImportError:
                missing.append((package_name, package_name))
        
        # Check the hid package separately: it may be installed but fail to load
        # the native hidapi library (raises ImportError with a descriptive message).
        try:
            import hid  # noqa: F401
        except ImportError as e:
            err = str(e)
            if any(lib in err for lib in ('hidapi', 'dll', 'library', '.so', 'dylib')):
                missing.append(('hid (native hidapi library missing – see fix hint below)', 'hid'))
            else:
                missing.append(('hid', 'hid'))
        
        if not missing:
            self.checks.append(DiagnosticCheck(
                "Required Dependencies",
                True,
                "All required packages are installed"
            ))
        else:
            display_names = ', '.join(label for label, _ in missing)
            pip_names = ' '.join(pip for _, pip in missing)
            self.checks.append(DiagnosticCheck(
                "Required Dependencies",
                False,
                f"Missing packages: {display_names}",
                f"Install with: pip install {pip_names}"
            ))
    
    def check_windows_specific(self):
        """Windows-specific checks"""
        # Check pywin32 for service support
        try:
            import win32serviceutil
            self.checks.append(DiagnosticCheck(
                "Windows Service Support",
                True,
                "pywin32 is installed (service support available)"
            ))
        except ImportError:
            self.checks.append(DiagnosticCheck(
                "Windows Service Support",
                False,
                "pywin32 not installed (no service support)",
                "Install with: pip install pywin32"
            ))
        
        # Check if running as Administrator
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin:
                self.checks.append(DiagnosticCheck(
                    "Administrator Privileges",
                    True,
                    "Running with Administrator privileges"
                ))
            else:
                self.checks.append(DiagnosticCheck(
                    "Administrator Privileges",
                    False,
                    "Not running as Administrator",
                    "USB device access may require Administrator privileges. Right-click and 'Run as Administrator'"
                ))
        except Exception:
            pass

        # Check hidapi native library (required by the hid Python package)
        self._check_hidapi_native_library()

        # Check libusb native library (required by pyusb for USB bulk devices)
        self._check_libusb_native_library()

    def _check_hidapi_native_library(self):
        """Check that the hidapi native DLL can be loaded (Windows only)"""
        try:
            import hid  # noqa: F401
            self.checks.append(DiagnosticCheck(
                "HID Native Library (hidapi.dll)",
                True,
                "hidapi native library loaded successfully"
            ))
        except ImportError as e:
            self.checks.append(DiagnosticCheck(
                "HID Native Library (hidapi.dll)",
                False,
                f"hidapi.dll not found: {e}",
                "Run install_windows.bat (or .ps1) – it downloads hidapi.dll automatically. "
                "Or manually place hidapi.dll in your venv\\Scripts\\ folder. "
                "Download from: https://github.com/libusb/hidapi/releases"
            ))

    def _check_libusb_native_library(self):
        """Check that libusb is available for pyusb (Windows only)"""
        try:
            import usb.backend.libusb1 as _lb1
            backend = _lb1.get_backend()
            if backend is not None:
                self.checks.append(DiagnosticCheck(
                    "USB Native Library (libusb)",
                    True,
                    "libusb backend loaded successfully (pyusb USB bulk devices work)"
                ))
            else:
                raise RuntimeError("no backend found")
        except Exception as e:
            self.checks.append(DiagnosticCheck(
                "USB Native Library (libusb)",
                False,
                f"libusb not found: {e}",
                "Install libusb-package: pip install libusb-package>=1.0.26  "
                "(already included in pip install .[windows])"
            ))
    
    def check_linux_specific(self):
        """Linux-specific checks"""
        # Check for udev rules
        udev_rules_path = Path("/etc/udev/rules.d")
        if udev_rules_path.exists():
            rules_files = list(udev_rules_path.glob("*thermalright*"))
            if rules_files:
                self.checks.append(DiagnosticCheck(
                    "USB Permissions (udev rules)",
                    True,
                    f"udev rules found: {', '.join(f.name for f in rules_files)}"
                ))
            else:
                self.checks.append(DiagnosticCheck(
                    "USB Permissions (udev rules)",
                    False,
                    "No udev rules found for Thermalright devices",
                    "USB access may require running as root or setting up udev rules"
                ))
    
    def check_usb_device(self):
        """Check if USB device is detected"""
        try:
            import usb.core
            
            # Check for known Thermalright devices
            known_devices = [
                (0x0416, 0x5302),
                (0x0418, 0x5304),
                (0x87AD, 0x70DB),
            ]
            
            found_devices = []
            for vid, pid in known_devices:
                dev = usb.core.find(idVendor=vid, idProduct=pid)
                if dev:
                    found_devices.append(f"{vid:04x}:{pid:04x}")
            
            if found_devices:
                self.checks.append(DiagnosticCheck(
                    "USB Device Detection",
                    True,
                    f"Found device(s): {', '.join(found_devices)}"
                ))
            else:
                self.checks.append(DiagnosticCheck(
                    "USB Device Detection",
                    False,
                    "No Thermalright USB device found",
                    "Check: Device is connected, USB cable is working, drivers installed (Windows)"
                ))
                
        except Exception as e:
            self.checks.append(DiagnosticCheck(
                "USB Device Detection",
                False,
                f"Error checking USB devices: {e}",
                "Ensure pyusb is installed and USB access is permitted"
            ))
    
    def check_gpu_support(self):
        """Check GPU support"""
        try:
            from thermalright_lcd_control.device_controller.metrics.gpu_metrics import GpuMetrics
            
            gpu = GpuMetrics()
            if gpu.gpu_vendor:
                self.checks.append(DiagnosticCheck(
                    "GPU Detection",
                    True,
                    f"Detected: {gpu.gpu_name} ({gpu.gpu_vendor})"
                ))
            else:
                self.checks.append(DiagnosticCheck(
                    "GPU Detection",
                    False,
                    "No GPU detected or GPU metrics unavailable",
                    "Check GPU drivers are installed. AMD/Intel support is Linux-only currently."
                ))
                
        except Exception as e:
            self.checks.append(DiagnosticCheck(
                "GPU Detection",
                False,
                f"Error detecting GPU: {e}",
                "GPU metrics may not be available"
            ))
    
    def check_window_capture(self):
        """Check window capture dependencies"""
        if is_windows():
            required = [('mss', 'mss'), ('pygetwindow', 'pygetwindow')]
        elif is_linux():
            required = [('Xlib', 'python-xlib')]
        else:
            return
        
        missing = []
        for import_name, package_name in required:
            try:
                __import__(import_name)
            except ImportError:
                missing.append(package_name)
        
        if not missing:
            self.checks.append(DiagnosticCheck(
                "Window Capture Support",
                True,
                "Window capture dependencies installed (iStripper support available)"
            ))
        else:
            self.checks.append(DiagnosticCheck(
                "Window Capture Support",
                False,
                f"Missing: {', '.join(missing)}",
                f"Install for iStripper support: pip install {' '.join(missing)}"
            ))
    
    def check_istripper(self):
        """Check if iStripper is installed"""
        try:
            from thermalright_lcd_control.common.app_detector import find_istripper_path
            
            path = find_istripper_path()
            if path:
                self.checks.append(DiagnosticCheck(
                    "iStripper Installation",
                    True,
                    f"Found at: {path}"
                ))
            else:
                self.checks.append(DiagnosticCheck(
                    "iStripper Installation",
                    False,
                    "iStripper not detected",
                    "iStripper integration is optional. Install from istripper.com if desired."
                ))
        except Exception:
            # iStripper check is optional, don't fail
            pass
    
    def check_video_codecs(self):
        """Check video codec support (Windows only)"""
        try:
            from thermalright_lcd_control.utils.codec_detector import CodecDetector
            
            detector = CodecDetector()
            result = detector.detect_all_codecs()
            
            # Check for codec packs
            has_codecs = bool(result.get('codec_packs'))
            has_ffmpeg = bool(result.get('ffmpeg'))
            
            if has_codecs or has_ffmpeg:
                codec_names = []
                if result.get('codec_packs'):
                    codec_names.extend(result['codec_packs'].keys())
                if has_ffmpeg:
                    codec_names.append('FFmpeg')
                
                self.checks.append(DiagnosticCheck(
                    "Video Codec Support",
                    True,
                    f"Codecs installed: {', '.join(codec_names)}"
                ))
            else:
                self.checks.append(DiagnosticCheck(
                    "Video Codec Support",
                    False,
                    "No video codec packs detected",
                    "Install K-Lite Codec Pack for video playback support. Run: python -m thermalright_lcd_control.utils.codec_detector"
                ))
            
            # Check OpenCV codec support
            opencv_info = result.get('opencv_codecs', {})
            if 'error' not in opencv_info:
                if opencv_info.get('ffmpeg_support') or opencv_info.get('media_foundation_support'):
                    self.checks.append(DiagnosticCheck(
                        "OpenCV Video Support",
                        True,
                        f"OpenCV {opencv_info.get('opencv_version', 'Unknown')} with video backend support"
                    ))
                else:
                    self.checks.append(DiagnosticCheck(
                        "OpenCV Video Support",
                        False,
                        "OpenCV lacks video codec support",
                        "Reinstall opencv-python: pip uninstall opencv-python && pip install opencv-python"
                    ))
        
        except ImportError:
            # Codec detector not available
            pass
        except Exception as e:
            self.logger.debug(f"Error checking codecs: {e}")
            pass
    
    def print_report(self):
        """Print diagnostic report to console"""
        print("\n" + "=" * 60)
        print("Thermalright LCD Control - System Diagnostics")
        print("=" * 60 + "\n")
        
        passed = sum(1 for check in self.checks if check.passed)
        total = len(self.checks)
        
        for check in self.checks:
            print(check)
            if not check.passed and check.fix_hint:
                print(f"  → Fix: {check.fix_hint}")
            print()
        
        print("=" * 60)
        print(f"Results: {passed}/{total} checks passed")
        print("=" * 60 + "\n")
        
        if passed < total:
            print("⚠ Some issues detected. See fix hints above.")
            print("  For more help, see: docs/TROUBLESHOOTING_WINDOWS.md")
        else:
            print("✓ All checks passed! System is ready.")
        print()
    
    def generate_report_dict(self) -> Dict:
        """Generate report as a dictionary for GUI display"""
        return {
            'checks': [
                {
                    'name': check.name,
                    'passed': check.passed,
                    'message': check.message,
                    'fix_hint': check.fix_hint
                }
                for check in self.checks
            ],
            'summary': {
                'total': len(self.checks),
                'passed': sum(1 for c in self.checks if c.passed),
                'failed': sum(1 for c in self.checks if not c.passed)
            }
        }


def main():
    """Command-line diagnostic tool"""
    print("Running system diagnostics...")
    print()
    
    checker = SystemChecker()
    checker.run_all_checks()
    checker.print_report()
    
    # Return exit code based on results
    failed = sum(1 for check in checker.checks if not check.passed)
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
