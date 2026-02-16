# Windows 11 Setup Guide

Complete guide for Windows 11-specific features and enhancements.

## Table of Contents

- [Auto-Start Configuration](#auto-start-configuration)
- [USB Driver Installation](#usb-driver-installation)
- [Video Codec Setup](#video-codec-setup)
- [iStripper Integration](#istripper-integration)
- [Troubleshooting](#troubleshooting)

## Auto-Start Configuration

Thermalright LCD Control offers two methods for auto-starting on Windows 11:

### Method 1: Windows Task Scheduler (Recommended)

**Advantages:**
- Lighter weight than Windows Service
- Starts at user logon (not system startup)
- Easier to manage
- No administrator required after initial setup

**Installation:**

```powershell
# Install auto-start task
python -m thermalright_lcd_control.utils.task_scheduler install

# Check status
python -m thermalright_lcd_control.utils.task_scheduler status

# Enable/disable
python -m thermalright_lcd_control.utils.task_scheduler enable
python -m thermalright_lcd_control.utils.task_scheduler disable

# Remove
python -m thermalright_lcd_control.utils.task_scheduler uninstall
```

**What it does:**
- Creates a scheduled task in Task Scheduler
- Launches system tray icon at user logon
- Task runs with normal user privileges (not elevated)

### Method 2: Windows Service

See [WINDOWS_SERVICE_SETUP.md](WINDOWS_SERVICE_SETUP.md) for full service documentation.

**When to use:**
- Need application running before user login
- Require system-level access
- Want service-level reliability features

### Choosing Between Methods

| Feature | Task Scheduler | Windows Service |
|---------|---------------|-----------------|
| Starts at | User logon | System startup |
| Privileges | User level | System level |
| Visibility | System tray | Background |
| Management | Task Scheduler | Service Manager |
| Complexity | Simple | Advanced |

**Recommendation:** Use Task Scheduler for most users, Windows Service for advanced scenarios.

## USB Driver Installation

Thermalright LCD devices require WinUSB drivers on Windows 11.

### Quick Installation

1. **Launch USB Driver Wizard:**

```powershell
python -m thermalright_lcd_control.gui.wizards.usb_driver_wizard
```

Or use command-line tool:

```powershell
python -m thermalright_lcd_control.utils.zadig_manager
```

### Installation Steps

The wizard will:

1. **Detect Your Device**
   - Automatically finds connected Thermalright devices
   - Shows current driver status

2. **Download Zadig**
   - Automatically downloads Zadig tool if needed
   - Shows download progress

3. **Guide Installation**
   - Provides step-by-step instructions
   - Shows what to select in Zadig

4. **Verify Installation**
   - Checks driver was installed correctly
   - Verifies device is accessible

### Manual Installation

If you prefer manual installation:

1. Download Zadig from https://zadig.akeo.ie/
2. Run Zadig as Administrator
3. Options → List All Devices
4. Select your Thermalright device (VID:PID shown in Device Manager)
5. Choose "WinUSB" driver
6. Click "Install Driver" or "Replace Driver"
7. Wait for completion
8. Restart Thermalright LCD Control

### Supported Devices

- VID:0416 PID:5302 - Thermalright LCD 320x240
- VID:0418 PID:5304 - Thermalright LCD 480x480
- VID:87AD PID:70DB - ChiZhu Tech USBDISPLAY

## Video Codec Setup

Windows 11 needs video codecs for video playback on the LCD.

### Check Codec Status

```powershell
# Run codec detector
python -m thermalright_lcd_control.utils.codec_detector
```

Output shows:
- Installed codec packs (K-Lite, LAV Filters)
- FFmpeg availability
- OpenCV codec support
- Windows Media Foundation status
- Recommendations for missing codecs

### Recommended Codec Pack

**K-Lite Codec Pack Basic** (Recommended)

**Advantages:**
- Comprehensive codec support
- Includes LAV Filters
- Small download (~50 MB)
- Free and regularly updated

**Installation:**

1. Download from https://codecguide.com/download_kl.htm
2. Run installer as Administrator
3. Use default settings (recommended)
4. Restart Thermalright LCD Control

**What you get:**
- H.264, H.265/HEVC support
- VP9, AV1 support
- All common formats (MP4, AVI, MKV, MOV, etc.)
- LAV Filters for OpenCV

### Alternative: FFmpeg

If you only need video conversion (not playback):

```powershell
# Install FFmpeg (using Chocolatey)
choco install ffmpeg

# Or download manually from:
# https://ffmpeg.org/download.html
```

### Verify Video Support

```powershell
# After installing codecs, verify:
python -m thermalright_lcd_control.utils.codec_detector

# Should show:
# ✓ K-Lite Codec Pack
# ✓ OpenCV FFmpeg support
# ✓ Windows Media Foundation enabled
```

### Troubleshooting Video Playback

If videos don't play:

1. **Check codecs:**
   ```powershell
   python -m thermalright_lcd_control.utils.codec_detector
   ```

2. **Reinstall OpenCV:**
   ```powershell
   pip uninstall opencv-python
   pip install opencv-python
   ```

3. **Install K-Lite Codec Pack** (see above)

4. **Check video file:**
   - Try a different video file
   - Use MP4 with H.264 codec (most compatible)
   - Convert with FFmpeg if needed:
     ```powershell
     ffmpeg -i input.mkv -c:v libx264 -c:a aac output.mp4
     ```

## iStripper Integration

Enhanced iStripper support with visual configuration wizard.

### Quick Setup

1. **Launch iStripper Wizard:**

```powershell
# From Python
python -c "from thermalright_lcd_control.gui.wizards.istripper_wizard import IStripperWizard; from PySide6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); w = IStripperWizard(); w.exec()"
```

### Wizard Features

**1. Auto-Detection**
- Finds iStripper installation automatically
- Checks if iStripper is running
- Detects process status in real-time

**2. Live Preview**
- Shows captured window content
- Updates in real-time
- Test before saving

**3. Visual Configuration**
- **FPS Slider:** 15-60 FPS (default: 30)
- **Scale Slider:** 0.5x-3.0x (default: 1.5x)
- **Rotation:** 0°, 90°, 180°, 270°

**4. One-Click Save**
- Generates configuration automatically
- Applies to your display config
- No manual YAML editing needed

### Manual Configuration

If you prefer manual configuration, edit your config YAML:

```yaml
display:
  background:
    type: "window_capture"
    path: ""
  window_title: "iStripper"
  capture_fps: 30
  scale_factor: 1.5
  rotation: 0
```

### Performance Tuning

**For smooth playback:**
- FPS: 30 (balanced)
- Scale: 1.5x (slight zoom)
- Close other applications

**For best quality:**
- FPS: 60 (smooth)
- Scale: 2.0x (more zoom)
- Ensure iStripper is not minimized

**For low-end systems:**
- FPS: 15 (lower CPU usage)
- Scale: 1.0x (no scaling)
- Reduce iStripper quality settings

## Troubleshooting

### Task Scheduler Issues

**Task doesn't start:**
```powershell
# Check task status
schtasks /Query /TN "\Thermalright\ThermalrightLCDControl"

# Try manual run
python -m thermalright_lcd_control.utils.task_scheduler run

# Check Task Scheduler Event Viewer:
# Event Viewer → Applications and Services Logs → Microsoft → Windows → TaskScheduler → Operational
```

**Task runs but app doesn't start:**
- Verify Python is in system PATH
- Check task properties in Task Scheduler
- Ensure working directory is correct

### USB Driver Issues

**Device not detected:**
```powershell
# Check Device Manager
# Look for:
# - Unknown Device
# - Device with yellow triangle
# - Under "Universal Serial Bus devices"
```

**Driver installation failed:**
- Run Zadig as Administrator
- Try different USB port
- Temporarily disable antivirus
- Check Windows Defender isn't blocking

**Access denied after driver install:**
- Unplug and replug device
- Restart computer
- Verify WinUSB driver in Device Manager

### Codec Issues

**Video doesn't play:**
1. Check codec status:
   ```powershell
   python -m thermalright_lcd_control.utils.codec_detector
   ```

2. Install K-Lite Codec Pack

3. Verify OpenCV:
   ```powershell
   python -c "import cv2; print(cv2.__version__); print(cv2.getBuildInformation())"
   ```

4. Test with simple MP4 file first

### iStripper Issues

**Window not captured:**
- Ensure iStripper is running
- Window must not be minimized
- Try different window title ("iStripper" or "VirtuaGirl HD")
- Check window capture dependencies:
  ```powershell
  pip install mss pygetwindow
  ```

**Preview is black:**
- Bring iStripper window to foreground
- Disable hardware acceleration in iStripper settings
- Try reducing scale factor

**Choppy playback:**
- Reduce FPS (30 → 15)
- Reduce scale factor
- Close background applications

## Getting Help

### Run Diagnostics

```powershell
# Comprehensive system check
python -m thermalright_lcd_control.diagnostics.system_checker
```

This checks:
- Python version
- Dependencies
- USB devices
- GPU support
- **Video codecs** (NEW)
- Window capture
- Service status
- Task Scheduler status

### Diagnostic Tools

| Tool | Command | Purpose |
|------|---------|---------|
| System Checker | `python -m thermalright_lcd_control.diagnostics.system_checker` | All checks |
| Codec Check | `python -m thermalright_lcd_control.utils.codec_detector` | Video codecs |
| USB Check | `python -m thermalright_lcd_control.utils.zadig_manager` | USB drivers |
| Task Check | `python -m thermalright_lcd_control.utils.task_scheduler status` | Auto-start |

### Additional Resources

- [Windows Service Setup](WINDOWS_SERVICE_SETUP.md)
- [iStripper Integration](ISTRIPPER_INTEGRATION.md)
- [Troubleshooting Guide](TROUBLESHOOTING_WINDOWS.md)
- [Main README](../README.md)

## Summary

Windows 11 enhancements provide:

✅ **Flexible auto-start** - Task Scheduler or Service  
✅ **Easy USB driver setup** - Automatic Zadig integration  
✅ **Video codec detection** - Know what's installed  
✅ **Visual iStripper config** - No manual editing  
✅ **Comprehensive diagnostics** - Find issues quickly  

All features designed specifically for Windows 11 with modern tooling and intuitive interfaces.
