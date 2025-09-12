#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend files locally
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def serve_frontend(port=3000):
    """Start a simple HTTP server to serve the frontend"""
    
    # Change to the directory containing the frontend files
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    print(f"🌐 Starting frontend server...")
    print(f"📁 Serving files from: {frontend_dir}")
    print(f"🔗 Local URL: http://localhost:{port}")
    print(f"🚀 API URL: https://claude-pdf-summarizer-wmpytqcfsa-uc.a.run.app")
    print("\n📋 Available files:")
    for file in ['index.html', 'styles.css', 'script.js']:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
    
    # Set up the HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    
    # Add CORS headers for API requests
    class CORSRequestHandler(handler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
            print(f"\n🎉 Server started successfully!")
            print(f"🌍 Open http://localhost:{port} in your browser")
            print("⌨️  Press Ctrl+C to stop the server")
            
            # Try to open the browser automatically
            try:
                webbrowser.open(f'http://localhost:{port}')
                print("🖥️  Browser opened automatically")
            except:
                print("🖥️  Please open your browser manually")
            
            print("\n" + "="*50)
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"\n❌ Port {port} is already in use")
            print(f"💡 Try a different port: python serve.py --port 3001")
        else:
            print(f"\n❌ Error starting server: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    port = 3000
    
    # Check for custom port
    if len(sys.argv) > 1:
        if sys.argv[1] == '--port' and len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print("❌ Invalid port number")
                sys.exit(1)
    
    serve_frontend(port)