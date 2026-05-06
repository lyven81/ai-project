@echo off
REM Bookshelf - start 4 agent services + 1 web app (5 cmd windows total).
REM Each agent runs via its own scripts\run-*.bat (visible logs, pause on exit).

setlocal EnableDelayedExpansion

set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM ---------- Load .env if it exists ----------
if exist "%PROJECT_ROOT%\.env" (
    echo Loading .env...
    for /f "usebackq tokens=1,* delims==" %%a in ("%PROJECT_ROOT%\.env") do (
        set "_key=%%a"
        if not "!_key!"=="" if not "!_key:~0,1!"=="#" (
            set "%%a=%%b"
        )
    )
)

if "%GOOGLE_API_KEY%"=="" (
    echo.
    echo [WARNING] GOOGLE_API_KEY is not set. Set it in .env first.
    echo Get a free key at https://aistudio.google.com/apikey
    timeout /t 3 >nul
)

set "PYTHONPATH=%PROJECT_ROOT%"
set "PYTHONUTF8=1"
set "AGENT_SERVER_URL=http://localhost:8004"

echo.
echo ====================================================================
echo  Bookshelf - starting 5 services
echo ====================================================================
echo  Project root: %PROJECT_ROOT%
echo  Dataset:      %PROJECT_ROOT%\dataset\dataset.xlsx
echo ====================================================================
echo.

echo Starting Researcher...
start "" cmd /c ""%PROJECT_ROOT%\scripts\run-researcher.bat""

echo Starting Judge...
start "" cmd /c ""%PROJECT_ROOT%\scripts\run-judge.bat""

echo Starting Content Builder...
start "" cmd /c ""%PROJECT_ROOT%\scripts\run-content-builder.bat""

echo Waiting 6 seconds for child agents to bind...
timeout /t 6 /nobreak >nul

echo Starting Orchestrator...
start "" cmd /c ""%PROJECT_ROOT%\scripts\run-orchestrator.bat""

echo Waiting 5 seconds for orchestrator to bind...
timeout /t 5 /nobreak >nul

echo Opening browser at http://localhost:8000 ...
start "" "http://localhost:8000"

echo.
echo ====================================================================
echo  Web app starting on :8000 in this window.
echo  Close this window OR run stop.bat to shut everything down.
echo ====================================================================
echo.
cd /d "%PROJECT_ROOT%\app"
python -m uvicorn main:app --host 0.0.0.0 --port 8000

echo.
echo Web app stopped. Run stop.bat to close the 4 agent windows.
pause
