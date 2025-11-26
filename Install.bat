@echo off
chcp 65001 >nul
title Photo Organizer - Installation
cls

echo ========================================
echo    PHOTO ORGANIZER - SETUP
echo ========================================
echo.
echo This will set up execution permissions...
echo.

:: Устанавливаем политику выполнения для текущего пользователя
PowerShell -Command "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force"

echo.
echo ✅ Permissions configured successfully!
echo.
echo You can now run:
echo   1. PhotoOrganizer.bat - Double click to start
echo   2. OR Сортировка_фото_GUI.ps1 - Right click → Run with PowerShell
echo.
echo Press any key to exit...
pause >nul