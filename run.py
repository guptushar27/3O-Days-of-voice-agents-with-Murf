
#!/usr/bin/env python3
"""
NeuralVoice AI - Startup Script
Simple script to launch the voice agent application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("🎙️ Starting NeuralVoice AI...")
    print("🌐 Application will be available at: http://localhost:5000")
    print("🔧 Make sure your API keys are configured in environment variables")
    print("📝 Check README.md for complete setup instructions")
    print("-" * 60)
    
    # Check for required API keys
    required_keys = ['ASSEMBLYAI_API_KEY', 'GEMINI_API_KEY', 'MURF_API_KEY']
    missing_keys = [key for key in required_keys if not os.environ.get(key)]
    
    if missing_keys:
        print("⚠️  Warning: Missing API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("   App will use fallback responses for missing services")
        print("-" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 NeuralVoice AI shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)
