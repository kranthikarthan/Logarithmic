#!/usr/bin/env python3
"""
End-to-End User Workflow Testing for Assertly
Tests complete user workflows from start to finish
"""

import requests
import time
import json
from datetime import datetime
import random

class UserWorkflowTester:
    """Comprehensive end-to-end user workflow testing"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.workflow_metrics = {
            'workflows_completed': 0,
            'average_workflow_time': 0,
            'success_rate': 0,
            'user_satisfaction_score': 0
        }
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        if status == 'PASS':
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: PASS - {message}")
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAIL - {message}")
    
    def make_request(self, endpoint, method='GET', data=None, timeout=10):
        """Make a single request and return metrics"""
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", timeout=timeout)
            elif method == 'POST':
                response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=timeout)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': response.status_code in [200, 201, 202],
                'status_code': response.status_code,
                'response_time': response_time,
                'endpoint': endpoint,
                'method': method,
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'status_code': 0,
                'response_time': end_time - start_time,
                'endpoint': endpoint,
                'method': method,
                'error': str(e)
            }
    
    def test_new_user_onboarding_workflow(self):
        """Test complete new user onboarding workflow"""
        try:
            print("🔍 Testing New User Onboarding Workflow...")
            
            workflow_steps = []
            start_time = time.time()
            
            # Step 1: User visits landing page
            print("  Step 1: Landing page visit...")
            step1 = self.make_request('/landing')
            workflow_steps.append(step1)
            if not step1['success']:
                self.log_test("New User Onboarding", "FAIL", "Landing page not accessible")
                return False
            
            # Step 2: User views features
            print("  Step 2: Features exploration...")
            step2 = self.make_request('/')
            workflow_steps.append(step2)
            if not step2['success']:
                self.log_test("New User Onboarding", "FAIL", "Main page not accessible")
                return False
            
            # Step 3: User checks system health
            print("  Step 3: System health check...")
            step3 = self.make_request('/health')
            workflow_steps.append(step3)
            if not step3['success']:
                self.log_test("New User Onboarding", "FAIL", "Health check failed")
                return False
            
            # Step 4: User explores integrations
            print("  Step 4: Integrations exploration...")
            step4 = self.make_request('/integrations')
            workflow_steps.append(step4)
            if not step4['success']:
                self.log_test("New User Onboarding", "FAIL", "Integrations page not accessible")
                return False
            
            # Step 5: User checks AI features
            print("  Step 5: AI features exploration...")
            step5 = self.make_request('/ai-test-generator')
            workflow_steps.append(step5)
            if not step5['success']:
                self.log_test("New User Onboarding", "FAIL", "AI features not accessible")
                return False
            
            end_time = time.time()
            workflow_duration = end_time - start_time
            
            # Calculate workflow metrics
            successful_steps = sum(1 for step in workflow_steps if step['success'])
            success_rate = (successful_steps / len(workflow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in workflow_steps) / len(workflow_steps)
            
            self.workflow_metrics['workflows_completed'] += 1
            self.workflow_metrics['average_workflow_time'] = workflow_duration
            
            if success_rate >= 90:
                self.log_test("New User Onboarding", "PASS", 
                    f"{success_rate:.1f}% success, {workflow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("New User Onboarding", "FAIL", 
                    f"Only {success_rate:.1f}% success, {workflow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("New User Onboarding", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_qa_engineer_workflow(self):
        """Test complete QA engineer workflow"""
        try:
            print("🔍 Testing QA Engineer Workflow...")
            
            workflow_steps = []
            start_time = time.time()
            
            # Step 1: QA engineer accesses dashboard
            print("  Step 1: Dashboard access...")
            step1 = self.make_request('/dashboard')
            workflow_steps.append(step1)
            if not step1['success']:
                self.log_test("QA Engineer Workflow", "FAIL", "Dashboard not accessible")
                return False
            
            # Step 2: Check system metrics
            print("  Step 2: System metrics check...")
            step2 = self.make_request('/api/dashboard-metrics')
            workflow_steps.append(step2)
            if not step2['success']:
                self.log_test("QA Engineer Workflow", "FAIL", "Dashboard metrics not accessible")
                return False
            
            # Step 3: View projects
            print("  Step 3: Projects overview...")
            step3 = self.make_request('/api/projects')
            workflow_steps.append(step3)
            if not step3['success']:
                self.log_test("QA Engineer Workflow", "FAIL", "Projects not accessible")
                return False
            
            # Step 4: Check enterprise health
            print("  Step 4: Enterprise health check...")
            step4 = self.make_request('/api/enterprise/health')
            workflow_steps.append(step4)
            if not step4['success']:
                self.log_test("QA Engineer Workflow", "FAIL", "Enterprise health check failed")
                return False
            
            # Step 5: View analytics
            print("  Step 5: Analytics review...")
            step5 = self.make_request('/api/analytics/business')
            workflow_steps.append(step5)
            if not step5['success']:
                self.log_test("QA Engineer Workflow", "FAIL", "Analytics not accessible")
                return False
            
            # Step 6: Check audit logs
            print("  Step 6: Audit logs review...")
            step6 = self.make_request('/api/enterprise/audit/logs')
            workflow_steps.append(step6)
            if not step6['success']:
                self.log_test("QA Engineer Workflow", "FAIL", "Audit logs not accessible")
                return False
            
            end_time = time.time()
            workflow_duration = end_time - start_time
            
            # Calculate workflow metrics
            successful_steps = sum(1 for step in workflow_steps if step['success'])
            success_rate = (successful_steps / len(workflow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in workflow_steps) / len(workflow_steps)
            
            if success_rate >= 80:  # Lower threshold due to authentication requirements
                self.log_test("QA Engineer Workflow", "PASS", 
                    f"{success_rate:.1f}% success, {workflow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("QA Engineer Workflow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {workflow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("QA Engineer Workflow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_test_generation_workflow(self):
        """Test complete AI test generation workflow"""
        try:
            print("🔍 Testing AI Test Generation Workflow...")
            
            workflow_steps = []
            start_time = time.time()
            
            # Step 1: Access AI test generator
            print("  Step 1: AI test generator access...")
            step1 = self.make_request('/ai-test-generator')
            workflow_steps.append(step1)
            if not step1['success']:
                self.log_test("AI Test Generation Workflow", "FAIL", "AI test generator not accessible")
                return False
            
            # Step 2: Check AI endpoint availability
            print("  Step 2: AI endpoints check...")
            step2 = self.make_request('/api/ai/generate-test-cases', method='POST', data={
                'title': 'Test User Story',
                'description': 'Test description',
                'acceptance_criteria': 'Test criteria',
                'business_value': 'High',
                'user_persona': 'User'
            })
            workflow_steps.append(step2)
            # This should return 200 with mock data or 400 due to missing API keys
            if step2['status_code'] not in [200, 400]:
                self.log_test("AI Test Generation Workflow", "FAIL", "AI endpoints not accessible")
                return False
            
            # Step 3: Test AI test case improvement
            print("  Step 3: AI test case improvement...")
            step3 = self.make_request('/api/ai/improve-test-case', method='POST', data={
                'test_case': {
                    'title': 'Test Case',
                    'description': 'Test description',
                    'steps': ['Step 1', 'Step 2'],
                    'expected_result': 'Expected result',
                    'test_type': 'functional',
                    'priority': 'high',
                    'tags': ['test'],
                    'preconditions': ['Precondition'],
                    'test_data': {},
                    'acceptance_criteria': ['Criteria']
                },
                'improvement_prompts': ['Make it better']
            })
            workflow_steps.append(step3)
            if step3['status_code'] not in [200, 400]:
                self.log_test("AI Test Generation Workflow", "FAIL", "AI improvement not accessible")
                return False
            
            # Step 4: Test BDD scenario generation
            print("  Step 4: BDD scenario generation...")
            step4 = self.make_request('/api/ai/generate-bdd-scenarios', method='POST', data={
                'title': 'Test User Story',
                'description': 'Test description',
                'acceptance_criteria': 'Test criteria',
                'business_value': 'High',
                'user_persona': 'User'
            })
            workflow_steps.append(step4)
            if step4['status_code'] not in [200, 400]:
                self.log_test("AI Test Generation Workflow", "FAIL", "BDD generation not accessible")
                return False
            
            # Step 5: Test coverage analysis
            print("  Step 5: Coverage analysis...")
            step5 = self.make_request('/api/ai/analyze-coverage', method='POST', data={
                'user_story': {
                    'title': 'Test User Story',
                    'description': 'Test description',
                    'acceptance_criteria': 'Test criteria',
                    'business_value': 'High',
                    'user_persona': 'User'
                },
                'existing_test_cases': [
                    {
                        'title': 'Test Case 1',
                        'description': 'Test description',
                        'steps': ['Step 1'],
                        'expected_result': 'Expected result',
                        'test_type': 'functional',
                        'priority': 'high',
                        'tags': ['test'],
                        'preconditions': ['Precondition'],
                        'test_data': {},
                        'acceptance_criteria': ['Criteria']
                    }
                ]
            })
            workflow_steps.append(step5)
            if step5['status_code'] not in [200, 400]:
                self.log_test("AI Test Generation Workflow", "FAIL", "Coverage analysis not accessible")
                return False
            
            end_time = time.time()
            workflow_duration = end_time - start_time
            
            # Calculate workflow metrics
            successful_steps = sum(1 for step in workflow_steps if step['success'] or step['status_code'] == 400)
            success_rate = (successful_steps / len(workflow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in workflow_steps) / len(workflow_steps)
            
            if success_rate >= 90:
                self.log_test("AI Test Generation Workflow", "PASS", 
                    f"{success_rate:.1f}% success, {workflow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("AI Test Generation Workflow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {workflow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("AI Test Generation Workflow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_integration_setup_workflow(self):
        """Test complete integration setup workflow"""
        try:
            print("🔍 Testing Integration Setup Workflow...")
            
            workflow_steps = []
            start_time = time.time()
            
            # Step 1: Access integrations page
            print("  Step 1: Integrations page access...")
            step1 = self.make_request('/integrations')
            workflow_steps.append(step1)
            if not step1['success']:
                self.log_test("Integration Setup Workflow", "FAIL", "Integrations page not accessible")
                return False
            
            # Step 2: Check VS Code integration
            print("  Step 2: VS Code integration...")
            step2 = self.make_request('/api/integrations/vscode/install')
            workflow_steps.append(step2)
            if not step2['success']:
                self.log_test("Integration Setup Workflow", "FAIL", "VS Code integration not accessible")
                return False
            
            # Step 3: Check GitHub Actions integration
            print("  Step 3: GitHub Actions integration...")
            step3 = self.make_request('/api/integrations/github-actions/template')
            workflow_steps.append(step3)
            if not step3['success']:
                self.log_test("Integration Setup Workflow", "FAIL", "GitHub Actions integration not accessible")
                return False
            
            # Step 4: Check Azure DevOps integration
            print("  Step 4: Azure DevOps integration...")
            step4 = self.make_request('/api/integrations/azure-devops/template')
            workflow_steps.append(step4)
            if not step4['success']:
                self.log_test("Integration Setup Workflow", "FAIL", "Azure DevOps integration not accessible")
                return False
            
            # Step 5: Check service discovery
            print("  Step 5: Service discovery...")
            step5 = self.make_request('/api/services')
            workflow_steps.append(step5)
            if not step5['success']:
                self.log_test("Integration Setup Workflow", "FAIL", "Service discovery not accessible")
                return False
            
            end_time = time.time()
            workflow_duration = end_time - start_time
            
            # Calculate workflow metrics
            successful_steps = sum(1 for step in workflow_steps if step['success'])
            success_rate = (successful_steps / len(workflow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in workflow_steps) / len(workflow_steps)
            
            if success_rate >= 90:
                self.log_test("Integration Setup Workflow", "PASS", 
                    f"{success_rate:.1f}% success, {workflow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Integration Setup Workflow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {workflow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Integration Setup Workflow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_enterprise_admin_workflow(self):
        """Test complete enterprise admin workflow"""
        try:
            print("🔍 Testing Enterprise Admin Workflow...")
            
            workflow_steps = []
            start_time = time.time()
            
            # Step 1: Access enterprise settings
            print("  Step 1: Enterprise settings access...")
            step1 = self.make_request('/enterprise-settings')
            workflow_steps.append(step1)
            if not step1['success']:
                self.log_test("Enterprise Admin Workflow", "FAIL", "Enterprise settings not accessible")
                return False
            
            # Step 2: Check enterprise health
            print("  Step 2: Enterprise health check...")
            step2 = self.make_request('/api/enterprise/health')
            workflow_steps.append(step2)
            if not step2['success']:
                self.log_test("Enterprise Admin Workflow", "FAIL", "Enterprise health check failed")
                return False
            
            # Step 3: View audit logs
            print("  Step 3: Audit logs review...")
            step3 = self.make_request('/api/enterprise/audit/logs')
            workflow_steps.append(step3)
            if not step3['success']:
                self.log_test("Enterprise Admin Workflow", "FAIL", "Audit logs not accessible")
                return False
            
            # Step 4: Generate compliance report
            print("  Step 4: Compliance report generation...")
            step4 = self.make_request('/api/enterprise/compliance/report', method='POST', data={'report_type': 'audit_summary'})
            workflow_steps.append(step4)
            if not step4['success']:
                self.log_test("Enterprise Admin Workflow", "FAIL", "Compliance report generation failed")
                return False
            
            # Step 5: Configure enterprise AI
            print("  Step 5: Enterprise AI configuration...")
            step5 = self.make_request('/api/enterprise/ai/configure', method='POST', data={
                'local_ai_url': 'http://test-ai.company.com:8080/api',
                'local_ai_model': 'enterprise-model'
            })
            workflow_steps.append(step5)
            if not step5['success']:
                self.log_test("Enterprise Admin Workflow", "FAIL", "Enterprise AI configuration failed")
                return False
            
            end_time = time.time()
            workflow_duration = end_time - start_time
            
            # Calculate workflow metrics
            successful_steps = sum(1 for step in workflow_steps if step['success'])
            success_rate = (successful_steps / len(workflow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in workflow_steps) / len(workflow_steps)
            
            if success_rate >= 80:
                self.log_test("Enterprise Admin Workflow", "PASS", 
                    f"{success_rate:.1f}% success, {workflow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Enterprise Admin Workflow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {workflow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Enterprise Admin Workflow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_monitoring_workflow(self):
        """Test complete monitoring and analytics workflow"""
        try:
            print("🔍 Testing Monitoring Workflow...")
            
            workflow_steps = []
            start_time = time.time()
            
            # Step 1: Access monitoring dashboard
            print("  Step 1: Monitoring dashboard access...")
            step1 = self.make_request('/monitoring')
            workflow_steps.append(step1)
            if not step1['success']:
                self.log_test("Monitoring Workflow", "FAIL", "Monitoring dashboard not accessible")
                return False
            
            # Step 2: Check system metrics
            print("  Step 2: System metrics...")
            step2 = self.make_request('/api/monitoring/system-metrics')
            workflow_steps.append(step2)
            if not step2['success']:
                self.log_test("Monitoring Workflow", "FAIL", "System metrics not accessible")
                return False
            
            # Step 3: Check performance summary
            print("  Step 3: Performance summary...")
            step3 = self.make_request('/api/monitoring/performance-summary')
            workflow_steps.append(step3)
            if not step3['success']:
                self.log_test("Monitoring Workflow", "FAIL", "Performance summary not accessible")
                return False
            
            # Step 4: Check monitoring health
            print("  Step 4: Monitoring health...")
            step4 = self.make_request('/api/monitoring/health')
            workflow_steps.append(step4)
            if not step4['success']:
                self.log_test("Monitoring Workflow", "FAIL", "Monitoring health check failed")
                return False
            
            # Step 5: Check cache statistics
            print("  Step 5: Cache statistics...")
            step5 = self.make_request('/api/cache/stats')
            workflow_steps.append(step5)
            if not step5['success']:
                self.log_test("Monitoring Workflow", "FAIL", "Cache statistics not accessible")
                return False
            
            end_time = time.time()
            workflow_duration = end_time - start_time
            
            # Calculate workflow metrics
            successful_steps = sum(1 for step in workflow_steps if step['success'])
            success_rate = (successful_steps / len(workflow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in workflow_steps) / len(workflow_steps)
            
            if success_rate >= 80:
                self.log_test("Monitoring Workflow", "PASS", 
                    f"{success_rate:.1f}% success, {workflow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Monitoring Workflow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {workflow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Monitoring Workflow", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_user_workflow_tests(self):
        """Run all user workflow tests"""
        print("🔍 Starting End-to-End User Workflow Testing...")
        print("=" * 70)
        
        # Run all user workflow tests
        self.test_new_user_onboarding_workflow()
        self.test_qa_engineer_workflow()
        self.test_ai_test_generation_workflow()
        self.test_integration_setup_workflow()
        self.test_enterprise_admin_workflow()
        self.test_monitoring_workflow()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 User Workflow Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # Print workflow metrics
        print(f"\n📈 Workflow Metrics:")
        print(f"  - Workflows Completed: {self.workflow_metrics['workflows_completed']}")
        print(f"  - Average Workflow Time: {self.workflow_metrics['average_workflow_time']:.2f}s")
        print(f"  - Success Rate: {self.workflow_metrics['success_rate']:.1f}%")
        print(f"  - User Satisfaction Score: {self.workflow_metrics['user_satisfaction_score']:.1f}%")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = UserWorkflowTester()
    success = tester.run_all_user_workflow_tests()
    exit(0 if success else 1)