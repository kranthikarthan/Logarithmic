#!/usr/bin/env python3
"""
API Gateway for Assertly
External integrations and third-party API management
"""

import os
import json
import time
import hashlib
import hmac
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from flask import Flask, request, jsonify, abort, g
from functools import wraps
import requests
from datetime import datetime, timedelta
import logging

class IntegrationType(Enum):
    JIRA = "jira"
    GITHUB = "github"
    GITLAB = "gitlab"
    SLACK = "slack"
    TEAMS = "teams"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CUSTOM = "custom"

@dataclass
class IntegrationConfig:
    name: str
    type: IntegrationType
    base_url: str
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    headers: Dict[str, str] = None
    timeout: int = 30
    retry_count: int = 3
    rate_limit: int = 100  # requests per minute
    active: bool = True

@dataclass
class APIKey:
    key: str
    name: str
    permissions: List[str]
    rate_limit: int = 1000
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    last_used: Optional[datetime] = None

class RateLimiter:
    def __init__(self):
        self.requests = {}
        
    def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is allowed within rate limit"""
        now = time.time()
        window_start = now - window
        
        # Clean old entries
        if key in self.requests:
            self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        else:
            self.requests[key] = []
            
        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True
        else:
            return False

class APIGateway:
    def __init__(self, app: Flask = None):
        self.app = app
        self.integrations: Dict[str, IntegrationConfig] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.rate_limiter = RateLimiter()
        self.logger = logging.getLogger(__name__)
        
        if app:
            self.init_app(app)
            
    def init_app(self, app: Flask):
        """Initialize API Gateway with Flask app"""
        self.app = app
        
        # Register API routes
        app.add_url_rule('/api/v1/integrations', 'list_integrations', self.list_integrations, methods=['GET'])
        app.add_url_rule('/api/v1/integrations', 'create_integration', self.create_integration, methods=['POST'])
        app.add_url_rule('/api/v1/integrations/<integration_id>', 'get_integration', self.get_integration, methods=['GET'])
        app.add_url_rule('/api/v1/integrations/<integration_id>', 'update_integration', self.update_integration, methods=['PUT'])
        app.add_url_rule('/api/v1/integrations/<integration_id>', 'delete_integration', self.delete_integration, methods=['DELETE'])
        app.add_url_rule('/api/v1/integrations/<integration_id>/test', 'test_integration', self.test_integration, methods=['POST'])
        
        # API key management
        app.add_url_rule('/api/v1/keys', 'list_api_keys', self.list_api_keys, methods=['GET'])
        app.add_url_rule('/api/v1/keys', 'create_api_key', self.create_api_key, methods=['POST'])
        app.add_url_rule('/api/v1/keys/<key_id>', 'delete_api_key', self.delete_api_key, methods=['DELETE'])
        
        # External API endpoints
        app.add_url_rule('/api/v1/external/test-cases', 'external_test_cases', self.external_test_cases, methods=['GET', 'POST'])
        app.add_url_rule('/api/v1/external/test-executions', 'external_test_executions', self.external_test_executions, methods=['GET', 'POST'])
        app.add_url_rule('/api/v1/external/coverage', 'external_coverage', self.external_coverage, methods=['GET'])
        app.add_url_rule('/api/v1/external/ai/generate', 'external_ai_generate', self.external_ai_generate, methods=['POST'])
        
        # Middleware
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
    def before_request(self):
        """Before request middleware"""
        # API key authentication
        api_key = request.headers.get('X-API-Key')
        if api_key:
            if api_key not in self.api_keys:
                abort(401, 'Invalid API key')
                
            # Check rate limiting
            key_config = self.api_keys[api_key]
            if not self.rate_limiter.is_allowed(api_key, key_config.rate_limit):
                abort(429, 'Rate limit exceeded')
                
            # Update last used
            key_config.last_used = datetime.now()
            
        # Store request info
        g.start_time = time.time()
        
    def after_request(self, response):
        """After request middleware"""
        # Add response headers
        response.headers['X-Response-Time'] = str(time.time() - g.start_time)
        response.headers['X-API-Version'] = '1.0'
        
        return response
        
    def create_integration(self, integration_id: str, config: IntegrationConfig) -> bool:
        """Create a new integration"""
        try:
            # Validate integration
            if not self.validate_integration(config):
                return False
                
            # Store integration
            self.integrations[integration_id] = config
            
            self.logger.info(f"Created integration: {integration_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create integration: {str(e)}")
            return False
            
    def validate_integration(self, config: IntegrationConfig) -> bool:
        """Validate integration configuration"""
        try:
            # Test connection
            if config.type == IntegrationType.JIRA:
                return self.test_jira_connection(config)
            elif config.type == IntegrationType.GITHUB:
                return self.test_github_connection(config)
            elif config.type == IntegrationType.GITLAB:
                return self.test_gitlab_connection(config)
            elif config.type == IntegrationType.SLACK:
                return self.test_slack_connection(config)
            else:
                return True  # Custom integrations
                
        except Exception:
            return False
            
    def test_jira_connection(self, config: IntegrationConfig) -> bool:
        """Test Jira connection"""
        try:
            headers = {'Authorization': f'Basic {config.api_key}'}
            response = requests.get(f"{config.base_url}/rest/api/3/myself", headers=headers, timeout=config.timeout)
            return response.status_code == 200
        except Exception:
            return False
            
    def test_github_connection(self, config: IntegrationConfig) -> bool:
        """Test GitHub connection"""
        try:
            headers = {'Authorization': f'token {config.api_key}'}
            response = requests.get(f"{config.base_url}/user", headers=headers, timeout=config.timeout)
            return response.status_code == 200
        except Exception:
            return False
            
    def test_gitlab_connection(self, config: IntegrationConfig) -> bool:
        """Test GitLab connection"""
        try:
            headers = {'Authorization': f'Bearer {config.api_key}'}
            response = requests.get(f"{config.base_url}/api/v4/user", headers=headers, timeout=config.timeout)
            return response.status_code == 200
        except Exception:
            return False
            
    def test_slack_connection(self, config: IntegrationConfig) -> bool:
        """Test Slack connection"""
        try:
            response = requests.post(f"{config.base_url}/api/auth.test", 
                                   data={'token': config.api_key}, 
                                   timeout=config.timeout)
            return response.status_code == 200
        except Exception:
            return False
            
    def create_api_key(self, name: str, permissions: List[str], rate_limit: int = 1000) -> str:
        """Create a new API key"""
        try:
            # Generate API key
            key = self.generate_api_key()
            
            # Create API key object
            api_key = APIKey(
                key=key,
                name=name,
                permissions=permissions,
                rate_limit=rate_limit,
                created_at=datetime.now()
            )
            
            # Store API key
            self.api_keys[key] = api_key
            
            self.logger.info(f"Created API key: {name}")
            return key
            
        except Exception as e:
            self.logger.error(f"Failed to create API key: {str(e)}")
            return None
            
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        import secrets
        return f"ak_{secrets.token_urlsafe(32)}"
        
    def list_integrations(self) -> List[Dict[str, Any]]:
        """List all integrations"""
        return [
            {
                'id': integration_id,
                'name': config.name,
                'type': config.type.value,
                'base_url': config.base_url,
                'active': config.active,
                'timeout': config.timeout,
                'rate_limit': config.rate_limit
            }
            for integration_id, config in self.integrations.items()
        ]
        
    def get_integration(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get integration by ID"""
        if integration_id not in self.integrations:
            return None
            
        config = self.integrations[integration_id]
        return {
            'id': integration_id,
            'name': config.name,
            'type': config.type.value,
            'base_url': config.base_url,
            'active': config.active,
            'timeout': config.timeout,
            'rate_limit': config.rate_limit
        }
        
    def update_integration(self, integration_id: str, updates: Dict[str, Any]) -> bool:
        """Update integration"""
        try:
            if integration_id not in self.integrations:
                return False
                
            config = self.integrations[integration_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    
            self.logger.info(f"Updated integration: {integration_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update integration: {str(e)}")
            return False
            
    def delete_integration(self, integration_id: str) -> bool:
        """Delete integration"""
        try:
            if integration_id in self.integrations:
                del self.integrations[integration_id]
                self.logger.info(f"Deleted integration: {integration_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete integration: {str(e)}")
            return False
            
    def test_integration(self, integration_id: str) -> Dict[str, Any]:
        """Test integration connection"""
        try:
            if integration_id not in self.integrations:
                return {'success': False, 'error': 'Integration not found'}
                
            config = self.integrations[integration_id]
            
            # Test connection based on type
            if config.type == IntegrationType.JIRA:
                result = self.test_jira_connection(config)
            elif config.type == IntegrationType.GITHUB:
                result = self.test_github_connection(config)
            elif config.type == IntegrationType.GITLAB:
                result = self.test_gitlab_connection(config)
            elif config.type == IntegrationType.SLACK:
                result = self.test_slack_connection(config)
            else:
                result = True  # Custom integrations
                
            return {'success': result, 'message': 'Connection test completed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def list_api_keys(self) -> List[Dict[str, Any]]:
        """List all API keys"""
        return [
            {
                'name': key_config.name,
                'permissions': key_config.permissions,
                'rate_limit': key_config.rate_limit,
                'created_at': key_config.created_at.isoformat(),
                'last_used': key_config.last_used.isoformat() if key_config.last_used else None
            }
            for key, key_config in self.api_keys.items()
        ]
        
    def delete_api_key(self, key_id: str) -> bool:
        """Delete API key"""
        try:
            if key_id in self.api_keys:
                del self.api_keys[key_id]
                self.logger.info(f"Deleted API key: {key_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete API key: {str(e)}")
            return False
            
    def external_test_cases(self):
        """External API endpoint for test cases"""
        try:
            if request.method == 'GET':
                # Get test cases
                # This would integrate with your main application
                return jsonify({
                    'success': True,
                    'test_cases': [],
                    'count': 0
                })
                
            elif request.method == 'POST':
                # Create test case
                data = request.get_json()
                # This would integrate with your main application
                return jsonify({
                    'success': True,
                    'test_case': data,
                    'id': 'test-123'
                })
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
            
    def external_test_executions(self):
        """External API endpoint for test executions"""
        try:
            if request.method == 'GET':
                # Get test executions
                return jsonify({
                    'success': True,
                    'executions': [],
                    'count': 0
                })
                
            elif request.method == 'POST':
                # Create test execution
                data = request.get_json()
                return jsonify({
                    'success': True,
                    'execution': data,
                    'id': 'exec-123'
                })
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
            
    def external_coverage(self):
        """External API endpoint for coverage analysis"""
        try:
            # Get coverage data
            return jsonify({
                'success': True,
                'coverage': {
                    'percentage': 85.5,
                    'covered_lines': 1200,
                    'total_lines': 1400
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
            
    def external_ai_generate(self):
        """External API endpoint for AI generation"""
        try:
            data = request.get_json()
            
            # This would integrate with your AI system
            return jsonify({
                'success': True,
                'generated_content': {
                    'test_cases': [],
                    'scenarios': [],
                    'coverage_analysis': {}
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

# Integration handlers
class IntegrationHandler:
    def __init__(self, gateway: APIGateway):
        self.gateway = gateway
        self.logger = logging.getLogger(__name__)
        
    def handle_jira_webhook(self, payload: Dict[str, Any]):
        """Handle Jira webhook"""
        try:
            event_type = payload.get('webhookEvent')
            
            if event_type == 'jira:issue_created':
                self.handle_jira_issue_created(payload)
            elif event_type == 'jira:issue_updated':
                self.handle_jira_issue_updated(payload)
            elif event_type == 'jira:issue_deleted':
                self.handle_jira_issue_deleted(payload)
                
        except Exception as e:
            self.logger.error(f"Failed to handle Jira webhook: {str(e)}")
            
    def handle_jira_issue_created(self, payload: Dict[str, Any]):
        """Handle Jira issue created"""
        issue = payload.get('issue', {})
        self.logger.info(f"Jira issue created: {issue.get('key')}")
        
    def handle_jira_issue_updated(self, payload: Dict[str, Any]):
        """Handle Jira issue updated"""
        issue = payload.get('issue', {})
        self.logger.info(f"Jira issue updated: {issue.get('key')}")
        
    def handle_jira_issue_deleted(self, payload: Dict[str, Any]):
        """Handle Jira issue deleted"""
        issue = payload.get('issue', {})
        self.logger.info(f"Jira issue deleted: {issue.get('key')}")
        
    def handle_github_webhook(self, payload: Dict[str, Any]):
        """Handle GitHub webhook"""
        try:
            event_type = request.headers.get('X-GitHub-Event')
            
            if event_type == 'pull_request':
                self.handle_github_pull_request(payload)
            elif event_type == 'push':
                self.handle_github_push(payload)
            elif event_type == 'issues':
                self.handle_github_issue(payload)
                
        except Exception as e:
            self.logger.error(f"Failed to handle GitHub webhook: {str(e)}")
            
    def handle_github_pull_request(self, payload: Dict[str, Any]):
        """Handle GitHub pull request"""
        pr = payload.get('pull_request', {})
        self.logger.info(f"GitHub PR: {pr.get('title')}")
        
    def handle_github_push(self, payload: Dict[str, Any]):
        """Handle GitHub push"""
        commits = payload.get('commits', [])
        self.logger.info(f"GitHub push: {len(commits)} commits")
        
    def handle_github_issue(self, payload: Dict[str, Any]):
        """Handle GitHub issue"""
        issue = payload.get('issue', {})
        self.logger.info(f"GitHub issue: {issue.get('title')}")

# Example usage
if __name__ == "__main__":
    from flask import Flask
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # Initialize API Gateway
    gateway = APIGateway(app)
    
    # Example integration
    jira_config = IntegrationConfig(
        name='Jira Integration',
        type=IntegrationType.JIRA,
        base_url='https://your-domain.atlassian.net',
        api_key='your-api-key',
        timeout=30,
        rate_limit=100
    )
    
    # Create integration
    gateway.create_integration('jira-001', jira_config)
    
    # Create API key
    api_key = gateway.create_api_key('Test API Key', ['read', 'write'], 1000)
    print(f"Created API key: {api_key}")
    
    # Run app
    app.run(debug=True, port=5000)