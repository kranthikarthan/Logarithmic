#!/usr/bin/env python3
"""
Jira Stub Server for Testing
Simulates Jira API responses for testing Assertly integration
"""

from flask import Flask, jsonify, request
import json
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Mock Jira data
MOCK_PROJECTS = [
    {"id": "10000", "key": "TEST", "name": "Test Project", "projectTypeKey": "software"},
    {"id": "10001", "key": "DEMO", "name": "Demo Project", "projectTypeKey": "business"},
    {"id": "10002", "key": "QA", "name": "QA Testing", "projectTypeKey": "software"}
]

MOCK_ISSUES = [
    {
        "id": "10001",
        "key": "TEST-1",
        "summary": "Test Case: User Login",
        "description": "Verify user can login with valid credentials",
        "status": {"name": "To Do", "id": "1"},
        "issuetype": {"name": "Test", "id": "10001"},
        "project": {"key": "TEST", "name": "Test Project"},
        "created": "2024-01-01T10:00:00.000+0000",
        "updated": "2024-01-01T10:00:00.000+0000"
    },
    {
        "id": "10002",
        "key": "TEST-2",
        "summary": "Test Case: User Registration",
        "description": "Verify user can register with valid information",
        "status": {"name": "In Progress", "id": "3"},
        "issuetype": {"name": "Test", "id": "10001"},
        "project": {"key": "TEST", "name": "Test Project"},
        "created": "2024-01-01T11:00:00.000+0000",
        "updated": "2024-01-01T11:00:00.000+0000"
    }
]

@app.route('/rest/api/3/project', methods=['GET'])
def get_projects():
    """Get all projects"""
    return jsonify(MOCK_PROJECTS)

@app.route('/rest/api/3/project/<project_key>', methods=['GET'])
def get_project(project_key):
    """Get specific project"""
    project = next((p for p in MOCK_PROJECTS if p['key'] == project_key), None)
    if project:
        return jsonify(project)
    return jsonify({"error": "Project not found"}), 404

@app.route('/rest/api/3/search', methods=['GET'])
def search_issues():
    """Search issues with JQL"""
    jql = request.args.get('jql', '')
    start_at = int(request.args.get('startAt', 0))
    max_results = int(request.args.get('maxResults', 50))
    
    # Filter issues based on JQL
    filtered_issues = MOCK_ISSUES.copy()
    
    if 'project = TEST' in jql:
        filtered_issues = [i for i in filtered_issues if i['project']['key'] == 'TEST']
    
    if 'issuetype = Test' in jql:
        filtered_issues = [i for i in filtered_issues if i['issuetype']['name'] == 'Test']
    
    # Pagination
    end_at = min(start_at + max_results, len(filtered_issues))
    issues = filtered_issues[start_at:end_at]
    
    return jsonify({
        "expand": "schema,names",
        "startAt": start_at,
        "maxResults": max_results,
        "total": len(filtered_issues),
        "issues": issues
    })

@app.route('/rest/api/3/issue/<issue_key>', methods=['GET'])
def get_issue(issue_key):
    """Get specific issue"""
    issue = next((i for i in MOCK_ISSUES if i['key'] == issue_key), None)
    if issue:
        return jsonify(issue)
    return jsonify({"error": "Issue not found"}), 404

@app.route('/rest/api/3/issue', methods=['POST'])
def create_issue():
    """Create new issue"""
    data = request.get_json()
    
    new_issue = {
        "id": str(random.randint(10000, 99999)),
        "key": f"TEST-{random.randint(100, 999)}",
        "summary": data.get('fields', {}).get('summary', 'New Test Case'),
        "description": data.get('fields', {}).get('description', ''),
        "status": {"name": "To Do", "id": "1"},
        "issuetype": {"name": "Test", "id": "10001"},
        "project": {"key": "TEST", "name": "Test Project"},
        "created": datetime.now().isoformat() + "+0000",
        "updated": datetime.now().isoformat() + "+0000"
    }
    
    MOCK_ISSUES.append(new_issue)
    return jsonify(new_issue), 201

@app.route('/rest/api/3/issue/<issue_key>/links', methods=['GET'])
def get_issue_links(issue_key):
    """Get issue links"""
    return jsonify({
        "issueLinks": [
            {
                "id": "10001",
                "type": {"name": "Tests", "inward": "is tested by", "outward": "tests"},
                "inwardIssue": {"key": issue_key, "summary": "Test Case"},
                "outwardIssue": {"key": "REQ-1", "summary": "Requirement 1"}
            }
        ]
    })

@app.route('/rest/api/3/issueLink', methods=['POST'])
def create_issue_link():
    """Create issue link"""
    data = request.get_json()
    return jsonify({
        "id": str(random.randint(10000, 99999)),
        "type": data.get('type', {}),
        "inwardIssue": data.get('inwardIssue', {}),
        "outwardIssue": data.get('outwardIssue', {})
    }), 201

@app.route('/rest/api/3/myself', methods=['GET'])
def get_myself():
    """Get current user info"""
    return jsonify({
        "accountId": "test-user-123",
        "displayName": "Test User",
        "emailAddress": "test@example.com",
        "active": True
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == '__main__':
    print("🚀 Starting Jira Stub Server...")
    print("📊 Available endpoints:")
    print("  GET  /rest/api/3/project - List projects")
    print("  GET  /rest/api/3/project/{key} - Get project")
    print("  GET  /rest/api/3/search - Search issues")
    print("  GET  /rest/api/3/issue/{key} - Get issue")
    print("  POST /rest/api/3/issue - Create issue")
    print("  GET  /rest/api/3/issue/{key}/links - Get issue links")
    print("  POST /rest/api/3/issueLink - Create issue link")
    print("  GET  /rest/api/3/myself - Get user info")
    print("  GET  /health - Health check")
    print("\n🌐 Server running on http://localhost:8080")
    
    app.run(host='0.0.0.0', port=8080, debug=True)