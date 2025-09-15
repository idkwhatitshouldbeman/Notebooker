@echo off
title Notebooker - Quick Start
color 0B

echo.
echo ========================================
echo    Notebooker - Quick Start
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check Python
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "notebooker_env\Scripts\activate.bat" (
    call notebooker_env\Scripts\activate.bat
)

REM Kill any existing process on port 5002
netstat -an | findstr ":5002" >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5002"') do (
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Create directories
if not exist "en_files" mkdir en_files
if not exist "images" mkdir images
if not exist "backups" mkdir backups
if not exist "static" mkdir static
if not exist "templates" mkdir templates

echo Starting Notebooker on http://localhost:5002
echo Press Ctrl+C to stop
echo.

REM Open browser after 2 seconds
start /b timeout /t 2 /nobreak >nul && start http://localhost:5002

REM Start the app
py app.py

pause
