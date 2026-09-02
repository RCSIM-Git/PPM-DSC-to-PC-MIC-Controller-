@echo off
title PPM-SIM Launcher
cd /d "%~dp0"

echo ===================================================
echo               PPM-SIM LAUNCHER
echo   RC Radio Audio Trainer Port to Virtual Gamepad
echo ===================================================
echo.

set PYTHON_CMD=

if exist "C:\Users\Mateusz\AppData\Local\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=C:\Users\Mateusz\AppData\Local\Programs\Python\Python312\python.exe"
) else (
    where py.exe >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3.12"
    ) else (
        set "PYTHON_CMD=python"
    )
)

echo Uruchamianie PPM-SIM za pomoca: %PYTHON_CMD%
%PYTHON_CMD% main.py

if errorlevel 1 (
    echo.
    echo Wystapil blad podczas dzialania aplikacji.
    pause
)
