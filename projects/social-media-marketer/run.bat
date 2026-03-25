@echo off
title Social Media Marketer
cd /d "%~dp0"

echo.
echo  ====================================
echo   SOCIAL MEDIA MARKETER
echo   Multi-Agent Marketing Simulation
echo  ====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python is not installed or not in PATH.
    echo  Download Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Install dependencies if needed
echo  Checking dependencies...
pip install -r requirements.txt -q --disable-pip-version-check

echo.
echo  Starting app — opening in your browser...
echo  (Press Ctrl+C in this window to stop the app)
echo.

start "" http://localhost:8501
streamlit run app.py --server.headless false --browser.gatherUsageStats false

pause
