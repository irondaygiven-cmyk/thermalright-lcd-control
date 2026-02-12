@echo off
REM Windows installation script for Thermalright LCD Control
REM Run this script as Administrator

echo ==========================================
echo Thermalright LCD Control - Windows Installer
echo ==========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click on this file and select "Run as administrator"
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: pip is not available
    echo.
    echo Please reinstall Python and make sure pip is included
    pause
    exit /b 1
)

echo pip detected:
pip --version
echo.

REM Install dependencies
echo Installing required Python packages...
echo This may take a few minutes...
echo.

pip install PySide6>=6.10.0 hid>=1.0.8 psutil>=7.1.3 opencv-python>=4.12.0.88 pyusb>=1.3.1 pillow>=12.0.0 pyyaml>=6.0.2

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Installation completed successfully!
echo ==========================================
echo.
echo To run the application:
echo   python -m thermalright_lcd_control.main_gui
echo.
echo Or create a desktop shortcut using:
echo   Target: python -m thermalright_lcd_control.main_gui
echo   Start in: %CD%
echo.
echo Note: Video playback is enabled without audio by default
echo Supported video formats: MP4, AVI, MKV, MOV, WEBM, FLV, WMV, M4V
echo.
pause
