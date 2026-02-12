@echo off
REM Quick launcher for Thermalright LCD Control on Windows
REM Double-click this file to start the application

echo Starting Thermalright LCD Control...
echo.

REM Check if venv environment exists at E:\IS
if exist "E:\IS\Scripts\activate.bat" (
    echo Activating virtual environment at E:\IS...
    call "E:\IS\Scripts\activate.bat"
    echo Virtual environment activated.
    echo.
) else (
    echo Warning: Virtual environment not found at E:\IS
    echo Attempting to run without venv activation...
    echo.
)

REM Run the application
python -m thermalright_lcd_control.main_gui

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to start the application
    echo.
    echo Please make sure:
    echo  1. Python is installed and in PATH
    echo  2. Dependencies are installed (run install_windows.bat)
    echo  3. Virtual environment exists at E:\IS (if required)
    echo.
    pause
)
