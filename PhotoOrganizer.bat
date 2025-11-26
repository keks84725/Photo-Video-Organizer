@echo off
chcp 65001 >nul
title Photo & Video Organizer
cls

echo ========================================
echo        PHOTO & VIDEO ORGANIZER
echo ========================================
echo.
echo This tool will organize your photos and videos
echo by date into folder structure
echo.
echo Press Ctrl+C to cancel or
echo.

:: Проверяем существование PowerShell скрипта
if not exist "Сортировка_фото_GUI.ps1" (
    echo ERROR: Main script file 'Сортировка_фото_GUI.ps1' not found!
    echo Please ensure all files are in the same folder.
    echo.
    pause
    exit /b 1
)

:: Запускаем PowerShell скрипт
echo Starting Photo Organizer...
echo.
PowerShell -ExecutionPolicy Bypass -WindowStyle Hidden -File "Сортировка_фото_GUI.ps1"

:: Если скрипт завершился, показываем сообщение
echo.
echo ========================================
echo           PROCESS COMPLETED
echo ========================================
echo.
echo Thank you for using Photo Organizer!
echo.
pause