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

**New in this version:** Full Windows 11 support with video playback (audio automatically disabled for LCD display).

## Features

- 🖥️ **User-friendly GUI** - Modern interface for device configuration
- ⚙️ **Background service** - Automatic device management (Linux) or application mode (Windows)
- 🎨 **Theme support** - Customizable display themes and backgrounds
- 🎬 **Video playback** - Support for video files (MP4, AVI, MKV, MOV, etc.) without audio
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

1. **Python 3.8 or higher** - Download from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"

2. **Microsoft Visual C++ Redistributable** - Usually already installed, but if needed, download from [Microsoft](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

#### Installation Steps

1. **Download** the release package from the [Releases](https://www.github.com/rejeb/thermalright-lcd-control/releases) page

2. **Extract** the package to a directory (e.g., `C:\Program Files\thermalright-lcd-control`)

3. **Install dependencies** using pip:
   ```powershell
   pip install PySide6 hid psutil opencv-python pyusb pillow pyyaml
   ```

4. **Run the application**:
   ```powershell
   python -m thermalright_lcd_control.main_gui
   ```

#### Video Playback on Windows

The application supports video playback on Windows 11 using OpenCV. All video files play **without audio** - only the visual frames are displayed on the LCD screen. Supported formats include:
- MP4, AVI, MKV, MOV, WEBM, FLV, WMV, M4V

**Note:** Audio is automatically disabled by OpenCV's VideoCapture - no sound will be played through your system speakers.

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
- For AMD/Intel GPUs on Windows, metrics are limited to what psutil can detect

**Performance issues:**
- Large video files are loaded entirely into memory - use shorter videos or lower resolutions
- Close other applications that may interfere with USB communication

## Usage

### Launch the Application

- **From Applications Menu**: Search for "Thermalright LCD Control" in your application launcher
- **From Terminal**: Run `thermalright-lcd-control`

### System Service

The background service starts automatically after installation. You can manage it using:

# Check service status

sudo systemctl status thermalright-lcd-control.service

# Restart service

sudo systemctl restart thermalright-lcd-control.service

# Stop service

sudo systemctl stop thermalright-lcd-control.service

## System Requirements

- **Operating System**: Ubuntu 20.04+ / Debian 11+ / Other modern Linux distributions
- **Python**: 3.8 or higher (automatically managed)
- **Desktop Environment**: Any modern Linux desktop (GNOME, KDE, XFCE, etc.)
- **Hardware**: Compatible Thermalright LCD device

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
