@echo off
title Notebooker - Starting...
color 0A

echo.
echo ========================================
echo    Notebooker - Engineering Notebook
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
echo [1/6] Checking Python installation...
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python found

REM Check if virtual environment exists
echo [2/6] Checking virtual environment...
if not exist "notebooker_env" (
    echo Creating virtual environment...
    py -m venv notebooker_env
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment exists
)

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call notebooker_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

REM Install/upgrade dependencies
echo [4/6] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Trying without --quiet flag...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Still failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✓ Dependencies installed

REM Create necessary directories
echo [5/6] Creating directories...
if not exist "en_files" mkdir en_files
if not exist "images" mkdir images
if not exist "backups" mkdir backups
if not exist "static" mkdir static
if not exist "templates" mkdir templates
echo ✓ Directories created

REM Check if port 5002 is available
echo [6/6] Checking port availability...
netstat -an | findstr ":5002" >nul 2>&1
if not errorlevel 1 (
    echo WARNING: Port 5002 is already in use
    echo Attempting to free the port...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5002"') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo.
echo ========================================
echo    Starting Notebooker Server...
echo ========================================
echo.
echo ✓ All checks passed!
echo ✓ Server starting on: http://localhost:5002
echo ✓ Press Ctrl+C to stop the server
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:5002

REM Start the application
echo Starting Flask application...
py app.py

REM If we get here, the app has stopped
echo.
echo ========================================
echo    Notebooker has stopped
echo ========================================
echo.
pause
