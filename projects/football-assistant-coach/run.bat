@echo off
echo Starting Football Assistant Coach...
echo.
echo Opening the app in your browser at http://localhost:8501
echo (It may take a few seconds to load the first time)
echo.
start "" http://localhost:8501
streamlit run app.py
pause
