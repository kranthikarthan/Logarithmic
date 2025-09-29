#!/usr/bin/env python3
"""
AI Service - Microservice for AI-powered test generation
Handles AI test case generation, improvement, and analysis
"""

from flask import Flask, request, jsonify
from datetime import datetime
import os
import json
from functools import wraps

app = Flask(__name__)

# AI Service Configuration
AI_PROVIDERS = {
    'openai': {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'base_url': 'https://api.openai.com/v1'
    },
    'anthropic': {
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'base_url': 'https://api.anthropic.com/v1'
    },
    'local': {
        'api_key': os.getenv('LOCAL_AI_API_KEY'),
        'base_url': os.getenv('LOCAL_AI_URL', 'http://localhost:8080')
    }
}

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        request.current_user_id = int(user_id)
        return f(*args, **kwargs)
    return decorated_function

# AI Generation Functions
def generate_test_cases_with_ai(user_story, provider='openai'):
    """Generate test cases using AI"""
    try:
        if provider not in AI_PROVIDERS:
            return {'error': 'Invalid AI provider'}
        
        config = AI_PROVIDERS[provider]
        if not config['api_key']:
            return {'error': f'{provider} API key not configured'}
        
        # Simulate AI generation (in real implementation, call actual AI API)
        test_cases = [
            {
                'title': f'Test Case 1: {user_story["title"]} - Valid Scenario',
                'description': f'Verify that {user_story["title"]} works correctly with valid inputs',
                'steps': [
                    'Navigate to the application',
                    'Enter valid credentials',
                    'Click login button',
                    'Verify successful login'
                ],
                'expected_result': 'User should be logged in successfully',
                'priority': 'high',
                'test_type': 'functional'
            },
            {
                'title': f'Test Case 2: {user_story["title"]} - Invalid Input',
                'description': f'Verify that {user_story["title"]} handles invalid inputs correctly',
                'steps': [
                    'Navigate to the application',
                    'Enter invalid credentials',
                    'Click login button',
                    'Verify error message is displayed'
                ],
                'expected_result': 'Appropriate error message should be displayed',
                'priority': 'medium',
                'test_type': 'negative'
            }
        ]
        
        return {
            'success': True,
            'test_cases': test_cases,
            'provider': provider,
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {'error': str(e)}

def improve_test_case_with_ai(test_case, improvement_type, provider='openai'):
    """Improve existing test case using AI"""
    try:
        if provider not in AI_PROVIDERS:
            return {'error': 'Invalid AI provider'}
        
        config = AI_PROVIDERS[provider]
        if not config['api_key']:
            return {'error': f'{provider} API key not configured'}
        
        # Simulate AI improvement
        improved_test_case = test_case.copy()
        
        if improvement_type == 'coverage':
            improved_test_case['steps'].extend([
                'Verify edge case handling',
                'Check boundary conditions',
                'Validate error scenarios'
            ])
        elif improvement_type == 'clarity':
            improved_test_case['description'] = f"Enhanced: {test_case['description']}"
            improved_test_case['expected_result'] = f"Detailed: {test_case['expected_result']}"
        
        return {
            'success': True,
            'improved_test_case': improved_test_case,
            'improvement_type': improvement_type,
            'provider': provider,
            'improved_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {'error': str(e)}

def generate_bdd_scenarios_with_ai(user_story, provider='openai'):
    """Generate BDD scenarios using AI"""
    try:
        if provider not in AI_PROVIDERS:
            return {'error': 'Invalid AI provider'}
        
        config = AI_PROVIDERS[provider]
        if not config['api_key']:
            return {'error': f'{provider} API key not configured'}
        
        # Simulate BDD scenario generation
        scenarios = [
            {
                'title': f'Scenario: {user_story["title"]} - Happy Path',
                'given': f'Given the user is on the {user_story["title"]} page',
                'when': f'When the user performs the {user_story["title"]} action',
                'then': f'Then the {user_story["title"]} should be completed successfully'
            },
            {
                'title': f'Scenario: {user_story["title"]} - Error Handling',
                'given': f'Given the user is on the {user_story["title"]} page',
                'when': f'When the user provides invalid input',
                'then': f'Then an appropriate error message should be displayed'
            }
        ]
        
        return {
            'success': True,
            'scenarios': scenarios,
            'provider': provider,
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {'error': str(e)}

def analyze_test_coverage_with_ai(test_cases, requirements, provider='openai'):
    """Analyze test coverage using AI"""
    try:
        if provider not in AI_PROVIDERS:
            return {'error': 'Invalid AI provider'}
        
        config = AI_PROVIDERS[provider]
        if not config['api_key']:
            return {'error': f'{provider} API key not configured'}
        
        # Simulate coverage analysis
        coverage_analysis = {
            'total_requirements': len(requirements),
            'covered_requirements': len(requirements) - 1,  # Simulate 1 uncovered
            'coverage_percentage': 85.0,
            'missing_coverage': [
                'Edge case: Invalid data format handling',
                'Performance: Large dataset processing',
                'Security: Input validation'
            ],
            'recommendations': [
                'Add negative test cases for input validation',
                'Include performance tests for large datasets',
                'Add security tests for malicious inputs'
            ]
        }
        
        return {
            'success': True,
            'coverage_analysis': coverage_analysis,
            'provider': provider,
            'analyzed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {'error': str(e)}

# Routes
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'service': 'ai-service',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'providers': list(AI_PROVIDERS.keys())
    })

@app.route('/generate-test-cases', methods=['POST'])
@require_auth
def generate_test_cases():
    """Generate test cases using AI"""
    try:
        data = request.get_json()
        
        if not data.get('user_story'):
            return jsonify({'error': 'User story is required'}), 400
        
        provider = data.get('provider', 'openai')
        result = generate_test_cases_with_ai(data['user_story'], provider)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/improve-test-case', methods=['POST'])
@require_auth
def improve_test_case():
    """Improve test case using AI"""
    try:
        data = request.get_json()
        
        if not data.get('test_case'):
            return jsonify({'error': 'Test case is required'}), 400
        
        improvement_type = data.get('improvement_type', 'coverage')
        provider = data.get('provider', 'openai')
        
        result = improve_test_case_with_ai(
            data['test_case'], 
            improvement_type, 
            provider
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-bdd-scenarios', methods=['POST'])
@require_auth
def generate_bdd_scenarios():
    """Generate BDD scenarios using AI"""
    try:
        data = request.get_json()
        
        if not data.get('user_story'):
            return jsonify({'error': 'User story is required'}), 400
        
        provider = data.get('provider', 'openai')
        result = generate_bdd_scenarios_with_ai(data['user_story'], provider)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-coverage', methods=['POST'])
@require_auth
def analyze_coverage():
    """Analyze test coverage using AI"""
    try:
        data = request.get_json()
        
        if not data.get('test_cases') or not data.get('requirements'):
            return jsonify({'error': 'Test cases and requirements are required'}), 400
        
        provider = data.get('provider', 'openai')
        result = analyze_test_coverage_with_ai(
            data['test_cases'],
            data['requirements'],
            provider
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/providers', methods=['GET'])
def list_providers():
    """List available AI providers"""
    try:
        providers = []
        for name, config in AI_PROVIDERS.items():
            providers.append({
                'name': name,
                'configured': bool(config['api_key']),
                'base_url': config['base_url']
            })
        
        return jsonify({'providers': providers})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-connection/<provider>', methods=['POST'])
@require_auth
def test_connection(provider):
    """Test AI provider connection"""
    try:
        if provider not in AI_PROVIDERS:
            return jsonify({'error': 'Invalid provider'}), 400
        
        config = AI_PROVIDERS[provider]
        if not config['api_key']:
            return jsonify({'error': f'{provider} API key not configured'}), 400
        
        # Simulate connection test
        return jsonify({
            'success': True,
            'provider': provider,
            'message': f'Connection to {provider} successful',
            'tested_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)