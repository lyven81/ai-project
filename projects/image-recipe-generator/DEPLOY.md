# Deployment Guide - Image Recipe Generator

## Prerequisites

1. **Google Cloud Account**: Sign up at https://cloud.google.com/
2. **Google Cloud CLI**: Install from https://cloud.google.com/sdk/docs/install
3. **Anthropic API Key**: Get from https://console.anthropic.com/

## Quick Deployment (Recommended)

### Option 1: Using the Deploy Script

1. **Make the script executable** (Linux/Mac):
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Or run directly** (Windows):
   ```bash
   bash deploy.sh
   ```

The script will:
- Authenticate you with Google Cloud
- Enable required APIs
- Prompt for your API key
- Deploy to Cloud Run
- Provide the live URL

### Option 2: Manual Deployment

1. **Install and setup Google Cloud CLI**:
   ```bash
   # Install gcloud CLI first, then:
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable required services**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy image-recipe-generator \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ANTHROPIC_API_KEY="your_api_key_here" \
     --memory 2Gi \
     --cpu 1
   ```

## Configuration

### Environment Variables
- `ANTHROPIC_API_KEY`: Required - Your Anthropic API key

### Resource Limits
- **Memory**: 2GB (configurable in deploy script)
- **CPU**: 1 vCPU
- **Timeout**: 300 seconds
- **Max Instances**: 10 (auto-scales down to 0)

## Monitoring & Debugging

Once deployed, your app will have these endpoints:
- **Main App**: `https://your-app-url.run.app/`
- **Health Check**: `https://your-app-url.run.app/healthz`
- **Environment Debug**: `https://your-app-url.run.app/debug/env`
- **Network Debug**: `https://your-app-url.run.app/debug/net`

## Cost Optimization

Cloud Run pricing is based on usage:
- **Free Tier**: 2 million requests/month
- **Pay-per-use**: Only when requests are being processed
- **Auto-scaling**: Scales to 0 when not in use

## Troubleshooting

### Common Issues

1. **"gcloud: command not found"**
   - Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install

2. **Authentication errors**
   - Run: `gcloud auth login`
   - Set project: `gcloud config set project YOUR_PROJECT_ID`

3. **API key errors**
   - Verify your Anthropic API key at https://console.anthropic.com/
   - Check environment variables in debug endpoint

4. **Memory/timeout errors**
   - Increase memory in deploy command: `--memory 4Gi`
   - Increase timeout: `--timeout 600`

### Viewing Logs
```bash
gcloud logs tail
# or
gcloud run services logs read image-recipe-generator --region us-central1
```

### Updating the App
```bash
gcloud run deploy image-recipe-generator \
  --source . \
  --region us-central1
```

## Security Notes

- API keys are stored as environment variables in Cloud Run
- The app allows unauthenticated access (public)
- Consider adding authentication for production use
- Monitor usage to prevent API key abuse