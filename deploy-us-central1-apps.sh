#!/bin/bash

echo "================================"
echo "Deploying US-Central1 AI Portfolio Apps"
echo "with Updated Color Scheme"
echo "================================"
echo ""

# Project ID placeholder - EDIT THIS LINE
PROJECT_ID="ai-project-470100"

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
echo "Starting US-Central1 deployments..."
echo ""

# Deploy AI Recipe Generator
echo "[1/1] Deploying AI Recipe Generator..."
cd "C:/Users/Lenovo/ai-project/projects/image-recipe-generator"
gcloud run deploy image-recipe-generator --source . --region us-central1 --allow-unauthenticated --project $PROJECT_ID
echo ""

echo "================================"
echo "US-Central1 deployments completed!"
echo "================================"
echo ""
echo "Your US-Central1 app is now live with the standardized color scheme:"
echo "- Recipe Generator: https://image-recipe-generator-218391175125.us-central1.run.app/"
echo ""

read -p "Press Enter to exit..."