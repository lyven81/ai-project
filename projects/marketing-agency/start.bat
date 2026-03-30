@echo off
title Marketing Agency Dashboard
echo ============================================
echo   Marketing Agency Dashboard
echo   Pau Analytics + Pau AI
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Installing dependencies...
pip install -q -r requirements.txt

echo [2/2] Starting dashboard at http://localhost:8100
echo.
echo   Open your browser to: http://localhost:8100
echo.

python -m uvicorn app:app --host 0.0.0.0 --port 8100 --reload

pause
