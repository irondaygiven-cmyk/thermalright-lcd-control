# Windows Service Setup Guide

Complete guide for setting up and managing the Thermalright LCD Control Windows Service.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Service Management](#service-management)
- [System Tray Icon](#system-tray-icon)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## Prerequisites

Before installing the Windows service, ensure you have:

1. **Windows 10 (21H2+) or Windows 11**
2. **Python 3.10 or higher** installed and added to PATH
3. **Administrator privileges** for service installation
4. **Thermalright LCD Control** installed via pip or from source
5. **pywin32 package** (will be auto-installed if missing)

## Installation

### Method 1: Using PowerShell Script (Recommended)

1. **Open PowerShell as Administrator:**
   - Right-click the Start button
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Navigate to the installation directory:**
   ```powershell
   cd C:\Path\To\thermalright-lcd-control
   ```

3. **Run the installer:**
   ```powershell
   .\scripts\windows\install_windows_service.ps1
   ```

The installer will:
- ✓ Check Python installation
- ✓ Install pywin32 if not present
- ✓ Register the Windows service
- ✓ Configure auto-start
- ✓ Optionally start the service

### Method 2: Using Batch File

1. **Right-click** `scripts\windows\install_windows_service.bat`
2. **Select** "Run as Administrator"
3. **Follow the prompts**

### Method 3: Manual Installation

```powershell
# Install pywin32 if not installed
pip install pywin32

# Install the service
python -m thermalright_lcd_control.service.windows_service_manager install
```

## Service Management

### Using Windows Services Manager (GUI)

1. **Open Services Manager:**
   - Press `Win + R`
   - Type `services.msc`
   - Press Enter

2. **Locate** "Thermalright LCD Control Service"

3. **Right-click** for options:
   - Start
   - Stop
   - Restart
   - Properties (change startup type, etc.)

### Using Command Line

**Start the service:**
```powershell
net start ThermalrightLCDControl
# or
sc start ThermalrightLCDControl
```

**Stop the service:**
```powershell
net stop ThermalrightLCDControl
# or
sc stop ThermalrightLCDControl
```

**Check service status:**
```powershell
sc query ThermalrightLCDControl
```

**Restart the service:**
```powershell
net stop ThermalrightLCDControl
net start ThermalrightLCDControl
```

### Using Service Manager CLI

```powershell
# Start
python -m thermalright_lcd_control.service.windows_service_manager start

# Stop
python -m thermalright_lcd_control.service.windows_service_manager stop

# Restart
python -m thermalright_lcd_control.service.windows_service_manager restart

# Check status
python -m thermalright_lcd_control.service.windows_service_manager status
```

## System Tray Icon

The system tray icon provides easy access to service control.

### Launch System Tray Icon

```powershell
python -m thermalright_lcd_control.ui.system_tray
```

**To start automatically with Windows:**
1. Create a shortcut to the command above
2. Place it in: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

### System Tray Features

- **Service Status Indicator**: Shows if service is running, stopped, or in error state
- **Right-click Menu**:
  - Start Service
  - Stop Service
  - Restart Service
  - Open Configuration folder
  - Open GUI
  - Exit

## Configuration

### Service Configuration

The service automatically uses the configuration from:
```
%LOCALAPPDATA%\thermalright-lcd-control\resources\config\
```

### Auto-start Configuration

By default, the service is set to start automatically with Windows.

**To change startup type:**

1. Open Services Manager (`services.msc`)
2. Right-click "Thermalright LCD Control Service"
3. Select "Properties"
4. Change "Startup type" to:
   - **Automatic** - Starts with Windows
   - **Automatic (Delayed Start)** - Starts shortly after Windows boots
   - **Manual** - Must be started manually
   - **Disabled** - Cannot be started

## Troubleshooting

### Service Won't Install

**Error: "Access Denied"**
- Solution: Run PowerShell as Administrator

**Error: "pywin32 not found"**
```powershell
pip install pywin32
python -m win32serviceutil --startup auto install
```

### Service Won't Start

**Check Event Viewer for details:**
1. Press `Win + R`, type `eventvwr.msc`
2. Navigate to: Windows Logs → Application
3. Look for errors from "ThermalrightLCDControl"

**Common causes:**
- **USB device not connected**: Connect the device
- **Configuration file missing**: Check `%LOCALAPPDATA%\thermalright-lcd-control\`
- **Permissions issue**: Ensure service has USB access rights

## Uninstallation

### Method 1: Using PowerShell Script

```powershell
# Run as Administrator
.\scripts\windows\uninstall_windows_service.ps1
```

### Method 2: Manual Uninstallation

```powershell
# Stop the service first
net stop ThermalrightLCDControl

# Uninstall
python -m thermalright_lcd_control.service.windows_service_manager uninstall
```

## Getting Help

If you encounter issues:

1. **Run diagnostics:**
   ```powershell
   python -m thermalright_lcd_control.diagnostics.system_checker
   ```

2. **Check logs:**
   - Service logs: Windows Event Viewer
   - Application logs: `%LOCALAPPDATA%\thermalright-lcd-control\logs\`

3. **Report issues:** GitHub Issues
