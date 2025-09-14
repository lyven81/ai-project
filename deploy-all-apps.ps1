Write-Host "================================" -ForegroundColor Green
Write-Host "Deploying All AI Portfolio Apps" -ForegroundColor Green  
Write-Host "with Updated Color Scheme" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

Write-Host "Please ensure you are logged into Google Cloud first:" -ForegroundColor Yellow
Write-Host "  gcloud auth login" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to continue once you're authenticated"

Write-Host ""
Write-Host "Starting deployments..." -ForegroundColor Cyan
Write-Host ""

# Deploy Pose Perfect AI
Write-Host "[1/9] Deploying Pose Perfect AI..." -ForegroundColor Cyan
Set-Location "C:\Users\Lenovo\ai-project\projects\pose-perfect-ai"
gcloud run deploy pose-perfect-ai --source . --region us-west1 --allow-unauthenticated

# Deploy Virtual Try-On Studio
Write-Host "[2/9] Deploying Virtual Try-On Studio..." -ForegroundColor Cyan
Set-Location "C:\Users\Lenovo\ai-project\projects\virtual-try-on-studio"
gcloud run deploy virtual-try-on-studio --source . --region us-west1 --allow-unauthenticated

# Deploy AI Group Photo Generator
Write-Host "[3/9] Deploying AI Group Photo Generator..." -ForegroundColor Cyan
Set-Location "C:\Users\Lenovo\ai-project\projects\ai-group-photo-generator"
gcloud run deploy ai-group-photo-generator --source . --region us-west1 --allow-unauthenticated

# Deploy AI Photo Editor
Write-Host "[4/9] Deploying AI Photo Editor (Gemini Image Editor)..." -ForegroundColor Cyan
Set-Location "C:\Users\Lenovo\ai-project\projects\ai-photo-editor"
gcloud run deploy gemini-image-editor --source . --region us-west1 --allow-unauthenticated

# Deploy Claude PDF Summarizer
Write-Host "[5/9] Deploying Claude PDF Summarizer..." -ForegroundColor Cyan
Set-Location "C:\Users\Lenovo\ai-project\projects\claude-pdf-summarizer"
gcloud run deploy summarizer --source . --region asia-southeast1 --allow-unauthenticated

# Deploy Chinese Traditional Calendar
Write-Host "[6/9] Deploying Chinese Traditional Calendar..." -ForegroundColor Cyan
Set-Location "C:\Users\Lenovo\ai-project\projects\chinese-calender"
gcloud run deploy chinese-calender --source . --region asia-southeast1 --allow-unauthenticated

# Deploy Horoscope Chatbot
Write-Host "[7/9] Deploying Horoscope Chatbot..." -ForegroundColor Cyan
Set-Location "C:\Users\Lenovo\ai-project\projects\horoscope-chatbot"
gcloud run deploy horoscope-chatbot --source . --region asia-southeast1 --allow-unauthenticated

# Deploy Feng Shui Chatbot
Write-Host "[8/9] Deploying Feng Shui Chatbot..." -ForegroundColor Cyan
Set-Location "C:\Users\Lenovo\ai-project\projects\fengshui-chatbot"
gcloud run deploy fengshui-chatbot --source . --region asia-southeast1 --allow-unauthenticated

# Deploy AI Recipe Generator
Write-Host "[9/9] Deploying AI Recipe Generator..." -ForegroundColor Cyan
Set-Location "C:\Users\Lenovo\ai-project\projects\image-recipe-generator"
gcloud run deploy image-recipe-generator --source . --region us-central1 --allow-unauthenticated

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "All deployments completed!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

Write-Host "Your portfolio apps are now live with the standardized color scheme:" -ForegroundColor Yellow
Write-Host "- Pose Perfect AI: https://pose-perfect-ai-169218045868.us-west1.run.app/" -ForegroundColor White
Write-Host "- Virtual Try-On Studio: https://virtual-try-on-studio-169218045868.us-west1.run.app/" -ForegroundColor White
Write-Host "- AI Group Photo Generator: https://ai-group-photo-generator-169218045868.us-west1.run.app/" -ForegroundColor White
Write-Host "- AI Photo Editor: https://gemini-image-editor-169218045868.us-west1.run.app/" -ForegroundColor White
Write-Host "- PDF Summarizer: https://summarizer-218391175125.asia-southeast1.run.app/" -ForegroundColor White
Write-Host "- Chinese Calendar: https://chinese-calender-218391175125.asia-southeast1.run.app/" -ForegroundColor White
Write-Host "- Horoscope Chatbot: https://horoscope-chatbot-218391175125.asia-southeast1.run.app/" -ForegroundColor White
Write-Host "- Feng Shui Chatbot: https://fengshui-chatbot-218391175125.asia-southeast1.run.app/" -ForegroundColor White
Write-Host "- Recipe Generator: https://image-recipe-generator-218391175125.us-central1.run.app/" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"