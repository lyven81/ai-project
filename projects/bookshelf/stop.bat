@echo off
REM Bookshelf - stop all running services started by start.bat.
REM Kills any python.exe listening on ports 8000-8005.

echo Stopping Bookshelf services on ports 8000-8005...
echo.

for %%p in (8000 8001 8002 8003 8004 8005) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p ^| findstr LISTENING') do (
        echo  Killing PID %%a on port %%p
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo Done. You can also close any remaining "Bookshelf ..." cmd windows manually.
pause
