@echo off
REM ============================================================
REM Bright Path Tuition Centre — Launch App
REM Double-click this file to start the server and open the app.
REM ============================================================

cd /d "%~dp0"

echo Starting Bright Path Tuition Centre...
echo.

REM Rename .env.example to .env on first run if .env missing
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo Created .env from .env.example
    )
)

REM Build data.db if missing
if not exist "data.db" (
    echo Building database for the first time...
    python seed_generator.py
    echo.
)

REM Launch server in a new window
start "Bright Path Server" cmd /k "python main.py"

REM Wait a few seconds for the server to start, then open browser
timeout /t 4 /nobreak >nul
start "" "http://localhost:8090"

echo.
echo App is opening in your browser at http://localhost:8090
echo Close the "Bright Path Server" window to stop the app.
echo.
pause
