#!/usr/bin/env python3
"""
Complete testing script for Claude PDF Summarizer
Tests both API endpoints and UI functionality
"""

import requests
import time
import webbrowser
from pathlib import Path
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Configuration
API_URL = "https://claude-pdf-summarizer-wmpytqcfsa-uc.a.run.app"
FRONTEND_URL = "http://localhost:3000"

def create_test_pdf():
    """Create a test PDF file for testing"""
    
    print("📄 Creating test PDF...")
    
    # Create temporary PDF file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
    
    # Content for the PDF
    styles = getSampleStyleSheet()
    content = []
    
    title = Paragraph("Test Document for Claude PDF Summarizer", styles['Title'])
    content.append(title)
    content.append(Spacer(1, 12))
    
    intro = Paragraph("""
    This is a test document created specifically for testing the Claude PDF Summarizer application.
    The document contains various types of content to ensure the summarization works properly across
    different text structures and information types.
    """, styles['Normal'])
    content.append(intro)
    content.append(Spacer(1, 12))
    
    section1 = Paragraph("Business Overview", styles['Heading2'])
    content.append(section1)
    content.append(Spacer(1, 6))
    
    business_text = Paragraph("""
    Our company specializes in developing innovative software solutions for small and medium-sized businesses.
    We focus on three core areas: customer relationship management, inventory tracking, and financial reporting.
    Over the past year, we have served over 500 clients and achieved a 95% customer satisfaction rate.
    Our revenue has grown by 40% year-over-year, and we plan to expand our team by 25% in the coming quarter.
    """, styles['Normal'])
    content.append(business_text)
    content.append(Spacer(1, 12))
    
    section2 = Paragraph("Technical Implementation", styles['Heading2'])
    content.append(section2)
    content.append(Spacer(1, 6))
    
    technical_text = Paragraph("""
    The application is built using modern web technologies including React for the frontend,
    Node.js for the backend, and PostgreSQL for data storage. We implement RESTful APIs
    for all data interactions and use JWT tokens for authentication. The system is deployed
    on Google Cloud Platform using Docker containers and Kubernetes for orchestration.
    We maintain 99.9% uptime and process over 10,000 API requests per day.
    """, styles['Normal'])
    content.append(technical_text)
    content.append(Spacer(1, 12))
    
    section3 = Paragraph("Future Plans", styles['Heading2'])
    content.append(section3)
    content.append(Spacer(1, 6))
    
    future_text = Paragraph("""
    In the next quarter, we plan to launch three new features: automated report generation,
    mobile application support, and integration with popular accounting software like QuickBooks.
    We are also exploring artificial intelligence capabilities to provide predictive analytics
    and automated insights for our customers. The development team will focus on improving
    performance and adding multi-language support for international expansion.
    """, styles['Normal'])
    content.append(future_text)
    
    # Build the PDF
    doc.build(content)
    temp_file.close()
    
    print(f"✅ Test PDF created: {temp_file.name}")
    return temp_file.name

def test_api_endpoints():
    """Test all API endpoints"""
    
    print("\n🧪 Testing API endpoints...")
    print(f"🔗 API Base URL: {API_URL}")
    
    # Test health endpoint
    try:
        print("\n1️⃣ Testing health endpoint...")
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test root endpoint
    try:
        print("\n2️⃣ Testing root endpoint...")
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            print("   ✅ Root endpoint working")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test summarize endpoint
    try:
        print("\n3️⃣ Testing summarize endpoint...")
        
        # Create test PDF
        pdf_path = create_test_pdf()
        
        with open(pdf_path, 'rb') as pdf_file:
            files = {'file': ('test.pdf', pdf_file, 'application/pdf')}
            data = {
                'style': 'Simple Version',
                'language': 'English',
                'bullet_points': 3
            }
            
            print("   📤 Sending summarization request...")
            response = requests.post(
                f"{API_URL}/summarize", 
                files=files, 
                data=data, 
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Summarization successful!")
                print("   📝 Summary preview:")
                summary = result.get('summary', '')[:200] + '...' if len(result.get('summary', '')) > 200 else result.get('summary', '')
                print(f"      {summary}")
                print(f"   📊 Metadata: {result.get('metadata', {})}")
            else:
                print(f"   ❌ Summarization failed: {result}")
        else:
            print(f"   ❌ Summarization request failed: {response.status_code}")
            print(f"   📄 Error: {response.text}")
        
        # Clean up test file
        Path(pdf_path).unlink(missing_ok=True)
        
    except Exception as e:
        print(f"   ❌ Summarization test error: {e}")
    
    return True

def test_frontend():
    """Test frontend accessibility"""
    
    print(f"\n🖥️ Testing frontend...")
    print(f"🔗 Frontend URL: {FRONTEND_URL}")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
            return True
        else:
            print(f"   ❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend test error: {e}")
        print("   💡 Make sure to start the frontend server first:")
        print("      python serve.py")
        return False

def run_complete_test():
    """Run complete test suite"""
    
    print("🚀 Claude PDF Summarizer - Complete Test Suite")
    print("=" * 55)
    
    # Test API
    api_ok = test_api_endpoints()
    
    # Test Frontend
    frontend_ok = test_frontend()
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 TEST SUMMARY")
    print("=" * 55)
    
    if api_ok:
        print("✅ API Backend: Working")
    else:
        print("❌ API Backend: Issues detected")
    
    if frontend_ok:
        print("✅ Frontend UI: Accessible")
    else:
        print("❌ Frontend UI: Not accessible")
    
    print("\n🎯 NEXT STEPS:")
    if not frontend_ok:
        print("1. Start frontend server: python serve.py")
        print("2. Open http://localhost:3000 in your browser")
    else:
        print("1. Frontend is ready at http://localhost:3000")
    
    if api_ok:
        print("2. Upload a PDF file to test the complete workflow")
        print("3. Try different summary styles and languages")
    
    print(f"\n🔗 Direct links:")
    print(f"   Frontend: {FRONTEND_URL}")
    print(f"   API Docs: {API_URL}/docs")
    print(f"   API Health: {API_URL}/health")

if __name__ == "__main__":
    try:
        run_complete_test()
    except KeyboardInterrupt:
        print("\n\n⛔ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")