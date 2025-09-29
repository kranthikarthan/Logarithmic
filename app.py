#!/usr/bin/env python3
"""
Standalone Xray Test Management Tool
A standalone application that replicates Xray test management functionality
using personal Jira credentials without requiring admin installation.
"""

import os
import json
import requests
import io
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from datetime import datetime, timedelta
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Excel export features will be limited.")
from dotenv import load_dotenv
import base64
import re
from functools import wraps
import time
from collections import defaultdict

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Security: Use environment variable for secret key, generate random if not set
import secrets
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Security decorators
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'jira_connected' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_input(data, required_fields=None, max_lengths=None):
    """Validate input data"""
    if required_fields:
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
    
    if max_lengths:
        for field, max_len in max_lengths.items():
            if field in data and len(str(data[field])) > max_len:
                return False, f"Field {field} exceeds maximum length of {max_len}"
    
    return True, None

def sanitize_jql(jql):
    """Sanitize JQL input to prevent injection"""
    if not jql:
        return jql
    
    # Remove potentially dangerous characters
    dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
    for char in dangerous_chars:
        jql = jql.replace(char, '')
    
    return jql.strip()

# Simple in-memory cache for performance
cache = defaultdict(dict)
CACHE_TTL = 300  # 5 minutes

def get_cached_data(key, ttl=CACHE_TTL):
    """Get data from cache if not expired"""
    if key in cache:
        data, timestamp = cache[key]
        if time.time() - timestamp < ttl:
            return data
    return None

def set_cached_data(key, data):
    """Set data in cache with timestamp"""
    cache[key] = (data, time.time())

def clear_cache():
    """Clear all cached data"""
    cache.clear()

class JiraXrayClient:
    """Client for interacting with Jira and Xray APIs"""
    
    def __init__(self, jira_url, username, api_token):
        self.jira_url = jira_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.session = requests.Session()
        self._setup_auth()
    
    def _setup_auth(self):
        """Setup authentication for Jira API"""
        auth_string = f"{self.username}:{self.api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        self.session.headers.update({
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_connection(self):
        """Test the connection to Jira"""
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/3/myself")
            return response.status_code == 200, response.json() if response.status_code == 200 else None
        except Exception as e:
            return False, str(e)
    
    def get_projects(self):
        """Get all accessible projects"""
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/3/project")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []
    
    def get_test_cases(self, project_key=None, jql=None):
        """Get test cases from Jira"""
        try:
            # Default JQL for test cases (Xray typically uses specific issue types)
            if not jql:
                if project_key:
                    jql = f'project = "{project_key}" AND issuetype = "Test"'
                else:
                    jql = 'issuetype = "Test"'
            
            params = {
                'jql': jql,
                'maxResults': 1000,
                'fields': 'summary,description,status,assignee,reporter,created,updated,labels,components,fixVersions,priority,issuetype,customfield_10014'  # customfield_10014 is often the test type
            }
            
            response = self.session.get(f"{self.jira_url}/rest/api/3/search", params=params)
            if response.status_code == 200:
                return response.json()
            return {'issues': []}
        except Exception as e:
            print(f"Error fetching test cases: {e}")
            return {'issues': []}
    
    def get_test_executions(self, project_key=None, jql=None):
        """Get test executions from Jira"""
        try:
            if not jql:
                if project_key:
                    jql = f'project = "{project_key}" AND issuetype = "Test Execution"'
                else:
                    jql = 'issuetype = "Test Execution"'
            
            params = {
                'jql': jql,
                'maxResults': 1000,
                'fields': 'summary,description,status,assignee,reporter,created,updated,labels,components,fixVersions,priority,issuetype'
            }
            
            response = self.session.get(f"{self.jira_url}/rest/api/3/search", params=params)
            if response.status_code == 200:
                return response.json()
            return {'issues': []}
        except Exception as e:
            print(f"Error fetching test executions: {e}")
            return {'issues': []}
    
    def get_test_plans(self, project_key=None, jql=None):
        """Get test plans from Jira"""
        try:
            if not jql:
                if project_key:
                    jql = f'project = "{project_key}" AND issuetype = "Test Plan"'
                else:
                    jql = 'issuetype = "Test Plan"'
            
            params = {
                'jql': jql,
                'maxResults': 1000,
                'fields': 'summary,description,status,assignee,reporter,created,updated,labels,components,fixVersions,priority,issuetype'
            }
            
            response = self.session.get(f"{self.jira_url}/rest/api/3/search", params=params)
            if response.status_code == 200:
                return response.json()
            return {'issues': []}
        except Exception as e:
            print(f"Error fetching test plans: {e}")
            return {'issues': []}
    
    def get_requirements(self, project_key=None, jql=None):
        """Get requirements from Jira (Epic, Story, or custom requirement issue types)"""
        try:
            if not jql:
                if project_key:
                    jql = f'project = "{project_key}" AND issuetype in ("Epic", "Story", "Requirement")'
                else:
                    jql = 'issuetype in ("Epic", "Story", "Requirement")'
            
            params = {
                'jql': jql,
                'maxResults': 1000,
                'fields': 'summary,description,status,assignee,reporter,created,updated,labels,components,fixVersions,priority,issuetype,parent'
            }
            
            response = self.session.get(f"{self.jira_url}/rest/api/3/search", params=params)
            if response.status_code == 200:
                return response.json()
            return {'issues': []}
        except Exception as e:
            print(f"Error fetching requirements: {e}")
            return {'issues': []}
    
    def get_issue_links(self, issue_key):
        """Get linked issues for traceability"""
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/3/issue/{issue_key}?fields=issuelinks")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching issue links for {issue_key}: {e}")
            return None
    
    def create_issue_link(self, inward_issue, outward_issue, link_type="relates"):
        """Create a link between issues for traceability"""
        try:
            link_data = {
                "type": {"name": link_type},
                "inwardIssue": {"key": inward_issue},
                "outwardIssue": {"key": outward_issue}
            }
            
            response = self.session.post(
                f"{self.jira_url}/rest/api/3/issueLink",
                json=link_data
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error creating issue link: {e}")
            return False

    def get_test_sets(self, project_key=None, jql=None):
        """Get test sets from Jira"""
        try:
            if not jql:
                if project_key:
                    jql = f'project = "{project_key}" AND issuetype = "Test Set"'
                else:
                    jql = 'issuetype = "Test Set"'
            
            params = {
                'jql': jql,
                'maxResults': 1000,
                'fields': 'summary,description,status,assignee,reporter,created,updated,labels,components,fixVersions,priority,issuetype,parent'
            }
            
            response = self.session.get(f"{self.jira_url}/rest/api/3/search", params=params)
            if response.status_code == 200:
                return response.json()
            return {'issues': []}
        except Exception as e:
            print(f"Error fetching test sets: {e}")
            return {'issues': []}

    def get_test_set_tests(self, test_set_key):
        """Get tests linked to a test set"""
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/3/issue/{test_set_key}?fields=issuelinks")
            if response.status_code == 200:
                data = response.json()
                issue_links = data.get('fields', {}).get('issuelinks', [])
                
                linked_tests = []
                for link in issue_links:
                    if link.get('type', {}).get('name') == 'Test Set contains':
                        linked_issue = link.get('inwardIssue') or link.get('outwardIssue')
                        if linked_issue:
                            linked_tests.append(linked_issue)
                
                return linked_tests
            return []
        except Exception as e:
            print(f"Error fetching test set tests: {e}")
            return []

    def add_test_to_set(self, test_set_key, test_key):
        """Add a test to a test set"""
        try:
            url = f"{self.jira_url}/rest/api/3/issueLink"
            data = {
                "type": {"name": "Test Set contains"},
                "inwardIssue": {"key": test_set_key},
                "outwardIssue": {"key": test_key}
            }
            
            response = self.session.post(url, json=data)
            return response.status_code == 201
        except Exception as e:
            print(f"Error adding test to set: {e}")
            return False

    def remove_test_from_set(self, test_set_key, test_key):
        """Remove a test from a test set"""
        try:
            # Get the link ID first
            response = self.session.get(f"{self.jira_url}/rest/api/3/issue/{test_set_key}?fields=issuelinks")
            if response.status_code != 200:
                return False
                
            data = response.json()
            issue_links = data.get('fields', {}).get('issuelinks', [])
            
            link_id = None
            for link in issue_links:
                if link.get('type', {}).get('name') == 'Test Set contains':
                    linked_issue = link.get('inwardIssue') or link.get('outwardIssue')
                    if linked_issue and linked_issue.get('key') == test_key:
                        link_id = link.get('id')
                        break
            
            if link_id:
                # Delete the link
                delete_url = f"{self.jira_url}/rest/api/3/issueLink/{link_id}"
                response = self.session.delete(delete_url)
                return response.status_code == 204
            
            return False
        except Exception as e:
            print(f"Error removing test from set: {e}")
            return False

    def get_preconditions(self, project_key=None, jql=None):
        """Get test preconditions from Jira"""
        try:
            if not jql:
                if project_key:
                    jql = f'project = "{project_key}" AND issuetype = "Precondition"'
                else:
                    jql = 'issuetype = "Precondition"'
            
            params = {
                'jql': jql,
                'maxResults': 1000,
                'fields': 'summary,description,status,assignee,reporter,created,updated,labels,components,fixVersions,priority,issuetype,parent'
            }
            
            response = self.session.get(f"{self.jira_url}/rest/api/3/search", params=params)
            if response.status_code == 200:
                return response.json()
            return {'issues': []}
        except Exception as e:
            print(f"Error fetching preconditions: {e}")
            return {'issues': []}

    def get_precondition_tests(self, precondition_key):
        """Get tests that use a specific precondition"""
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/3/issue/{precondition_key}?fields=issuelinks")
            if response.status_code == 200:
                data = response.json()
                issue_links = data.get('fields', {}).get('issuelinks', [])
                
                linked_tests = []
                for link in issue_links:
                    if link.get('type', {}).get('name') == 'Precondition':
                        linked_issue = link.get('inwardIssue') or link.get('outwardIssue')
                        if linked_issue:
                            linked_tests.append(linked_issue)
                
                return linked_tests
            return []
        except Exception as e:
            print(f"Error fetching precondition tests: {e}")
            return []

    def link_precondition_to_test(self, test_key, precondition_key):
        """Link a precondition to a test"""
        try:
            url = f"{self.jira_url}/rest/api/3/issueLink"
            data = {
                "type": {"name": "Precondition"},
                "inwardIssue": {"key": test_key},
                "outwardIssue": {"key": precondition_key}
            }
            
            response = self.session.post(url, json=data)
            return response.status_code == 201
        except Exception as e:
            print(f"Error linking precondition to test: {e}")
            return False

    def unlink_precondition_from_test(self, test_key, precondition_key):
        """Unlink a precondition from a test"""
        try:
            # Get the link ID first
            response = self.session.get(f"{self.jira_url}/rest/api/3/issue/{test_key}?fields=issuelinks")
            if response.status_code != 200:
                return False
                
            data = response.json()
            issue_links = data.get('fields', {}).get('issuelinks', [])
            
            link_id = None
            for link in issue_links:
                if link.get('type', {}).get('name') == 'Precondition':
                    linked_issue = link.get('inwardIssue') or link.get('outwardIssue')
                    if linked_issue and linked_issue.get('key') == precondition_key:
                        link_id = link.get('id')
                        break
            
            if link_id:
                # Delete the link
                delete_url = f"{self.jira_url}/rest/api/3/issueLink/{link_id}"
                response = self.session.delete(delete_url)
                return response.status_code == 204
            
            return False
        except Exception as e:
            print(f"Error unlinking precondition from test: {e}")
            return False

    def get_advanced_metrics(self, project_key=None, date_range=None):
        """Get advanced test metrics and analytics"""
        try:
            # Mock advanced metrics data
            metrics = {
                'test_execution_trends': {
                    'daily': [
                        {'date': '2024-01-01', 'executed': 45, 'passed': 42, 'failed': 3},
                        {'date': '2024-01-02', 'executed': 52, 'passed': 48, 'failed': 4},
                        {'date': '2024-01-03', 'executed': 38, 'passed': 35, 'failed': 3},
                        {'date': '2024-01-04', 'executed': 61, 'passed': 58, 'failed': 3},
                        {'date': '2024-01-05', 'executed': 47, 'passed': 44, 'failed': 3}
                    ],
                    'weekly': [
                        {'week': '2024-W01', 'executed': 234, 'passed': 220, 'failed': 14},
                        {'week': '2024-W02', 'executed': 267, 'passed': 251, 'failed': 16},
                        {'week': '2024-W03', 'executed': 289, 'passed': 273, 'failed': 16}
                    ]
                },
                'test_coverage_metrics': {
                    'requirements_coverage': 85.5,
                    'code_coverage': 78.2,
                    'functional_coverage': 92.1,
                    'regression_coverage': 88.7
                },
                'defect_metrics': {
                    'total_defects': 127,
                    'open_defects': 23,
                    'closed_defects': 104,
                    'defect_density': 2.3,
                    'defect_resolution_time': 3.2
                },
                'test_automation_metrics': {
                    'automation_coverage': 65.8,
                    'automated_tests': 156,
                    'manual_tests': 89,
                    'automation_success_rate': 94.2
                },
                'performance_metrics': {
                    'avg_execution_time': 12.5,
                    'slowest_tests': [
                        {'test': 'TEST-001', 'duration': 45.2},
                        {'test': 'TEST-015', 'duration': 38.7},
                        {'test': 'TEST-023', 'duration': 32.1}
                    ]
                }
            }
            return metrics
        except Exception as e:
            print(f"Error fetching advanced metrics: {e}")
            return {}

    def get_test_analytics(self, project_key=None, analysis_type='overview'):
        """Get detailed test analytics"""
        try:
            analytics = {
                'overview': {
                    'total_tests': 245,
                    'executed_tests': 198,
                    'passed_tests': 185,
                    'failed_tests': 13,
                    'pass_rate': 93.4,
                    'execution_rate': 80.8
                },
                'trends': {
                    'test_creation_trend': 'increasing',
                    'execution_trend': 'stable',
                    'pass_rate_trend': 'improving'
                },
                'bottlenecks': [
                    {'area': 'Database Tests', 'issue': 'Slow execution', 'impact': 'High'},
                    {'area': 'UI Tests', 'issue': 'Flaky tests', 'impact': 'Medium'},
                    {'area': 'API Tests', 'issue': 'Environment issues', 'impact': 'Low'}
                ],
                'recommendations': [
                    'Optimize database test setup',
                    'Implement better test data management',
                    'Add more automated tests for regression coverage'
                ]
            }
            return analytics
        except Exception as e:
            print(f"Error fetching test analytics: {e}")
            return {}

    def get_custom_reports(self, report_type='executive'):
        """Get custom reports for different stakeholders"""
        try:
            reports = {
                'executive': {
                    'title': 'Executive Summary',
                    'summary': 'Overall test health and progress',
                    'metrics': {
                        'test_coverage': 85.5,
                        'defect_escape_rate': 2.1,
                        'release_readiness': 87.3
                    }
                },
                'manager': {
                    'title': 'Management Dashboard',
                    'summary': 'Team performance and resource utilization',
                    'metrics': {
                        'team_velocity': 45.2,
                        'test_automation_ratio': 65.8,
                        'defect_resolution_time': 3.2
                    }
                },
                'tester': {
                    'title': 'Tester Dashboard',
                    'summary': 'Individual and team testing activities',
                    'metrics': {
                        'tests_created': 23,
                        'tests_executed': 156,
                        'defects_found': 8
                    }
                }
            }
            return reports.get(report_type, {})
        except Exception as e:
            print(f"Error fetching custom reports: {e}")
            return {}

    def get_workflows(self, project_key=None):
        """Get test workflows and approval processes"""
        try:
            # Mock workflow data
            workflows = {
                'workflows': [
                    {
                        'id': 'wf-001',
                        'name': 'Standard Test Workflow',
                        'description': 'Standard workflow for test execution and approval',
                        'status': 'active',
                        'steps': [
                            {'id': 1, 'name': 'Test Creation', 'type': 'manual', 'approver': None},
                            {'id': 2, 'name': 'Test Review', 'type': 'approval', 'approver': 'Test Lead'},
                            {'id': 3, 'name': 'Test Execution', 'type': 'manual', 'approver': None},
                            {'id': 4, 'name': 'Results Review', 'type': 'approval', 'approver': 'Test Manager'}
                        ]
                    },
                    {
                        'id': 'wf-002',
                        'name': 'Automated Test Workflow',
                        'description': 'Workflow for automated test execution',
                        'status': 'active',
                        'steps': [
                            {'id': 1, 'name': 'Test Creation', 'type': 'manual', 'approver': None},
                            {'id': 2, 'name': 'Automation Review', 'type': 'approval', 'approver': 'Automation Lead'},
                            {'id': 3, 'name': 'Automated Execution', 'type': 'automated', 'approver': None},
                            {'id': 4, 'name': 'Results Analysis', 'type': 'approval', 'approver': 'Test Manager'}
                        ]
                    }
                ]
            }
            return workflows
        except Exception as e:
            print(f"Error fetching workflows: {e}")
            return {'workflows': []}

    def get_approval_requests(self, project_key=None, status=None):
        """Get pending approval requests"""
        try:
            # Mock approval requests data
            requests = {
                'requests': [
                    {
                        'id': 'req-001',
                        'test_key': 'TEST-001',
                        'test_name': 'Login Functionality Test',
                        'requestor': 'John Doe',
                        'request_date': '2024-01-15T10:30:00Z',
                        'approval_type': 'Test Review',
                        'status': 'pending',
                        'approver': 'Test Lead',
                        'priority': 'High'
                    },
                    {
                        'id': 'req-002',
                        'test_key': 'TEST-015',
                        'test_name': 'Payment Processing Test',
                        'requestor': 'Jane Smith',
                        'request_date': '2024-01-15T14:20:00Z',
                        'approval_type': 'Automation Review',
                        'status': 'pending',
                        'approver': 'Automation Lead',
                        'priority': 'Medium'
                    }
                ]
            }
            return requests
        except Exception as e:
            print(f"Error fetching approval requests: {e}")
            return {'requests': []}

    def approve_request(self, request_id, approver, comments=None):
        """Approve a test request"""
        try:
            # Mock approval process
            return {
                'success': True,
                'message': f'Request {request_id} approved by {approver}',
                'approval_date': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error approving request: {e}")
            return {'success': False, 'error': str(e)}

    def reject_request(self, request_id, approver, comments=None):
        """Reject a test request"""
        try:
            # Mock rejection process
            return {
                'success': True,
                'message': f'Request {request_id} rejected by {approver}',
                'rejection_date': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error rejecting request: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_bdd_scenarios(self, project_key=None, jql=None):
        """Get BDD scenarios from Jira"""
        try:
            if not jql:
                if project_key:
                    jql = f'project = "{project_key}" AND issuetype = "Test" AND summary ~ "Scenario:"'
                else:
                    jql = 'issuetype = "Test" AND summary ~ "Scenario:"'
            
            params = {
                'jql': jql,
                'maxResults': 1000,
                'fields': 'summary,description,status,assignee,reporter,created,updated,labels,components,fixVersions,priority,issuetype'
            }
            
            response = self.session.get(f"{self.jira_url}/rest/api/3/search", params=params)
            if response.status_code == 200:
                return response.json()
            return {'issues': []}
        except Exception as e:
            print(f"Error fetching BDD scenarios: {e}")
            return {'issues': []}
    
    def parse_gherkin_from_description(self, description):
        """Parse Gherkin syntax from issue description"""
        if not description:
            return None
        
        lines = description.split('\n')
        gherkin_data = {
            'feature': '',
            'scenarios': [],
            'background': [],
            'tags': []
        }
        
        current_scenario = None
        in_background = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('@'):
                gherkin_data['tags'].append(line[1:])
            elif line.startswith('Feature:'):
                gherkin_data['feature'] = line.replace('Feature:', '').strip()
            elif line.startswith('Background:'):
                in_background = True
            elif line.startswith('Scenario:'):
                if current_scenario:
                    gherkin_data['scenarios'].append(current_scenario)
                current_scenario = {
                    'name': line.replace('Scenario:', '').strip(),
                    'steps': []
                }
                in_background = False
            elif line.startswith('Given') or line.startswith('When') or line.startswith('Then') or line.startswith('And') or line.startswith('But'):
                step = {
                    'keyword': line.split()[0],
                    'text': ' '.join(line.split()[1:])
                }
                if in_background:
                    gherkin_data['background'].append(step)
                elif current_scenario:
                    current_scenario['steps'].append(step)
        
        if current_scenario:
            gherkin_data['scenarios'].append(current_scenario)
        
        return gherkin_data
    
    def get_issue_details(self, issue_key):
        """Get detailed information about a specific issue"""
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/3/issue/{issue_key}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching issue {issue_key}: {e}")
            return None

def get_jira_client():
    """Get Jira client from session or create new one"""
    if 'jira_connected' not in session:
        return None
    
    # Create client from session data
    return JiraXrayClient(
        session['jira_url'],
        session['username'],
        session.get('api_token')  # Store token securely in session
    )

@app.route('/')
def index():
    """Main dashboard"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/test-execution')
def test_execution():
    """Test execution page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('test-execution.html')

@app.route('/requirements-traceability')
def requirements_traceability():
    """Requirements traceability page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('requirements-traceability.html')

@app.route('/bdd-scenarios')
def bdd_scenarios():
    """BDD scenarios page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('bdd-scenarios.html')

@app.route('/automated-testing')
def automated_testing():
    """Automated testing page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('automated-testing.html')

@app.route('/defect-management')
def defect_management():
    """Defect management page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('defect-management.html')

@app.route('/test-data-management')
def test_data_management():
    """Test data management page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('test-data-management.html')

@app.route('/scheduling-environments')
def scheduling_environments():
    """Scheduling and environments page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('scheduling-environments.html')

@app.route('/test-sets')
def test_sets():
    """Test sets management page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('test-sets.html')

@app.route('/preconditions')
def preconditions():
    """Preconditions management page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('preconditions.html')

@app.route('/advanced-reporting')
def advanced_reporting():
    """Advanced reporting and analytics page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('advanced-reporting.html')

@app.route('/workflow-approval')
def workflow_approval():
    """Workflow and approval management page"""
    if 'jira_connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('workflow-approval.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for Jira credentials"""
    if request.method == 'POST':
        jira_url = request.form.get('jira_url')
        username = request.form.get('username')
        api_token = request.form.get('api_token')
        
        if not all([jira_url, username, api_token]):
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        # Create temporary client for testing
        temp_client = JiraXrayClient(jira_url, username, api_token)
        
        # Test connection
        success, user_info = temp_client.test_connection()
        if success:
            session['jira_connected'] = True
            session['jira_url'] = jira_url
            session['username'] = username
            session['api_token'] = api_token  # Store token in session
            session['user_info'] = user_info
            flash('Successfully connected to Jira!', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Failed to connect to Jira: {user_info}', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/api/projects')
def api_projects():
    """API endpoint to get projects"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        projects = jira_client.get_projects()
        return jsonify(projects)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-cases')
def api_test_cases():
    """API endpoint to get test cases"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        jql = request.args.get('jql')
        
        test_cases = jira_client.get_test_cases(project_key, jql)
        return jsonify(test_cases)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-executions')
def api_test_executions():
    """API endpoint to get test executions"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        jql = request.args.get('jql')
        
        test_executions = jira_client.get_test_executions(project_key, jql)
        return jsonify(test_executions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-plans')
def api_test_plans():
    """API endpoint to get test plans"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        jql = request.args.get('jql')
        
        test_plans = jira_client.get_test_plans(project_key, jql)
        return jsonify(test_plans)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requirements')
def api_requirements():
    """API endpoint to get requirements"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        jql = request.args.get('jql')
        
        requirements = jira_client.get_requirements(project_key, jql)
        return jsonify(requirements)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/issue/<issue_key>/links')
def api_issue_links(issue_key):
    """API endpoint to get issue links for traceability"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        links = jira_client.get_issue_links(issue_key)
        if links:
            return jsonify(links)
        else:
            return jsonify({'error': 'Issue not found or no links'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/issue-links', methods=['POST'])
def api_create_issue_link():
    """API endpoint to create issue links for traceability"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        inward_issue = data.get('inward_issue')
        outward_issue = data.get('outward_issue')
        link_type = data.get('link_type', 'relates')
        
        if not inward_issue or not outward_issue:
            return jsonify({'error': 'Both inward_issue and outward_issue are required'}), 400
        
        success = jira_client.create_issue_link(inward_issue, outward_issue, link_type)
        if success:
            return jsonify({'success': True, 'message': 'Issue link created successfully'})
        else:
            return jsonify({'error': 'Failed to create issue link'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bdd-scenarios')
def api_bdd_scenarios():
    """API endpoint to get BDD scenarios"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        jql = request.args.get('jql')
        
        scenarios = jira_client.get_bdd_scenarios(project_key, jql)
        
        # Parse Gherkin from descriptions
        for issue in scenarios.get('issues', []):
            description = issue.get('fields', {}).get('description', '')
            if description:
                gherkin_data = jira_client.parse_gherkin_from_description(description)
                issue['gherkin'] = gherkin_data
        
        return jsonify(scenarios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bdd-scenarios/<issue_key>/gherkin')
def api_parse_gherkin(issue_key):
    """API endpoint to parse Gherkin from a specific issue"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        issue = jira_client.get_issue_details(issue_key)
        if not issue:
            return jsonify({'error': 'Issue not found'}), 404
        
        description = issue.get('fields', {}).get('description', '')
        gherkin_data = jira_client.parse_gherkin_from_description(description)
        
        return jsonify({
            'issue_key': issue_key,
            'gherkin': gherkin_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automated-tests')
def api_automated_tests():
    """API endpoint to get automated test results"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        test_framework = request.args.get('framework', 'all')
        
        # Mock automated test results - in real implementation, integrate with CI/CD
        automated_tests = {
            'total_tests': 150,
            'passed': 120,
            'failed': 20,
            'skipped': 10,
            'execution_time': '15m 30s',
            'framework_results': {
                'selenium': {
                    'total': 80,
                    'passed': 70,
                    'failed': 8,
                    'skipped': 2,
                    'execution_time': '8m 15s'
                },
                'junit': {
                    'total': 50,
                    'passed': 40,
                    'failed': 8,
                    'skipped': 2,
                    'execution_time': '4m 30s'
                },
                'cucumber': {
                    'total': 20,
                    'passed': 10,
                    'failed': 4,
                    'skipped': 6,
                    'execution_time': '2m 45s'
                }
            },
            'recent_executions': [
                {
                    'id': 'exec-001',
                    'timestamp': '2024-01-15T10:30:00Z',
                    'status': 'completed',
                    'total_tests': 150,
                    'passed': 120,
                    'failed': 20,
                    'skipped': 10,
                    'duration': '15m 30s',
                    'framework': 'selenium'
                },
                {
                    'id': 'exec-002',
                    'timestamp': '2024-01-15T09:15:00Z',
                    'status': 'completed',
                    'total_tests': 150,
                    'passed': 140,
                    'failed': 8,
                    'skipped': 2,
                    'duration': '12m 45s',
                    'framework': 'junit'
                }
            ]
        }
        
        return jsonify(automated_tests)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ci-cd-integration')
def api_ci_cd_integration():
    """API endpoint for CI/CD integration status"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        # Mock CI/CD integration data
        ci_cd_data = {
            'integrations': {
                'jenkins': {
                    'enabled': True,
                    'url': 'https://jenkins.company.com',
                    'last_build': '2024-01-15T10:30:00Z',
                    'status': 'success',
                    'test_results': {
                        'total': 150,
                        'passed': 120,
                        'failed': 20,
                        'skipped': 10
                    }
                },
                'bamboo': {
                    'enabled': False,
                    'url': None,
                    'last_build': None,
                    'status': 'disabled'
                },
                'gitlab': {
                    'enabled': True,
                    'url': 'https://gitlab.company.com',
                    'last_build': '2024-01-15T09:45:00Z',
                    'status': 'success',
                    'test_results': {
                        'total': 100,
                        'passed': 95,
                        'failed': 3,
                        'skipped': 2
                    }
                }
            },
            'pipeline_status': {
                'total_pipelines': 2,
                'active_pipelines': 2,
                'success_rate': 85.5,
                'average_execution_time': '14m 30s'
            }
        }
        
        return jsonify(ci_cd_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trigger-automated-test', methods=['POST'])
def api_trigger_automated_test():
    """API endpoint to trigger automated test execution"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        test_suite = data.get('test_suite', 'all')
        framework = data.get('framework', 'selenium')
        environment = data.get('environment', 'staging')
        
        # Mock test execution trigger
        execution_id = f"exec-{int(time.time())}"
        
        return jsonify({
            'success': True,
            'execution_id': execution_id,
            'message': f'Automated test execution triggered for {test_suite} using {framework}',
            'estimated_duration': '15-20 minutes',
            'status_url': f'/api/execution-status/{execution_id}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/defects')
def api_defects():
    """API endpoint to get defects/bugs"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        jql = request.args.get('jql')
        
        if not jql:
            if project_key:
                jql = f'project = "{project_key}" AND issuetype = "Bug"'
            else:
                jql = 'issuetype = "Bug"'
        
        params = {
            'jql': jql,
            'maxResults': 1000,
            'fields': 'summary,description,status,assignee,reporter,created,updated,labels,components,fixVersions,priority,issuetype,issuelinks'
        }
        
        response = jira_client.session.get(f"{jira_client.jira_url}/rest/api/3/search", params=params)
        if response.status_code == 200:
            return response.json()
        return {'issues': []}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/defect-analysis')
def api_defect_analysis():
    """API endpoint to get defect analysis and statistics"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        # Get defects
        defects = jira_client.get_requirements(project_key)  # Using requirements method as placeholder
        defects_list = defects.get('issues', [])
        
        # Mock defect analysis data
        analysis = {
            'total_defects': len(defects_list),
            'open_defects': len([d for d in defects_list if d.get('fields', {}).get('status', {}).get('name') in ['Open', 'In Progress']]),
            'closed_defects': len([d for d in defects_list if d.get('fields', {}).get('status', {}).get('name') in ['Closed', 'Resolved']]),
            'critical_defects': len([d for d in defects_list if d.get('fields', {}).get('priority', {}).get('name') == 'Critical']),
            'defects_by_priority': {
                'Critical': 5,
                'High': 12,
                'Medium': 25,
                'Low': 8
            },
            'defects_by_status': {
                'Open': 15,
                'In Progress': 8,
                'Resolved': 20,
                'Closed': 7
            },
            'defects_by_component': {
                'Authentication': 8,
                'Dashboard': 12,
                'User Management': 6,
                'Reports': 4
            },
            'average_resolution_time': '3.5 days',
            'defect_trend': [
                {'date': '2024-01-01', 'opened': 5, 'closed': 3},
                {'date': '2024-01-02', 'opened': 3, 'closed': 4},
                {'date': '2024-01-03', 'opened': 7, 'closed': 2},
                {'date': '2024-01-04', 'opened': 4, 'closed': 6},
                {'date': '2024-01-05', 'opened': 6, 'closed': 5}
            ]
        }
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-failure-analysis')
def api_test_failure_analysis():
    """API endpoint to analyze test failures and link to defects"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        # Mock test failure analysis
        failure_analysis = {
            'total_failures': 25,
            'linked_to_defects': 18,
            'unlinked_failures': 7,
            'failure_rate': 16.7,
            'top_failure_reasons': [
                {'reason': 'Element not found', 'count': 8, 'percentage': 32},
                {'reason': 'Timeout waiting for element', 'count': 6, 'percentage': 24},
                {'reason': 'Assertion failed', 'count': 5, 'percentage': 20},
                {'reason': 'Network error', 'count': 3, 'percentage': 12},
                {'reason': 'Data validation error', 'count': 3, 'percentage': 12}
            ],
            'recent_failures': [
                {
                    'test_key': 'TEST-001',
                    'test_name': 'Login with valid credentials',
                    'failure_reason': 'Element not found',
                    'timestamp': '2024-01-15T10:30:00Z',
                    'linked_defect': 'BUG-123',
                    'status': 'linked'
                },
                {
                    'test_key': 'TEST-002',
                    'test_name': 'User registration',
                    'failure_reason': 'Timeout waiting for element',
                    'timestamp': '2024-01-15T09:45:00Z',
                    'linked_defect': None,
                    'status': 'unlinked'
                }
            ]
        }
        
        return jsonify(failure_analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-data-sets')
def api_test_data_sets():
    """API endpoint to get test data sets"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        # Mock test data sets
        test_data_sets = {
            'data_sets': [
                {
                    'id': 'tds-001',
                    'name': 'User Credentials',
                    'description': 'Valid and invalid user credentials for authentication testing',
                    'data_type': 'credentials',
                    'created': '2024-01-10T09:00:00Z',
                    'updated': '2024-01-15T14:30:00Z',
                    'records_count': 25,
                    'fields': ['username', 'password', 'role', 'status'],
                    'sample_data': [
                        {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'status': 'active'},
                        {'username': 'user1', 'password': 'user123', 'role': 'user', 'status': 'active'},
                        {'username': 'locked', 'password': 'locked123', 'role': 'user', 'status': 'locked'}
                    ]
                },
                {
                    'id': 'tds-002',
                    'name': 'Product Catalog',
                    'description': 'Product data for e-commerce testing',
                    'data_type': 'products',
                    'created': '2024-01-12T10:15:00Z',
                    'updated': '2024-01-15T16:45:00Z',
                    'records_count': 100,
                    'fields': ['product_id', 'name', 'price', 'category', 'in_stock'],
                    'sample_data': [
                        {'product_id': 'P001', 'name': 'Laptop', 'price': 999.99, 'category': 'Electronics', 'in_stock': True},
                        {'product_id': 'P002', 'name': 'Mouse', 'price': 29.99, 'category': 'Accessories', 'in_stock': True},
                        {'product_id': 'P003', 'name': 'Keyboard', 'price': 79.99, 'category': 'Accessories', 'in_stock': False}
                    ]
                },
                {
                    'id': 'tds-003',
                    'name': 'API Test Data',
                    'description': 'API endpoints and test payloads',
                    'data_type': 'api',
                    'created': '2024-01-14T11:30:00Z',
                    'updated': '2024-01-15T13:20:00Z',
                    'records_count': 50,
                    'fields': ['endpoint', 'method', 'payload', 'expected_status'],
                    'sample_data': [
                        {'endpoint': '/api/users', 'method': 'GET', 'payload': '{}', 'expected_status': 200},
                        {'endpoint': '/api/users', 'method': 'POST', 'payload': '{"name":"John","email":"john@test.com"}', 'expected_status': 201},
                        {'endpoint': '/api/users/1', 'method': 'PUT', 'payload': '{"name":"John Updated"}', 'expected_status': 200}
                    ]
                }
            ],
            'total_sets': 3,
            'total_records': 175
        }
        
        return jsonify(test_data_sets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-data-sets/<data_set_id>')
def api_test_data_set_details(data_set_id):
    """API endpoint to get detailed test data set information"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        # Mock detailed data set
        data_set = {
            'id': data_set_id,
            'name': 'User Credentials',
            'description': 'Valid and invalid user credentials for authentication testing',
            'data_type': 'credentials',
            'created': '2024-01-10T09:00:00Z',
            'updated': '2024-01-15T14:30:00Z',
            'records_count': 25,
            'fields': [
                {'name': 'username', 'type': 'string', 'required': True, 'description': 'User login name'},
                {'name': 'password', 'type': 'string', 'required': True, 'description': 'User password'},
                {'name': 'role', 'type': 'enum', 'required': True, 'values': ['admin', 'user', 'guest'], 'description': 'User role'},
                {'name': 'status', 'type': 'enum', 'required': True, 'values': ['active', 'inactive', 'locked'], 'description': 'Account status'}
            ],
            'data_records': [
                {'id': 1, 'username': 'admin', 'password': 'admin123', 'role': 'admin', 'status': 'active'},
                {'id': 2, 'username': 'user1', 'password': 'user123', 'role': 'user', 'status': 'active'},
                {'id': 3, 'username': 'user2', 'password': 'user456', 'role': 'user', 'status': 'active'},
                {'id': 4, 'username': 'locked', 'password': 'locked123', 'role': 'user', 'status': 'locked'},
                {'id': 5, 'username': 'inactive', 'password': 'inactive123', 'role': 'user', 'status': 'inactive'}
            ],
            'usage_stats': {
                'tests_using': 15,
                'last_used': '2024-01-15T10:30:00Z',
                'execution_count': 45
            }
        }
        
        return jsonify(data_set)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parameterized-tests')
def api_parameterized_tests():
    """API endpoint to get parameterized test configurations"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        # Mock parameterized tests
        parameterized_tests = {
            'tests': [
                {
                    'id': 'pt-001',
                    'name': 'Login Parameterized Test',
                    'description': 'Test login functionality with different user credentials',
                    'test_type': 'parameterized',
                    'data_set_id': 'tds-001',
                    'parameters': ['username', 'password', 'expected_result'],
                    'test_steps': [
                        'Navigate to login page',
                        'Enter username: {username}',
                        'Enter password: {password}',
                        'Click login button',
                        'Verify result: {expected_result}'
                    ],
                    'iterations': 5,
                    'status': 'active'
                },
                {
                    'id': 'pt-002',
                    'name': 'Product Search Test',
                    'description': 'Test product search with different search terms',
                    'test_type': 'parameterized',
                    'data_set_id': 'tds-002',
                    'parameters': ['search_term', 'category', 'expected_count'],
                    'test_steps': [
                        'Navigate to search page',
                        'Enter search term: {search_term}',
                        'Select category: {category}',
                        'Click search button',
                        'Verify result count: {expected_count}'
                    ],
                    'iterations': 10,
                    'status': 'active'
                }
            ],
            'total_tests': 2,
            'total_iterations': 15
        }
        
        return jsonify(parameterized_tests)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-schedules')
def api_test_schedules():
    """API endpoint to get test schedules"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        # Mock test schedules
        schedules = {
            'schedules': [
                {
                    'id': 'sched-001',
                    'name': 'Daily Smoke Tests',
                    'description': 'Run smoke tests every day at 6 AM',
                    'test_suite': 'smoke',
                    'environment': 'staging',
                    'schedule_type': 'recurring',
                    'cron_expression': '0 6 * * *',
                    'next_run': '2024-01-16T06:00:00Z',
                    'status': 'active',
                    'created_by': 'admin',
                    'created_at': '2024-01-10T09:00:00Z'
                },
                {
                    'id': 'sched-002',
                    'name': 'Weekly Regression Tests',
                    'description': 'Run full regression suite every Sunday at 2 AM',
                    'test_suite': 'regression',
                    'environment': 'production',
                    'schedule_type': 'recurring',
                    'cron_expression': '0 2 * * 0',
                    'next_run': '2024-01-21T02:00:00Z',
                    'status': 'active',
                    'created_by': 'admin',
                    'created_at': '2024-01-08T14:30:00Z'
                },
                {
                    'id': 'sched-003',
                    'name': 'One-time API Tests',
                    'description': 'Run API tests after deployment',
                    'test_suite': 'api',
                    'environment': 'staging',
                    'schedule_type': 'one-time',
                    'scheduled_time': '2024-01-16T10:00:00Z',
                    'status': 'pending',
                    'created_by': 'developer',
                    'created_at': '2024-01-15T16:45:00Z'
                }
            ],
            'total_schedules': 3,
            'active_schedules': 2,
            'pending_schedules': 1
        }
        
        return jsonify(schedules)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/environments')
def api_environments():
    """API endpoint to get test environments"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        # Mock environments
        environments = {
            'environments': [
                {
                    'id': 'env-001',
                    'name': 'Development',
                    'description': 'Development environment for feature testing',
                    'url': 'https://dev.company.com',
                    'status': 'active',
                    'type': 'development',
                    'config': {
                        'database': 'dev_db',
                        'api_version': 'v1.0',
                        'features_enabled': ['feature_a', 'feature_b']
                    },
                    'last_deployment': '2024-01-15T14:30:00Z',
                    'health_status': 'healthy'
                },
                {
                    'id': 'env-002',
                    'name': 'Staging',
                    'description': 'Staging environment for integration testing',
                    'url': 'https://staging.company.com',
                    'status': 'active',
                    'type': 'staging',
                    'config': {
                        'database': 'staging_db',
                        'api_version': 'v1.1',
                        'features_enabled': ['feature_a', 'feature_b', 'feature_c']
                    },
                    'last_deployment': '2024-01-15T16:45:00Z',
                    'health_status': 'healthy'
                },
                {
                    'id': 'env-003',
                    'name': 'Production',
                    'description': 'Production environment',
                    'url': 'https://company.com',
                    'status': 'active',
                    'type': 'production',
                    'config': {
                        'database': 'prod_db',
                        'api_version': 'v1.0',
                        'features_enabled': ['feature_a']
                    },
                    'last_deployment': '2024-01-14T10:00:00Z',
                    'health_status': 'healthy'
                },
                {
                    'id': 'env-004',
                    'name': 'Performance',
                    'description': 'Performance testing environment',
                    'url': 'https://perf.company.com',
                    'status': 'maintenance',
                    'type': 'performance',
                    'config': {
                        'database': 'perf_db',
                        'api_version': 'v1.1',
                        'features_enabled': ['feature_a', 'feature_b', 'feature_c', 'feature_d']
                    },
                    'last_deployment': '2024-01-12T09:15:00Z',
                    'health_status': 'degraded'
                }
            ],
            'total_environments': 4,
            'active_environments': 3,
            'maintenance_environments': 1
        }
        
        return jsonify(environments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-schedule', methods=['POST'])
def api_create_schedule():
    """API endpoint to create a new test schedule"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        test_suite = data.get('test_suite')
        environment = data.get('environment')
        schedule_type = data.get('schedule_type')
        cron_expression = data.get('cron_expression')
        scheduled_time = data.get('scheduled_time')
        
        if not all([name, test_suite, environment, schedule_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Mock schedule creation
        schedule_id = f"sched-{int(time.time())}"
        
        return jsonify({
            'success': True,
            'schedule_id': schedule_id,
            'message': f'Test schedule "{name}" created successfully',
            'next_run': cron_expression if schedule_type == 'recurring' else scheduled_time
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-sets')
def api_test_sets():
    """API endpoint to get test sets"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        jql = request.args.get('jql')
        
        test_sets = jira_client.get_test_sets(project_key, jql)
        return jsonify(test_sets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-sets/<test_set_key>/tests')
def api_test_set_tests(test_set_key):
    """API endpoint to get tests in a test set"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        tests = jira_client.get_test_set_tests(test_set_key)
        return jsonify(tests)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-sets/<test_set_key>/add-test', methods=['POST'])
def api_add_test_to_set(test_set_key):
    """API endpoint to add a test to a test set"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        test_key = data.get('test_key')
        
        if not test_key:
            return jsonify({'error': 'test_key is required'}), 400
        
        success = jira_client.add_test_to_set(test_set_key, test_key)
        if success:
            return jsonify({'success': True, 'message': f'Test {test_key} added to set {test_set_key}'})
        else:
            return jsonify({'error': 'Failed to add test to set'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-sets/<test_set_key>/remove-test', methods=['POST'])
def api_remove_test_from_set(test_set_key):
    """API endpoint to remove a test from a test set"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        test_key = data.get('test_key')
        
        if not test_key:
            return jsonify({'error': 'test_key is required'}), 400
        
        success = jira_client.remove_test_from_set(test_set_key, test_key)
        if success:
            return jsonify({'success': True, 'message': f'Test {test_key} removed from set {test_set_key}'})
        else:
            return jsonify({'error': 'Failed to remove test from set'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preconditions')
def api_preconditions():
    """API endpoint to get preconditions"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        jql = request.args.get('jql')
        
        preconditions = jira_client.get_preconditions(project_key, jql)
        return jsonify(preconditions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preconditions/<precondition_key>/tests')
def api_precondition_tests(precondition_key):
    """API endpoint to get tests using a precondition"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        tests = jira_client.get_precondition_tests(precondition_key)
        return jsonify(tests)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preconditions/link', methods=['POST'])
def api_link_precondition():
    """API endpoint to link a precondition to a test"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        test_key = data.get('test_key')
        precondition_key = data.get('precondition_key')
        
        if not test_key or not precondition_key:
            return jsonify({'error': 'test_key and precondition_key are required'}), 400
        
        success = jira_client.link_precondition_to_test(test_key, precondition_key)
        if success:
            return jsonify({'success': True, 'message': f'Precondition {precondition_key} linked to test {test_key}'})
        else:
            return jsonify({'error': 'Failed to link precondition to test'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preconditions/unlink', methods=['POST'])
def api_unlink_precondition():
    """API endpoint to unlink a precondition from a test"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        test_key = data.get('test_key')
        precondition_key = data.get('precondition_key')
        
        if not test_key or not precondition_key:
            return jsonify({'error': 'test_key and precondition_key are required'}), 400
        
        success = jira_client.unlink_precondition_from_test(test_key, precondition_key)
        if success:
            return jsonify({'success': True, 'message': f'Precondition {precondition_key} unlinked from test {test_key}'})
        else:
            return jsonify({'error': 'Failed to unlink precondition from test'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced-metrics')
def api_advanced_metrics():
    """API endpoint to get advanced test metrics"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        date_range = request.args.get('date_range')
        
        metrics = jira_client.get_advanced_metrics(project_key, date_range)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-analytics')
def api_test_analytics():
    """API endpoint to get test analytics"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        analysis_type = request.args.get('analysis_type', 'overview')
        
        analytics = jira_client.get_test_analytics(project_key, analysis_type)
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/custom-reports')
def api_custom_reports():
    """API endpoint to get custom reports"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        report_type = request.args.get('report_type', 'executive')
        
        reports = jira_client.get_custom_reports(report_type)
        return jsonify(reports)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflows')
def api_workflows():
    """API endpoint to get workflows"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        workflows = jira_client.get_workflows(project_key)
        return jsonify(workflows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/approval-requests')
def api_approval_requests():
    """API endpoint to get approval requests"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        status = request.args.get('status')
        
        requests = jira_client.get_approval_requests(project_key, status)
        return jsonify(requests)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/approve-request', methods=['POST'])
def api_approve_request():
    """API endpoint to approve a request"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        approver = data.get('approver')
        comments = data.get('comments')
        
        if not request_id or not approver:
            return jsonify({'error': 'request_id and approver are required'}), 400
        
        result = jira_client.approve_request(request_id, approver, comments)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reject-request', methods=['POST'])
def api_reject_request():
    """API endpoint to reject a request"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        approver = data.get('approver')
        comments = data.get('comments')
        
        if not request_id or not approver:
            return jsonify({'error': 'request_id and approver are required'}), 400
        
        result = jira_client.reject_request(request_id, approver, comments)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/issue/<issue_key>')
def api_issue_details(issue_key):
    """API endpoint to get issue details"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        issue = jira_client.get_issue_details(issue_key)
        if issue:
            return jsonify(issue)
        else:
            return jsonify({'error': 'Issue not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-steps/<execution_key>')
def api_test_steps(execution_key):
    """Get test steps for a test execution"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        # In a real implementation, this would fetch test steps from the execution
        # For demo purposes, we'll return mock data
        mock_steps = [
            {
                'id': 1,
                'test_key': 'TEST-001',
                'summary': 'Login with valid credentials',
                'status': 'TODO',
                'assignee': None,
                'duration': None,
                'comment': None
            },
            {
                'id': 2,
                'test_key': 'TEST-002',
                'summary': 'Navigate to dashboard',
                'status': 'PASS',
                'assignee': 'John Doe',
                'duration': '2m 30s',
                'comment': 'Test passed successfully'
            },
            {
                'id': 3,
                'test_key': 'TEST-003',
                'summary': 'Create new test case',
                'status': 'FAIL',
                'assignee': 'Jane Smith',
                'duration': '1m 45s',
                'comment': 'Button not found'
            }
        ]
        
        return jsonify({'test_steps': mock_steps})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-steps/<execution_key>/<int:step_id>', methods=['PUT'])
def update_test_step(execution_key, step_id):
    """Update a test step status"""
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        data = request.get_json()
        status = data.get('status')
        assignee = data.get('assignee')
        comment = data.get('comment')
        
        # In a real implementation, this would update the test step in Jira
        # For demo purposes, we'll return success
        
        return jsonify({
            'success': True,
            'message': 'Test step updated successfully',
            'step_id': step_id,
            'status': status,
            'assignee': assignee,
            'comment': comment
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execution-progress/<execution_key>')
def api_execution_progress(execution_key):
    """Get execution progress statistics"""
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        # Mock progress data - in real implementation, calculate from actual data
        progress_data = {
            'total': 10,
            'passed': 6,
            'failed': 2,
            'todo': 2,
            'blocked': 0,
            'aborted': 0,
            'percentage': 80
        }
        
        return jsonify(progress_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/coverage-report')
def api_coverage_report():
    """Get test coverage report"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        # Get requirements and test cases for coverage calculation
        requirements = jira_client.get_requirements(project_key)
        test_cases = jira_client.get_test_cases(project_key)
        
        # Calculate coverage based on linked issues
        requirements_list = requirements.get('issues', [])
        test_cases_list = test_cases.get('issues', [])
        
        # Mock coverage data - in real implementation, calculate from actual test data
        coverage_data = {
            'overall_coverage': 75,
            'test_cases_total': len(test_cases_list),
            'test_cases_executed': 75,
            'test_cases_passed': 60,
            'test_cases_failed': 15,
            'requirements_total': len(requirements_list),
            'requirements_covered': 60,
            'coverage_by_component': {
                'Authentication': 90,
                'Dashboard': 80,
                'User Management': 70,
                'Reports': 60
            }
        }
        
        return jsonify(coverage_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traceability-matrix')
def api_traceability_matrix():
    """Get requirements traceability matrix"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        # Get requirements and test cases
        requirements = jira_client.get_requirements(project_key)
        test_cases = jira_client.get_test_cases(project_key)
        
        # Build traceability matrix
        matrix = []
        requirements_list = requirements.get('issues', [])
        test_cases_list = test_cases.get('issues', [])
        
        for req in requirements_list:
            req_key = req.get('key')
            req_summary = req.get('fields', {}).get('summary', '')
            req_status = req.get('fields', {}).get('status', {}).get('name', '')
            
            # Find linked test cases (in real implementation, check actual links)
            linked_tests = []
            for test in test_cases_list:
                # Mock linking - in real implementation, check issue links
                if req_key in test.get('fields', {}).get('summary', ''):
                    linked_tests.append({
                        'key': test.get('key'),
                        'summary': test.get('fields', {}).get('summary', ''),
                        'status': test.get('fields', {}).get('status', {}).get('name', ''),
                        'execution_status': 'Not Executed'  # Would be calculated from executions
                    })
            
            matrix.append({
                'requirement_key': req_key,
                'requirement_summary': req_summary,
                'requirement_status': req_status,
                'linked_tests': linked_tests,
                'coverage_status': 'Covered' if linked_tests else 'Not Covered',
                'test_count': len(linked_tests)
            })
        
        return jsonify({
            'matrix': matrix,
            'summary': {
                'total_requirements': len(requirements_list),
                'covered_requirements': len([m for m in matrix if m['linked_tests']]),
                'total_test_cases': len(test_cases_list),
                'coverage_percentage': round((len([m for m in matrix if m['linked_tests']]) / len(requirements_list)) * 100, 2) if requirements_list else 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard-metrics')
@require_auth
def api_dashboard_metrics():
    """Get dashboard metrics with caching"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        # Check cache first
        cache_key = f"dashboard_metrics_{session['username']}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return jsonify(cached_data)
        
        # Get counts for dashboard
        test_cases = jira_client.get_test_cases()
        test_executions = jira_client.get_test_executions()
        test_plans = jira_client.get_test_plans()
        requirements = jira_client.get_requirements()
        
        # Calculate requirements coverage
        requirements_list = requirements.get('issues', [])
        test_cases_list = test_cases.get('issues', [])
        
        # Mock coverage calculation - in real implementation, check actual links
        covered_requirements = len([r for r in requirements_list if any(
            r.get('key') in test.get('fields', {}).get('summary', '') 
            for test in test_cases_list
        )])
        
        coverage_percentage = round((covered_requirements / len(requirements_list)) * 100, 2) if requirements_list else 0
        
        metrics = {
            'test_cases_count': len(test_cases_list),
            'test_executions_count': len(test_executions.get('issues', [])),
            'test_plans_count': len(test_plans.get('issues', [])),
            'requirements_count': len(requirements_list),
            'covered_requirements_count': covered_requirements,
            'coverage_percentage': coverage_percentage,
            'active_executions': len([e for e in test_executions.get('issues', []) 
                                    if e.get('fields', {}).get('status', {}).get('name') in ['In Progress', 'To Do']]),
            'recent_activity': [
                {
                    'type': 'test_execution',
                    'key': 'TEST-EXEC-001',
                    'summary': 'Login Test Execution',
                    'status': 'Completed',
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'type': 'test_case',
                    'key': 'TEST-002',
                    'summary': 'User Registration Test',
                    'status': 'Created',
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat()
                }
            ]
        }
        
        # Cache the results
        set_cached_data(cache_key, metrics)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-all-tests/<execution_key>', methods=['POST'])
def execute_all_tests(execution_key):
    """Execute all tests in an execution"""
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        # In real implementation, this would update all test steps to 'EXECUTING'
        return jsonify({
            'success': True,
            'message': 'All tests marked as executing',
            'execution_key': execution_key
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-all-tests/<execution_key>', methods=['POST'])
def reset_all_tests(execution_key):
    """Reset all tests in an execution"""
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        # In real implementation, this would reset all test steps to 'TODO'
        return jsonify({
            'success': True,
            'message': 'All tests reset to To Do',
            'execution_key': execution_key
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export/test-cases')
def export_test_cases():
    """Export test cases to Excel"""
    jira_client = get_jira_client()
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    if not PANDAS_AVAILABLE:
        return jsonify({'error': 'Excel export requires pandas. Please install: pip install pandas'}), 500
    
    project_key = request.args.get('project')
    jql = request.args.get('jql')
    
    test_cases = jira_client.get_test_cases(project_key, jql)
    
    # Convert to DataFrame
    data = []
    for issue in test_cases.get('issues', []):
        fields = issue.get('fields', {})
        data.append({
            'Key': issue.get('key'),
            'Summary': fields.get('summary', ''),
            'Status': fields.get('status', {}).get('name', ''),
            'Assignee': fields.get('assignee', {}).get('displayName', '') if fields.get('assignee') else '',
            'Reporter': fields.get('reporter', {}).get('displayName', '') if fields.get('reporter') else '',
            'Created': fields.get('created', ''),
            'Updated': fields.get('updated', ''),
            'Priority': fields.get('priority', {}).get('name', '') if fields.get('priority') else '',
            'Labels': ', '.join(fields.get('labels', [])),
            'Components': ', '.join([comp.get('name', '') for comp in fields.get('components', [])]),
            'Fix Versions': ', '.join([fv.get('name', '') for fv in fields.get('fixVersions', [])])
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Test Cases', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'test_cases_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

if __name__ == '__main__':
    # Security: Disable debug mode in production
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)