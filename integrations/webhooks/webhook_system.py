#!/usr/bin/env python3
"""
Webhook System for Assertly
Real-time integrations with external systems
"""

import os
import json
import hmac
import hashlib
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from flask import Flask, request, jsonify, abort
import requests
from threading import Thread
import queue
import logging

class WebhookEvent(Enum):
    TEST_CASE_CREATED = "test_case.created"
    TEST_CASE_UPDATED = "test_case.updated"
    TEST_CASE_DELETED = "test_case.deleted"
    TEST_EXECUTION_STARTED = "test_execution.started"
    TEST_EXECUTION_COMPLETED = "test_execution.completed"
    TEST_EXECUTION_FAILED = "test_execution.failed"
    COVERAGE_ANALYSIS_COMPLETED = "coverage_analysis.completed"
    AI_GENERATION_COMPLETED = "ai_generation.completed"
    JIRA_SYNC_COMPLETED = "jira_sync.completed"
    USER_STORY_CREATED = "user_story.created"
    USER_STORY_UPDATED = "user_story.updated"

@dataclass
class WebhookPayload:
    event: str
    timestamp: float
    data: Dict[str, Any]
    source: str = "assertly"
    version: str = "1.0"

@dataclass
class WebhookEndpoint:
    url: str
    events: List[str]
    secret: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    active: bool = True
    headers: Dict[str, str] = None

class WebhookManager:
    def __init__(self, app: Flask = None):
        self.app = app
        self.endpoints: List[WebhookEndpoint] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.queue = queue.Queue()
        self.worker_thread = None
        self.logger = logging.getLogger(__name__)
        
        if app:
            self.init_app(app)
            
    def init_app(self, app: Flask):
        """Initialize webhook manager with Flask app"""
        self.app = app
        
        # Register webhook endpoints
        app.add_url_rule('/webhooks/register', 'register_webhook', self.register_webhook, methods=['POST'])
        app.add_url_rule('/webhooks/unregister', 'unregister_webhook', self.unregister_webhook, methods=['POST'])
        app.add_url_rule('/webhooks/list', 'list_webhooks', self.list_webhooks, methods=['GET'])
        app.add_url_rule('/webhooks/test', 'test_webhook', self.test_webhook, methods=['POST'])
        
        # Start webhook worker thread
        self.start_worker()
        
    def register_webhook(self, endpoint: WebhookEndpoint) -> bool:
        """Register a new webhook endpoint"""
        try:
            # Validate endpoint
            if not self.validate_endpoint(endpoint):
                return False
                
            # Add to endpoints list
            self.endpoints.append(endpoint)
            
            # Log registration
            self.logger.info(f"Registered webhook endpoint: {endpoint.url}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register webhook: {str(e)}")
            return False
            
    def unregister_webhook(self, url: str) -> bool:
        """Unregister a webhook endpoint"""
        try:
            # Find and remove endpoint
            self.endpoints = [ep for ep in self.endpoints if ep.url != url]
            
            self.logger.info(f"Unregistered webhook endpoint: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister webhook: {str(e)}")
            return False
            
    def validate_endpoint(self, endpoint: WebhookEndpoint) -> bool:
        """Validate webhook endpoint"""
        try:
            # Check if URL is reachable
            response = requests.head(endpoint.url, timeout=5)
            return response.status_code < 400
            
        except Exception:
            return False
            
    def trigger_webhook(self, event: WebhookEvent, data: Dict[str, Any], source: str = "assertly"):
        """Trigger webhook for an event"""
        try:
            # Create payload
            payload = WebhookPayload(
                event=event.value,
                timestamp=time.time(),
                data=data,
                source=source
            )
            
            # Add to queue for processing
            self.queue.put(payload)
            
            self.logger.info(f"Triggered webhook for event: {event.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger webhook: {str(e)}")
            
    def start_worker(self):
        """Start webhook worker thread"""
        if not self.worker_thread or not self.worker_thread.is_alive():
            self.worker_thread = Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
    def _worker_loop(self):
        """Webhook worker loop"""
        while True:
            try:
                # Get payload from queue
                payload = self.queue.get(timeout=1)
                
                # Process webhook
                self._process_webhook(payload)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Webhook worker error: {str(e)}")
                
    def _process_webhook(self, payload: WebhookPayload):
        """Process webhook payload"""
        try:
            # Find matching endpoints
            matching_endpoints = [
                ep for ep in self.endpoints 
                if ep.active and payload.event in ep.events
            ]
            
            # Send to each matching endpoint
            for endpoint in matching_endpoints:
                self._send_webhook(endpoint, payload)
                
        except Exception as e:
            self.logger.error(f"Failed to process webhook: {str(e)}")
            
    def _send_webhook(self, endpoint: WebhookEndpoint, payload: WebhookPayload):
        """Send webhook to specific endpoint"""
        try:
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Assertly-Webhook/1.0',
                'X-Webhook-Event': payload.event,
                'X-Webhook-Timestamp': str(payload.timestamp),
                'X-Webhook-Source': payload.source
            }
            
            # Add custom headers
            if endpoint.headers:
                headers.update(endpoint.headers)
                
            # Add signature if secret is provided
            if endpoint.secret:
                signature = self._generate_signature(payload, endpoint.secret)
                headers['X-Webhook-Signature'] = f'sha256={signature}'
                
            # Convert payload to JSON
            payload_json = json.dumps(asdict(payload), default=str)
            
            # Send webhook with retries
            for attempt in range(endpoint.retry_count):
                try:
                    response = requests.post(
                        endpoint.url,
                        data=payload_json,
                        headers=headers,
                        timeout=endpoint.timeout
                    )
                    
                    if response.status_code < 400:
                        self.logger.info(f"Webhook sent successfully to {endpoint.url}")
                        break
                    else:
                        self.logger.warning(f"Webhook failed with status {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Webhook request failed (attempt {attempt + 1}): {str(e)}")
                    
                    if attempt < endpoint.retry_count - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        
        except Exception as e:
            self.logger.error(f"Failed to send webhook to {endpoint.url}: {str(e)}")
            
    def _generate_signature(self, payload: WebhookPayload, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        payload_json = json.dumps(asdict(payload), default=str, sort_keys=True)
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
        
    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception:
            return False
            
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List all registered webhooks"""
        return [
            {
                'url': ep.url,
                'events': ep.events,
                'active': ep.active,
                'timeout': ep.timeout,
                'retry_count': ep.retry_count
            }
            for ep in self.endpoints
        ]
        
    def test_webhook(self, url: str) -> Dict[str, Any]:
        """Test webhook endpoint"""
        try:
            # Create test payload
            test_payload = WebhookPayload(
                event=WebhookEvent.TEST_CASE_CREATED.value,
                timestamp=time.time(),
                data={'test': True, 'message': 'Webhook test from Assertly'},
                source='assertly'
            )
            
            # Send test webhook
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Assertly-Webhook/1.0',
                'X-Webhook-Event': test_payload.event,
                'X-Webhook-Timestamp': str(test_payload.timestamp),
                'X-Webhook-Source': test_payload.source
            }
            
            response = requests.post(
                url,
                data=json.dumps(asdict(test_payload), default=str),
                headers=headers,
                timeout=30
            )
            
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'response': response.text[:500] if response.text else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Flask routes for webhook management
def register_webhook():
    """Register a new webhook endpoint"""
    try:
        data = request.get_json()
        
        endpoint = WebhookEndpoint(
            url=data['url'],
            events=data.get('events', []),
            secret=data.get('secret'),
            timeout=data.get('timeout', 30),
            retry_count=data.get('retry_count', 3),
            headers=data.get('headers', {})
        )
        
        # Get webhook manager from app context
        webhook_manager = current_app.webhook_manager
        
        if webhook_manager.register_webhook(endpoint):
            return jsonify({'success': True, 'message': 'Webhook registered successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to register webhook'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def unregister_webhook():
    """Unregister a webhook endpoint"""
    try:
        data = request.get_json()
        url = data['url']
        
        # Get webhook manager from app context
        webhook_manager = current_app.webhook_manager
        
        if webhook_manager.unregister_webhook(url):
            return jsonify({'success': True, 'message': 'Webhook unregistered successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to unregister webhook'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def list_webhooks():
    """List all registered webhooks"""
    try:
        # Get webhook manager from app context
        webhook_manager = current_app.webhook_manager
        
        webhooks = webhook_manager.list_webhooks()
        return jsonify({'success': True, 'webhooks': webhooks})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def test_webhook():
    """Test a webhook endpoint"""
    try:
        data = request.get_json()
        url = data['url']
        
        # Get webhook manager from app context
        webhook_manager = current_app.webhook_manager
        
        result = webhook_manager.test_webhook(url)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Webhook event handlers
class WebhookEventHandler:
    def __init__(self, webhook_manager: WebhookManager):
        self.webhook_manager = webhook_manager
        self.logger = logging.getLogger(__name__)
        
    def on_test_case_created(self, test_case: Dict[str, Any]):
        """Handle test case created event"""
        self.webhook_manager.trigger_webhook(
            WebhookEvent.TEST_CASE_CREATED,
            {'test_case': test_case}
        )
        
    def on_test_case_updated(self, test_case: Dict[str, Any]):
        """Handle test case updated event"""
        self.webhook_manager.trigger_webhook(
            WebhookEvent.TEST_CASE_UPDATED,
            {'test_case': test_case}
        )
        
    def on_test_case_deleted(self, test_case_id: str):
        """Handle test case deleted event"""
        self.webhook_manager.trigger_webhook(
            WebhookEvent.TEST_CASE_DELETED,
            {'test_case_id': test_case_id}
        )
        
    def on_test_execution_started(self, execution: Dict[str, Any]):
        """Handle test execution started event"""
        self.webhook_manager.trigger_webhook(
            WebhookEvent.TEST_EXECUTION_STARTED,
            {'execution': execution}
        )
        
    def on_test_execution_completed(self, execution: Dict[str, Any]):
        """Handle test execution completed event"""
        self.webhook_manager.trigger_webhook(
            WebhookEvent.TEST_EXECUTION_COMPLETED,
            {'execution': execution}
        )
        
    def on_test_execution_failed(self, execution: Dict[str, Any], error: str):
        """Handle test execution failed event"""
        self.webhook_manager.trigger_webhook(
            WebhookEvent.TEST_EXECUTION_FAILED,
            {'execution': execution, 'error': error}
        )
        
    def on_coverage_analysis_completed(self, analysis: Dict[str, Any]):
        """Handle coverage analysis completed event"""
        self.webhook_manager.trigger_webhook(
            WebhookEvent.COVERAGE_ANALYSIS_COMPLETED,
            {'analysis': analysis}
        )
        
    def on_ai_generation_completed(self, generation: Dict[str, Any]):
        """Handle AI generation completed event"""
        self.webhook_manager.trigger_webhook(
            WebhookEvent.AI_GENERATION_COMPLETED,
            {'generation': generation}
        )
        
    def on_jira_sync_completed(self, sync_result: Dict[str, Any]):
        """Handle Jira sync completed event"""
        self.webhook_manager.trigger_webhook(
            WebhookEvent.JIRA_SYNC_COMPLETED,
            {'sync_result': sync_result}
        )

# Example usage and testing
if __name__ == "__main__":
    from flask import Flask, current_app
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # Initialize webhook manager
    webhook_manager = WebhookManager(app)
    app.webhook_manager = webhook_manager
    
    # Initialize event handler
    event_handler = WebhookEventHandler(webhook_manager)
    
    # Example webhook endpoint
    @app.route('/webhook-receiver', methods=['POST'])
    def webhook_receiver():
        """Example webhook receiver"""
        try:
            # Get webhook data
            data = request.get_json()
            event = request.headers.get('X-Webhook-Event')
            timestamp = request.headers.get('X-Webhook-Timestamp')
            signature = request.headers.get('X-Webhook-Signature')
            
            print(f"Received webhook event: {event}")
            print(f"Data: {json.dumps(data, indent=2)}")
            
            return jsonify({'success': True, 'message': 'Webhook received'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    # Test webhook system
    @app.route('/test-webhook-system')
    def test_webhook_system():
        """Test webhook system"""
        try:
            # Register test webhook
            test_endpoint = WebhookEndpoint(
                url='http://localhost:5000/webhook-receiver',
                events=[WebhookEvent.TEST_CASE_CREATED.value],
                secret='test-secret'
            )
            
            webhook_manager.register_webhook(test_endpoint)
            
            # Trigger test event
            event_handler.on_test_case_created({
                'id': 'test-123',
                'title': 'Test Case',
                'description': 'Test description'
            })
            
            return jsonify({'success': True, 'message': 'Webhook system tested'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    # Run app
    app.run(debug=True, port=5000)