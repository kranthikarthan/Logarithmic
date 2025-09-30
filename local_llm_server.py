#!/usr/bin/env python3
"""
Local LLM Server for AI Test Generation
Simulates Ollama functionality for local AI test generation
"""

import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
import threading
import os

class LocalLLMServer:
    """Local LLM server that simulates Ollama functionality"""
    
    def __init__(self, host='localhost', port=11434):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.models = {
            'llama2': {
                'name': 'llama2',
                'size': '3.8GB',
                'modified_at': datetime.now().isoformat(),
                'digest': 'sha256:abc123',
                'details': {
                    'format': 'gguf',
                    'family': 'llama',
                    'families': ['llama'],
                    'parameter_size': '7B',
                    'quantization_level': 'Q4_0'
                }
            },
            'codellama': {
                'name': 'codellama',
                'size': '3.8GB',
                'modified_at': datetime.now().isoformat(),
                'digest': 'sha256:def456',
                'details': {
                    'format': 'gguf',
                    'family': 'llama',
                    'families': ['llama'],
                    'parameter_size': '7B',
                    'quantization_level': 'Q4_0'
                }
            },
            'mistral': {
                'name': 'mistral',
                'size': '4.1GB',
                'modified_at': datetime.now().isoformat(),
                'digest': 'sha256:ghi789',
                'details': {
                    'format': 'gguf',
                    'family': 'mistral',
                    'families': ['mistral'],
                    'parameter_size': '7B',
                    'quantization_level': 'Q4_0'
                }
            }
        }
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/api/tags', methods=['GET'])
        def list_models():
            """List available models"""
            return jsonify({
                'models': list(self.models.values())
            })
        
        @self.app.route('/api/generate', methods=['POST'])
        def generate():
            """Generate text using local LLM"""
            try:
                data = request.get_json()
                model = data.get('model', 'llama2')
                prompt = data.get('prompt', '')
                stream = data.get('stream', False)
                
                # Simulate processing time
                time.sleep(random.uniform(0.5, 2.0))
                
                # Generate response based on prompt
                response = self._generate_response(prompt, model)
                
                if stream:
                    # For streaming, we'll return a single response
                    return jsonify({
                        'model': model,
                        'created_at': datetime.now().isoformat(),
                        'response': response,
                        'done': True
                    })
                else:
                    return jsonify({
                        'model': model,
                        'created_at': datetime.now().isoformat(),
                        'response': response,
                        'done': True,
                        'context': [],
                        'total_duration': random.randint(1000, 3000),
                        'load_duration': random.randint(100, 500),
                        'prompt_eval_count': len(prompt.split()),
                        'prompt_eval_duration': random.randint(100, 500),
                        'eval_count': len(response.split()),
                        'eval_duration': random.randint(1000, 2000)
                    })
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/pull', methods=['POST'])
        def pull_model():
            """Pull/download a model"""
            try:
                data = request.get_json()
                model_name = data.get('name', 'llama2')
                
                # Simulate model download
                return jsonify({
                    'status': 'success',
                    'message': f'Successfully pulled {model_name}'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/ps', methods=['GET'])
        def list_running():
            """List running models"""
            return jsonify({
                'models': []
            })
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'models_available': len(self.models)
            })
    
    def _generate_response(self, prompt: str, model: str) -> str:
        """Generate response based on prompt and model"""
        
        # Test case generation
        if "test case" in prompt.lower() or "test" in prompt.lower():
            return self._generate_test_cases(prompt)
        
        # BDD scenario generation
        elif "bdd" in prompt.lower() or "scenario" in prompt.lower() or "gherkin" in prompt.lower():
            return self._generate_bdd_scenarios(prompt)
        
        # Test data generation
        elif "test data" in prompt.lower() or "data" in prompt.lower():
            return self._generate_test_data(prompt)
        
        # Coverage analysis
        elif "coverage" in prompt.lower() or "analysis" in prompt.lower():
            return self._generate_coverage_analysis(prompt)
        
        # General response
        else:
            return self._generate_general_response(prompt)
    
    def _generate_test_cases(self, prompt: str) -> str:
        """Generate test cases"""
        return """Test Case 1: User Login with Valid Credentials
Description: Verify user can login with valid username and password
Steps:
1. Navigate to login page
2. Enter valid username
3. Enter valid password
4. Click login button
Expected Result: User should be successfully logged in and redirected to dashboard

Test Case 2: User Login with Invalid Credentials
Description: Verify user cannot login with invalid credentials
Steps:
1. Navigate to login page
2. Enter invalid username
3. Enter invalid password
4. Click login button
Expected Result: Error message should be displayed

Test Case 3: User Login with Empty Fields
Description: Verify user cannot login with empty fields
Steps:
1. Navigate to login page
2. Leave username field empty
3. Leave password field empty
4. Click login button
Expected Result: Validation error should be displayed"""
    
    def _generate_bdd_scenarios(self, prompt: str) -> str:
        """Generate BDD scenarios"""
        return """Feature: User Login
  As a registered user
  I want to login to the system
  So that I can access my account

  Background:
    Given the user is on the login page

  Scenario: Successful login with valid credentials
    Given the user enters valid username "testuser@example.com"
    And the user enters valid password "password123"
    When the user clicks the login button
    Then the user should be redirected to the dashboard
    And the user should see a welcome message

  Scenario: Failed login with invalid credentials
    Given the user enters invalid username "invalid@email.com"
    And the user enters invalid password "wrongpassword"
    When the user clicks the login button
    Then an error message "Invalid credentials" should be displayed
    And the user should remain on the login page

  Scenario: Login with empty fields
    Given the user leaves the username field empty
    And the user leaves the password field empty
    When the user clicks the login button
    Then a validation error "Username and password are required" should be displayed"""
    
    def _generate_test_data(self, prompt: str) -> str:
        """Generate test data"""
        return """Valid Test Data:
- Username: testuser@example.com
- Password: TestPass123!
- Email: user@test.com
- Phone: +1234567890

Invalid Test Data:
- Username: invalid@email
- Password: 123
- Email: notanemail
- Phone: 123

Boundary Test Data:
- Username: a@b.co (minimum valid email)
- Password: A1! (minimum valid password)
- Email: test@domain.com
- Phone: +1234567890

Edge Case Test Data:
- Username: "" (empty string)
- Password: None (null value)
- Email: " " (whitespace only)
- Phone: "" (empty string)"""
    
    def _generate_coverage_analysis(self, prompt: str) -> str:
        """Generate coverage analysis"""
        return """Coverage Analysis Report:

Current Coverage: 75%
Target Coverage: 90%

Missing Test Scenarios:
1. Error handling for network timeouts
2. Performance testing under load
3. Security testing for SQL injection
4. Accessibility testing for screen readers
5. Cross-browser compatibility testing

Recommendations:
1. Add negative test cases for all input fields
2. Include boundary value testing
3. Add integration tests for external dependencies
4. Implement security test cases
5. Add performance benchmarks

Risk Areas:
- Authentication edge cases
- Data validation boundaries
- Error recovery scenarios
- Concurrent user access

Priority for Additional Test Cases:
- High: Security and authentication
- Medium: Performance and integration
- Low: UI and accessibility"""
    
    def _generate_general_response(self, prompt: str) -> str:
        """Generate general response"""
        return f"""I understand you're asking about: {prompt[:100]}...

Based on the context, here's my response:

This appears to be related to software testing and quality assurance. I can help you with:

1. Test case generation
2. BDD scenario creation
3. Test data preparation
4. Coverage analysis
5. Test automation strategies

Please let me know if you need specific assistance with any of these areas, and I'll provide detailed guidance and examples."""
    
    def start(self):
        """Start the local LLM server"""
        print(f"🚀 Starting Local LLM Server on {self.host}:{self.port}")
        print(f"📊 Available models: {list(self.models.keys())}")
        print(f"🔗 Health check: http://{self.host}:{self.port}/health")
        print(f"📋 Models list: http://{self.host}:{self.port}/api/tags")
        
        try:
            self.app.run(host=self.host, port=self.port, debug=False, threaded=True)
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
        return True
    
    def stop(self):
        """Stop the server"""
        print("🛑 Stopping Local LLM Server...")

def main():
    """Main function to start the local LLM server"""
    server = LocalLLMServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        server.stop()
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())