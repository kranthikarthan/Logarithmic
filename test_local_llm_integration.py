#!/usr/bin/env python3
"""
Test Local LLM Integration with Assertly
"""

import requests
import json

def test_local_llm_integration():
    """Test if local LLM is being used as fallback"""
    print("🔍 Testing Local LLM Integration...")
    
    # Test data
    test_data = {
        "title": "User Login",
        "description": "As a user, I want to login to the system",
        "acceptance_criteria": ["User can login with valid credentials"],
        "business_value": "Access to user account",
        "user_persona": "Registered user"
    }
    
    try:
        # Test AI generate test cases endpoint
        print("  Testing /api/ai/generate-test-cases...")
        response = requests.post(
            'http://localhost:5000/api/ai/generate-test-cases',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            provider = data.get('provider', 'unknown')
            note = data.get('note', '')
            
            print(f"    ✅ Response received")
            print(f"    Provider: {provider}")
            print(f"    Note: {note}")
            
            if provider == 'local-llm':
                print("    🎉 Local LLM is being used!")
                return True
            elif provider == 'mock-fallback':
                print("    ⚠️ Using mock fallback - local LLM not working")
                return False
            else:
                print(f"    ❓ Unknown provider: {provider}")
                return False
        else:
            print(f"    ❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_local_llm_server():
    """Test if local LLM server is accessible"""
    print("🔍 Testing Local LLM Server...")
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"    ✅ Local LLM server is running")
            print(f"    Available models: {len(models)}")
            for model in models:
                print(f"      - {model.get('name', 'unknown')}")
            return True
        else:
            print(f"    ❌ Local LLM server not responding: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ Local LLM server not accessible: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Local LLM Integration Test")
    print("=" * 50)
    
    # Test local LLM server
    server_ok = test_local_llm_server()
    
    # Test integration
    integration_ok = test_local_llm_integration()
    
    print("\n📊 Test Results:")
    print(f"  Local LLM Server: {'✅ OK' if server_ok else '❌ FAIL'}")
    print(f"  Integration: {'✅ OK' if integration_ok else '❌ FAIL'}")
    
    if server_ok and integration_ok:
        print("\n🎉 Local LLM integration is working!")
    else:
        print("\n⚠️ Local LLM integration needs attention")

if __name__ == "__main__":
    main()