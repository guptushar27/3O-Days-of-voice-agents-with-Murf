
#!/usr/bin/env python3
"""
Environment setup script for VoxAura Day 19
Helps configure API keys and test connections
"""
import os

def setup_environment():
    """Setup environment variables and test configuration"""
    print("🚀 VoxAura Day 19 Environment Setup")
    print("=" * 50)
    
    # Check current environment
    gemini_key = os.environ.get("GEMINI_API_KEY")
    assemblyai_key = os.environ.get("ASSEMBLYAI_API_KEY")
    
    print("Current Environment Status:")
    print(f"GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Not set'}")
    print(f"ASSEMBLYAI_API_KEY: {'✅ Set' if assemblyai_key else '❌ Not set'}")
    print()
    
    if not gemini_key:
        print("❌ GEMINI_API_KEY is required for Day 19 streaming LLM")
        print("Get your API key from: https://aistudio.google.com/apikey")
        print("Then set it using Replit Secrets or export GEMINI_API_KEY='your-key'")
        print()
    
    if not assemblyai_key:
        print("❌ ASSEMBLYAI_API_KEY is required for turn detection")
        print("Get your API key from: https://www.assemblyai.com/")
        print("Then set it using Replit Secrets or export ASSEMBLYAI_API_KEY='your-key'")
        print()
    
    if gemini_key and assemblyai_key:
        print("✅ All API keys are configured!")
        print("You can now run the application with: python app.py")
    else:
        print("⚠️  Please configure the missing API keys to use all features")
    
    print("\nFor Replit users:")
    print("1. Click on 'Secrets' in the left sidebar")
    print("2. Add GEMINI_API_KEY and ASSEMBLYAI_API_KEY")
    print("3. Restart the application")

if __name__ == "__main__":
    setup_environment()
