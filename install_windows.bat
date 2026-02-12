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

REM Detect installed applications
echo Searching for installed applications...
echo.

setlocal enabledelayedexpansion

REM Search for iStripper
set "ISTRIPPER_PATH="
set "SEARCH_DIRS=%ProgramFiles%,%ProgramFiles(x86)%"

for %%D in (%SEARCH_DIRS%) do (
    if exist "%%D\iStripper\iStripper.exe" (
        set "ISTRIPPER_PATH=%%D\iStripper\iStripper.exe"
        goto :found_istripper
    )
    if exist "%%D\Totem Entertainment\iStripper.exe" (
        set "ISTRIPPER_PATH=%%D\Totem Entertainment\iStripper.exe"
        goto :found_istripper
    )
    if exist "%%D\VirtuaGirl HD\vghd.exe" (
        set "ISTRIPPER_PATH=%%D\VirtuaGirl HD\vghd.exe"
        goto :found_istripper
    )
)

:found_istripper
if defined ISTRIPPER_PATH (
    echo [OK] iStripper detected: !ISTRIPPER_PATH!
) else (
    echo [--] iStripper not found (optional)
)

REM Search for VLC
set "VLC_PATH="

for %%D in (%SEARCH_DIRS%) do (
    if exist "%%D\VLC\vlc.exe" (
        set "VLC_PATH=%%D\VLC\vlc.exe"
        goto :found_vlc
    )
    if exist "%%D\VideoLAN\VLC\vlc.exe" (
        set "VLC_PATH=%%D\VideoLAN\VLC\vlc.exe"
        goto :found_vlc
    )
)

:found_vlc
if defined VLC_PATH (
    echo [OK] VLC Media Player detected: !VLC_PATH!
) else (
    echo [--] VLC Media Player not found (optional)
)

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

REM Create configuration file with detected applications
set "CONFIG_DIR=%LOCALAPPDATA%\thermalright-lcd-control"
set "CONFIG_FILE=%CONFIG_DIR%\detected_apps.json"

if not exist "%CONFIG_DIR%" (
    mkdir "%CONFIG_DIR%"
)

REM Create JSON config file
(
echo {
echo   "istripper_path": "!ISTRIPPER_PATH!",
echo   "vlc_path": "!VLC_PATH!",
echo   "detection_date": "%DATE% %TIME%"
echo }
) > "%CONFIG_FILE%"

echo Configuration saved to: %CONFIG_FILE%
echo.

echo ==========================================
echo Installation completed successfully!
echo ==========================================
echo.

REM Show detected applications summary
if defined ISTRIPPER_PATH (
    echo Detected Applications:
    echo   - iStripper: !ISTRIPPER_PATH!
    echo     You can capture iStripper content using window capture mode
    echo.
)

if defined VLC_PATH (
    if not defined ISTRIPPER_PATH echo Detected Applications:
    echo   - VLC: !VLC_PATH!
    echo     You can capture VLC player content using window capture mode
    echo.
)

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

endlocal
pause
