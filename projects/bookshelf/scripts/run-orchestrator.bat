@echo off
title Bookshelf Orchestrator (8004)
set "PROJECT_ROOT=%~dp0.."
for %%i in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fi"

set "PYTHONPATH=%PROJECT_ROOT%"
set "PYTHONUTF8=1"
set "RESEARCHER_AGENT_CARD_URL=http://localhost:8001/a2a/agent/.well-known/agent-card.json"
set "JUDGE_AGENT_CARD_URL=http://localhost:8002/a2a/agent/.well-known/agent-card.json"
set "CONTENT_BUILDER_AGENT_CARD_URL=http://localhost:8003/a2a/agent/.well-known/agent-card.json"
if "%BOOKSHELF_MODEL%"=="" set "BOOKSHELF_MODEL=gemini-2.5-flash"

echo.
echo === Orchestrator (port 8004) ===
echo PROJECT_ROOT=%PROJECT_ROOT%
echo.

cd /d "%PROJECT_ROOT%\agents\orchestrator"
python adk_app.py --host 0.0.0.0 --port 8004 .

echo.
echo Orchestrator exited. Press any key to close.
pause >nul
