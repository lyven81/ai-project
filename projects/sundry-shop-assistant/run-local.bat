@echo off
REM Start the local FastAPI backend + open the browser.
REM First run: create venv + install deps (1-2 minutes). Subsequent runs: start in 3s.

cd /d "%~dp0"

IF NOT EXIST .env (
  echo ERROR: .env file not found.
  echo.
  echo Copy .env.example to .env and paste your Gemini API key.
  echo Get a key at: https://aistudio.google.com/apikey
  pause
  exit /b 1
)

set AUTO_OPEN=1
IF NOT EXIST .venv (
  set AUTO_OPEN=0
  echo.
  echo ================================================
  echo First run detected — setting up Python venv.
  echo This takes 1-2 minutes. Please wait.
  echo ================================================
  echo.
  python -m venv .venv
  IF ERRORLEVEL 1 (
    echo ERROR: Could not create venv. Is Python 3.11+ installed and on PATH?
    pause
    exit /b 1
  )
  call .venv\Scripts\activate.bat
  pip install -r backend\requirements.txt
  IF ERRORLEVEL 1 (
    echo.
    echo ERROR: pip install failed. Check the output above.
    pause
    exit /b 1
  )
  echo.
  echo ================================================
  echo Setup complete. Starting server now.
  echo When you see "Uvicorn running on...", open:
  echo   http://localhost:8000
  echo ================================================
  echo.
) ELSE (
  call .venv\Scripts\activate.bat
  echo Starting backend at http://localhost:8000 ...
)

REM On subsequent runs, open the browser after a short delay (server is up in ~2-3s)
IF "%AUTO_OPEN%"=="1" (
  start "" cmd /c "timeout /t 4 /nobreak >nul && start "" http://localhost:8000"
)

cd backend
python main.py
