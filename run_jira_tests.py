#!/usr/bin/env python3
"""
Run Jira Integration Tests
Quick script to test Jira integration with stub server
"""

import subprocess
import sys
import time
import os

def main():
    """Run Jira integration tests"""
    print("🚀 Starting Jira Integration Tests")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        'jira_stub.py',
        'test_jira_integration.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file not found: {file}")
            return 1
    
    print("✅ All required files found")
    
    # Run Jira integration test
    print("\n🧪 Running Jira Integration Test...")
    try:
        result = subprocess.run([
            'python3', 'test_jira_integration.py'
        ], timeout=300)
        
        if result.returncode == 0:
            print("\n🎉 Jira Integration Test: PASSED")
            print("✅ Jira integration is working correctly")
            return 0
        else:
            print("\n⚠️ Jira Integration Test: FAILED")
            print("❌ Some Jira integration features need attention")
            return 1
            
    except subprocess.TimeoutExpired:
        print("\n⏰ Jira Integration Test: TIMEOUT")
        print("❌ Test took too long to complete")
        return 1
    except Exception as e:
        print(f"\n❌ Jira Integration Test: ERROR - {e}")
        return 1

if __name__ == "__main__":
    exit(main())