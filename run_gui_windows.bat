@echo off
REM Quick launcher for Thermalright LCD Control on Windows
REM Double-click this file to start the application

echo Starting Thermalright LCD Control...
echo.

setlocal enabledelayedexpansion

REM First, try to use the local venv created by install_windows.bat
set "PYTHON_EXE="
set "LOCAL_VENV=%~dp0venv"
if exist "%LOCAL_VENV%\Scripts\python.exe" (
    echo Found local virtual environment at %LOCAL_VENV%
    set "PYTHON_EXE=%LOCAL_VENV%\Scripts\python.exe"
    echo Using Python from: !PYTHON_EXE!
    echo.
    goto :run_app
)

REM If not found, search for venv in subfolders
echo Local venv not found, searching subfolders...
for /d %%d in ("%~dp0*") do (
    if exist "%%d\Scripts\python.exe" (
        echo Found virtual environment in subfolder: %%d
        set "PYTHON_EXE=%%d\Scripts\python.exe"
        echo Using Python from: !PYTHON_EXE!
        echo.
        goto :run_app
    )
)

REM Search for venv environment "IS" on all drives (legacy support)
set "VENV_PATH="
for %%d in (E D C F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\IS\Scripts\python.exe" (
        set "VENV_PATH=%%d:\IS"
        goto :found_venv
    )
)

:found_venv
if defined VENV_PATH (
    echo Found virtual environment "IS" at !VENV_PATH!...
    set "PYTHON_EXE=!VENV_PATH!\Scripts\python.exe"
    echo Using Python from: !PYTHON_EXE!
    echo.
    goto :run_app
) else (
    echo Warning: No virtual environment found
    echo Please run install_windows.bat first to create the virtual environment
    echo.
    echo Attempting to run with system Python...
    echo This may fail if dependencies are not installed globally.
    echo.
    set "PYTHON_EXE=python"
)

:run_app

REM Run the application using the determined Python executable
"%PYTHON_EXE%" -m thermalright_lcd_control.main_gui

set "EXIT_CODE=%errorLevel%"
endlocal

if %EXIT_CODE% neq 0 (
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
