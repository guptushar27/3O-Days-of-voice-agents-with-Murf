
"""
Error Simulation Script
This script can be used to simulate various API failures by temporarily
commenting out or modifying API configurations in the main application.

Run this to test different error scenarios:
1. STT (Speech-to-Text) failures
2. LLM (Language Model) failures  
3. TTS (Text-to-Speech) failures
4. Network timeouts
"""

import os
import sys

def simulate_assemblyai_error():
    """Simulate AssemblyAI API failure by clearing the API key"""
    print("🔧 Simulating AssemblyAI (STT) Error...")
    print("Set ASSEMBLYAI_API_KEY to empty or invalid value in environment")
    print("This will trigger fallback transcription responses")
    print("Expected behavior: Fallback audio saying 'I'm having trouble with speech recognition'")

def simulate_gemini_error():
    """Simulate Gemini API failure by clearing the API key"""
    print("🔧 Simulating Gemini (LLM) Error...")
    print("Set GEMINI_API_KEY to empty or invalid value in environment")
    print("This will trigger fallback LLM responses")
    print("Expected behavior: Predefined conversational fallback responses")

def simulate_murf_error():
    """Simulate Murf API failure by clearing the API key"""
    print("🔧 Simulating Murf (TTS) Error...")
    print("Set MURF_API_KEY to empty or invalid value in environment")
    print("This will trigger fallback gTTS audio generation")
    print("Expected behavior: Fallback audio using Google TTS")

def simulate_all_errors():
    """Simulate all API failures at once"""
    print("🔧 Simulating ALL API Errors...")
    print("Clear all API keys: ASSEMBLYAI_API_KEY, GEMINI_API_KEY, MURF_API_KEY")
    print("This will trigger complete fallback mode")
    print("Expected behavior: 'I'm having trouble connecting right now' fallback audio")

def print_current_config():
    """Print current API configuration status"""
    print("\n📊 Current API Configuration Status:")
    print(f"AssemblyAI API Key: {'✓ Set' if os.environ.get('ASSEMBLYAI_API_KEY') else '✗ Not Set'}")
    print(f"Gemini API Key: {'✓ Set' if os.environ.get('GEMINI_API_KEY') else '✗ Not Set'}")
    print(f"Murf API Key: {'✓ Set' if os.environ.get('MURF_API_KEY') else '✗ Not Set'}")
    print()

def main():
    print("🚨 Voice Agent Error Simulation Testing")
    print("=" * 50)
    
    print_current_config()
    
    print("Choose an error scenario to simulate:")
    print("1. AssemblyAI (STT) Error")
    print("2. Gemini (LLM) Error") 
    print("3. Murf (TTS) Error")
    print("4. All APIs Error")
    print("5. Show current configuration")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-5): ").strip()
    
    if choice == "1":
        simulate_assemblyai_error()
    elif choice == "2":
        simulate_gemini_error()
    elif choice == "3":
        simulate_murf_error()
    elif choice == "4":
        simulate_all_errors()
    elif choice == "5":
        print_current_config()
    elif choice == "0":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice. Please try again.")
    
    print("\n" + "=" * 50)
    print("💡 Testing Instructions:")
    print("1. Clear the appropriate API keys from your environment or .env file")
    print("2. Restart the Flask application")
    print("3. Test the voice agent functionality")
    print("4. Observe the fallback responses in action")
    print("5. Check the console logs for error handling details")
    print("6. Restore API keys when testing is complete")

if __name__ == "__main__":
    main()
