
#!/usr/bin/env python3
"""
Test Weather Service Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.weather_service import WeatherService
from services.llm_service import LLMService

def test_weather_integration():
    print("🧪 Testing Weather Service Integration...")
    
    # Initialize services
    weather_service = WeatherService()
    llm_service = LLMService()
    
    # Test 1: Direct weather service call
    print("\n1️⃣ Testing direct weather service call:")
    result = weather_service.get_comprehensive_weather_analysis("Mumbai")
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    if result['success']:
        print(f"   Location: {result['location_info']['name']}")
        print(f"   Temperature: {result['current_conditions']['temperature']}°C")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Test 2: LLM service weather skill
    print("\n2️⃣ Testing LLM weather skill integration:")
    result = llm_service.generate_response("What's the weather in Mumbai?")
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    if result['success']:
        print(f"   Skill used: {result.get('skill_used', 'none')}")
        print(f"   Response length: {len(result['response'])} characters")
        print(f"   Preview: {result['response'][:100]}...")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Test 3: Legacy compatibility
    print("\n3️⃣ Testing legacy weather method:")
    result = weather_service.get_weather("Mumbai")
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    if result['success']:
        print(f"   City: {result['city']}")
        print(f"   Temperature: {result['temperature']}°C")
    
    print("\n🏁 Weather integration test completed!")

if __name__ == "__main__":
    test_weather_integration()
