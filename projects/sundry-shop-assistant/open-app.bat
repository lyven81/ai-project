@echo off
REM Open the app in your browser.
REM This requires the backend to already be running locally
REM (via run-local.bat) OR deployed to Cloud Run.
REM
REM For local dev, use run-local.bat instead — it starts the server AND opens the browser.

start "" "http://localhost:8000"
