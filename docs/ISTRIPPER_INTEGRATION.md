# iStripper Integration Guide

Complete guide for integrating iStripper with Thermalright LCD Control.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Detection Methods](#detection-methods)
- [Configuration](#configuration)
- [Process Monitoring](#process-monitoring)
- [Troubleshooting](#troubleshooting)

## Overview

Thermalright LCD Control can capture and display content from iStripper (or any application window) on your LCD screen in real-time.

**Features:**
- ✅ Automatic iStripper detection
- ✅ Real-time window capture
- ✅ Configurable FPS (15-60)
- ✅ Manual scaling (zoom in/out)
- ✅ Rotation support (0°, 90°, 180°, 270°)
- ✅ Process monitoring (auto-start/stop)
- ✅ Multi-monitor support

## Quick Start

### 1. Install Window Capture Dependencies

**Windows:**
```powershell
pip install mss pygetwindow
```

**Linux:**
```bash
pip install python-xlib
```

### 2. Detect iStripper Installation

The installer automatically searches for iStripper. You can also manually detect it:

```powershell
# Test iStripper detection
python -m thermalright_lcd_control.integrations.istripper_manager
```

### 3. Configure Window Capture

Edit your display configuration YAML file:

```yaml
display:
  background:
    type: "window_capture"
    path: ""  # Not used for window capture
  window_title: "iStripper"  # Window title to capture
  capture_fps: 30  # Frame rate (15-60 recommended)
  scale_factor: 1.5  # Zoom level (1.0 = normal, >1.0 = zoom in)
  rotation: 0  # Rotation angle (0, 90, 180, 270, or custom)
```

### 4. Start iStripper and LCD Control

1. **Launch iStripper first**
2. **Start Thermalright LCD Control:**
   - GUI: `python -m thermalright_lcd_control.main_gui`
   - Service: Start the Windows service

The LCD should now display iStripper content!

## Detection Methods

iStripper is detected using multiple methods (in order):

### 1. Windows Registry (Fastest)

Checks these registry keys:
- `HKLM\SOFTWARE\Totem Entertainment\iStripper`
- `HKLM\SOFTWARE\WOW6432Node\Totem Entertainment\iStripper`
- `HKCU\SOFTWARE\Totem Entertainment\iStripper`

### 2. Common Installation Paths

Checks:
- `C:\Program Files\iStripper\`
- `C:\Program Files (x86)\iStripper\`
- `D:\Program Files\iStripper\`
- `D:\Games\iStripper\`
- Other common locations

### 3. Full Drive Search (Slowest)

Searches all drives for:
- `iStripper.exe`
- `vghd.exe` (older version)

**Note:** The detection result is cached for faster subsequent lookups.

## Configuration

### Window Capture Settings

#### Window Title

The window title to capture. Common values:
- `"iStripper"` - Current iStripper version
- `"VirtuaGirl HD"` - Legacy version

To find the exact window title:
```powershell
# Windows
python -c "import pygetwindow as gw; print([w.title for w in gw.getAllWindows() if 'strip' in w.title.lower()])"
```

#### Capture FPS

Frame rate for window capture:
- **15 FPS**: Low CPU usage, slightly choppy
- **30 FPS**: Balanced (recommended)
- **60 FPS**: Smooth, higher CPU usage

Example:
```yaml
capture_fps: 30
```

#### Scale Factor

Zoom in or out on the captured content:
- **< 1.0**: Zoom out (show more of window)
- **1.0**: Normal size
- **> 1.0**: Zoom in (show less, but larger)

Example:
```yaml
scale_factor: 1.5  # Zoom in 1.5x
```

**Tip:** Use values between 1.2 and 2.0 for best results.

#### Rotation

Rotate the captured content:
- **0**: No rotation (default)
- **90**: Rotate 90° clockwise
- **180**: Rotate 180° (upside down)
- **270**: Rotate 270° clockwise (90° counter-clockwise)
- **Custom**: Any angle in degrees

Example:
```yaml
rotation: 90  # Rotate 90 degrees
```

### Complete Configuration Example

```yaml
display:
  background:
    type: "window_capture"
    path: ""
  window_title: "iStripper"
  capture_fps: 30
  scale_factor: 1.5
  rotation: 0
  
  # Optional: Foreground overlay (metrics, etc.)
  foreground:
    path: "path/to/overlay.png"
    opacity: 0.8
```

## Process Monitoring

### Auto-Start/Stop Window Capture

Enable process monitoring to automatically start/stop capture when iStripper launches:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()

def on_istripper_started():
    print("iStripper started - beginning capture")
    # Start window capture

def on_istripper_stopped():
    print("iStripper stopped - stopping capture")
    # Stop window capture

# Start monitoring
manager.start_monitoring(
    on_started=on_istripper_started,
    on_stopped=on_istripper_stopped
)
```

**Note:** This feature is automatically enabled when using the Windows service.

### Manual Process Check

Check if iStripper is currently running:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()
is_running = manager.is_process_running()

if is_running:
    print("iStripper is running")
else:
    print("iStripper is not running")
```

## Troubleshooting

### iStripper Not Detected

**Check installation manually:**

```powershell
# Windows
dir "C:\Program Files\iStripper\iStripper.exe"
dir "C:\Program Files (x86)\iStripper\iStripper.exe"

# Check all drives
for %d in (C D E F G) do @if exist "%d:\Program Files\iStripper" echo Found on %d:
```

**Manually configure path:**

If auto-detection fails, you can manually specify the window title in the config YAML.

### Window Not Capturing

**Verify window is visible:**
1. Ensure iStripper window is not minimized
2. The window must be visible (not hidden behind other windows)

**Check window title:**

```powershell
# List all windows
python -c "import pygetwindow as gw; [print(w.title) for w in gw.getAllWindows()]"
```

Find the exact title and use it in your config.

**Permissions:**
- On Windows, window capture works in user space (no admin required)
- On Linux, X11 permissions may be needed

### Low Frame Rate

If capture is slow or choppy:

1. **Reduce capture_fps:**
   ```yaml
   capture_fps: 15  # Lower FPS
   ```

2. **Reduce LCD resolution** (if your device supports multiple resolutions)

3. **Close other applications** using the GPU

4. **Check CPU usage** - window capture is CPU-intensive

### High CPU Usage

If LCD control uses too much CPU:

1. **Lower FPS:**
   ```yaml
   capture_fps: 15  # Lower = less CPU
   ```

2. **Simplify foreground overlay** (if any)

3. **Reduce scale_factor** (less processing)

### Content Appears Stretched or Cropped

**Adjust scale_factor:**
```yaml
scale_factor: 1.0  # Try different values
```

**Try rotation:**
```yaml
rotation: 90  # If content orientation is wrong
```

### Multi-Monitor Issues

If you have multiple monitors:

1. **Ensure iStripper is on the primary monitor** (or the monitor Windows considers primary)
2. Window capture may not work properly with DPI scaling differences between monitors
3. Move iStripper window to the primary monitor

### iStripper Window Not Found After Restart

The window title may change. Check with:
```powershell
python -c "import pygetwindow as gw; [print(w.title) for w in gw.getAllWindows() if 'strip' in w.title.lower()]"
```

Update config YAML with the correct title.

## Performance Tips

### Optimal Settings

For best balance of quality and performance:

```yaml
display:
  background:
    type: "window_capture"
  window_title: "iStripper"
  capture_fps: 30  # 30 FPS is sweet spot
  scale_factor: 1.5  # Zoom in slightly
  rotation: 0
```

### Low-End Systems

For systems with limited resources:

```yaml
capture_fps: 15  # Lower FPS
scale_factor: 1.0  # No scaling
```

### High-End Systems

For maximum quality:

```yaml
capture_fps: 60  # Smooth 60 FPS
scale_factor: 2.0  # More zoom
```

## Alternative Applications

Window capture works with **any application**, not just iStripper:

### VLC Player
```yaml
window_title: "VLC media player"
capture_fps: 30
```

### Web Browser
```yaml
window_title: "YouTube - Mozilla Firefox"
capture_fps: 24
```

### Custom Application
```yaml
window_title: "Your App Title"
capture_fps: 30
```

**Tip:** Use the window title detection command to find the exact title:
```powershell
python -c "import pygetwindow as gw; [print(w.title) for w in gw.getAllWindows()]"
```

## Related Documentation

- [Main README](../README.md)
- [Windows Service Setup](WINDOWS_SERVICE_SETUP.md)
- [Troubleshooting Guide](TROUBLESHOOTING_WINDOWS.md)
