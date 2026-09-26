@echo off
chcp 65001 >nul
title Photo & Video Organizer - Installation
cls

echo ========================================
echo     PHOTO & VIDEO ORGANIZER - SETUP
echo ========================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [*] Installing requirements (PySide6, Pillow)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] All dependencies installed successfully!
    echo You can now launch the app using PhotoOrganizer.bat
) else (
    echo.
    echo [ERROR] Installation failed. Please check internet connection.
)

echo.
pause
