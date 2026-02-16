# Thermalright LCD Control - Windows Service Installer
# Requires Administrator privileges

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Thermalright LCD Control Service Installer" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check for Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "  1. Right-click on PowerShell" -ForegroundColor Yellow
    Write-Host "  2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "  3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.10 or higher from:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Check if pywin32 is installed
Write-Host "Checking pywin32 installation..." -ForegroundColor Cyan
$pywin32Check = python -c "import win32serviceutil" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "! pywin32 not found, installing..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        pip install pywin32
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ pywin32 installed successfully" -ForegroundColor Green
            
            # Run post-install script
            Write-Host "Running pywin32 post-install..." -ForegroundColor Cyan
            python -m win32serviceutil --startup auto install
        } else {
            Write-Host "✗ Failed to install pywin32" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    } catch {
        Write-Host "✗ Error installing pywin32: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "✓ pywin32 is installed" -ForegroundColor Green
}
Write-Host ""

# Install the service
Write-Host "Installing Thermalright LCD Control Service..." -ForegroundColor Cyan
Write-Host ""

try {
    # Use the service manager to install
    python -m thermalright_lcd_control.service.windows_service_manager install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "Service Installed Successfully!" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Service Name: ThermalrightLCDControl" -ForegroundColor Cyan
        Write-Host "Display Name: Thermalright LCD Control Service" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Yellow
        Write-Host "  1. Start the service:" -ForegroundColor White
        Write-Host "     net start ThermalrightLCDControl" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  2. Or use the system tray icon:" -ForegroundColor White
        Write-Host "     python -m thermalright_lcd_control.ui.system_tray" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  3. Check service status:" -ForegroundColor White
        Write-Host "     sc query ThermalrightLCDControl" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  4. View logs in Windows Event Viewer:" -ForegroundColor White
        Write-Host "     eventvwr.msc" -ForegroundColor Gray
        Write-Host ""
        
        # Ask if user wants to start the service now
        $startNow = Read-Host "Do you want to start the service now? (Y/N)"
        if ($startNow -eq "Y" -or $startNow -eq "y") {
            Write-Host ""
            Write-Host "Starting service..." -ForegroundColor Cyan
            net start ThermalrightLCDControl
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Service started successfully!" -ForegroundColor Green
            } else {
                Write-Host "! Service start may have failed. Check Event Viewer for details." -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host ""
        Write-Host "✗ Service installation failed!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Troubleshooting:" -ForegroundColor Yellow
        Write-Host "  - Ensure you have Administrator privileges" -ForegroundColor White
        Write-Host "  - Check that all dependencies are installed" -ForegroundColor White
        Write-Host "  - View Event Viewer for error details" -ForegroundColor White
    }
    
} catch {
    Write-Host ""
    Write-Host "✗ Error during installation: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  - Python is in PATH" -ForegroundColor White
    Write-Host "  - thermalright-lcd-control is installed" -ForegroundColor White
    Write-Host "  - pywin32 is installed correctly" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to exit"
