#!/usr/bin/env python3
"""
Direct test of local LLM integration
"""

def test_direct_local_llm():
    """Test local LLM directly"""
    print("🔍 Testing Local LLM Direct Integration...")
    
    try:
        from ai_test_generator import AITestGenerator, UserStory, TestCaseType, TestPriority
        
        # Create a test user story
        user_story = UserStory(
            title="User Login",
            description="As a user, I want to login to the system",
            acceptance_criteria=["User can login with valid credentials"],
            business_value="Access to user account",
            user_persona="Registered user"
        )
        
        print("  Creating AI generator with local provider...")
        generator = AITestGenerator(provider='local', enterprise_mode=True)
        
        print("  Generating test cases...")
        test_cases = generator.generate_test_cases_from_story(
            user_story=user_story,
            test_types=[TestCaseType.FUNCTIONAL],
            num_cases=2
        )
        
        print(f"  ✅ Generated {len(test_cases)} test cases")
        for i, tc in enumerate(test_cases, 1):
            print(f"    Test Case {i}: {tc.title}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enterprise_config():
    """Test enterprise configuration"""
    print("🔍 Testing Enterprise Configuration...")
    
    try:
        from enterprise_config import EnterpriseConfigManager
        config_manager = EnterpriseConfigManager()
        settings = config_manager.load_enterprise_settings()
        
        if settings:
            print(f"  ✅ Enterprise settings loaded")
            print(f"    Local AI URL: {settings.local_ai_url}")
            print(f"    Local AI Model: {settings.local_ai_model}")
            return True
        else:
            print("  ❌ No enterprise settings found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Direct Local LLM Test")
    print("=" * 50)
    
    # Test enterprise config
    config_ok = test_enterprise_config()
    
    # Test direct local LLM
    llm_ok = test_direct_local_llm()
    
    print("\n📊 Test Results:")
    print(f"  Enterprise Config: {'✅ OK' if config_ok else '❌ FAIL'}")
    print(f"  Local LLM: {'✅ OK' if llm_ok else '❌ FAIL'}")
    
    if config_ok and llm_ok:
        print("\n🎉 Local LLM is working directly!")
    else:
        print("\n⚠️ Local LLM needs attention")

if __name__ == "__main__":
    main()