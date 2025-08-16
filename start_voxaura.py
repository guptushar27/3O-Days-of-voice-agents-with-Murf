
#!/usr/bin/env python3
"""
VoxAura AI Voice Agent Startup Script
Enhanced version with better error handling and dependency checking
"""

import os
import sys
import logging
import time
from pathlib import Path

def setup_logging():
    """Setup enhanced logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('voxaura.log')
        ]
    )

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_socketio',
        'pydantic',
        'sqlalchemy',
        'assemblyai',
        'google.genai',
        'gtts',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: uv sync --reinstall")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_environment():
    """Check environment variables"""
    print("\n🔑 Checking environment variables...")
    
    env_vars = {
        'ASSEMBLYAI_API_KEY': 'AssemblyAI (Speech-to-Text)',
        'GEMINI_API_KEY': 'Google Gemini (LLM)',
        'MURF_API_KEY': 'Murf AI (Text-to-Speech)'
    }
    
    for var, description in env_vars.items():
        if os.environ.get(var):
            print(f"✅ {var} - {description}")
        else:
            print(f"⚠️  {var} - {description} (will use fallbacks)")
    
    print("💡 Set API keys in Replit Secrets for full functionality")

def create_directories():
    """Create necessary directories"""
    directories = [
        'instance/static/audio',
        'instance/uploads',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def main():
    """Main startup function"""
    print("🎙️ Starting VoxAura AI Voice Agent...")
    print("=" * 50)
    
    # Setup
    setup_logging()
    
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first!")
        sys.exit(1)
    
    check_environment()
    create_directories()
    
    print("\n🚀 Launching VoxAura server...")
    print("🌐 Server will be available at: http://0.0.0.0:5000")
    print("🔗 WebSocket endpoint: ws://0.0.0.0:5000/socket.io/")
    print("💡 Test interface: http://0.0.0.0:5000/test-websocket")
    print("\n" + "=" * 50)
    
    try:
        # Import after dependency check
        from app import app, socketio
        
        # Start the SocketIO server
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000, 
            debug=True,
            allow_unsafe_werkzeug=True,
            log_output=True
        )
    except KeyboardInterrupt:
        print("\n👋 VoxAura shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting VoxAura: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
