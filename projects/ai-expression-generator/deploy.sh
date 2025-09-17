#!/bin/bash

# AI Expression Generator - Deployment Script
# Supports multiple deployment targets: Vercel, Netlify, Docker

set -e

echo "🚀 AI Expression Generator Deployment Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env.local exists
check_env() {
    if [ ! -f ".env.local" ]; then
        print_warning ".env.local not found. Creating from .env.example..."
        cp .env.example .env.local
        print_error "Please update .env.local with your Gemini API key before deploying!"
        exit 1
    fi
}

# Install dependencies
install_deps() {
    print_status "Installing dependencies..."
    npm ci
    print_success "Dependencies installed successfully"
}

# Build the project
build_project() {
    print_status "Building the project..."
    npm run build
    print_success "Project built successfully"
}

# Deploy to Vercel
deploy_vercel() {
    print_status "Deploying to Vercel..."

    if ! command -v vercel &> /dev/null; then
        print_status "Installing Vercel CLI..."
        npm install -g vercel
    fi

    vercel --prod
    print_success "Deployed to Vercel successfully!"
}

# Deploy to Netlify
deploy_netlify() {
    print_status "Deploying to Netlify..."

    if ! command -v netlify &> /dev/null; then
        print_status "Installing Netlify CLI..."
        npm install -g netlify-cli
    fi

    netlify deploy --prod --dir=dist
    print_success "Deployed to Netlify successfully!"
}

# Build Docker image
build_docker() {
    print_status "Building Docker image..."
    docker build -t ai-expression-generator:latest .
    print_success "Docker image built successfully!"

    print_status "To run the container:"
    echo "docker run -p 80:80 ai-expression-generator:latest"
}

# Main deployment logic
main() {
    echo ""
    echo "Select deployment target:"
    echo "1) Vercel (Recommended)"
    echo "2) Netlify"
    echo "3) Docker"
    echo "4) Build only"
    echo ""

    read -p "Enter your choice (1-4): " choice

    case $choice in
        1)
            check_env
            install_deps
            build_project
            deploy_vercel
            ;;
        2)
            check_env
            install_deps
            build_project
            deploy_netlify
            ;;
        3)
            check_env
            build_docker
            ;;
        4)
            check_env
            install_deps
            build_project
            print_success "Build completed. Files are in the 'dist' directory."
            ;;
        *)
            print_error "Invalid choice. Please select 1-4."
            exit 1
            ;;
    esac
}

# Run main function
main "$@"