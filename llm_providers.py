#!/usr/bin/env python3
"""
LLM Providers for Assertly AI Test Generation
Supports multiple LLM providers for improved testing percentage
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    LOCAL = "local"
    MOCK = "mock"

@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens_used: int = 0
    cost: float = 0.0
    success: bool = True
    error: str = None

class LLMProviderManager:
    """Manages multiple LLM providers for AI test generation"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers"""
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            self.providers['openai'] = OpenAIProvider()
        
        # Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            self.providers['anthropic'] = AnthropicProvider()
        
        # Google Gemini
        if os.getenv('GOOGLE_API_KEY'):
            self.providers['google'] = GoogleProvider()
        
        # Azure OpenAI
        if os.getenv('AZURE_OPENAI_API_KEY'):
            self.providers['azure'] = AzureProvider()
        
        # Hugging Face
        if os.getenv('HUGGINGFACE_API_KEY'):
            self.providers['huggingface'] = HuggingFaceProvider()
        
        # Ollama (Local)
        if self._check_ollama_available():
            self.providers['ollama'] = OllamaProvider()
        
        # Mock provider (always available)
        self.providers['mock'] = MockProvider()
    
    def _check_ollama_available(self):
        """Check if Ollama is available locally"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def generate_with_fallback(self, prompt: str, preferred_provider: str = None) -> LLMResponse:
        """Generate response with fallback to other providers"""
        providers_to_try = []
        
        if preferred_provider and preferred_provider in self.providers:
            providers_to_try.append(preferred_provider)
        
        # Add other providers as fallbacks
        for provider_name in self.providers:
            if provider_name != preferred_provider and provider_name != 'mock':
                providers_to_try.append(provider_name)
        
        # Always try mock as last resort
        providers_to_try.append('mock')
        
        for provider_name in providers_to_try:
            try:
                provider = self.providers[provider_name]
                response = provider.generate(prompt)
                if response.success:
                    return response
            except Exception as e:
                print(f"Provider {provider_name} failed: {e}")
                continue
        
        # If all providers fail, return error
        return LLMResponse(
            content="",
            provider="error",
            model="none",
            success=False,
            error="All providers failed"
        )

class BaseLLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, name: str, model: str = None):
        self.name = name
        self.model = model or self.get_default_model()
    
    def get_default_model(self) -> str:
        return "gpt-3.5-turbo"
    
    def generate(self, prompt: str) -> LLMResponse:
        raise NotImplementedError

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self):
        super().__init__("openai", "gpt-4")
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            pass
    
    def generate(self, prompt: str) -> LLMResponse:
        if not self.client:
            return LLMResponse("", "openai", "gpt-4", success=False, error="OpenAI client not available")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider="openai",
                model=self.model,
                tokens_used=response.usage.total_tokens,
                cost=response.usage.total_tokens * 0.00003  # Approximate cost
            )
        except Exception as e:
            return LLMResponse("", "openai", self.model, success=False, error=str(e))

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self):
        super().__init__("anthropic", "claude-3-sonnet-20240229")
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            pass
    
    def generate(self, prompt: str) -> LLMResponse:
        if not self.client:
            return LLMResponse("", "anthropic", "claude-3", success=False, error="Anthropic client not available")
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return LLMResponse(
                content=response.content[0].text,
                provider="anthropic",
                model=self.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                cost=(response.usage.input_tokens + response.usage.output_tokens) * 0.000015
            )
        except Exception as e:
            return LLMResponse("", "anthropic", self.model, success=False, error=str(e))

class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider"""
    
    def __init__(self):
        super().__init__("google", "gemini-pro")
        self.api_key = os.getenv('GOOGLE_API_KEY')
    
    def generate(self, prompt: str) -> LLMResponse:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2000
                }
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                return LLMResponse(
                    content=content,
                    provider="google",
                    model=self.model,
                    tokens_used=len(prompt.split()) + len(content.split()),
                    cost=0.0  # Free tier
                )
            else:
                return LLMResponse("", "google", self.model, success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return LLMResponse("", "google", self.model, success=False, error=str(e))

class AzureProvider(BaseLLMProvider):
    """Azure OpenAI provider"""
    
    def __init__(self):
        super().__init__("azure", "gpt-4")
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')
    
    def generate(self, prompt: str) -> LLMResponse:
        try:
            url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version=2024-02-15-preview"
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            data = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return LLMResponse(
                    content=content,
                    provider="azure",
                    model=self.deployment,
                    tokens_used=result['usage']['total_tokens'],
                    cost=result['usage']['total_tokens'] * 0.00003
                )
            else:
                return LLMResponse("", "azure", self.deployment, success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return LLMResponse("", "azure", self.deployment, success=False, error=str(e))

class HuggingFaceProvider(BaseLLMProvider):
    """Hugging Face provider"""
    
    def __init__(self):
        super().__init__("huggingface", "microsoft/DialoGPT-medium")
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    def generate(self, prompt: str) -> LLMResponse:
        try:
            url = f"https://api-inference.huggingface.co/models/{self.model}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            data = {"inputs": prompt}
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result[0]['generated_text'] if isinstance(result, list) else str(result)
                return LLMResponse(
                    content=content,
                    provider="huggingface",
                    model=self.model,
                    tokens_used=len(prompt.split()) + len(content.split()),
                    cost=0.0  # Free tier
                )
            else:
                return LLMResponse("", "huggingface", self.model, success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return LLMResponse("", "huggingface", self.model, success=False, error=str(e))

class OllamaProvider(BaseLLMProvider):
    """Ollama local provider"""
    
    def __init__(self):
        super().__init__("ollama", "llama2")
        self.base_url = "http://localhost:11434"
    
    def generate(self, prompt: str) -> LLMResponse:
        try:
            url = f"{self.base_url}/api/generate"
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result['response']
                return LLMResponse(
                    content=content,
                    provider="ollama",
                    model=self.model,
                    tokens_used=len(prompt.split()) + len(content.split()),
                    cost=0.0  # Local, no cost
                )
            else:
                return LLMResponse("", "ollama", self.model, success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return LLMResponse("", "ollama", self.model, success=False, error=str(e))

class MockProvider(BaseLLMProvider):
    """Mock provider for testing and fallback"""
    
    def __init__(self):
        super().__init__("mock", "mock-llm")
    
    def generate(self, prompt: str) -> LLMResponse:
        # Generate mock test cases based on prompt
        if "test case" in prompt.lower():
            mock_response = self._generate_mock_test_cases(prompt)
        elif "bdd" in prompt.lower() or "scenario" in prompt.lower():
            mock_response = self._generate_mock_bdd_scenarios(prompt)
        elif "test data" in prompt.lower():
            mock_response = self._generate_mock_test_data(prompt)
        else:
            mock_response = self._generate_mock_general(prompt)
        
        return LLMResponse(
            content=mock_response,
            provider="mock",
            model="mock-llm",
            tokens_used=len(prompt.split()) + len(mock_response.split()),
            cost=0.0
        )
    
    def _generate_mock_test_cases(self, prompt: str) -> str:
        return """Test Case 1: Verify user can login with valid credentials
Description: Test the login functionality with valid username and password
Steps:
1. Navigate to login page
2. Enter valid username
3. Enter valid password
4. Click login button
Expected Result: User should be successfully logged in

Test Case 2: Verify user cannot login with invalid credentials
Description: Test the login functionality with invalid credentials
Steps:
1. Navigate to login page
2. Enter invalid username
3. Enter invalid password
4. Click login button
Expected Result: Error message should be displayed"""
    
    def _generate_mock_bdd_scenarios(self, prompt: str) -> str:
        return """Feature: User Login
  As a user
  I want to login to the system
  So that I can access my account

  Scenario: Successful login with valid credentials
    Given the user is on the login page
    When the user enters valid username and password
    Then the user should be redirected to dashboard

  Scenario: Failed login with invalid credentials
    Given the user is on the login page
    When the user enters invalid username and password
    Then an error message should be displayed"""
    
    def _generate_mock_test_data(self, prompt: str) -> str:
        return """Valid Test Data:
- Username: testuser@example.com
- Password: TestPass123!
- Email: user@test.com

Invalid Test Data:
- Username: invalid@email
- Password: 123
- Email: notanemail

Boundary Test Data:
- Username: a@b.co (minimum valid email)
- Password: A1! (minimum valid password)
- Email: test@domain.com"""
    
    def _generate_mock_general(self, prompt: str) -> str:
        return f"Mock AI response for: {prompt[:100]}..."

# Global provider manager instance
llm_manager = LLMProviderManager()

def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Get LLM provider by name"""
    if provider_name and provider_name in llm_manager.providers:
        return llm_manager.providers[provider_name]
    return llm_manager.providers.get('mock', MockProvider())

def generate_with_llm(prompt: str, provider: str = None) -> LLMResponse:
    """Generate response using LLM with fallback"""
    return llm_manager.generate_with_fallback(prompt, provider)

def get_available_providers() -> List[str]:
    """Get list of available LLM providers"""
    return llm_manager.get_available_providers()

if __name__ == "__main__":
    # Test the LLM providers
    print("🧪 Testing LLM Providers...")
    print(f"Available providers: {get_available_providers()}")
    
    test_prompt = "Generate test cases for user login functionality"
    response = generate_with_llm(test_prompt)
    
    print(f"\nResponse from {response.provider}:")
    print(f"Success: {response.success}")
    print(f"Content: {response.content[:200]}...")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Cost: ${response.cost:.4f}")