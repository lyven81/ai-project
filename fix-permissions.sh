#!/bin/bash

echo "================================"
echo "Fixing Google Cloud Build Permissions"
echo "================================"
echo ""

# Project IDs
PROJECT_1="ai-project-471204"
PROJECT_2="ai-project-470100"

echo "Setting up permissions for projects:"
echo "- $PROJECT_1 (US-West1)"
echo "- $PROJECT_2 (Asia-Southeast1 & US-Central1)"
echo ""

# Enable Cloud Build API for both projects
echo "Step 1: Enabling Cloud Build API..."
echo "Enabling for $PROJECT_1..."
gcloud services enable cloudbuild.googleapis.com --project $PROJECT_1

echo "Enabling for $PROJECT_2..."
gcloud services enable cloudbuild.googleapis.com --project $PROJECT_2
echo ""

# Get project numbers and set permissions for Project 1
echo "Step 2: Setting up IAM permissions for $PROJECT_1..."
PROJECT_NUMBER_1=$(gcloud projects describe $PROJECT_1 --format="value(projectNumber)")
echo "Project number: $PROJECT_NUMBER_1"

gcloud projects add-iam-policy-binding $PROJECT_1 \
  --member="serviceAccount:$PROJECT_NUMBER_1@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_1 \
  --member="serviceAccount:$PROJECT_NUMBER_1@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_1 \
  --member="serviceAccount:$PROJECT_NUMBER_1@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin"
echo ""

# Get project numbers and set permissions for Project 2
echo "Step 3: Setting up IAM permissions for $PROJECT_2..."
PROJECT_NUMBER_2=$(gcloud projects describe $PROJECT_2 --format="value(projectNumber)")
echo "Project number: $PROJECT_NUMBER_2"

gcloud projects add-iam-policy-binding $PROJECT_2 \
  --member="serviceAccount:$PROJECT_NUMBER_2@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_2 \
  --member="serviceAccount:$PROJECT_NUMBER_2@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_2 \
  --member="serviceAccount:$PROJECT_NUMBER_2@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin"
echo ""

# Verify current account has necessary permissions
echo "Step 4: Verifying your account permissions..."
echo "Your current account:"
gcloud auth list --filter=status:ACTIVE --format="value(account)"

echo ""
echo "Checking your roles in $PROJECT_1:"
gcloud projects get-iam-policy $PROJECT_1 --flatten="bindings[].members" --filter="bindings.members:yven81@gmail.com" --format="table(bindings.role)"

echo ""
echo "Checking your roles in $PROJECT_2:"
gcloud projects get-iam-policy $PROJECT_2 --flatten="bindings[].members" --filter="bindings.members:yven81@gmail.com" --format="table(bindings.role)"

echo ""
echo "================================"
echo "Permission setup completed!"
echo "================================"
echo ""
echo "You can now run the deployment scripts:"
echo "1. ./deploy-us-west1-apps.sh"
echo "2. ./deploy-asia-apps.sh"
echo "3. ./deploy-us-central1-apps.sh"
echo ""

read -p "Press Enter to exit..."