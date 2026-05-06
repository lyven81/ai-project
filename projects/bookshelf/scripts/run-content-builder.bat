@echo off
title Bookshelf Content Builder (8003)
set "PROJECT_ROOT=%~dp0.."
for %%i in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fi"

set "PYTHONPATH=%PROJECT_ROOT%"
set "PYTHONUTF8=1"
if "%BOOKSHELF_MODEL%"=="" set "BOOKSHELF_MODEL=gemini-2.5-flash"

echo.
echo === Content Builder (port 8003) ===
echo PROJECT_ROOT=%PROJECT_ROOT%
echo.

cd /d "%PROJECT_ROOT%\agents\content_builder"
python adk_app.py --host 0.0.0.0 --port 8003 --a2a .

echo.
echo Content Builder exited. Press any key to close.
pause >nul
