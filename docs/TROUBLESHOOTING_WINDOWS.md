# Windows Troubleshooting Guide

Comprehensive troubleshooting guide for Thermalright LCD Control on Windows.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [USB Device Issues](#usb-device-issues)
- [Service Issues](#service-issues)
- [GPU Metrics Issues](#gpu-metrics-issues)
- [Window Capture Issues](#window-capture-issues)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)

## Quick Diagnostics

Before troubleshooting specific issues, run the built-in diagnostics tool:

```powershell
python -m thermalright_lcd_control.diagnostics.system_checker
```

This will check:
- ✓ Python version
- ✓ Required dependencies
- ✓ USB device detection
- ✓ GPU support
- ✓ Window capture dependencies
- ✓ Windows service support
- ✓ Administrator privileges
- ✓ iStripper installation

The tool provides **actionable fix suggestions** for any issues found.

## Installation Issues

### Python Not Found

**Error:** `'python' is not recognized as an internal or external command`

**Solutions:**

1. **Check if Python is installed:**
   ```powershell
   py --version
   ```

2. **If not installed, download from:** https://www.python.org/downloads/
   - ✓ Check "Add Python to PATH" during installation

3. **If installed but not in PATH:**
   - Find Python installation (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX`)
   - Add to PATH:
     1. Right-click "This PC" → Properties
     2. Advanced system settings → Environment Variables
     3. Edit "Path" under User variables
     4. Add Python directory

### Pip Install Fails

**Error:** Various pip installation errors

**Solutions:**

1. **Upgrade pip:**
   ```powershell
   python -m pip install --upgrade pip
   ```

2. **Use pip with python -m:**
   ```powershell
   python -m pip install thermalright-lcd-control
   ```

3. **Check internet connection** - pip needs internet to download packages

4. **Try with --user flag:**
   ```powershell
   pip install --user thermalright-lcd-control
   ```

### Permission Errors During Install

**Error:** `Permission denied` or `Access is denied`

**Solutions:**

1. **Run as Administrator:**
   - Right-click PowerShell → "Run as Administrator"

2. **Install for user only:**
   ```powershell
   pip install --user thermalright-lcd-control
   ```

3. **Check antivirus** - temporarily disable if blocking

## USB Device Issues

### Device Not Detected

**Run diagnostics first:**
```powershell
python -m thermalright_lcd_control.diagnostics.system_checker
```

**Check Device Manager:**
1. Press `Win + X` → Device Manager
2. Look under:
   - "Human Interface Devices"
   - "Universal Serial Bus devices"
   - "Other devices" (if driver missing)

**Solutions:**

1. **Try different USB port:**
   - Use USB 2.0 port (better compatibility)
   - Avoid USB hubs

2. **Check USB cable:**
   - Ensure cable is data cable (not charge-only)
   - Try different cable if available

3. **Reconnect device:**
   - Unplug device
   - Wait 10 seconds
   - Plug back in

4. **Check Device Manager for errors:**
   - Yellow triangle = driver issue
   - Unknown device = driver not installed

### USB Access Denied

**Error:** `Access to USB device denied`

**Solutions:**

1. **Run as Administrator:**
   ```powershell
   # Right-click and "Run as Administrator"
   python -m thermalright_lcd_control.main_gui
   ```

2. **Check if device is in use:**
   - Close other applications that might use the device
   - Check Task Manager for multiple instances

3. **Install proper USB drivers:**
   - Check manufacturer website for drivers
   - Use Zadig for generic USB HID driver (advanced users)

### Device Disconnects Randomly

**Solutions:**

1. **Disable USB selective suspend:**
   - Control Panel → Power Options
   - Edit Plan Settings → Advanced
   - USB settings → USB selective suspend → Disabled

2. **Update USB drivers:**
   - Device Manager → Right-click device
   - Update driver

3. **Check USB power:**
   - Some devices need more power
   - Try powered USB hub
   - Use different USB port

## Service Issues

### Service Won't Install

**Error:** Various installation errors

**Solutions:**

1. **Ensure running as Administrator**

2. **Install pywin32:**
   ```powershell
   pip install pywin32
   python -m pywin32_postinstall.py -install
   ```

3. **Manual installation:**
   ```powershell
   python -m win32serviceutil install
   ```

### Service Won't Start

**Check Event Viewer:**
1. `Win + R` → `eventvwr.msc`
2. Windows Logs → Application
3. Look for "ThermalrightLCDControl" errors

**Common causes:**

1. **USB device not connected:**
   - Connect device before starting service

2. **Configuration missing:**
   - Check: `%LOCALAPPDATA%\thermalright-lcd-control\`
   - Ensure config files exist

3. **Permissions:**
   - Service may need access to USB devices
   - Try running service as different user

4. **Python not in system PATH:**
   - Service may not find Python
   - Reinstall Python with "Add to PATH"

### Service Crashes

**Check logs:**
- Event Viewer (Windows Logs → Application)
- `%LOCALAPPDATA%\thermalright-lcd-control\logs\`

**Solutions:**

1. **Update dependencies:**
   ```powershell
   pip install --upgrade thermalright-lcd-control
   ```

2. **Test manually:**
   ```powershell
   python -m thermalright_lcd_control.service --config %LOCALAPPDATA%\thermalright-lcd-control\resources\config
   ```

3. **Check for conflicting software:**
   - Other RGB control software
   - Antivirus blocking access

## GPU Metrics Issues

### GPU Not Detected

**Run GPU diagnostics:**
```powershell
python -m thermalright_lcd_control.device_controller.metrics.gpu_detector
```

**Solutions by GPU vendor:**

#### NVIDIA GPU

1. **Check nvidia-smi:**
   ```powershell
   nvidia-smi
   ```
   If it works, GPU metrics should work

2. **If nvidia-smi not found:**
   - Update NVIDIA drivers
   - Ensure nvidia-smi is in PATH
   - Typically: `C:\Program Files\NVIDIA Corporation\NVSMI`

#### AMD GPU

1. **Install WMI support:**
   ```powershell
   pip install wmi
   ```

2. **For enhanced metrics, install OpenHardwareMonitor:**
   - Download from: https://openhardwaremonitor.org/
   - Run as Administrator
   - Keep running in background

3. **Update AMD drivers**

#### Intel GPU

1. **Install WMI support:**
   ```powershell
   pip install wmi
   ```

2. **Update Intel graphics drivers**

3. **Note:** Intel integrated GPU metrics are limited

### Temperature/Usage Not Showing

**Solutions:**

1. **Install monitoring software:**
   - OpenHardwareMonitor (provides WMI sensors)
   - HWiNFO (alternative)

2. **Check GPU drivers:**
   - Update to latest version

3. **Verify WMI working:**
   ```powershell
   python -c "import wmi; w=wmi.WMI(); print([g.Name for g in w.Win32_VideoController()])"
   ```

## Window Capture Issues

### Window Capture Not Working

**Check dependencies:**
```powershell
pip install mss pygetwindow
```

**Test window detection:**
```powershell
python -c "import pygetwindow as gw; [print(w.title) for w in gw.getAllWindows()]"
```

**Solutions:**

1. **Ensure target window is visible:**
   - Not minimized
   - Not hidden behind other windows

2. **Check window title in config:**
   - Must match exactly
   - Use detection command above to find exact title

3. **Try different window title:**
   - "iStripper" (current version)
   - "VirtuaGirl HD" (older version)

### Capture is Black or Blank

**Solutions:**

1. **Check DPI scaling:**
   - High DPI can cause issues
   - Try disabling DPI scaling for application

2. **Window must be visible:**
   - Cannot capture minimized windows
   - Bring window to foreground

3. **Try different capture region**

## Performance Issues

### High CPU Usage

**Solutions:**

1. **Reduce capture FPS:**
   ```yaml
   capture_fps: 15  # Lower FPS
   ```

2. **Use simpler backgrounds:**
   - Static images instead of videos
   - Lower resolution media

3. **Close unnecessary applications**

4. **Check Task Manager:**
   - Identify which part is using CPU
   - Look for runaway processes

### High Memory Usage

**Solutions:**

1. **Use smaller media files:**
   - Videos are loaded entirely into memory
   - Use lower resolution or shorter videos

2. **Reduce image collection size**

3. **Restart application periodically**

### Laggy Performance

**Solutions:**

1. **Update GPU drivers**

2. **Check system resources:**
   - CPU usage
   - RAM usage
   - Disk activity

3. **Reduce metrics update frequency** in config

4. **Use performance power plan:**
   - Control Panel → Power Options → High Performance

## Common Error Messages

### "pywin32 not found"

**Solution:**
```powershell
pip install pywin32
python -m pywin32_postinstall.py -install
```

### "USB device not found"

**Solutions:**
1. Check device is connected
2. Try different USB port
3. Run as Administrator
4. Check Device Manager

### "Failed to initialize WMI"

**Solution:**
```powershell
pip install wmi
# Restart Python/application
```

### "Window 'X' not found"

**Solutions:**
1. Check window title exactly matches
2. Ensure window is visible
3. Use detection command to find exact title

### "Access Denied"

**Solutions:**
1. Run as Administrator
2. Check permissions
3. Disable antivirus temporarily

### "Configuration file not found"

**Solutions:**
1. Check config directory exists: `%LOCALAPPDATA%\thermalright-lcd-control\`
2. Copy default config from resources
3. Run GUI to generate config

## Getting More Help

If issues persist:

1. **Run full diagnostics:**
   ```powershell
   python -m thermalright_lcd_control.diagnostics.system_checker
   ```

2. **Check logs:**
   - `%LOCALAPPDATA%\thermalright-lcd-control\logs\`
   - Windows Event Viewer

3. **Report issue on GitHub:**
   - Include diagnostic output
   - Include error messages
   - Include system info (Windows version, Python version)

4. **Community support:**
   - Check GitHub Issues for similar problems
   - Search for your error message

## Related Documentation

- [Windows Service Setup](WINDOWS_SERVICE_SETUP.md)
- [iStripper Integration](ISTRIPPER_INTEGRATION.md)
- [Main README](../README.md)
