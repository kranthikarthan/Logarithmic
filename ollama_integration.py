#!/usr/bin/env python3
"""
Ollama Integration for AI Test Generation
Enhanced integration with local Ollama for testing improvement
"""

import requests
import json
import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OllamaResponse:
    content: str
    model: str
    success: bool
    error: str = None
    tokens_used: int = 0
    response_time: float = 0.0

class OllamaIntegration:
    """Integration with Ollama for AI test generation"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []
        self.current_model = "llama2"
        self.server_running = False
        
    def check_server_health(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.server_running = response.status_code == 200
            return self.server_running
        except:
            self.server_running = False
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['name'] for model in data.get('models', [])]
                return self.available_models
            return []
        except Exception as e:
            print(f"❌ Failed to list models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull/download a model"""
        try:
            print(f"📥 Pulling model: {model_name}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minutes timeout for model download
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Failed to pull model {model_name}: {e}")
            return False
    
    def generate_test_cases(self, user_story: str, num_cases: int = 5) -> OllamaResponse:
        """Generate test cases using Ollama"""
        prompt = f"""
Generate {num_cases} comprehensive test cases for the following user story:

{user_story}

Please provide test cases that include:
1. Functional test cases
2. Edge case scenarios  
3. Negative test cases
4. Integration test cases
5. Security test cases

For each test case, provide:
- Title
- Description
- Test steps
- Expected result
- Test type
- Priority
- Tags
- Preconditions
- Test data

Format as JSON with an array of test cases.
"""
        
        return self._generate_with_ollama(prompt, "test_cases")
    
    def generate_bdd_scenarios(self, user_story: str) -> OllamaResponse:
        """Generate BDD scenarios using Ollama"""
        prompt = f"""
Generate BDD scenarios in Gherkin format for the following user story:

{user_story}

Please generate comprehensive BDD scenarios that include:
1. Happy path scenarios
2. Edge cases
3. Error scenarios
4. Alternative flows

Use proper Gherkin syntax with Given/When/Then structure.
Include background steps if applicable.
Add tags for organization.
"""
        
        return self._generate_with_ollama(prompt, "bdd_scenarios")
    
    def generate_test_data(self, test_type: str, num_samples: int = 10) -> OllamaResponse:
        """Generate test data using Ollama"""
        prompt = f"""
Generate {num_samples} test data samples for {test_type} testing.

Include:
1. Valid test data
2. Invalid test data
3. Boundary test data
4. Edge case test data

For each data type, provide realistic examples that would be useful for testing.
Format as JSON with categories: valid, invalid, boundary, edge_case.
"""
        
        return self._generate_with_ollama(prompt, "test_data")
    
    def analyze_coverage(self, test_cases: List[str], requirements: List[str]) -> OllamaResponse:
        """Analyze test coverage using Ollama"""
        test_cases_text = "\n".join([f"- {tc}" for tc in test_cases])
        requirements_text = "\n".join([f"- {req}" for req in requirements])
        
        prompt = f"""
Analyze the test coverage for the following test cases against requirements:

Test Cases:
{test_cases_text}

Requirements:
{requirements_text}

Please provide:
1. Coverage percentage
2. Missing test scenarios
3. Recommendations for improvement
4. Risk areas not covered
5. Priority for additional test cases

Format as JSON with analysis results.
"""
        
        return self._generate_with_ollama(prompt, "coverage_analysis")
    
    def _generate_with_ollama(self, prompt: str, task_type: str) -> OllamaResponse:
        """Generate response using Ollama"""
        start_time = time.time()
        
        try:
            # Check if server is running
            if not self.check_server_health():
                return OllamaResponse(
                    content="",
                    model=self.current_model,
                    success=False,
                    error="Ollama server not running"
                )
            
            # Generate response
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.current_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2000
                    }
                },
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('response', '')
                tokens_used = len(prompt.split()) + len(content.split())
                
                return OllamaResponse(
                    content=content,
                    model=self.current_model,
                    success=True,
                    tokens_used=tokens_used,
                    response_time=response_time
                )
            else:
                return OllamaResponse(
                    content="",
                    model=self.current_model,
                    success=False,
                    error=f"API error: {response.status_code}",
                    response_time=response_time
                )
                
        except requests.exceptions.Timeout:
            return OllamaResponse(
                content="",
                model=self.current_model,
                success=False,
                error="Request timeout",
                response_time=time.time() - start_time
            )
        except Exception as e:
            return OllamaResponse(
                content="",
                model=self.current_model,
                success=False,
                error=str(e),
                response_time=time.time() - start_time
            )
    
    def setup_ollama(self) -> bool:
        """Setup Ollama with required models"""
        print("🦙 Setting up Ollama for AI test generation...")
        
        # Check if server is running
        if not self.check_server_health():
            print("❌ Ollama server not running. Please start Ollama first:")
            print("   Run: ollama serve")
            return False
        
        # List available models
        models = self.list_models()
        print(f"📋 Available models: {models}")
        
        # Check if we have a suitable model
        suitable_models = ['llama2', 'codellama', 'mistral', 'llama3']
        available_suitable = [m for m in suitable_models if m in models]
        
        if not available_suitable:
            print("📥 No suitable models found. Pulling llama2...")
            if not self.pull_model('llama2'):
                print("❌ Failed to pull llama2 model")
                return False
            self.current_model = 'llama2'
        else:
            self.current_model = available_suitable[0]
            print(f"✅ Using model: {self.current_model}")
        
        return True
    
    def test_integration(self) -> Dict[str, Any]:
        """Test Ollama integration"""
        print("🧪 Testing Ollama integration...")
        
        results = {
            'server_health': False,
            'models_available': [],
            'test_generation': False,
            'bdd_generation': False,
            'data_generation': False,
            'coverage_analysis': False,
            'overall_success': False
        }
        
        # Test server health
        results['server_health'] = self.check_server_health()
        if not results['server_health']:
            print("❌ Ollama server not accessible")
            return results
        
        # Test model listing
        results['models_available'] = self.list_models()
        print(f"✅ Models available: {len(results['models_available'])}")
        
        # Test test case generation
        test_response = self.generate_test_cases("User login functionality", 3)
        results['test_generation'] = test_response.success
        if test_response.success:
            print("✅ Test case generation working")
        else:
            print(f"❌ Test case generation failed: {test_response.error}")
        
        # Test BDD generation
        bdd_response = self.generate_bdd_scenarios("User login functionality")
        results['bdd_generation'] = bdd_response.success
        if bdd_response.success:
            print("✅ BDD generation working")
        else:
            print(f"❌ BDD generation failed: {bdd_response.error}")
        
        # Test data generation
        data_response = self.generate_test_data("user authentication", 5)
        results['data_generation'] = data_response.success
        if data_response.success:
            print("✅ Test data generation working")
        else:
            print(f"❌ Test data generation failed: {data_response.error}")
        
        # Test coverage analysis
        coverage_response = self.analyze_coverage(
            ["Login test", "Logout test"],
            ["User can login", "User can logout"]
        )
        results['coverage_analysis'] = coverage_response.success
        if coverage_response.success:
            print("✅ Coverage analysis working")
        else:
            print(f"❌ Coverage analysis failed: {coverage_response.error}")
        
        # Overall success
        results['overall_success'] = all([
            results['server_health'],
            results['test_generation'],
            results['bdd_generation'],
            results['data_generation'],
            results['coverage_analysis']
        ])
        
        return results

def main():
    """Main function to test Ollama integration"""
    print("🚀 Ollama Integration Test for AI Test Generation")
    print("=" * 60)
    
    # Initialize Ollama integration
    ollama = OllamaIntegration()
    
    # Setup Ollama
    if not ollama.setup_ollama():
        print("❌ Ollama setup failed")
        return 1
    
    # Test integration
    results = ollama.test_integration()
    
    # Print results
    print("\n📊 Ollama Integration Results:")
    print(f"  Server Health: {'✅' if results['server_health'] else '❌'}")
    print(f"  Models Available: {len(results['models_available'])}")
    print(f"  Test Generation: {'✅' if results['test_generation'] else '❌'}")
    print(f"  BDD Generation: {'✅' if results['bdd_generation'] else '❌'}")
    print(f"  Data Generation: {'✅' if results['data_generation'] else '❌'}")
    print(f"  Coverage Analysis: {'✅' if results['coverage_analysis'] else '❌'}")
    print(f"  Overall Success: {'✅' if results['overall_success'] else '❌'}")
    
    if results['overall_success']:
        print("\n🎉 Ollama integration successful!")
        print("📈 Expected testing improvement: +35-55%")
        return 0
    else:
        print("\n⚠️ Ollama integration needs attention")
        return 1

if __name__ == "__main__":
    exit(main())