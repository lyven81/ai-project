@echo off
echo ================================
echo Deploying All AI Portfolio Apps
echo with Updated Color Scheme
echo ================================

echo.
echo Please ensure you are logged into Google Cloud first:
echo   gcloud auth login
echo.

pause

echo.
echo Starting deployments...
echo.

REM Deploy Pose Perfect AI
echo [1/9] Deploying Pose Perfect AI...
cd /d "C:\Users\Lenovo\ai-project\projects\pose-perfect-ai"
gcloud run deploy pose-perfect-ai --source . --region us-west1 --allow-unauthenticated
echo.

REM Deploy Virtual Try-On Studio
echo [2/9] Deploying Virtual Try-On Studio...
cd /d "C:\Users\Lenovo\ai-project\projects\virtual-try-on-studio"
gcloud run deploy virtual-try-on-studio --source . --region us-west1 --allow-unauthenticated
echo.

REM Deploy AI Group Photo Generator
echo [3/9] Deploying AI Group Photo Generator...
cd /d "C:\Users\Lenovo\ai-project\projects\ai-group-photo-generator"
gcloud run deploy ai-group-photo-generator --source . --region us-west1 --allow-unauthenticated
echo.

REM Deploy AI Photo Editor
echo [4/9] Deploying AI Photo Editor (Gemini Image Editor)...
cd /d "C:\Users\Lenovo\ai-project\projects\ai-photo-editor"
gcloud run deploy gemini-image-editor --source . --region us-west1 --allow-unauthenticated
echo.

REM Deploy Claude PDF Summarizer
echo [5/9] Deploying Claude PDF Summarizer...
cd /d "C:\Users\Lenovo\ai-project\projects\claude-pdf-summarizer"
gcloud run deploy summarizer --source . --region asia-southeast1 --allow-unauthenticated
echo.

REM Deploy Chinese Traditional Calendar
echo [6/9] Deploying Chinese Traditional Calendar...
cd /d "C:\Users\Lenovo\ai-project\projects\chinese-calender"
gcloud run deploy chinese-calender --source . --region asia-southeast1 --allow-unauthenticated
echo.

REM Deploy Horoscope Chatbot
echo [7/9] Deploying Horoscope Chatbot...
cd /d "C:\Users\Lenovo\ai-project\projects\horoscope-chatbot"
gcloud run deploy horoscope-chatbot --source . --region asia-southeast1 --allow-unauthenticated
echo.

REM Deploy Feng Shui Chatbot
echo [8/9] Deploying Feng Shui Chatbot...
cd /d "C:\Users\Lenovo\ai-project\projects\fengshui-chatbot"
gcloud run deploy fengshui-chatbot --source . --region asia-southeast1 --allow-unauthenticated
echo.

REM Deploy AI Recipe Generator
echo [9/9] Deploying AI Recipe Generator...
cd /d "C:\Users\Lenovo\ai-project\projects\image-recipe-generator"
gcloud run deploy image-recipe-generator --source . --region us-central1 --allow-unauthenticated
echo.

echo ================================
echo All deployments completed!
echo ================================
echo.
echo Your portfolio apps are now live with the standardized color scheme:
echo - Pose Perfect AI: https://pose-perfect-ai-169218045868.us-west1.run.app/
echo - Virtual Try-On Studio: https://virtual-try-on-studio-169218045868.us-west1.run.app/
echo - AI Group Photo Generator: https://ai-group-photo-generator-169218045868.us-west1.run.app/
echo - AI Photo Editor: https://gemini-image-editor-169218045868.us-west1.run.app/
echo - PDF Summarizer: https://summarizer-218391175125.asia-southeast1.run.app/
echo - Chinese Calendar: https://chinese-calender-218391175125.asia-southeast1.run.app/
echo - Horoscope Chatbot: https://horoscope-chatbot-218391175125.asia-southeast1.run.app/
echo - Feng Shui Chatbot: https://fengshui-chatbot-218391175125.asia-southeast1.run.app/
echo - Recipe Generator: https://image-recipe-generator-218391175125.us-central1.run.app/
echo.

pause