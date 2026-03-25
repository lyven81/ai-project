@echo off
title Unusual Coloring Book
color 0E

set APP_DIR=%~dp0

echo. > "%APP_DIR%launch-log.txt"
echo Starting Unusual Coloring Book... >> "%APP_DIR%launch-log.txt"
echo App folder: %APP_DIR% >> "%APP_DIR%launch-log.txt"

echo.
echo  =========================================
echo    Unusual Coloring Book
echo    Starting up...
echo  =========================================
echo.

echo  Starting backend...
echo  Backend: starting >> "%APP_DIR%launch-log.txt"
start "UCB-Backend" /d "%APP_DIR%backend" cmd /k "call venv\Scripts\activate.bat && python main.py"

echo  Waiting for backend...
timeout /t 5 /nobreak >nul

echo  Starting frontend...
echo  Frontend: starting >> "%APP_DIR%launch-log.txt"
start "UCB-Frontend" /d "%APP_DIR%frontend" cmd /k "npm start"

echo  Waiting for frontend...
timeout /t 8 /nobreak >nul

echo  Opening browser...
echo  Browser: opening >> "%APP_DIR%launch-log.txt"
start http://localhost:3000

echo  Done >> "%APP_DIR%launch-log.txt"

echo.
echo  =========================================
echo    App is running at http://localhost:3000
echo    Close UCB-Backend and UCB-Frontend
echo    windows to stop.
echo  =========================================
echo.
pause
