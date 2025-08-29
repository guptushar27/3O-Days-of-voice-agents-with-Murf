
#!/usr/bin/env python3
"""
VoxAura AI Voice Assistant Startup Script
This script properly initializes and runs the VoxAura application
"""

import os
import sys
import logging
import subprocess

def check_dependencies():
    """Check and install required dependencies"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'pydantic',
        'flask', 
        'flask_socketio',
        'websockets',
        'assemblyai',
        'google.generativeai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
        try:
            if 'google.generativeai' in missing_packages:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'google-generativeai'])
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Could not install {missing_packages}: {e}")
            print("⚠️ Some features may not work without proper dependencies")

def main():
    """Main startup function"""
    print("🚀 VoxAura AI Voice Agent Startup")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    print("\n🎯 Starting VoxAura Server...")
    print("🌐 Access at: http://0.0.0.0:5000")
    print("🎯 Day 18 Turn Detection: http://0.0.0.0:5000/day18-turn-detection")
    print("=" * 50)
    
    # Import and run main app
    try:
        from main import app, socketio
        
        # Run with SocketIO
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=5000, 
                    debug=False,  # Set to False to reduce console noise
                    allow_unsafe_werkzeug=True)
                    
    except KeyboardInterrupt:
        print("\n👋 VoxAura server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting VoxAura: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
