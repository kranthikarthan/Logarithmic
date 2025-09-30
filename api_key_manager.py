#!/usr/bin/env python3
"""
API Key Management System for Assertly
Allows clients to configure their preferred AI providers
"""

import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class AIProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    CUSTOM = "custom"

@dataclass
class APIKeyConfig:
    """API Key configuration for AI providers"""
    provider: AIProvider
    api_key: str
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    is_active: bool = True
    created_at: datetime = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    monthly_limit: Optional[int] = None
    cost_per_token: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class APIKeyUsage:
    """API Key usage tracking"""
    provider: AIProvider
    tokens_used: int
    cost: float
    timestamp: datetime
    endpoint: str
    success: bool
    response_time: float

class APIKeyManager:
    """Manages API keys for different AI providers"""
    
    def __init__(self, config_file: str = "api_keys.json"):
        self.config_file = config_file
        self.keys: Dict[AIProvider, APIKeyConfig] = {}
        self.usage_log: List[APIKeyUsage] = []
        self.load_keys()
    
    def load_keys(self):
        """Load API keys from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                for provider_str, key_data in data.items():
                    provider = AIProvider(provider_str)
                    key_data['provider'] = provider
                    key_data['created_at'] = datetime.fromisoformat(key_data['created_at'])
                    if key_data.get('last_used'):
                        key_data['last_used'] = datetime.fromisoformat(key_data['last_used'])
                    
                    self.keys[provider] = APIKeyConfig(**key_data)
                    
        except Exception as e:
            print(f"Warning: Could not load API keys: {e}")
    
    def save_keys(self):
        """Save API keys to configuration file"""
        try:
            data = {}
            for provider, config in self.keys.items():
                config_dict = asdict(config)
                config_dict['provider'] = provider.value
                config_dict['created_at'] = config.created_at.isoformat()
                if config.last_used:
                    config_dict['last_used'] = config.last_used.isoformat()
                else:
                    config_dict['last_used'] = None
                data[provider.value] = config_dict
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving API keys: {e}")
    
    def add_api_key(self, provider: AIProvider, api_key: str, **kwargs) -> bool:
        """Add or update API key for a provider"""
        try:
            # Validate API key format
            if not self._validate_api_key(provider, api_key):
                return False
            
            config = APIKeyConfig(
                provider=provider,
                api_key=api_key,
                **kwargs
            )
            
            self.keys[provider] = config
            self.save_keys()
            return True
            
        except Exception as e:
            print(f"Error adding API key: {e}")
            return False
    
    def remove_api_key(self, provider: AIProvider) -> bool:
        """Remove API key for a provider"""
        try:
            if provider in self.keys:
                del self.keys[provider]
                self.save_keys()
                return True
            return False
        except Exception as e:
            print(f"Error removing API key: {e}")
            return False
    
    def get_api_key(self, provider: AIProvider) -> Optional[str]:
        """Get API key for a provider"""
        if provider in self.keys and self.keys[provider].is_active:
            return self.keys[provider].api_key
        return None
    
    def get_active_providers(self) -> List[AIProvider]:
        """Get list of active AI providers"""
        return [provider for provider, config in self.keys.items() if config.is_active]
    
    def test_api_key(self, provider: AIProvider) -> Dict[str, Any]:
        """Test API key for a provider"""
        if provider not in self.keys:
            return {"success": False, "error": "API key not configured"}
        
        config = self.keys[provider]
        
        try:
            if provider == AIProvider.OPENAI:
                return self._test_openai_key(config)
            elif provider == AIProvider.ANTHROPIC:
                return self._test_anthropic_key(config)
            elif provider == AIProvider.GOOGLE:
                return self._test_google_key(config)
            elif provider == AIProvider.AZURE:
                return self._test_azure_key(config)
            elif provider == AIProvider.HUGGINGFACE:
                return self._test_huggingface_key(config)
            elif provider == AIProvider.LOCAL:
                return self._test_local_key(config)
            else:
                return {"success": False, "error": "Provider not supported for testing"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_openai_key(self, config: APIKeyConfig) -> Dict[str, Any]:
        """Test OpenAI API key"""
        try:
            import openai
            client = openai.OpenAI(api_key=config.api_key, base_url=config.base_url)
            
            response = client.chat.completions.create(
                model=config.model or "gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10,
                timeout=config.timeout
            )
            
            return {
                "success": True,
                "model": config.model or "gpt-3.5-turbo",
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_anthropic_key(self, config: APIKeyConfig) -> Dict[str, Any]:
        """Test Anthropic API key"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=config.api_key)
            
            response = client.messages.create(
                model=config.model or "claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Test connection"}]
            )
            
            return {
                "success": True,
                "model": config.model or "claude-3-haiku-20240307",
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_google_key(self, config: APIKeyConfig) -> Dict[str, Any]:
        """Test Google AI API key"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.api_key)
            
            model = genai.GenerativeModel(config.model or "gemini-pro")
            response = model.generate_content("Test connection")
            
            return {
                "success": True,
                "model": config.model or "gemini-pro",
                "tokens_used": 0  # Google doesn't provide token count in response
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_azure_key(self, config: APIKeyConfig) -> Dict[str, Any]:
        """Test Azure OpenAI API key"""
        try:
            import openai
            client = openai.AzureOpenAI(
                api_key=config.api_key,
                azure_endpoint=config.base_url,
                api_version="2024-02-15-preview"
            )
            
            response = client.chat.completions.create(
                model=config.model or "gpt-35-turbo",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            
            return {
                "success": True,
                "model": config.model or "gpt-35-turbo",
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_huggingface_key(self, config: APIKeyConfig) -> Dict[str, Any]:
        """Test Hugging Face API key"""
        try:
            import requests
            
            headers = {"Authorization": f"Bearer {config.api_key}"}
            response = requests.get(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                headers=headers,
                timeout=config.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "model": "huggingface-inference",
                    "tokens_used": 0
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_local_key(self, config: APIKeyConfig) -> Dict[str, Any]:
        """Test local LLM connection"""
        try:
            import requests
            
            response = requests.get(
                config.base_url or "http://localhost:11434/api/tags",
                timeout=config.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "model": config.model or "local-llm",
                    "tokens_used": 0
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_api_key(self, provider: AIProvider, api_key: str) -> bool:
        """Validate API key format"""
        if not api_key or len(api_key) < 10:
            return False
        
        if provider == AIProvider.OPENAI:
            return api_key.startswith('sk-')
        elif provider == AIProvider.ANTHROPIC:
            return api_key.startswith('sk-ant-')
        elif provider == AIProvider.GOOGLE:
            return len(api_key) > 20  # Google API keys are longer
        elif provider == AIProvider.AZURE:
            return len(api_key) > 20  # Azure API keys are longer
        elif provider == AIProvider.HUGGINGFACE:
            return api_key.startswith('hf_')
        elif provider == AIProvider.LOCAL:
            return True  # Local doesn't need validation
        else:
            return True  # Custom providers
    
    def log_usage(self, provider: AIProvider, tokens_used: int, cost: float, 
                   endpoint: str, success: bool, response_time: float):
        """Log API key usage"""
        usage = APIKeyUsage(
            provider=provider,
            tokens_used=tokens_used,
            cost=cost,
            timestamp=datetime.now(),
            endpoint=endpoint,
            success=success,
            response_time=response_time
        )
        
        self.usage_log.append(usage)
        
        # Update key usage stats
        if provider in self.keys:
            self.keys[provider].last_used = datetime.now()
            self.keys[provider].usage_count += 1
            self.save_keys()
    
    def get_usage_stats(self, provider: AIProvider = None) -> Dict[str, Any]:
        """Get usage statistics"""
        if provider:
            stats = [usage for usage in self.usage_log if usage.provider == provider]
        else:
            stats = self.usage_log
        
        if not stats:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0}
        
        return {
            "total_requests": len(stats),
            "successful_requests": len([s for s in stats if s.success]),
            "total_tokens": sum(s.tokens_used for s in stats),
            "total_cost": sum(s.cost for s in stats),
            "average_response_time": sum(s.response_time for s in stats) / len(stats),
            "success_rate": len([s for s in stats if s.success]) / len(stats) * 100
        }
    
    def generate_client_config(self) -> Dict[str, Any]:
        """Generate client configuration for deployment"""
        config = {
            "ai_providers": {},
            "default_provider": None,
            "fallback_chain": [],
            "cost_limits": {},
            "usage_tracking": True
        }
        
        for provider, key_config in self.keys.items():
            if key_config.is_active:
                config["ai_providers"][provider.value] = {
                    "model": key_config.model,
                    "max_tokens": key_config.max_tokens,
                    "temperature": key_config.temperature,
                    "timeout": key_config.timeout,
                    "retry_attempts": key_config.retry_attempts,
                    "monthly_limit": key_config.monthly_limit,
                    "cost_per_token": key_config.cost_per_token
                }
        
        # Set default provider (first active one)
        active_providers = self.get_active_providers()
        if active_providers:
            config["default_provider"] = active_providers[0].value
            config["fallback_chain"] = [p.value for p in active_providers]
        
        return config

def main():
    """Main function for testing API key management"""
    print("🔑 API Key Management System")
    print("=" * 40)
    
    manager = APIKeyManager()
    
    # Example: Add some test API keys
    print("Adding test API keys...")
    
    # OpenAI key
    manager.add_api_key(
        AIProvider.OPENAI,
        "sk-test-key-12345",
        model="gpt-4",
        max_tokens=4000,
        temperature=0.7
    )
    
    # Anthropic key
    manager.add_api_key(
        AIProvider.ANTHROPIC,
        "sk-ant-test-key-12345",
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0.7
    )
    
    # Local LLM
    manager.add_api_key(
        AIProvider.LOCAL,
        "local-key",
        base_url="http://localhost:11434",
        model="llama2"
    )
    
    print("✅ API keys added")
    
    # Test connections
    print("\nTesting API key connections...")
    for provider in manager.get_active_providers():
        result = manager.test_api_key(provider)
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {provider.value}: {result.get('error', 'Connected')}")
    
    # Show usage stats
    print("\nUsage Statistics:")
    stats = manager.get_usage_stats()
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Total tokens: {stats['total_tokens']}")
    print(f"  Total cost: ${stats['total_cost']:.4f}")
    
    # Generate client config
    print("\nClient Configuration:")
    config = manager.generate_client_config()
    print(json.dumps(config, indent=2))

if __name__ == "__main__":
    main()