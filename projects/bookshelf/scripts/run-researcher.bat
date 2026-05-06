@echo off
title Bookshelf Researcher (8001)
set "PROJECT_ROOT=%~dp0.."
for %%i in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fi"

set "PYTHONPATH=%PROJECT_ROOT%"
set "PYTHONUTF8=1"
set "BOOKSHELF_DATASET_PATH=%PROJECT_ROOT%\dataset\dataset.xlsx"
if "%BOOKSHELF_MODEL%"=="" set "BOOKSHELF_MODEL=gemini-2.5-flash"

echo.
echo === Researcher (port 8001) ===
echo PROJECT_ROOT=%PROJECT_ROOT%
echo DATASET=%BOOKSHELF_DATASET_PATH%
echo.

cd /d "%PROJECT_ROOT%\agents\researcher"
python adk_app.py --host 0.0.0.0 --port 8001 --a2a .

echo.
echo Researcher exited. Press any key to close.
pause >nul
