@echo off
chcp 65001 >nul
title Photo & Video Organizer
cls

:: Check pythonw first for background launch without black terminal window
where pythonw >nul 2>nul
if %errorlevel% equ 0 (
    start "" pythonw main.py
    exit /b 0
)

:: Fallback to python
where python >nul 2>nul
if %errorlevel% equ 0 (
    python main.py
    exit /b 0
)

echo [ERROR] Python not found. Please run Install.bat first.
pause
