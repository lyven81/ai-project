@echo off
cd /d "%~dp0"
echo Starting Football Assistant Coach...
echo.
echo The app will open in your browser automatically.
echo To stop the app, close this window or press Ctrl+C.
echo.
streamlit run app.py
pause
