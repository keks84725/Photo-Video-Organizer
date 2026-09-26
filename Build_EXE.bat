@echo off
chcp 65001 >nul
title Build Photo & Video Organizer EXE
cls

echo ========================================
echo   BUILDING STANDALONE WINDOWS .EXE
echo ========================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

echo [*] Installing dependencies and PyInstaller...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

echo.
echo [*] Compiling executable via PyInstaller...
python build.py

echo.
if exist "dist\PhotoVideoOrganizer.exe" (
    echo ========================================================
    echo  [SUCCESS] PhotoVideoOrganizer.exe is ready!
    echo  Location: %~dp0dist\PhotoVideoOrganizer.exe
    echo ========================================================
    explorer "%~dp0dist"
) else (
    echo [ERROR] Build failed. Please check output messages above.
)

pause
