#!/usr/bin/env python3
"""
Simple test script for Assertly Test Management Platform
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from app import app, JiraAssertlyClient
        print("✅ App module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_flask_app():
    """Test that Flask app can be created"""
    try:
        from app import app
        with app.test_client() as client:
            response = client.get('/')
            print("✅ Flask app responds to requests")
            return True
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

def test_jira_client():
    """Test JiraAssertlyClient class"""
    try:
        from app import JiraAssertlyClient
        # Test with dummy credentials
        client = JiraAssertlyClient("https://example.atlassian.net", "user", "token")
        print("✅ JiraAssertlyClient can be instantiated")
        return True
    except Exception as e:
        print(f"❌ JiraAssertlyClient error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Assertly Test Management Platform...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Flask App Test", test_flask_app),
        ("Jira Client Test", test_jira_client)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   Failed: {test_name}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())