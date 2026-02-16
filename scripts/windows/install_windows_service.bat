@echo off
REM Thermalright LCD Control - Windows Service Installer (Batch Wrapper)
REM This will launch the PowerShell installer with Administrator privileges

echo ============================================
echo Thermalright LCD Control Service Installer
echo ============================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with Administrator privileges...
    echo.
    
    REM Run the PowerShell script
    powershell -ExecutionPolicy Bypass -File "%~dp0install_windows_service.ps1"
) else (
    echo This script requires Administrator privileges.
    echo.
    echo Please right-click this file and select "Run as Administrator"
    echo.
    pause
)
