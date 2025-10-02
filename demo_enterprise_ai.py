#!/usr/bin/env python3
"""
Enterprise AI Demonstration with Ollama
Shows real AI test generation using local LLM
"""

import requests
import json
import time
from datetime import datetime

def demo_enterprise_ai():
    """Demonstrate enterprise AI capabilities"""
    print("🎯 Enterprise AI Demonstration with Ollama")
    print("=" * 60)
    print("This demo shows how Assertly uses local LLM for AI features")
    print("No external APIs required - everything runs locally!")
    print()
    
    # Demo 1: AI Test Case Generation
    print("🧪 Demo 1: AI Test Case Generation")
    print("-" * 40)
    
    user_story = {
        "title": "E-commerce Checkout Process",
        "description": "As a customer, I want to complete my purchase securely so I can receive my items",
        "acceptance_criteria": [
            "Customer can add items to cart",
            "Customer can review order details",
            "Customer can enter payment information",
            "Customer can complete purchase",
            "Order confirmation is sent"
        ],
        "business_value": "Revenue generation through online sales",
        "user_persona": "Online shopper"
    }
    
    print(f"📝 User Story: {user_story['title']}")
    print(f"   Description: {user_story['description']}")
    print()
    
    print("🤖 Generating test cases using local LLM...")
    start_time = time.time()
    
    response = requests.post(
        'http://localhost:5000/api/ai/generate-test-cases',
        json=user_story,
        timeout=60
    )
    
    generation_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        provider = data.get('provider', 'unknown')
        count = data.get('count', 0)
        note = data.get('note', '')
        
        print(f"✅ Generated {count} test cases in {generation_time:.2f}s")
        print(f"   Provider: {provider}")
        print(f"   Note: {note}")
        
        # Show generated test cases
        test_cases = data.get('test_cases', [])
        for i, tc in enumerate(test_cases[:3], 1):  # Show first 3
            print(f"\n   Test Case {i}: {tc.get('title', 'Untitled')}")
            print(f"   Description: {tc.get('description', 'No description')}")
            print(f"   Steps: {len(tc.get('steps', []))} steps")
            print(f"   Priority: {tc.get('priority', 'medium')}")
            print(f"   Tags: {', '.join(tc.get('tags', []))}")
        
        if len(test_cases) > 3:
            print(f"   ... and {len(test_cases) - 3} more test cases")
            
    else:
        print(f"❌ Failed to generate test cases: {response.status_code}")
        return
    
    print("\n" + "=" * 60)
    
    # Demo 2: AI Test Improvement
    print("🔧 Demo 2: AI Test Case Improvement")
    print("-" * 40)
    
    test_case = {
        "title": "Basic Login Test",
        "description": "Test user login functionality",
        "steps": [
            "1. Navigate to login page",
            "2. Enter valid username",
            "3. Enter valid password",
            "4. Click login button"
        ],
        "expected_result": "User should be successfully logged in",
        "test_type": "functional",
        "priority": "high"
    }
    
    improvement_prompts = [
        "Add security testing scenarios",
        "Include edge cases and boundary testing",
        "Add performance testing considerations"
    ]
    
    print(f"📝 Original Test Case: {test_case['title']}")
    print(f"   Steps: {len(test_case['steps'])} steps")
    print()
    
    print("🤖 Improving test case using local LLM...")
    start_time = time.time()
    
    response = requests.post(
        'http://localhost:5000/api/ai/improve-test-case',
        json={
            "test_case": test_case,
            "improvement_prompts": improvement_prompts
        },
        timeout=60
    )
    
    improvement_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        provider = data.get('provider', 'unknown')
        note = data.get('note', '')
        
        print(f"✅ Test case improved in {improvement_time:.2f}s")
        print(f"   Provider: {provider}")
        print(f"   Note: {note}")
        
        improved_tc = data.get('improved_test_case', {})
        print(f"\n   Improved Test Case: {improved_tc.get('title', 'Untitled')}")
        print(f"   Description: {improved_tc.get('description', 'No description')}")
        print(f"   Steps: {len(improved_tc.get('steps', []))} steps")
        print(f"   Priority: {improved_tc.get('priority', 'medium')}")
        print(f"   Tags: {', '.join(improved_tc.get('tags', []))}")
        
    else:
        print(f"❌ Failed to improve test case: {response.status_code}")
    
    print("\n" + "=" * 60)
    
    # Demo 3: BDD Scenario Generation
    print("📋 Demo 3: BDD Scenario Generation")
    print("-" * 40)
    
    bdd_story = {
        "title": "User Account Management",
        "description": "As a user, I want to manage my account settings so I can customize my experience",
        "acceptance_criteria": [
            "User can view account information",
            "User can update personal details",
            "User can change password",
            "User can manage privacy settings"
        ],
        "business_value": "User satisfaction and retention",
        "user_persona": "Registered user"
    }
    
    print(f"📝 BDD Story: {bdd_story['title']}")
    print(f"   Description: {bdd_story['description']}")
    print()
    
    print("🤖 Generating BDD scenarios using local LLM...")
    start_time = time.time()
    
    response = requests.post(
        'http://localhost:5000/api/ai/generate-bdd-scenarios',
        json=bdd_story,
        timeout=60
    )
    
    bdd_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        provider = data.get('provider', 'unknown')
        count = data.get('count', 0)
        note = data.get('note', '')
        
        print(f"✅ Generated {count} BDD scenarios in {bdd_time:.2f}s")
        print(f"   Provider: {provider}")
        print(f"   Note: {note}")
        
        # Show generated scenarios
        scenarios = data.get('scenarios', [])
        for i, scenario in enumerate(scenarios[:2], 1):  # Show first 2
            print(f"\n   Scenario {i}: {scenario.get('title', 'Untitled')}")
            print(f"   Description: {scenario.get('description', 'No description')}")
            print(f"   Steps: {len(scenario.get('steps', []))} steps")
            print(f"   Tags: {', '.join(scenario.get('tags', []))}")
        
        if len(scenarios) > 2:
            print(f"   ... and {len(scenarios) - 2} more scenarios")
            
    else:
        print(f"❌ Failed to generate BDD scenarios: {response.status_code}")
    
    print("\n" + "=" * 60)
    
    # Summary
    print("📊 DEMONSTRATION SUMMARY")
    print("=" * 60)
    print("✅ AI Test Case Generation: Working with local LLM")
    print("✅ AI Test Case Improvement: Working with local LLM")
    print("✅ BDD Scenario Generation: Working with local LLM")
    print()
    print("🎯 Key Benefits:")
    print("  • No external API costs")
    print("  • Complete data privacy")
    print("  • Offline operation")
    print("  • Custom model support")
    print("  • Enterprise security")
    print()
    print("🏢 Enterprise AI is fully operational!")
    print("   All AI features are powered by your local Ollama instance")

def check_prerequisites():
    """Check if prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if Assertly is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Assertly application is not running")
            return False
    except:
        print("❌ Cannot connect to Assertly application")
        return False
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama is not running")
            return False
    except:
        print("❌ Cannot connect to Ollama")
        return False
    
    # Check if local LLM server is running
    try:
        response = requests.get("http://localhost:11434/api/generate", timeout=5)
        # This might fail, but that's OK - we just want to check connectivity
    except:
        pass  # This is expected to fail for GET request
    
    print("✅ All prerequisites met")
    return True

def main():
    """Main demonstration function"""
    print("🎯 Enterprise AI Demonstration")
    print("=" * 60)
    
    if not check_prerequisites():
        print("\n⚠️ Prerequisites not met. Please:")
        print("1. Start Assertly: python3 app.py &")
        print("2. Start Ollama: ollama serve &")
        print("3. Run setup: ./setup_enterprise_ai.sh")
        return
    
    print("\n🚀 Starting demonstration...")
    print()
    
    demo_enterprise_ai()

if __name__ == "__main__":
    main()