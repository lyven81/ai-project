#!/usr/bin/env python3
"""
Quick deployment helper for frontend files
Creates a clean deployment package
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_deployment_package():
    """Create a clean package for frontend deployment"""
    
    print("📦 Creating frontend deployment package...")
    
    # Files to include in deployment
    frontend_files = [
        'index.html',
        'styles.css', 
        'script.js',
        'netlify.toml'
    ]
    
    # Create deployment directory
    deploy_dir = Path('frontend-deploy')
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Copy frontend files
    for file in frontend_files:
        if Path(file).exists():
            shutil.copy2(file, deploy_dir / file)
            print(f"   ✅ Added {file}")
        else:
            print(f"   ⚠️  Missing {file}")
    
    # Create ZIP package for easy upload
    with zipfile.ZipFile('claude-pdf-summarizer-frontend.zip', 'w') as zipf:
        for file in frontend_files:
            if Path(file).exists():
                zipf.write(file)
    
    print(f"\n🎉 Deployment package created!")
    print(f"📁 Files in './frontend-deploy/' directory")
    print(f"📦 ZIP package: './claude-pdf-summarizer-frontend.zip'")
    
    print(f"\n🚀 Next steps:")
    print(f"1. Go to https://netlify.com")
    print(f"2. Drag & drop the 'frontend-deploy' folder")
    print(f"3. Get instant public URL!")
    
    print(f"\n🔗 Your API is already public:")
    print(f"   https://claude-pdf-summarizer-wmpytqcfsa-uc.a.run.app")
    
    return deploy_dir

def open_deploy_folder():
    """Open the deployment folder in file explorer"""
    deploy_dir = Path('frontend-deploy')
    if deploy_dir.exists():
        if os.name == 'nt':  # Windows
            os.startfile(deploy_dir)
        elif os.name == 'posix':  # macOS/Linux
            os.system(f'open "{deploy_dir}"')  # macOS
            # os.system(f'xdg-open "{deploy_dir}"')  # Linux

if __name__ == "__main__":
    try:
        deploy_dir = create_deployment_package()
        
        # Ask user if they want to open the folder
        response = input("\n📂 Open deployment folder? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            open_deploy_folder()
            
        print(f"\n✨ Ready for deployment! See 'deploy_frontend.md' for detailed instructions.")
        
    except Exception as e:
        print(f"❌ Error: {e}")