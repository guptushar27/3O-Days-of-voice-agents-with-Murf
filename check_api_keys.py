
#!/usr/bin/env python3
"""
API Key Validation Script for VoxAura Day 20
"""
import os

def check_api_keys():
    """Check all required API keys"""
    print("🔍 API Key Validation for Day 20")
    print("=" * 50)
    
    # Check AssemblyAI
    assemblyai_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if assemblyai_key:
        if len(assemblyai_key) > 20:
            print(f"✅ ASSEMBLYAI_API_KEY: Configured ({len(assemblyai_key)} chars)")
        else:
            print(f"⚠️ ASSEMBLYAI_API_KEY: Too short ({len(assemblyai_key)} chars)")
    else:
        print("❌ ASSEMBLYAI_API_KEY: Not configured")
        print("   💡 Get from: https://www.assemblyai.com/")
    
    # Check Google AI
    google_key = os.environ.get("GOOGLE_AI_API_KEY")
    if google_key:
        if len(google_key) > 30:
            print(f"✅ GOOGLE_AI_API_KEY: Configured ({len(google_key)} chars)")
        else:
            print(f"⚠️ GOOGLE_AI_API_KEY: Too short ({len(google_key)} chars)")
    else:
        print("❌ GOOGLE_AI_API_KEY: Not configured")
        print("   💡 Get from: https://aistudio.google.com/")
    
    # Check Murf
    murf_key = os.environ.get("MURF_API_KEY")
    if murf_key:
        if len(murf_key) > 10:
            print(f"✅ MURF_API_KEY: Configured ({len(murf_key)} chars)")
        else:
            print(f"⚠️ MURF_API_KEY: Too short ({len(murf_key)} chars)")
    else:
        print("❌ MURF_API_KEY: Not configured")
        print("   💡 Get from: https://murf.ai/")
    
    print("\n" + "=" * 50)
    
    # Check if all keys are present
    all_configured = all([assemblyai_key, google_key, murf_key])
    
    if all_configured:
        print("✅ All API keys are configured!")
        print("🚀 Ready to run Day 20 tests")
    else:
        print("❌ Some API keys are missing")
        print("💡 Please configure missing keys in the Secrets panel")
        print("💡 Go to: Secrets tab → Add new secret")
    
    return all_configured

if __name__ == "__main__":
    check_api_keys()
#!/usr/bin/env python3
"""
API Keys Configuration Checker
"""

import os

def check_api_keys():
    """Check if all required API keys are configured"""
    keys = {
        'ASSEMBLYAI_API_KEY': os.environ.get('ASSEMBLYAI_API_KEY'),
        'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY'),
        'MURF_API_KEY': os.environ.get('MURF_API_KEY')
    }
    
    print("🔑 API Keys Status:")
    print("-" * 40)
    
    all_configured = True
    for key_name, key_value in keys.items():
        status = "✅ Configured" if key_value else "❌ Missing"
        print(f"{key_name}: {status}")
        if not key_value:
            all_configured = False
    
    print("-" * 40)
    
    if all_configured:
        print("✅ All API keys are configured!")
    else:
        print("⚠️  Some API keys are missing. App will use fallbacks where possible.")
    
    print()
    return all_configured

if __name__ == '__main__':
    check_api_keys()
