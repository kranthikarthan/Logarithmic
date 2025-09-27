#!/usr/bin/env python3
"""
Demo script for Xray Test Management Tool
Shows how to use the application programmatically
"""

import requests
import json
from datetime import datetime

class XrayDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def demo_connection(self, jira_url, username, api_token):
        """Demo: Connect to Jira"""
        print("🔌 Demo: Connecting to Jira...")
        
        # This would normally be done through the web interface
        # For demo purposes, we'll show the API endpoints
        print(f"   Jira URL: {jira_url}")
        print(f"   Username: {username}")
        print(f"   API Token: {'*' * len(api_token)}")
        print("   ✅ Connection would be established through web interface")
        return True
    
    def demo_get_projects(self):
        """Demo: Get projects"""
        print("\n📁 Demo: Getting projects...")
        try:
            response = self.session.get(f"{self.base_url}/api/projects")
            if response.status_code == 200:
                projects = response.json()
                print(f"   Found {len(projects)} projects:")
                for project in projects[:3]:  # Show first 3
                    print(f"   - {project.get('key', 'N/A')}: {project.get('name', 'N/A')}")
                if len(projects) > 3:
                    print(f"   ... and {len(projects) - 3} more")
                return projects
            else:
                print(f"   ❌ Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def demo_get_test_cases(self, project_key=None):
        """Demo: Get test cases"""
        print(f"\n🧪 Demo: Getting test cases{' for project ' + project_key if project_key else ''}...")
        try:
            params = {}
            if project_key:
                params['project'] = project_key
            
            response = self.session.get(f"{self.base_url}/api/test-cases", params=params)
            if response.status_code == 200:
                data = response.json()
                test_cases = data.get('issues', [])
                print(f"   Found {len(test_cases)} test cases:")
                for tc in test_cases[:3]:  # Show first 3
                    fields = tc.get('fields', {})
                    print(f"   - {tc.get('key', 'N/A')}: {fields.get('summary', 'N/A')}")
                if len(test_cases) > 3:
                    print(f"   ... and {len(test_cases) - 3} more")
                return test_cases
            else:
                print(f"   ❌ Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def demo_export_data(self):
        """Demo: Export test cases"""
        print("\n📊 Demo: Exporting test cases...")
        try:
            response = self.session.get(f"{self.base_url}/export/test-cases")
            if response.status_code == 200:
                print("   ✅ Export successful")
                print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                print(f"   File size: {len(response.content)} bytes")
                return True
            else:
                print(f"   ❌ Export failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Export error: {e}")
            return False
    
    def demo_custom_jql(self):
        """Demo: Custom JQL queries"""
        print("\n🔍 Demo: Custom JQL queries...")
        
        jql_examples = [
            "issuetype = 'Test' AND status = 'Open'",
            "project = 'TEST' AND assignee = currentUser()",
            "created >= -7d AND issuetype = 'Test'",
            "labels in ('regression', 'smoke') AND priority in ('High', 'Highest')"
        ]
        
        print("   Example JQL queries you can use:")
        for i, jql in enumerate(jql_examples, 1):
            print(f"   {i}. {jql}")
        
        return jql_examples
    
    def run_full_demo(self):
        """Run the complete demo"""
        print("🚀 Xray Test Management Tool - Demo")
        print("=" * 50)
        
        # Note: This demo assumes the app is running
        # In a real scenario, you'd connect through the web interface first
        
        print("\n📝 Note: This demo shows the API capabilities.")
        print("   To use the full application, start the server and use the web interface.")
        print("   Run: python run.py")
        print("   Then visit: http://localhost:5000")
        
        # Demo API endpoints
        self.demo_get_projects()
        self.demo_get_test_cases()
        self.demo_export_data()
        self.demo_custom_jql()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed!")
        print("\nNext steps:")
        print("1. Start the application: python run.py")
        print("2. Open your browser: http://localhost:5000")
        print("3. Login with your Jira credentials")
        print("4. Start managing your test data!")

def main():
    """Main demo function"""
    demo = XrayDemo()
    demo.run_full_demo()

if __name__ == "__main__":
    main()