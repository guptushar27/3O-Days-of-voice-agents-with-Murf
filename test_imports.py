
#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import traceback

def test_import(module_name, description=""):
    """Test importing a module"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} {description}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} {description}: {e}")
        return False

def main():
    print("🧪 VoxAura Import Test")
    print("=" * 40)
    
    # Test critical imports
    imports_to_test = [
        ('flask', 'Web framework'),
        ('flask_socketio', 'WebSocket support'),
        ('pydantic', 'Data validation'),
        ('assemblyai', 'Speech-to-text'),
        ('google.generativeai', 'LLM service'),
        ('websockets', 'WebSocket client'),
        ('requests', 'HTTP client'),
        ('sqlalchemy', 'Database ORM'),
    ]
    
    failed_count = 0
    for module, desc in imports_to_test:
        if not test_import(module, desc):
            failed_count += 1
    
    print("\n" + "=" * 40)
    if failed_count == 0:
        print("🎉 All imports successful!")
        
        # Test app import
        try:
            print("\n🧪 Testing app import...")
            from app import app
            print("✅ App imported successfully!")
            print("🚀 Ready to start VoxAura!")
        except Exception as e:
            print(f"❌ App import failed: {e}")
            traceback.print_exc()
            return 1
    else:
        print(f"❌ {failed_count} imports failed")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
