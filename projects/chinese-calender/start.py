#!/usr/bin/env python
"""
黄道吉日APP启动脚本
自动处理数据库初始化、依赖检查等
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version}")

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ All dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        sys.exit(1)

def init_database():
    """初始化数据库"""
    db_file = Path("huangdao_calendar.db")
    if not db_file.exists():
        print("🔄 Initializing database...")
        try:
            from init_db import init_database as init_db
            init_db()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            sys.exit(1)
    else:
        print("✅ Database already exists")

def start_server(host="0.0.0.0", port=8080, reload=False):
    """启动服务器"""
    print(f"🚀 Starting server at http://{host}:{port}")
    print("📱 Open the URL in your browser to access the app")
    print("📖 API Documentation: http://localhost:8080/docs")
    print("💖 Press Ctrl+C to stop\n")
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app:app", 
        "--host", host, 
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")

def main():
    """主函数"""
    print("🗓️  黄道吉日APP启动器")
    print("=" * 40)
    
    # 1. 检查Python版本
    check_python_version()
    
    # 2. 检查依赖
    check_dependencies()
    
    # 3. 初始化数据库
    init_database()
    
    # 4. 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='黄道吉日APP启动器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址 (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口 (default: 8080)')
    parser.add_argument('--reload', action='store_true', help='启用自动重载 (开发模式)')
    parser.add_argument('--test', action='store_true', help='运行API测试')
    
    args = parser.parse_args()
    
    # 5. 运行测试（如果指定）
    if args.test:
        print("🧪 Running tests...")
        try:
            subprocess.run([sys.executable, "simple_test.py"], check=True)
            print("✅ All tests passed!")
        except subprocess.CalledProcessError:
            print("❌ Tests failed!")
            sys.exit(1)
        return
    
    # 6. 启动服务器
    start_server(args.host, args.port, args.reload)

if __name__ == "__main__":
    main()