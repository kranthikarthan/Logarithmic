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
import pandas as pd
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

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

# Global client instance
jira_client = None

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
        
        global jira_client
        jira_client = JiraXrayClient(jira_url, username, api_token)
        
        # Test connection
        success, user_info = jira_client.test_connection()
        if success:
            session['jira_connected'] = True
            session['jira_url'] = jira_url
            session['username'] = username
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
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    projects = jira_client.get_projects()
    return jsonify(projects)

@app.route('/api/test-cases')
def api_test_cases():
    """API endpoint to get test cases"""
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    project_key = request.args.get('project')
    jql = request.args.get('jql')
    
    test_cases = jira_client.get_test_cases(project_key, jql)
    return jsonify(test_cases)

@app.route('/api/test-executions')
def api_test_executions():
    """API endpoint to get test executions"""
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    project_key = request.args.get('project')
    jql = request.args.get('jql')
    
    test_executions = jira_client.get_test_executions(project_key, jql)
    return jsonify(test_executions)

@app.route('/api/test-plans')
def api_test_plans():
    """API endpoint to get test plans"""
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    project_key = request.args.get('project')
    jql = request.args.get('jql')
    
    test_plans = jira_client.get_test_plans(project_key, jql)
    return jsonify(test_plans)

@app.route('/api/issue/<issue_key>')
def api_issue_details(issue_key):
    """API endpoint to get issue details"""
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    issue = jira_client.get_issue_details(issue_key)
    if issue:
        return jsonify(issue)
    else:
        return jsonify({'error': 'Issue not found'}), 404

@app.route('/api/test-steps/<execution_key>')
def api_test_steps(execution_key):
    """Get test steps for a test execution"""
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
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        project_key = request.args.get('project')
        
        # Mock coverage data - in real implementation, calculate from actual test data
        coverage_data = {
            'overall_coverage': 75,
            'test_cases_total': 100,
            'test_cases_executed': 75,
            'test_cases_passed': 60,
            'test_cases_failed': 15,
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

@app.route('/api/dashboard-metrics')
def api_dashboard_metrics():
    """Get dashboard metrics"""
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
    try:
        # Get counts for dashboard
        test_cases = jira_client.get_test_cases()
        test_executions = jira_client.get_test_executions()
        test_plans = jira_client.get_test_plans()
        
        metrics = {
            'test_cases_count': len(test_cases.get('issues', [])),
            'test_executions_count': len(test_executions.get('issues', [])),
            'test_plans_count': len(test_plans.get('issues', [])),
            'coverage_percentage': 75,  # Mock data
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
    if not jira_client:
        return jsonify({'error': 'Not connected to Jira'}), 401
    
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
    app.run(debug=True, host='0.0.0.0', port=5000)