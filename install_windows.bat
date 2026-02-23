@echo off
setlocal enabledelayedexpansion
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
    powershell -Command "Start-Process cmd -ArgumentList '/K cd /d \"%CD%\" && \"%~f0\"' -Verb RunAs"
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
        echo The Python venv module appears to be missing or incomplete.
        echo Please reinstall Python with all standard library modules included.
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

REM Install the package with dependencies
echo Installing thermalright-lcd-control package and dependencies...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip
if %errorLevel% neq 0 (
    echo Warning: Failed to upgrade pip, continuing with current version...
)

REM Install with Windows-specific extras
python -m pip install -e .[windows]

if %errorLevel% neq 0 (
    echo ERROR: Failed to install package dependencies
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo.
echo [OK] Package installed successfully
echo.

REM -------------------------------------------------------
REM Install hidapi native library (required by the hid package)
REM -------------------------------------------------------
call :install_hidapi "%VENV_DIR%"

REM -------------------------------------------------------
REM Also install into the IS venv (E:\IS) if it exists
REM -------------------------------------------------------
call :install_to_is_venv

goto :detect_apps

:install_hidapi
setlocal enabledelayedexpansion
set "TARGET_VENV=%~1"
set "HIDAPI_DLL=%TARGET_VENV%\Scripts\hidapi.dll"

if exist "%HIDAPI_DLL%" (
    echo [OK] hidapi.dll already present in %TARGET_VENV%\Scripts\
    endlocal
    exit /b 0
)

echo Downloading hidapi native library for Windows HID device support...
set "HIDAPI_ZIP=%TEMP%\hidapi-win.zip"
set "HIDAPI_EXTRACT=%TEMP%\hidapi-win"

powershell -NoProfile -Command ^
    "try { Invoke-WebRequest -Uri 'https://github.com/libusb/hidapi/releases/download/hidapi-0.14.0/hidapi-win.zip' -OutFile '%HIDAPI_ZIP%' -UseBasicParsing -TimeoutSec 30; exit 0 } catch { exit 1 }"

if %errorLevel% neq 0 (
    echo [!!] Warning: Could not download hidapi.dll automatically.
    echo     HID devices ^(0x0418:0x5304, 0x0416:0x5302^) will not work until hidapi.dll
    echo     is placed in: %TARGET_VENV%\Scripts\
    echo     Manual download: https://github.com/libusb/hidapi/releases
    endlocal
    exit /b 1
)

powershell -NoProfile -Command ^
    "Expand-Archive -Path '%HIDAPI_ZIP%' -DestinationPath '%HIDAPI_EXTRACT%' -Force"

set "DLL_SRC=%HIDAPI_EXTRACT%\x64\hidapi.dll"
if not exist "%DLL_SRC%" set "DLL_SRC=%HIDAPI_EXTRACT%\hidapi-win\x64\hidapi.dll"

if exist "%DLL_SRC%" (
    copy /Y "%DLL_SRC%" "%HIDAPI_DLL%" >nul
    echo [OK] hidapi.dll installed to %TARGET_VENV%\Scripts\
) else (
    echo [!!] Warning: hidapi.dll not found in downloaded archive.
    echo     Please install it manually: https://github.com/libusb/hidapi/releases
)

if exist "%HIDAPI_ZIP%" del /Q "%HIDAPI_ZIP%"
if exist "%HIDAPI_EXTRACT%" rmdir /S /Q "%HIDAPI_EXTRACT%"

endlocal
exit /b 0

:install_to_is_venv
setlocal enabledelayedexpansion
set "IS_VENV="
for %%d in (E D C F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\IS\Scripts\python.exe" (
        set "IS_VENV=%%d:\IS"
        goto :found_is
    )
)
endlocal
exit /b 0

:found_is
echo.
echo Found IS virtual environment at !IS_VENV!
echo Installing thermalright-lcd-control into IS venv...

"!IS_VENV!\Scripts\pip.exe" install --upgrade pip >nul 2>&1
"!IS_VENV!\Scripts\pip.exe" install -e ".[windows]"
if %errorLevel% equ 0 (
    echo [OK] Package installed into IS venv
) else (
    echo [!!] Warning: Could not install package into IS venv
)

call :install_hidapi "!IS_VENV!"

endlocal
exit /b 0

:detect_apps
echo Searching for installed applications...
echo.

REM Use subroutines to avoid setlocal/endlocal issues with goto
call :detect_istripper
call :detect_vlc

goto :save_config

:detect_istripper
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
    for %%A in ("!ISTRIPPER_PATH!") do endlocal & set "GLOBAL_ISTRIPPER_PATH=%%~A"
) else (
    echo [--] iStripper not found (optional)
    endlocal & set "GLOBAL_ISTRIPPER_PATH="
)
exit /b

:detect_vlc
setlocal enabledelayedexpansion

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
    for %%A in ("!VLC_PATH!") do endlocal & set "GLOBAL_VLC_PATH=%%~A"
) else (
    echo [--] VLC Media Player not found (optional)
    endlocal & set "GLOBAL_VLC_PATH="
)
echo.
exit /b

:save_config

REM Create configuration file with detected applications
set "CONFIG_DIR=%LOCALAPPDATA%\thermalright-lcd-control"
set "CONFIG_FILE=%CONFIG_DIR%\detected_apps.json"

if not exist "%CONFIG_DIR%" (
    mkdir "%CONFIG_DIR%"
)

REM Create JSON config file
(
echo {
echo   "istripper_path": "%GLOBAL_ISTRIPPER_PATH%",
echo   "vlc_path": "%GLOBAL_VLC_PATH%",
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
if defined GLOBAL_ISTRIPPER_PATH (
    echo Detected Applications:
    echo   - iStripper: %GLOBAL_ISTRIPPER_PATH%
    echo     You can capture iStripper content using window capture mode
    echo.
)

if defined GLOBAL_VLC_PATH (
    if not defined GLOBAL_ISTRIPPER_PATH echo Detected Applications:
    echo   - VLC: %GLOBAL_VLC_PATH%
    echo     You can capture VLC player content using window capture mode
    echo.
)

echo You can now run the application using:
echo   - run_gui_windows.bat (for GUI)
echo   - Other scripts as documented in README.md
echo.
echo To run manually:
echo   1. Activate the virtual environment:
echo      %VENV_DIR%\Scripts\activate.bat
echo   2. Run the application:
echo      python -m thermalright_lcd_control.main_gui
echo.
echo Note: Video playback is enabled without audio by default
echo Supported video formats: MP4, AVI, MKV, MOV, WEBM, FLV, WMV, M4V
echo.

endlocal
echo.
echo Installation complete! Window will remain open for review.
echo Press any key to exit...
pause >nul
