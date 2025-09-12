#!/usr/bin/env python3
"""
Test script for Claude PDF Summarizer API
"""

import requests
import os
from pathlib import Path

def test_api(base_url="http://localhost:8000"):
    """Test the FastAPI endpoints"""
    
    print(f"🧪 Testing API at {base_url}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test summarize endpoint (you'd need a test PDF file)
    print("\n📝 To test the summarize endpoint:")
    print("1. Create a test PDF file")
    print("2. Use curl or a tool like Postman:")
    print(f"""
curl -X POST "{base_url}/summarize" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@test.pdf" \\
  -F "style=Simple Version" \\
  -F "language=English" \\
  -F "bullet_points=3"
    """)
    
    return True

if __name__ == "__main__":
    # Test locally
    test_api()
    
    # Test deployed version (uncomment and replace with your URL)
    # test_api("https://your-service-url.run.app")