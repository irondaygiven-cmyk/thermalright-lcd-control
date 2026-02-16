# Thermalright LCD Control

A cross-platform application for controlling Thermalright LCD displays with an intuitive graphical interface.

![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%2011-lightgrey.svg)
![version](https://img.shields.io/badge/version-1.3.1-green.svg)

## Overview

Thermalright LCD Control provides an easy-to-use interface for managing your Thermalright LCD display on Linux and Windows 11 systems.

The application features both a desktop GUI and a background service for seamless device control.

I performed reverse engineering on the Thermalright Windows application to understand its internal mechanisms.

During my analysis, I identified four different USB VID:PID combinations handled by the Windows application, all sharing
the same interaction logic.

Since I have access only to the Frozen Warframe 420 BLACK ARGB, my testing was limited exclusively to this specific
device.

Also, this application implements reading metrics from AMD, Nvidia, and Intel GPU. My testing was limited to Nvidia GPU.

Feel free to contribute to this project and let me know if the application is working with other devices.

For backgrounds, i have included all media formats supported by the Windows application
and added the option to select a collection of images to cycle through on the display.

**New in this version:** Full Windows 11 support with video playback (audio automatically disabled, seamless looping).

## Features

- 🖥️ **User-friendly GUI** - Modern interface for device configuration
- ⚙️ **Background service** - Automatic device management (Linux) or application mode (Windows)
- 🎨 **Theme support** - Customizable display themes and backgrounds
- 🎬 **Video playback** - Support for video files (MP4, AVI, MKV, MOV, etc.) without audio, continuous looping
- 🔄 **Seamless looping** - Videos, GIFs, and image collections loop continuously until changed
- 🔄 **Display rotation** - Rotate images and videos at any angle (0°, 90°, 180°, 270°, or custom angles)
- 🔍 **Content scaling** - Manual zoom control for videos and iStripper (zoom in/out with scale_factor)
- 🖼️ **iStripper integration** - Capture and display content from iStripper or other applications
- 📋 **System integration** - Native Linux desktop integration
- 🪟 **Windows 11 support** - Full compatibility with Windows 11
- 🔌 **Cross-platform** - Works on both Linux and Windows 11

## Supported devices

| VID:PID   | SCREEN RESOLUTION |
|-----------|-------------------|
| 0416:5302 | 320x240           |
| 0418:5304 | 480x480           |
| 87AD:70DB | 320x320,480x480   |

## Installation

### Linux Installation

#### Download Packages

Download the appropriate package for your Linux distribution from
the [Releases](https://www.github.com/rejeb/thermalright-lcd-control/releases) page:

- **`.tar.gz`** - For any distribution

#### Installation Steps

1. **Check** for required dependencies:
   /!\ Make sure you have these required dependencies installed:
    - python3
    - python3-pip
    - python3-venv
    - libhidapi-* or hidapi depending on your distribution

2. **Download** the `.tar.gz` package:
   ```bash
   wget https://github.com/rejeb/thermalright-lcd-control/releases/download/1.3.1/thermalright-lcd-control-1.3.1.tar.gz -P /tmp/
   ```

3. **Untar** the archive file:
   ```bash
   cd /tmp
   
   tar -xvf thermalright-lcd-control-1.3.1.tar.gz
   ```

4. **Install** application:
   ```bash
   cd /thermalright-lcd-control
   
   sudo bash install.sh
   ```

That's it! The application is now installed. You can see the default theme displayed on your Thermalright LCD device.

### Windows 11 Installation

#### Prerequisites

1. **Python 3.10 or higher** - Download from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"

2. **Microsoft Visual C++ Redistributable** - Usually already installed, but if needed, download from [Microsoft](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

#### Installation Steps

1. **Download** the release package from the [Releases](https://www.github.com/rejeb/thermalright-lcd-control/releases) page

2. **Extract** the package to a directory (e.g., `C:\Program Files\thermalright-lcd-control`)

3. **Run the installer** (Recommended):
   
   **PowerShell (Recommended):**
   ```powershell
   # Right-click PowerShell, select "Run as Administrator"
   .\install_windows.ps1
   ```
   
   **Or Batch File:**
   ```cmd
   # Right-click install_windows.bat, select "Run as Administrator"
   ```
   
   The installer will:
   - Check for Python and pip
   - **Automatically detect iStripper and VLC** if installed
     - Searches C:\Program Files and C:\Program Files (x86) by default
     - **Option to search all drives** for iStripper (D:, E:, etc.)
     - Checks common installation directories (Games, root directories)
   - Install all required dependencies
   - Create a configuration file with detected application paths
   - Optionally create a desktop shortcut

4. **Manual installation** (Alternative):
   ```powershell
   # Core dependencies (required)
   pip install PySide6 hid psutil opencv-python pyusb pillow pyyaml
   
   # Optional: For iStripper/window capture support
   pip install mss pygetwindow
   ```

5. **Run the application**:
   ```powershell
   python -m thermalright_lcd_control.main_gui
   ```

#### Video Playback on Windows

The application supports video playback on Windows 11 using OpenCV. All video files play **without audio** - only the visual frames are displayed on the LCD screen. Supported formats include:
- MP4, AVI, MKV, MOV, WEBM, FLV, WMV, M4V

**Video Features:**
- ✅ **Audio automatically disabled** - No sound will be played through your system speakers
- ✅ **Continuous looping** - Videos loop seamlessly until you select a different image or video
- ✅ **Full frame rate** - Videos play at their original FPS for smooth playback
- ✅ **Automatic resizing** - Videos are automatically scaled to fit your LCD display resolution
- ✅ **Rotation support** - Rotate videos at any angle (see Display Rotation section below)

#### Display Rotation

Adjust the viewing angle of all media types (images, videos, GIFs, image collections, window capture):

**Configuration:** Edit your config YAML file and set the `rotation` value:

```yaml
display:
  rotation: 90  # Rotate 90 degrees clockwise
  # Other options: 0 (no rotation), 180 (upside down), 270 (rotate left)
  # Or use custom angles: 45, 135, etc.
```

**Supported Angles:**
- **Standard angles** (0°, 90°, 180°, 270°) - Fast, no quality loss
- **Custom angles** (any degree 0-360) - Flexible, slight edge cropping

**Use Cases:**
- Mount your LCD at different orientations
- Adjust for display mounting position
- Correct orientation for window capture

#### Content Scaling (Zoom)

Manually adjust the scale/zoom of videos and iStripper window capture:

**Configuration:** Edit your config YAML file and set the `scale_factor` value:

```yaml
display:
  scale_factor: 1.5  # 150% zoom (zoom in)
  # Other options:
  # 1.0 - Original size (default, no scaling)
  # 0.5 - 50% size (zoom out, shows more content with black borders)
  # 1.5 - 150% size (zoom in, crops edges)
  # 2.0 - 200% size (2x zoom in, crops more)
```

**How it works:**
- **scale_factor = 1.0** - Original size, no scaling applied
- **scale_factor < 1.0** (e.g., 0.5) - **Zoom out** - Content is smaller with black padding
- **scale_factor > 1.0** (e.g., 1.5) - **Zoom in** - Content is larger, cropped from center

**Applies to:**
- ✅ Videos (MP4, AVI, MKV, etc.)
- ✅ Window capture (iStripper, VLC, etc.)
- ✅ Static images
- ✅ GIFs
- ✅ Image collections

**Use Cases:**
- Zoom in on iStripper performers
- Crop unwanted edges from videos
- Adjust video framing for LCD display
- Fit content better to your screen

#### iStripper Integration

Capture and display content from iStripper or any other application window:

**Automatic Detection:**

The Windows installer automatically searches for iStripper and VLC installations:
- Searches Program Files and Program Files (x86) directories on C: drive
- **Optional: Search all drives** (D:, E:, F:, etc.) when prompted
  - Checks Program Files on all fixed drives
  - Checks Games folders and root directories
  - Useful if iStripper is installed on a secondary drive
- Checks common installation subdirectories
- Saves detected paths to configuration file
- Shows detected applications at the end of installation

**Tip:** If iStripper is installed on a drive other than C:, choose "Y" when the installer asks to search all drives.

**Setup:**

1. **Install window capture dependencies:**
   ```powershell
   # Windows
   pip install mss pygetwindow
   
   # Linux
   pip install python-xlib
   ```

2. **Configure window capture** in your config YAML file:
   ```yaml
   display:
     background:
       type: "window_capture"
       path: ""  # Not used for window capture
     window_title: "iStripper"  # Window title to capture
     capture_fps: 30  # Frame rate for capture (adjust for performance)
     scale_factor: 1.5  # Optional: Zoom in 1.5x (default is 1.0)
     rotation: 0  # Optional: Rotate display (default is 0)
   ```

3. **Start iStripper** before launching the LCD control application

**Features:**
- ✅ **Real-time capture** - Live display of application window content
- ✅ **Configurable FPS** - Adjust capture rate for performance (15-60 FPS)
- ✅ **Manual scaling** - Zoom in/out with scale_factor (see Content Scaling section)
- ✅ **Rotation support** - Rotate captured content at any angle
- ✅ **Works with any app** - Not limited to iStripper, works with any window title

**Supported Applications:**
- iStripper
- Video players (VLC, MPC-HC, etc.)
- Web browsers
- Any application with a window title

#### GPU Metrics on Windows

- ✅ **NVIDIA GPUs**: Fully supported via nvidia-smi (must have NVIDIA drivers installed)
- ⚠️ **AMD GPUs**: Limited support - temperature and usage via psutil only (no detailed metrics)
- ⚠️ **Intel GPUs**: Limited support - temperature via psutil only

For best experience on Windows, NVIDIA GPUs are recommended for full metrics support.

## Troubleshooting

### Linux

If your device is 0416:5302 and nothing is displayed:
- Check service status to see if it is running
- Try restart service
- Check service logs located in /var/log/thermalright-lcd-control.log

If your device is one of the other devices, contributions are welcome.
Here some tips to help you:
- Check service status to see if it is running
- Check service logs located in /var/log/thermalright-lcd-control.log
- If the device is not working then this possibly mean that header value is not correct.
See [Add new device](#add-new-device) section to fix header generation.
- If the device is working but image is not good, this means that the image is not encoded correctly.
See [Add new device](#add-new-device) section to fix image encoding by overriding method _`_encode_image`.

### Windows 11

**Device not detected:**
- Make sure Python has permission to access USB devices
- Try running the application as Administrator
- Check if the device is recognized in Device Manager
- Install/update USB HID drivers if needed

**Video playback issues:**
- Ensure OpenCV is installed: `pip install opencv-python`
- Check that the video codec is supported by your system
- Try converting the video to MP4 (H.264) format for best compatibility

**Metrics not showing:**
- CPU/GPU temperature requires appropriate drivers installed
- For NVIDIA GPUs, ensure nvidia-smi is accessible from command line
- For AMD/Intel GPUs on Windows:
  - Install WMI support: `pip install wmi` (included in windows extras)
  - For enhanced metrics, install OpenHardwareMonitor
- Run diagnostics: `python -m thermalright_lcd_control.diagnostics.system_checker`

**Performance issues:**
- Large video files are loaded entirely into memory - use shorter videos or lower resolutions
- Close other applications that may interfere with USB communication

## System Diagnostics

Run the built-in diagnostics tool to check your system configuration:

```bash
# Run system diagnostics
python -m thermalright_lcd_control.diagnostics.system_checker
```

The diagnostics tool checks:
- ✓ Python version (3.10+ required)
- ✓ All required dependencies
- ✓ USB device detection
- ✓ GPU detection and driver support
- ✓ Window capture dependencies (for iStripper)
- ✓ Windows service support (Windows only)
- ✓ Administrator privileges (Windows only)
- ✓ iStripper installation (if present)

The tool will provide actionable fix suggestions for any issues detected.

## Usage

### Linux - Launch the Application

- **From Applications Menu**: Search for "Thermalright LCD Control" in your application launcher
- **From Terminal**: Run `thermalright-lcd-control`

### Linux - System Service

The background service starts automatically after installation. You can manage it using:

```bash
# Check service status
sudo systemctl status thermalright-lcd-control.service

# Restart service
sudo systemctl restart thermalright-lcd-control.service

# Stop service
sudo systemctl stop thermalright-lcd-control.service
```

### Windows 11 - Launch the Application

- **Using launcher**: Double-click `run_gui_windows.bat` in the installation directory
- **From Command Prompt/PowerShell**: 
  ```powershell
  python -m thermalright_lcd_control.main_gui
  ```
- **Using Desktop Shortcut**: If you created one during installation, double-click it

### Windows 11 - Background Service (NEW!)

The application now supports running as a Windows service that starts automatically with your system:

#### Install Windows Service

1. **Open PowerShell or Command Prompt as Administrator**
2. **Navigate to the installation directory**
3. **Run the installer script:**
   ```powershell
   # Using PowerShell
   .\scripts\windows\install_windows_service.ps1
   
   # Or using batch file
   scripts\windows\install_windows_service.bat
   ```

The installer will:
- Check for required dependencies (pywin32)
- Install the Windows service
- Configure it to start automatically
- Optionally start the service immediately

#### Manage Windows Service

**Using Command Line:**
```powershell
# Start service
net start ThermalrightLCDControl

# Stop service
net stop ThermalrightLCDControl

# Check service status
sc query ThermalrightLCDControl

# Restart service
net stop ThermalrightLCDControl && net start ThermalrightLCDControl
```

**Using Service Manager CLI:**
```powershell
# Start the service
python -m thermalright_lcd_control.service.windows_service_manager start

# Stop the service
python -m thermalright_lcd_control.service.windows_service_manager stop

# Check status
python -m thermalright_lcd_control.service.windows_service_manager status

# Restart
python -m thermalright_lcd_control.service.windows_service_manager restart
```

**Using System Tray Icon:**
```powershell
# Launch system tray icon for easy control
python -m thermalright_lcd_control.ui.system_tray
```

The system tray icon provides:
- Service status indicator (running/stopped)
- Right-click menu for Start/Stop/Restart
- Quick access to configuration
- Quick access to GUI

#### Uninstall Windows Service

To remove the Windows service:

```powershell
# Using PowerShell
.\scripts\windows\uninstall_windows_service.ps1

# Or using batch file
scripts\windows\uninstall_windows_service.bat
```

#### View Service Logs

Service logs are written to Windows Event Viewer:

1. Press `Win + R` and type `eventvwr.msc`
2. Navigate to: Windows Logs → Application
3. Look for events from source "ThermalrightLCDControl"

## System Requirements

### Linux
- **Operating System**: Ubuntu 20.04+ / Debian 11+ / Other modern Linux distributions
- **Python**: 3.8 or higher (automatically managed)
- **Desktop Environment**: Any modern Linux desktop (GNOME, KDE, XFCE, etc.)
- **Hardware**: Compatible Thermalright LCD device
- **Additional**: libhidapi or hidapi package

### Windows 11
- **Operating System**: Windows 11 or Windows 10 (21H2+)
- **Python**: 3.10 or higher
- **Hardware**: Compatible Thermalright LCD device
- **Additional**: USB HID drivers (usually included with Windows)
- **For video playback**: OpenCV-supported video codecs
- **For Windows Service**: pywin32 package (auto-installed)
- **For GPU metrics**: 
  - NVIDIA GPU: NVIDIA drivers with nvidia-smi
  - AMD GPU: WMI support (basic metrics on Windows)
  - Intel GPU: WMI support (basic metrics on Windows)
- **For enhanced GPU metrics**: Install OpenHardwareMonitor for detailed AMD/Intel metrics

## Add new device

In [HOWTO.md](doc/HOWTO.md) I detail all the steps I gone through to find out how myy device works and all steps to add
a new device.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Author

**REJEB BEN REJEB** - [benrejebrejeb@gmail.com](mailto:benrejebrejeb@gmail.com)

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add my feature'`)
4. Push to your branch (`git push origin feature/my-feature`)
5. Create a Pull Request
