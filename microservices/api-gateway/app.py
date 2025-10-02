#!/usr/bin/env python3
"""
API Gateway - Central entry point for microservices
Handles routing, authentication, rate limiting, and service discovery
"""

from flask import Flask, request, jsonify, redirect
import requests
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
import time
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'api-gateway-secret')

# Service Registry
SERVICES = {
    'user-service': {
        'url': os.getenv('USER_SERVICE_URL', 'http://localhost:5001'),
        'health_endpoint': '/health',
        'auth_required': False
    },
    'test-service': {
        'url': os.getenv('TEST_SERVICE_URL', 'http://localhost:5002'),
        'health_endpoint': '/health',
        'auth_required': True
    },
    'ai-service': {
        'url': os.getenv('AI_SERVICE_URL', 'http://localhost:5003'),
        'health_endpoint': '/health',
        'auth_required': True
    },
    'integration-service': {
        'url': os.getenv('INTEGRATION_SERVICE_URL', 'http://localhost:5004'),
        'health_endpoint': '/health',
        'auth_required': True
    },
    'notification-service': {
        'url': os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:5005'),
        'health_endpoint': '/health',
        'auth_required': True
    }
}

# Rate limiting storage (in production, use Redis)
rate_limits = {}

def check_rate_limit(client_ip, endpoint):
    """Check rate limit for client"""
    key = f"{client_ip}:{endpoint}"
    current_time = time.time()
    
    if key not in rate_limits:
        rate_limits[key] = {'count': 1, 'window_start': current_time}
        return True
    
    # Reset window if more than 1 hour has passed
    if current_time - rate_limits[key]['window_start'] > 3600:
        rate_limits[key] = {'count': 1, 'window_start': current_time}
        return True
    
    # Check if within rate limit (100 requests per hour)
    if rate_limits[key]['count'] >= 100:
        return False
    
    rate_limits[key]['count'] += 1
    return True

def authenticate_request():
    """Authenticate incoming request"""
    token = request.headers.get('Authorization')
    if not token:
        return None, 'No token provided'
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decode JWT token
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload, None
        
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'

def proxy_request(service_name, path, method='GET', data=None, headers=None):
    """Proxy request to microservice"""
    if service_name not in SERVICES:
        return {'error': 'Service not found'}, 404
    
    service = SERVICES[service_name]
    url = f"{service['url']}{path}"
    
    try:
        # Prepare headers
        proxy_headers = {}
        if headers:
            proxy_headers.update(headers)
        
        # Add user ID to headers for authenticated services
        if service['auth_required'] and 'user_id' in request.__dict__:
            proxy_headers['X-User-ID'] = str(request.user_id)
        
        # Make request to microservice
        if method.upper() == 'GET':
            response = requests.get(url, headers=proxy_headers, timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=proxy_headers, timeout=30)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=proxy_headers, timeout=30)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=proxy_headers, timeout=30)
        else:
            return {'error': 'Unsupported method'}, 405
        
        return response.json(), response.status_code
        
    except requests.exceptions.Timeout:
        return {'error': 'Service timeout'}, 504
    except requests.exceptions.ConnectionError:
        return {'error': 'Service unavailable'}, 503
    except Exception as e:
        return {'error': str(e)}, 500

# Middleware
@app.before_request
def before_request():
    """Process request before routing"""
    # Check rate limiting
    client_ip = request.remote_addr
    endpoint = request.endpoint or 'unknown'
    
    if not check_rate_limit(client_ip, endpoint):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    # Authenticate if needed
    if request.endpoint and not request.endpoint.startswith('health'):
        payload, error = authenticate_request()
        if error:
            return jsonify({'error': error}), 401
        
        if payload:
            request.user_id = payload.get('user_id')
            request.user_role = payload.get('role', 'user')

# Health check
@app.route('/health', methods=['GET'])
def health():
    """API Gateway health check"""
    service_status = {}
    
    for service_name, service in SERVICES.items():
        try:
            response = requests.get(
                f"{service['url']}{service['health_endpoint']}", 
                timeout=5
            )
            service_status[service_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            service_status[service_name] = {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    return jsonify({
        'service': 'api-gateway',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': service_status
    })

# User Service Routes
@app.route('/api/users', methods=['GET', 'POST'])
def users():
    """Route to user service"""
    if request.method == 'GET':
        return proxy_request('user-service', '/users', 'GET')
    else:
        return proxy_request('user-service', '/users', 'POST', request.get_json())

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT'])
def user_by_id(user_id):
    """Route to user service"""
    if request.method == 'GET':
        return proxy_request('user-service', f'/users/{user_id}', 'GET')
    else:
        return proxy_request('user-service', f'/users/{user_id}', 'PUT', request.get_json())

@app.route('/api/users/me', methods=['GET', 'PUT'])
def current_user():
    """Route to user service"""
    if request.method == 'GET':
        return proxy_request('user-service', '/users/me', 'GET')
    else:
        return proxy_request('user-service', '/users/me', 'PUT', request.get_json())

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Route to user service for login"""
    return proxy_request('user-service', '/auth/login', 'POST', request.get_json())

@app.route('/api/auth/validate', methods=['POST'])
def validate_token():
    """Route to user service for token validation"""
    return proxy_request('user-service', '/auth/validate', 'POST', request.get_json())

# Test Service Routes
@app.route('/api/test-cases', methods=['GET', 'POST'])
def test_cases():
    """Route to test service"""
    if request.method == 'GET':
        return proxy_request('test-service', '/test-cases', 'GET')
    else:
        return proxy_request('test-service', '/test-cases', 'POST', request.get_json())

@app.route('/api/test-cases/<int:test_case_id>', methods=['GET', 'PUT', 'DELETE'])
def test_case_by_id(test_case_id):
    """Route to test service"""
    if request.method == 'GET':
        return proxy_request('test-service', f'/test-cases/{test_case_id}', 'GET')
    elif request.method == 'PUT':
        return proxy_request('test-service', f'/test-cases/{test_case_id}', 'PUT', request.get_json())
    else:
        return proxy_request('test-service', f'/test-cases/{test_case_id}', 'DELETE')

@app.route('/api/test-executions', methods=['GET', 'POST'])
def test_executions():
    """Route to test service"""
    if request.method == 'GET':
        return proxy_request('test-service', '/test-executions', 'GET')
    else:
        return proxy_request('test-service', '/test-executions', 'POST', request.get_json())

@app.route('/api/test-sets', methods=['GET', 'POST'])
def test_sets():
    """Route to test service"""
    if request.method == 'GET':
        return proxy_request('test-service', '/test-sets', 'GET')
    else:
        return proxy_request('test-service', '/test-sets', 'POST', request.get_json())

@app.route('/api/analytics/coverage', methods=['GET'])
def coverage_analytics():
    """Route to test service"""
    return proxy_request('test-service', '/analytics/coverage', 'GET')

# AI Service Routes
@app.route('/api/ai/generate-test-cases', methods=['POST'])
def generate_test_cases():
    """Route to AI service"""
    return proxy_request('ai-service', '/generate-test-cases', 'POST', request.get_json())

@app.route('/api/ai/improve-test-case', methods=['POST'])
def improve_test_case():
    """Route to AI service"""
    return proxy_request('ai-service', '/improve-test-case', 'POST', request.get_json())

@app.route('/api/ai/generate-bdd-scenarios', methods=['POST'])
def generate_bdd_scenarios():
    """Route to AI service"""
    return proxy_request('ai-service', '/generate-bdd-scenarios', 'POST', request.get_json())

@app.route('/api/ai/analyze-coverage', methods=['POST'])
def analyze_coverage():
    """Route to AI service"""
    return proxy_request('ai-service', '/analyze-coverage', 'POST', request.get_json())

@app.route('/api/ai/providers', methods=['GET'])
def ai_providers():
    """Route to AI service"""
    return proxy_request('ai-service', '/providers', 'GET')

@app.route('/api/ai/test-connection/<provider>', methods=['POST'])
def test_ai_connection(provider):
    """Route to AI service"""
    return proxy_request('ai-service', f'/test-connection/{provider}', 'POST')

# Service Discovery
@app.route('/api/services', methods=['GET'])
def list_services():
    """List available services"""
    return jsonify({
        'services': list(SERVICES.keys()),
        'gateway_url': request.url_root,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/services/<service_name>/health', methods=['GET'])
def service_health(service_name):
    """Check specific service health"""
    if service_name not in SERVICES:
        return jsonify({'error': 'Service not found'}), 404
    
    try:
        service = SERVICES[service_name]
        response = requests.get(
            f"{service['url']}{service['health_endpoint']}", 
            timeout=5
        )
        
        return jsonify({
            'service': service_name,
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'response_time': response.elapsed.total_seconds(),
            'url': service['url']
        })
        
    except Exception as e:
        return jsonify({
            'service': service_name,
            'status': 'unhealthy',
            'error': str(e)
        })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)