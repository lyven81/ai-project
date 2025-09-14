#!/bin/bash

echo "================================"
echo "Deploying Asia-Southeast1 AI Portfolio Apps"
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
echo "Starting Asia-Southeast1 deployments..."
echo ""

# Deploy Claude PDF Summarizer
echo "[1/4] Deploying Claude PDF Summarizer..."
cd "C:/Users/Lenovo/ai-project/projects/claude-pdf-summarizer"
gcloud run deploy summarizer --source . --region asia-southeast1 --allow-unauthenticated --project $PROJECT_ID
echo ""

# Deploy Chinese Traditional Calendar
echo "[2/4] Deploying Chinese Traditional Calendar..."
cd "C:/Users/Lenovo/ai-project/projects/chinese-calender"
gcloud run deploy chinese-calender --source . --region asia-southeast1 --allow-unauthenticated --project $PROJECT_ID
echo ""

# Deploy Horoscope Chatbot
echo "[3/4] Deploying Horoscope Chatbot..."
cd "C:/Users/Lenovo/ai-project/projects/horoscope-chatbot"
gcloud run deploy horoscope-chatbot --source . --region asia-southeast1 --allow-unauthenticated --project $PROJECT_ID
echo ""

# Deploy Feng Shui Chatbot
echo "[4/4] Deploying Feng Shui Chatbot..."
cd "C:/Users/Lenovo/ai-project/projects/fengshui-chatbot"
gcloud run deploy fengshui-chatbot --source . --region asia-southeast1 --allow-unauthenticated --project $PROJECT_ID
echo ""

echo "================================"
echo "Asia-Southeast1 deployments completed!"
echo "================================"
echo ""
echo "Your Asia-Southeast1 apps are now live with the standardized color scheme:"
echo "- PDF Summarizer: https://summarizer-218391175125.asia-southeast1.run.app/"
echo "- Chinese Calendar: https://chinese-calender-218391175125.asia-southeast1.run.app/"
echo "- Horoscope Chatbot: https://horoscope-chatbot-218391175125.asia-southeast1.run.app/"
echo "- Feng Shui Chatbot: https://fengshui-chatbot-218391175125.asia-southeast1.run.app/"
echo ""

read -p "Press Enter to exit..."