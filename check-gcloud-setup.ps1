Write-Host "================================" -ForegroundColor Green
Write-Host "Google Cloud Setup Verification" -ForegroundColor Green  
Write-Host "================================" -ForegroundColor Green
Write-Host ""

Write-Host "1. Checking current authentication..." -ForegroundColor Cyan
gcloud auth list

Write-Host ""
Write-Host "2. Checking current project..." -ForegroundColor Cyan
gcloud config get-value project

Write-Host ""
Write-Host "3. Checking available projects..." -ForegroundColor Cyan
gcloud projects list

Write-Host ""
Write-Host "4. Checking Cloud Run services..." -ForegroundColor Cyan
Write-Host "Services in us-west1:" -ForegroundColor Yellow
gcloud run services list --region=us-west1

Write-Host ""
Write-Host "Services in asia-southeast1:" -ForegroundColor Yellow
gcloud run services list --region=asia-southeast1

Write-Host ""
Write-Host "Services in us-central1:" -ForegroundColor Yellow
gcloud run services list --region=us-central1

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Setup Check Complete" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

Read-Host "Press Enter to exit"