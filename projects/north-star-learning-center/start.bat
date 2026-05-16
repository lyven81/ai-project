@echo off
cd /d "%~dp0"

echo.
echo =====================================================
echo   North Star Learning Center
echo   AI Ecosystem for Personalized Education
echo =====================================================
echo.

REM Check Python is on PATH
where python >nul 2>&1
if errorlevel 1 (
    echo [error] Python is not in your PATH.
    echo         Install Python 3.11 or newer from https://python.org
    echo.
    pause
    exit /b 1
)

REM Warn if no .env (app still runs with canned letters)
if not exist .env (
    echo [info] No .env file found.
    echo        Parent letters will use canned fallback text.
    echo        For live Gemini letters: copy .env.example to .env and
    echo        paste your API key from https://aistudio.google.com/apikey
    echo.
)

REM Install / update deps (silent unless something fails)
echo Installing Python dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [error] pip install failed.
    pause
    exit /b 1
)

REM Prepare data (idempotent — safe to re-run)
echo Preparing data...
python prepare_data.py
if errorlevel 1 (
    echo [error] Data preparation failed.
    pause
    exit /b 1
)

REM Open browser in 3 seconds while server starts
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8080"

echo.
echo =====================================================
echo   Server starting at http://localhost:8080
echo   Your browser will open in 3 seconds.
echo   Press Ctrl+C in this window to stop the server.
echo =====================================================
echo.

python main.py

REM If python exits, pause so the user can see any error
echo.
echo Server stopped.
pause
