@echo off
REM Quick launcher for Thermalright LCD Control on Windows
REM Double-click this file to start the application

echo Starting Thermalright LCD Control...
echo.

setlocal enabledelayedexpansion

REM First, try to use the local venv created by install_windows.bat
set "LOCAL_VENV=%~dp0venv"
if exist "%LOCAL_VENV%\Scripts\activate.bat" (
    echo Found local virtual environment at %LOCAL_VENV%
    echo Activating...
    call "%LOCAL_VENV%\Scripts\activate.bat"
    echo Virtual environment activated.
    echo.
    goto :run_app
)

REM Search for venv environment "IS" on all drives (legacy support)
set "VENV_PATH="
for %%d in (E D C F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\IS\Scripts\activate.bat" (
        set "VENV_PATH=%%d:\IS"
        goto :found_venv
    )
)

:found_venv
if defined VENV_PATH (
    echo Found virtual environment "IS" at !VENV_PATH!...
    call "!VENV_PATH!\Scripts\activate.bat"
    echo Virtual environment activated.
    echo.
    goto :run_app
) else (
    echo Warning: No virtual environment found
    echo Please run install_windows.bat first to create the virtual environment
    echo.
    echo Attempting to run without venv activation...
    echo This may fail if dependencies are not installed globally.
    echo.
)

:run_app
endlocal

REM Run the application
python -m thermalright_lcd_control.main_gui

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to start the application
    echo.
    echo Please make sure:
    echo  1. Python is installed and in PATH
    echo  2. You have run install_windows.bat to set up the virtual environment
    echo  3. Dependencies are installed in the virtual environment
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM If application exits normally, don't show the pause message
exit /b 0
