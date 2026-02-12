@echo off
REM Quick launcher for Thermalright LCD Control on Windows
REM Double-click this file to start the application

echo Starting Thermalright LCD Control...
echo.

setlocal enabledelayedexpansion

REM Search for venv environment "IS" on all drives
set "VENV_PATH="
for %%d in (E D C F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\IS\Scripts\activate.bat" (
        set "VENV_PATH=%%d:\IS"
        goto :found_venv
    )
)

:found_venv
if defined VENV_PATH (
    echo Activating virtual environment at !VENV_PATH!...
    call "!VENV_PATH!\Scripts\activate.bat"
    echo Virtual environment activated.
    echo.
) else (
    echo Warning: Virtual environment "IS" not found on any drive
    echo Attempting to run without venv activation...
    echo.
)

endlocal

REM Run the application
python -m thermalright_lcd_control.main_gui

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to start the application
    echo.
    echo Please make sure:
    echo  1. Python is installed and in PATH
    echo  2. Dependencies are installed (run install_windows.bat)
    echo  3. Virtual environment "IS" exists on one of your drives (if required)
    echo.
    pause
)
