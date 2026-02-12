@echo off
REM Quick launcher for Thermalright LCD Control on Windows
REM Double-click this file to start the application

echo Starting Thermalright LCD Control...
python -m thermalright_lcd_control.main_gui

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to start the application
    echo.
    echo Please make sure:
    echo  1. Python is installed and in PATH
    echo  2. Dependencies are installed (run install_windows.bat)
    echo.
    pause
)
