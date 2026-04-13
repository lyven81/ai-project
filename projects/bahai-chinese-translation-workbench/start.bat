@echo off
echo ==========================================
echo  Bahai Chinese Translation Workbench
echo ==========================================
echo.

cd /d "%~dp0"

if not exist .env (
    echo ERROR: .env file not found.
    echo Please copy .env.example to .env and add your API key.
    echo.
    pause
    exit /b 1
)

echo Installing dependencies (first run only)...
pip install -r requirements.txt -q

echo.
echo Starting the Workbench at http://localhost:8080
echo Press Ctrl+C to stop.
echo.

python app.py
pause
