#!/bin/bash

# AI Background Changer Deployment Script
# Deploys the application to Google Cloud Run

set -e

# Configuration
PROJECT_ID="your-project-id"
SERVICE_NAME="ai-background-changer"
REGION="us-west1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Starting deployment of AI Background Changer..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Build the application
echo "📦 Building the application..."
npm run build

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t $IMAGE_NAME .

# Push to Container Registry
echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars API_KEY=$GEMINI_API_KEY \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10

echo "✅ Deployment completed successfully!"
echo "🔗 Service URL: $(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')"