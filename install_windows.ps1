# Windows PowerShell installation script for Thermalright LCD Control
# Run this script as Administrator in PowerShell

Write-Host "=========================================="
Write-Host "Thermalright LCD Control - Windows Installer"
Write-Host "=========================================="
Write-Host ""

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click on PowerShell and select 'Run as administrator', then run this script again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8 or higher from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "pip not found"
    }
    Write-Host "pip detected: $pipVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "ERROR: pip is not available" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please reinstall Python and make sure pip is included" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "Installing required Python packages..." -ForegroundColor Cyan
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

$packages = @(
    "PySide6>=6.10.0",
    "hid>=1.0.8",
    "psutil>=7.1.3",
    "opencv-python>=4.12.0.88",
    "pyusb>=1.3.1",
    "pillow>=12.0.0",
    "pyyaml>=6.0.2"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    pip install $package
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Failed to install $package" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "=========================================="
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "  python -m thermalright_lcd_control.main_gui" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or create a desktop shortcut with:" -ForegroundColor Cyan
Write-Host "  Target: python -m thermalright_lcd_control.main_gui" -ForegroundColor Yellow
Write-Host "  Start in: $PWD" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: Video playback is enabled without audio by default" -ForegroundColor Green
Write-Host "Supported video formats: MP4, AVI, MKV, MOV, WEBM, FLV, WMV, M4V" -ForegroundColor Green
Write-Host ""

# Offer to create a desktop shortcut
Write-Host "Would you like to create a desktop shortcut? (Y/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopPath "Thermalright LCD Control.lnk"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = "python"
    $Shortcut.Arguments = "-m thermalright_lcd_control.main_gui"
    $Shortcut.WorkingDirectory = $PWD
    $Shortcut.Description = "Thermalright LCD Control"
    $Shortcut.Save()
    
    Write-Host ""
    Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
}

Read-Host "Press Enter to exit"
