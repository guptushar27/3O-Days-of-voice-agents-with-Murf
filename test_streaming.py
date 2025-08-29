#!/usr/bin/env python3
"""
Test script for Day 16 & 17 - Streaming Audio and Real-time Transcription
"""
import os
import sys
import requests
import time

def test_server_status():
    """Test if the server is running"""
    try:
        response = requests.get('http://localhost:5000/')
        print(f"✅ Server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        return False

def test_websocket_endpoint():
    """Test WebSocket test page"""
    try:
        response = requests.get('http://localhost:5000/test-websocket')
        print(f"✅ WebSocket test page accessible (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ WebSocket test page error: {e}")
        return False

def test_streaming_endpoint():
    """Test streaming test page"""
    try:
        response = requests.get('http://localhost:5000/test-streaming')
        print(f"✅ Streaming test page accessible (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Streaming test page error: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n📋 Environment Configuration:")

    # Check AssemblyAI API key
    assemblyai_key = os.environ.get('ASSEMBLYAI_API_KEY')
    if assemblyai_key:
        print(f"✅ ASSEMBLYAI_API_KEY: {'*' * 20}{assemblyai_key[-4:]}")
    else:
        print("❌ ASSEMBLYAI_API_KEY: Not configured")
        print("   📝 Set this for Day 17 transcription to work")

    # Check other keys
    keys_to_check = ['GEMINI_API_KEY', 'MURF_API_KEY']
    for key in keys_to_check:
        value = os.environ.get(key)
        if value:
            print(f"✅ {key}: {'*' * 20}{value[-4:]}")
        else:
            print(f"⚠️  {key}: Not configured")

def check_directories():
    """Check if required directories exist"""
    print("\n📁 Directory Structure:")

    dirs_to_check = [
        'instance',
        'instance/audio_streams',
        'services',
        'static/js',
        'templates'
    ]

    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (missing)")
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"   📝 Created {dir_path}/")
            except Exception as e:
                print(f"   ❌ Failed to create: {e}")

def main():
    """Run all tests"""
    print("🧪 VoxAura Day 16 & 17 Testing")
    print("=" * 50)

    # Check environment and directories first
    check_environment()
    check_directories()

    print("\n🌐 Server Tests:")

    # Test server
    if not test_server_status():
        print("\n💡 To start the server, run: python app.py")
        sys.exit(1)

    # Test endpoints
    test_websocket_endpoint()
    test_streaming_endpoint()

    print("\n📋 Detailed Testing Instructions:")

    print("\n🎯 Day 16 (Audio Streaming):")
    print("   1. Visit: http://0.0.0.0:5000/test-streaming")
    print("   2. Click 'Start Audio Streaming'")
    print("   3. Speak into microphone for 10-15 seconds")
    print("   4. Click 'Stop Audio Streaming'")
    print("   5. Check instance/audio_streams/ for saved files")

    print("\n📝 Day 17 (Real-time Transcription):")
    print("   1. Click 'Start Streaming + Transcription'")
    print("   2. Speak clearly: \"Hello, this is a test for day seventeen\"")
    print("   3. Pause and speak again: \"The transcription should appear in real time\"")
    print("   4. Watch for transcriptions in the UI (yellow=partial, green=final)")
    print("   5. Check server console for detailed output:")
    print("      - Look for \"📝 DAY 17 TRANSCRIPTION OUTPUT\"")
    print("      - Final transcriptions will show as \"🎯 FINAL TRANSCRIPTION:\"")

    print("\n🎯 Day 18 (Turn Detection):")
    print("   1. With transcription running, speak a sentence")
    print("   2. Pause for 2+ seconds (stay silent)")
    print("   3. Watch for blue \"Turn Detected\" notifications in UI")
    print("   4. Check server console for:")
    print("      - \"🎯 DAY 18 TURN DETECTION TRIGGERED!\"")
    print("      - \"📍 User stopped talking - End of turn detected\"")
    print("   5. Browser console should show turn detection logs")

    print("\n✨ All tests configured!")

if __name__ == '__main__':
    main()