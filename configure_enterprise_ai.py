#!/usr/bin/env python3
"""
Configure Enterprise AI Settings for Ollama Simulation
"""

from enterprise_config import EnterpriseConfigManager, EnterpriseSettings
import os

def configure_enterprise_ai():
    """Configure enterprise AI settings for Ollama simulation"""
    print("🎯 Configuring Enterprise AI with Ollama")
    print("=" * 50)
    
    config_manager = EnterpriseConfigManager()
    
    # Enterprise AI settings for Ollama
    settings = EnterpriseSettings(
        # AI Configuration
        local_ai_url='http://localhost:11434',
        local_api_key='enterprise-key-12345',
        local_ai_model='llama2',
        
        # Network Configuration
        proxy_url=None,
        cert_path=None,
        verify_ssl=False,
        
        # Security Configuration
        audit_enabled=True,
        data_encryption=True,
        session_timeout=3600,  # 1 hour
        
        # Compliance Configuration
        data_retention_days=365,
        log_retention_days=90,
        compliance_mode='enterprise',
        
        # Feature Flags
        offline_mode=True,
        custom_models=True,
        external_integrations=False
    )
    
    try:
        # Save enterprise settings
        success = config_manager.save_enterprise_settings(settings)
        
        if success:
            print("✅ Enterprise AI settings configured successfully")
            print(f"   Local AI URL: {settings.local_ai_url}")
            print(f"   Local AI Model: {settings.local_ai_model}")
            print(f"   Offline Mode: {settings.offline_mode}")
            print(f"   Custom Models: {settings.custom_models}")
            print(f"   Audit Enabled: {settings.audit_enabled}")
            
            # Test the configuration
            print("\n🔍 Testing configuration...")
            loaded_settings = config_manager.load_enterprise_settings()
            
            if loaded_settings:
                print("✅ Configuration loaded successfully")
                print(f"   Verified URL: {loaded_settings.local_ai_url}")
                print(f"   Verified Model: {loaded_settings.local_ai_model}")
            else:
                print("❌ Failed to load configuration")
                return False
                
        else:
            print("❌ Failed to save enterprise settings")
            return False
            
    except Exception as e:
        print(f"❌ Error configuring enterprise AI: {e}")
        return False
    
    print("\n🎉 Enterprise AI configuration complete!")
    print("\nNext steps:")
    print("1. Start Ollama: ollama serve &")
    print("2. Pull models: ollama pull llama2:7b")
    print("3. Start local LLM server: python3 local_llm_server.py &")
    print("4. Test integration: python3 test_enterprise_ai_simulation.py")
    
    return True

def check_ollama_status():
    """Check if Ollama is running and accessible"""
    print("\n🔍 Checking Ollama status...")
    
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Ollama is running")
            print(f"   Available models: {len(models)}")
            
            for model in models:
                print(f"   - {model.get('name', 'unknown')}")
            
            return True
        else:
            print(f"❌ Ollama not responding: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama not accessible: {e}")
        print("   Please start Ollama: ollama serve &")
        return False

def main():
    """Main configuration function"""
    print("🏢 Enterprise AI Configuration for Ollama")
    print("=" * 60)
    
    # Check Ollama status
    ollama_ok = check_ollama_status()
    
    # Configure enterprise AI
    config_ok = configure_enterprise_ai()
    
    print("\n📊 Configuration Summary:")
    print(f"  Ollama Status: {'✅ OK' if ollama_ok else '❌ FAIL'}")
    print(f"  Enterprise Config: {'✅ OK' if config_ok else '❌ FAIL'}")
    
    if ollama_ok and config_ok:
        print("\n🎉 Enterprise AI is ready!")
        print("   You can now use local LLM for all AI features")
    else:
        print("\n⚠️ Configuration incomplete")
        if not ollama_ok:
            print("   - Start Ollama: ollama serve &")
        if not config_ok:
            print("   - Check enterprise configuration")

if __name__ == "__main__":
    main()