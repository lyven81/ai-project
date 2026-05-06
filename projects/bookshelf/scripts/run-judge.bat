@echo off
title Bookshelf Judge (8002)
set "PROJECT_ROOT=%~dp0.."
for %%i in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fi"

set "PYTHONPATH=%PROJECT_ROOT%"
set "PYTHONUTF8=1"
if "%BOOKSHELF_MODEL%"=="" set "BOOKSHELF_MODEL=gemini-2.5-flash"

echo.
echo === Judge (port 8002) ===
echo PROJECT_ROOT=%PROJECT_ROOT%
echo.

cd /d "%PROJECT_ROOT%\agents\judge"
python adk_app.py --host 0.0.0.0 --port 8002 --a2a .

echo.
echo Judge exited. Press any key to close.
pause >nul
