@echo off
REM Windows installation script for Thermalright LCD Control
REM Automatically elevates to Administrator if needed
REM Uses virtual environment for dependency isolation

echo ==========================================
echo Thermalright LCD Control - Windows Installer
echo ==========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Not running as Administrator. Elevating privileges...
    echo.
    REM Re-launch as administrator using PowerShell with persistent window
    powershell -NoExit -Command "Start-Process cmd -ArgumentList '/K cd /d \"%CD%\" && \"%~f0\"' -Verb RunAs"
    exit /b 0
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo Python detected:
python --version
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: pip is not available
    echo.
    echo Please reinstall Python and make sure pip is included
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo pip detected:
python -m pip --version
echo.

REM Create virtual environment if it doesn't exist
set "VENV_DIR=%~dp0venv"
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if %errorLevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        echo.
        echo Make sure Python venv module is installed
        echo You can install it with: python -m pip install --user virtualenv
        echo.
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
) else (
    echo Virtual environment already exists.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %errorLevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo Virtual environment activated.
echo.

REM Detect installed applications
echo Searching for installed applications...
echo.

setlocal enabledelayedexpansion

REM Search for iStripper
set "ISTRIPPER_PATH="
set "SEARCH_DIRS=%ProgramFiles%,%ProgramFiles(x86)%"

REM First check for venv environment with vghd.exe on all drives
echo Checking for iStripper venv environment (IS\vghd\bin\vghd.exe)...
for %%d in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\" (
        if exist "%%d:\IS\vghd\bin\vghd.exe" (
            set "ISTRIPPER_PATH=%%d:\IS\vghd\bin\vghd.exe"
            echo   Found iStripper venv on drive %%d:\
            goto :found_istripper
        )
    )
)

REM Check standard Program Files directories
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

REM Check additional drives for standard installations
echo   Searching additional drives for iStripper...
for %%d in (D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\" (
        REM Check common paths on each drive
        if exist "%%d:\Program Files\iStripper\iStripper.exe" (
            set "ISTRIPPER_PATH=%%d:\Program Files\iStripper\iStripper.exe"
            echo   Found on drive %%d:\
            goto :found_istripper
        )
        if exist "%%d:\Program Files (x86)\iStripper\iStripper.exe" (
            set "ISTRIPPER_PATH=%%d:\Program Files (x86)\iStripper\iStripper.exe"
            echo   Found on drive %%d:\
            goto :found_istripper
        )
        if exist "%%d:\Games\iStripper\iStripper.exe" (
            set "ISTRIPPER_PATH=%%d:\Games\iStripper\iStripper.exe"
            echo   Found on drive %%d:\
            goto :found_istripper
        )
        if exist "%%d:\iStripper\iStripper.exe" (
            set "ISTRIPPER_PATH=%%d:\iStripper\iStripper.exe"
            echo   Found on drive %%d:\
            goto :found_istripper
        )
        if exist "%%d:\Totem Entertainment\iStripper.exe" (
            set "ISTRIPPER_PATH=%%d:\Totem Entertainment\iStripper.exe"
            echo   Found on drive %%d:\
            goto :found_istripper
        )
        if exist "%%d:\VirtuaGirl HD\vghd.exe" (
            set "ISTRIPPER_PATH=%%d:\VirtuaGirl HD\vghd.exe"
            echo   Found on drive %%d:\
            goto :found_istripper
        )
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

REM Check standard Program Files\VideoLAN\VLC location
if exist "%ProgramFiles%\VideoLAN\VLC\vlc.exe" (
    set "VLC_PATH=%ProgramFiles%\VideoLAN\VLC\vlc.exe"
    goto :found_vlc
)
if exist "%ProgramFiles(x86)%\VideoLAN\VLC\vlc.exe" (
    set "VLC_PATH=%ProgramFiles(x86)%\VideoLAN\VLC\vlc.exe"
    goto :found_vlc
)

REM Fallback to other VLC locations
for %%D in (%SEARCH_DIRS%) do (
    if exist "%%D\VLC\vlc.exe" (
        set "VLC_PATH=%%D\VLC\vlc.exe"
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
echo Installing required Python packages into virtual environment...
echo This may take a few minutes...
echo.

python -m pip install --upgrade pip
python -m pip install PySide6>=6.10.0 hid>=1.0.8 psutil>=7.1.3 opencv-python>=4.12.0.88 pyusb>=1.3.1 pillow>=12.0.0 pyyaml>=6.0.2

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo.
    echo Press any key to exit...
    pause >nul
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
echo   1. Activate the virtual environment:
echo      %VENV_DIR%\Scripts\activate.bat
echo   2. Run the application:
echo      python -m thermalright_lcd_control.main_gui
echo.
echo Or simply double-click run_gui_windows.bat
echo.
echo Note: Video playback is enabled without audio by default
echo Supported video formats: MP4, AVI, MKV, MOV, WEBM, FLV, WMV, M4V
echo.

endlocal
echo.
echo Installation complete! Window will remain open for review.
echo Press any key to exit...
pause >nul
