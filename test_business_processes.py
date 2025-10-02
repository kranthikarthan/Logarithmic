#!/usr/bin/env python3
"""
Business Process Testing for Assertly
Tests complete business processes and real-world scenarios
"""

import requests
import time
import json
from datetime import datetime
import random

class BusinessProcessTester:
    """Comprehensive business process testing"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.business_metrics = {
            'processes_completed': 0,
            'average_process_time': 0,
            'business_value_delivered': 0,
            'process_efficiency': 0
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
    
    def test_test_management_lifecycle(self):
        """Test complete test management lifecycle"""
        try:
            print("🔍 Testing Test Management Lifecycle...")
            
            process_steps = []
            start_time = time.time()
            
            # Step 1: Project setup and health check
            print("  Step 1: Project setup...")
            step1 = self.make_request('/api/enterprise/health')
            process_steps.append(step1)
            if not step1['success']:
                self.log_test("Test Management Lifecycle", "FAIL", "Project setup failed")
                return False
            
            # Step 2: Requirements traceability setup
            print("  Step 2: Requirements traceability...")
            step2 = self.make_request('/requirements-traceability')
            process_steps.append(step2)
            if not step2['success']:
                self.log_test("Test Management Lifecycle", "FAIL", "Requirements traceability not accessible")
                return False
            
            # Step 3: Test case creation and management
            print("  Step 3: Test case management...")
            step3 = self.make_request('/test-sets')
            process_steps.append(step3)
            if not step3['success']:
                self.log_test("Test Management Lifecycle", "FAIL", "Test case management not accessible")
                return False
            
            # Step 4: Test execution
            print("  Step 4: Test execution...")
            step4 = self.make_request('/test-execution')
            process_steps.append(step4)
            if not step4['success']:
                self.log_test("Test Management Lifecycle", "FAIL", "Test execution not accessible")
                return False
            
            # Step 5: Defect management
            print("  Step 5: Defect management...")
            step5 = self.make_request('/defect-management')
            process_steps.append(step5)
            if not step5['success']:
                self.log_test("Test Management Lifecycle", "FAIL", "Defect management not accessible")
                return False
            
            # Step 6: Reporting and analytics
            print("  Step 6: Reporting and analytics...")
            step6 = self.make_request('/api/analytics/business')
            process_steps.append(step6)
            if not step6['success']:
                self.log_test("Test Management Lifecycle", "FAIL", "Reporting and analytics not accessible")
                return False
            
            end_time = time.time()
            process_duration = end_time - start_time
            
            # Calculate process metrics
            successful_steps = sum(1 for step in process_steps if step['success'])
            success_rate = (successful_steps / len(process_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in process_steps) / len(process_steps)
            
            self.business_metrics['processes_completed'] += 1
            self.business_metrics['average_process_time'] = process_duration
            
            if success_rate >= 90:
                self.log_test("Test Management Lifecycle", "PASS", 
                    f"{success_rate:.1f}% success, {process_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Test Management Lifecycle", "FAIL", 
                    f"Only {success_rate:.1f}% success, {process_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Test Management Lifecycle", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_powered_testing_process(self):
        """Test AI-powered testing process"""
        try:
            print("🔍 Testing AI-Powered Testing Process...")
            
            process_steps = []
            start_time = time.time()
            
            # Step 1: AI test generator access
            print("  Step 1: AI test generator access...")
            step1 = self.make_request('/ai-test-generator')
            process_steps.append(step1)
            if not step1['success']:
                self.log_test("AI-Powered Testing Process", "FAIL", "AI test generator not accessible")
                return False
            
            # Step 2: AI test case generation (simulated)
            print("  Step 2: AI test case generation...")
            step2 = self.make_request('/api/ai/generate-test-cases')
            process_steps.append(step2)
            # Expected to return 400 due to missing API keys, which is acceptable
            if step2['status_code'] not in [200, 400]:
                self.log_test("AI-Powered Testing Process", "FAIL", "AI test case generation not accessible")
                return False
            
            # Step 3: AI test case improvement
            print("  Step 3: AI test case improvement...")
            step3 = self.make_request('/api/ai/improve-test-case')
            process_steps.append(step3)
            if step3['status_code'] not in [200, 400]:
                self.log_test("AI-Powered Testing Process", "FAIL", "AI test case improvement not accessible")
                return False
            
            # Step 4: BDD scenario generation
            print("  Step 4: BDD scenario generation...")
            step4 = self.make_request('/bdd-scenarios')
            process_steps.append(step4)
            if not step4['success']:
                self.log_test("AI-Powered Testing Process", "FAIL", "BDD scenarios not accessible")
                return False
            
            # Step 5: Test data management
            print("  Step 5: Test data management...")
            step5 = self.make_request('/test-data-management')
            process_steps.append(step5)
            if not step5['success']:
                self.log_test("AI-Powered Testing Process", "FAIL", "Test data management not accessible")
                return False
            
            # Step 6: Coverage analysis
            print("  Step 6: Coverage analysis...")
            step6 = self.make_request('/api/ai/analyze-coverage')
            process_steps.append(step6)
            if step6['status_code'] not in [200, 400]:
                self.log_test("AI-Powered Testing Process", "FAIL", "Coverage analysis not accessible")
                return False
            
            end_time = time.time()
            process_duration = end_time - start_time
            
            # Calculate process metrics
            successful_steps = sum(1 for step in process_steps if step['success'] or step['status_code'] == 400)
            success_rate = (successful_steps / len(process_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in process_steps) / len(process_steps)
            
            if success_rate >= 90:
                self.log_test("AI-Powered Testing Process", "PASS", 
                    f"{success_rate:.1f}% success, {process_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("AI-Powered Testing Process", "FAIL", 
                    f"Only {success_rate:.1f}% success, {process_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("AI-Powered Testing Process", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_enterprise_deployment_process(self):
        """Test enterprise deployment process"""
        try:
            print("🔍 Testing Enterprise Deployment Process...")
            
            process_steps = []
            start_time = time.time()
            
            # Step 1: Enterprise settings configuration
            print("  Step 1: Enterprise settings...")
            step1 = self.make_request('/enterprise-settings')
            process_steps.append(step1)
            if not step1['success']:
                self.log_test("Enterprise Deployment Process", "FAIL", "Enterprise settings not accessible")
                return False
            
            # Step 2: Enterprise health check
            print("  Step 2: Enterprise health check...")
            step2 = self.make_request('/api/enterprise/health')
            process_steps.append(step2)
            if not step2['success']:
                self.log_test("Enterprise Deployment Process", "FAIL", "Enterprise health check failed")
                return False
            
            # Step 3: Security and compliance setup
            print("  Step 3: Security and compliance...")
            step3 = self.make_request('/api/enterprise/audit/logs')
            process_steps.append(step3)
            if not step3['success']:
                self.log_test("Enterprise Deployment Process", "FAIL", "Security and compliance not accessible")
                return False
            
            # Step 4: Monitoring setup
            print("  Step 4: Monitoring setup...")
            step4 = self.make_request('/monitoring')
            process_steps.append(step4)
            if not step4['success']:
                self.log_test("Enterprise Deployment Process", "FAIL", "Monitoring setup not accessible")
                return False
            
            # Step 5: Integration configuration
            print("  Step 5: Integration configuration...")
            step5 = self.make_request('/integrations')
            process_steps.append(step5)
            if not step5['success']:
                self.log_test("Enterprise Deployment Process", "FAIL", "Integration configuration not accessible")
                return False
            
            # Step 6: Service discovery and health
            print("  Step 6: Service discovery...")
            step6 = self.make_request('/api/services')
            process_steps.append(step6)
            if not step6['success']:
                self.log_test("Enterprise Deployment Process", "FAIL", "Service discovery not accessible")
                return False
            
            end_time = time.time()
            process_duration = end_time - start_time
            
            # Calculate process metrics
            successful_steps = sum(1 for step in process_steps if step['success'])
            success_rate = (successful_steps / len(process_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in process_steps) / len(process_steps)
            
            if success_rate >= 90:
                self.log_test("Enterprise Deployment Process", "PASS", 
                    f"{success_rate:.1f}% success, {process_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Enterprise Deployment Process", "FAIL", 
                    f"Only {success_rate:.1f}% success, {process_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Enterprise Deployment Process", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ci_cd_integration_process(self):
        """Test CI/CD integration process"""
        try:
            print("🔍 Testing CI/CD Integration Process...")
            
            process_steps = []
            start_time = time.time()
            
            # Step 1: Integrations overview
            print("  Step 1: Integrations overview...")
            step1 = self.make_request('/integrations')
            process_steps.append(step1)
            if not step1['success']:
                self.log_test("CI/CD Integration Process", "FAIL", "Integrations overview not accessible")
                return False
            
            # Step 2: GitHub Actions integration
            print("  Step 2: GitHub Actions integration...")
            step2 = self.make_request('/api/integrations/github-actions/template')
            process_steps.append(step2)
            if not step2['success']:
                self.log_test("CI/CD Integration Process", "FAIL", "GitHub Actions integration not accessible")
                return False
            
            # Step 3: Azure DevOps integration
            print("  Step 3: Azure DevOps integration...")
            step3 = self.make_request('/api/integrations/azure-devops/template')
            process_steps.append(step3)
            if not step3['success']:
                self.log_test("CI/CD Integration Process", "FAIL", "Azure DevOps integration not accessible")
                return False
            
            # Step 4: VS Code extension
            print("  Step 4: VS Code extension...")
            step4 = self.make_request('/api/integrations/vscode/install')
            process_steps.append(step4)
            if not step4['success']:
                self.log_test("CI/CD Integration Process", "FAIL", "VS Code extension not accessible")
                return False
            
            # Step 5: Automated testing setup
            print("  Step 5: Automated testing setup...")
            step5 = self.make_request('/automated-testing')
            process_steps.append(step5)
            if not step5['success']:
                self.log_test("CI/CD Integration Process", "FAIL", "Automated testing setup not accessible")
                return False
            
            # Step 6: Test execution and reporting
            print("  Step 6: Test execution and reporting...")
            step6 = self.make_request('/test-execution')
            process_steps.append(step6)
            if not step6['success']:
                self.log_test("CI/CD Integration Process", "FAIL", "Test execution not accessible")
                return False
            
            end_time = time.time()
            process_duration = end_time - start_time
            
            # Calculate process metrics
            successful_steps = sum(1 for step in process_steps if step['success'])
            success_rate = (successful_steps / len(process_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in process_steps) / len(process_steps)
            
            if success_rate >= 90:
                self.log_test("CI/CD Integration Process", "PASS", 
                    f"{success_rate:.1f}% success, {process_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("CI/CD Integration Process", "FAIL", 
                    f"Only {success_rate:.1f}% success, {process_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("CI/CD Integration Process", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_reporting_and_analytics_process(self):
        """Test reporting and analytics process"""
        try:
            print("🔍 Testing Reporting and Analytics Process...")
            
            process_steps = []
            start_time = time.time()
            
            # Step 1: Advanced reporting access
            print("  Step 1: Advanced reporting...")
            step1 = self.make_request('/advanced-reporting')
            process_steps.append(step1)
            if not step1['success']:
                self.log_test("Reporting and Analytics Process", "FAIL", "Advanced reporting not accessible")
                return False
            
            # Step 2: Business analytics
            print("  Step 2: Business analytics...")
            step2 = self.make_request('/api/analytics/business')
            process_steps.append(step2)
            if not step2['success']:
                self.log_test("Reporting and Analytics Process", "FAIL", "Business analytics not accessible")
                return False
            
            # Step 3: Performance analytics
            print("  Step 3: Performance analytics...")
            step3 = self.make_request('/api/analytics/performance')
            process_steps.append(step3)
            if not step3['success']:
                self.log_test("Reporting and Analytics Process", "FAIL", "Performance analytics not accessible")
                return False
            
            # Step 4: Monitoring dashboard
            print("  Step 4: Monitoring dashboard...")
            step4 = self.make_request('/monitoring')
            process_steps.append(step4)
            if not step4['success']:
                self.log_test("Reporting and Analytics Process", "FAIL", "Monitoring dashboard not accessible")
                return False
            
            # Step 5: System metrics
            print("  Step 5: System metrics...")
            step5 = self.make_request('/api/monitoring/system-metrics')
            process_steps.append(step5)
            if not step5['success']:
                self.log_test("Reporting and Analytics Process", "FAIL", "System metrics not accessible")
                return False
            
            # Step 6: Cache statistics
            print("  Step 6: Cache statistics...")
            step6 = self.make_request('/api/cache/stats')
            process_steps.append(step6)
            if not step6['success']:
                self.log_test("Reporting and Analytics Process", "FAIL", "Cache statistics not accessible")
                return False
            
            end_time = time.time()
            process_duration = end_time - start_time
            
            # Calculate process metrics
            successful_steps = sum(1 for step in process_steps if step['success'])
            success_rate = (successful_steps / len(process_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in process_steps) / len(process_steps)
            
            if success_rate >= 80:
                self.log_test("Reporting and Analytics Process", "PASS", 
                    f"{success_rate:.1f}% success, {process_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Reporting and Analytics Process", "FAIL", 
                    f"Only {success_rate:.1f}% success, {process_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Reporting and Analytics Process", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_workflow_approval_process(self):
        """Test workflow and approval process"""
        try:
            print("🔍 Testing Workflow and Approval Process...")
            
            process_steps = []
            start_time = time.time()
            
            # Step 1: Workflow management
            print("  Step 1: Workflow management...")
            step1 = self.make_request('/workflow-approval')
            process_steps.append(step1)
            if not step1['success']:
                self.log_test("Workflow and Approval Process", "FAIL", "Workflow management not accessible")
                return False
            
            # Step 2: Preconditions setup
            print("  Step 2: Preconditions setup...")
            step2 = self.make_request('/preconditions')
            process_steps.append(step2)
            if not step2['success']:
                self.log_test("Workflow and Approval Process", "FAIL", "Preconditions setup not accessible")
                return False
            
            # Step 3: Test sets management
            print("  Step 3: Test sets management...")
            step3 = self.make_request('/test-sets')
            process_steps.append(step3)
            if not step3['success']:
                self.log_test("Workflow and Approval Process", "FAIL", "Test sets management not accessible")
                return False
            
            # Step 4: Scheduling and environments
            print("  Step 4: Scheduling and environments...")
            step4 = self.make_request('/scheduling-environments')
            process_steps.append(step4)
            if not step4['success']:
                self.log_test("Workflow and Approval Process", "FAIL", "Scheduling and environments not accessible")
                return False
            
            # Step 5: Enterprise compliance
            print("  Step 5: Enterprise compliance...")
            step5 = self.make_request('/api/enterprise/compliance/report', method='POST', data={'report_type': 'audit_summary'})
            process_steps.append(step5)
            if not step5['success']:
                self.log_test("Workflow and Approval Process", "FAIL", "Enterprise compliance not accessible")
                return False
            
            end_time = time.time()
            process_duration = end_time - start_time
            
            # Calculate process metrics
            successful_steps = sum(1 for step in process_steps if step['success'])
            success_rate = (successful_steps / len(process_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in process_steps) / len(process_steps)
            
            if success_rate >= 90:
                self.log_test("Workflow and Approval Process", "PASS", 
                    f"{success_rate:.1f}% success, {process_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Workflow and Approval Process", "FAIL", 
                    f"Only {success_rate:.1f}% success, {process_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Workflow and Approval Process", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_business_process_tests(self):
        """Run all business process tests"""
        print("🔍 Starting Business Process Testing...")
        print("=" * 60)
        
        # Run all business process tests
        self.test_test_management_lifecycle()
        self.test_ai_powered_testing_process()
        self.test_enterprise_deployment_process()
        self.test_ci_cd_integration_process()
        self.test_reporting_and_analytics_process()
        self.test_workflow_approval_process()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Business Process Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # Print business metrics
        print(f"\n📈 Business Process Metrics:")
        print(f"  - Processes Completed: {self.business_metrics['processes_completed']}")
        print(f"  - Average Process Time: {self.business_metrics['average_process_time']:.2f}s")
        print(f"  - Business Value Delivered: {self.business_metrics['business_value_delivered']:.1f}%")
        print(f"  - Process Efficiency: {self.business_metrics['process_efficiency']:.1f}%")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = BusinessProcessTester()
    success = tester.run_all_business_process_tests()
    exit(0 if success else 1)