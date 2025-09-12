#!/bin/bash

# Claude PDF Summarizer - Google Cloud Run Deployment Script

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"ai-project-470100"}
SERVICE_NAME="claude-pdf-summarizer"
REGION="us-central1"
REPOSITORY="claude-apps"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}"

echo "🚀 Deploying Claude PDF Summarizer to Google Cloud Run"
echo "Project ID: $PROJECT_ID"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run: gcloud auth login"
    exit 1
fi

# Set the project
echo "📋 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create Artifact Registry repository if it doesn't exist
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Claude apps" \
    || echo "Repository may already exist"

# Configure Docker to use gcloud as a credential helper
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY environment variable is not set"
    echo "Please set it with: export ANTHROPIC_API_KEY=your-api-key"
    exit 1
fi

echo "🔨 Building and deploying..."

# Build and submit using Cloud Build
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --port 8000

echo "✅ Deployment completed!"
echo "🌐 Service URL:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
