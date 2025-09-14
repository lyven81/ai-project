#!/bin/bash

echo "================================"
echo "Deploying US-West1 AI Portfolio Apps"
echo "with Updated Color Scheme"
echo "================================"
echo ""

# Project ID placeholder - EDIT THIS LINE
PROJECT_ID="ai-project-471204"

echo "Using Project ID: $PROJECT_ID"
echo ""
echo "Please ensure you are logged into Google Cloud first:"
echo "  gcloud auth login"
echo ""

read -p "Press Enter to continue once you're authenticated..."

echo ""
echo "Setting project context..."
gcloud config set project $PROJECT_ID

echo ""
echo "Starting US-West1 deployments..."
echo ""

# Deploy Pose Perfect AI
echo "[1/4] Deploying Pose Perfect AI..."
cd "C:/Users/Lenovo/ai-project/projects/pose-perfect-ai"
gcloud run deploy pose-perfect-ai --source . --region us-west1 --allow-unauthenticated --project $PROJECT_ID
echo ""

# Deploy Virtual Try-On Studio
echo "[2/4] Deploying Virtual Try-On Studio..."
cd "C:/Users/Lenovo/ai-project/projects/virtual-try-on-studio"
gcloud run deploy virtual-try-on-studio --source . --region us-west1 --allow-unauthenticated --project $PROJECT_ID
echo ""

# Deploy AI Group Photo Generator
echo "[3/4] Deploying AI Group Photo Generator..."
cd "C:/Users/Lenovo/ai-project/projects/ai-group-photo-generator"
gcloud run deploy ai-group-photo-generator --source . --region us-west1 --allow-unauthenticated --project $PROJECT_ID
echo ""

# Deploy AI Photo Editor (Gemini Image Editor)
echo "[4/4] Deploying AI Photo Editor (Gemini Image Editor)..."
cd "C:/Users/Lenovo/ai-project/projects/ai-photo-editor"
gcloud run deploy gemini-image-editor --source . --region us-west1 --allow-unauthenticated --project $PROJECT_ID
echo ""

echo "================================"
echo "US-West1 deployments completed!"
echo "================================"
echo ""
echo "Your US-West1 apps are now live with the standardized color scheme:"
echo "- Pose Perfect AI: https://pose-perfect-ai-169218045868.us-west1.run.app/"
echo "- Virtual Try-On Studio: https://virtual-try-on-studio-169218045868.us-west1.run.app/"
echo "- AI Group Photo Generator: https://ai-group-photo-generator-169218045868.us-west1.run.app/"
echo "- AI Photo Editor: https://gemini-image-editor-169218045868.us-west1.run.app/"
echo ""

read -p "Press Enter to exit..."