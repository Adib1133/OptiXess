@echo off
title OptiScaler XeSS Suite (Dev Launcher)
cd /d "%~dp0"

echo Starting OptiScaler XeSS Suite in development mode...
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =========================================================
    echo [ERROR] Application exited with error code %ERRORLEVEL%.
    echo =========================================================
    pause
)
