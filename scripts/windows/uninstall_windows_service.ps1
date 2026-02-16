# Thermalright LCD Control - Windows Service Uninstaller
# Requires Administrator privileges

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Thermalright LCD Control Service Uninstaller" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
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

# Confirm uninstallation
Write-Host "This will uninstall the Thermalright LCD Control Windows Service." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Are you sure you want to continue? (Y/N)"

if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Uninstallation cancelled." -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "Uninstalling service..." -ForegroundColor Cyan
Write-Host ""

try {
    # Stop the service first if it's running
    Write-Host "Stopping service..." -ForegroundColor Cyan
    net stop ThermalrightLCDControl 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    
    # Uninstall using the service manager
    python -m thermalright_lcd_control.service.windows_service_manager uninstall
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "Service Uninstalled Successfully!" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "The Thermalright LCD Control service has been removed." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Note: Configuration files and logs have been preserved." -ForegroundColor Yellow
        Write-Host "To reinstall, run install_windows_service.ps1" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "✗ Service uninstallation failed!" -ForegroundColor Red
        Write-Host ""
        Write-Host "You can try manually:" -ForegroundColor Yellow
        Write-Host "  sc delete ThermalrightLCDControl" -ForegroundColor White
    }
    
} catch {
    Write-Host ""
    Write-Host "✗ Error during uninstallation: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try manually with:" -ForegroundColor Yellow
    Write-Host "  sc delete ThermalrightLCDControl" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to exit"
