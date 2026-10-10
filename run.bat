@echo off
title SURF - Satellite Urban Resilience Framework
echo ========================================================
echo   SURF: Satellite Urban Resilience Framework
echo   NASA Space Apps Challenge Platform
echo ========================================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your system PATH.
    echo Please install Python 3.9+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

echo Installing / verifying required dependencies...
python -m pip install -r backend\requirements.txt

echo.
echo Starting SURF Local Server on http://localhost:8000 ...
echo Press Ctrl+C in this terminal window to stop the server.
echo.
python app.py
pause
