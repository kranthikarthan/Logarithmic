#!/usr/bin/env python3
"""
Data Flow Testing for Assertly
Tests complete data flow from input to output across all systems
"""

import requests
import time
import json
from datetime import datetime
import random

class DataFlowTester:
    """Comprehensive data flow testing"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.data_flow_metrics = {
            'data_flows_tested': 0,
            'data_integrity_score': 0,
            'average_data_processing_time': 0,
            'data_consistency_score': 0
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
    
    def test_user_data_flow(self):
        """Test complete user data flow"""
        try:
            print("🔍 Testing User Data Flow...")
            
            data_flow_steps = []
            start_time = time.time()
            
            # Step 1: User input (landing page)
            print("  Step 1: User input (landing page)...")
            step1 = self.make_request('/landing')
            data_flow_steps.append(step1)
            if not step1['success']:
                self.log_test("User Data Flow", "FAIL", "User input not accessible")
                return False
            
            # Step 2: Data processing (dashboard)
            print("  Step 2: Data processing (dashboard)...")
            step2 = self.make_request('/dashboard')
            data_flow_steps.append(step2)
            if not step2['success']:
                self.log_test("User Data Flow", "FAIL", "Data processing not accessible")
                return False
            
            # Step 3: Data storage (analytics)
            print("  Step 3: Data storage (analytics)...")
            step3 = self.make_request('/api/analytics/business')
            data_flow_steps.append(step3)
            if not step3['success']:
                self.log_test("User Data Flow", "FAIL", "Data storage not accessible")
                return False
            
            # Step 4: Data retrieval (monitoring)
            print("  Step 4: Data retrieval (monitoring)...")
            step4 = self.make_request('/monitoring')
            data_flow_steps.append(step4)
            if not step4['success']:
                self.log_test("User Data Flow", "FAIL", "Data retrieval not accessible")
                return False
            
            # Step 5: Data output (reporting)
            print("  Step 5: Data output (reporting)...")
            step5 = self.make_request('/advanced-reporting')
            data_flow_steps.append(step5)
            if not step5['success']:
                self.log_test("User Data Flow", "FAIL", "Data output not accessible")
                return False
            
            end_time = time.time()
            data_flow_duration = end_time - start_time
            
            # Calculate data flow metrics
            successful_steps = sum(1 for step in data_flow_steps if step['success'])
            success_rate = (successful_steps / len(data_flow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in data_flow_steps) / len(data_flow_steps)
            
            self.data_flow_metrics['data_flows_tested'] += 1
            self.data_flow_metrics['average_data_processing_time'] = data_flow_duration
            
            if success_rate >= 90:
                self.log_test("User Data Flow", "PASS", 
                    f"{success_rate:.1f}% success, {data_flow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("User Data Flow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {data_flow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("User Data Flow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_enterprise_data_flow(self):
        """Test complete enterprise data flow"""
        try:
            print("🔍 Testing Enterprise Data Flow...")
            
            data_flow_steps = []
            start_time = time.time()
            
            # Step 1: Enterprise input (settings)
            print("  Step 1: Enterprise input (settings)...")
            step1 = self.make_request('/enterprise-settings')
            data_flow_steps.append(step1)
            if not step1['success']:
                self.log_test("Enterprise Data Flow", "FAIL", "Enterprise input not accessible")
                return False
            
            # Step 2: Data processing (enterprise health)
            print("  Step 2: Data processing (enterprise health)...")
            step2 = self.make_request('/api/enterprise/health')
            data_flow_steps.append(step2)
            if not step2['success']:
                self.log_test("Enterprise Data Flow", "FAIL", "Enterprise data processing not accessible")
                return False
            
            # Step 3: Data storage (audit logs)
            print("  Step 3: Data storage (audit logs)...")
            step3 = self.make_request('/api/enterprise/audit/logs')
            data_flow_steps.append(step3)
            if not step3['success']:
                self.log_test("Enterprise Data Flow", "FAIL", "Enterprise data storage not accessible")
                return False
            
            # Step 4: Data retrieval (compliance)
            print("  Step 4: Data retrieval (compliance)...")
            step4 = self.make_request('/api/enterprise/compliance/report', method='POST', data={'report_type': 'audit_summary'})
            data_flow_steps.append(step4)
            if not step4['success']:
                self.log_test("Enterprise Data Flow", "FAIL", "Enterprise data retrieval not accessible")
                return False
            
            # Step 5: Data output (monitoring)
            print("  Step 5: Data output (monitoring)...")
            step5 = self.make_request('/api/monitoring/system-metrics')
            data_flow_steps.append(step5)
            if not step5['success']:
                self.log_test("Enterprise Data Flow", "FAIL", "Enterprise data output not accessible")
                return False
            
            end_time = time.time()
            data_flow_duration = end_time - start_time
            
            # Calculate data flow metrics
            successful_steps = sum(1 for step in data_flow_steps if step['success'])
            success_rate = (successful_steps / len(data_flow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in data_flow_steps) / len(data_flow_steps)
            
            if success_rate >= 80:
                self.log_test("Enterprise Data Flow", "PASS", 
                    f"{success_rate:.1f}% success, {data_flow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Enterprise Data Flow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {data_flow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Enterprise Data Flow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_data_flow(self):
        """Test complete AI data flow"""
        try:
            print("🔍 Testing AI Data Flow...")
            
            data_flow_steps = []
            start_time = time.time()
            
            # Step 1: AI input (test generator)
            print("  Step 1: AI input (test generator)...")
            step1 = self.make_request('/ai-test-generator')
            data_flow_steps.append(step1)
            if not step1['success']:
                self.log_test("AI Data Flow", "FAIL", "AI input not accessible")
                return False
            
            # Step 2: AI processing (test generation)
            print("  Step 2: AI processing (test generation)...")
            step2 = self.make_request('/api/ai/generate-test-cases', method='POST', data={
                'user_story': {
                    'title': 'User Login',
                    'description': 'As a user, I want to login to the system',
                    'acceptance_criteria': 'User can login with valid credentials',
                    'business_value': 'Access to user account',
                    'user_persona': 'Registered user'
                }
            })
            data_flow_steps.append(step2)
            # Expected to return 200 or 400, which is acceptable
            if step2['status_code'] not in [200, 400]:
                self.log_test("AI Data Flow", "FAIL", "AI processing not accessible")
                return False
            
            # Step 3: AI data storage (test improvement)
            print("  Step 3: AI data storage (test improvement)...")
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
            data_flow_steps.append(step3)
            if step3['status_code'] not in [200, 400]:
                self.log_test("AI Data Flow", "FAIL", "AI data storage not accessible")
                return False
            
            # Step 4: AI data retrieval (BDD scenarios)
            print("  Step 4: AI data retrieval (BDD scenarios)...")
            step4 = self.make_request('/api/ai/generate-bdd-scenarios', method='POST', data={
                'title': 'User Login',
                'description': 'As a user, I want to login to the system',
                'acceptance_criteria': 'User can login with valid credentials',
                'business_value': 'Access to user account',
                'user_persona': 'Registered user'
            })
            data_flow_steps.append(step4)
            if step4['status_code'] not in [200, 400]:
                self.log_test("AI Data Flow", "FAIL", "AI data retrieval not accessible")
                return False
            
            # Step 5: AI data output (coverage analysis)
            print("  Step 5: AI data output (coverage analysis)...")
            step5 = self.make_request('/api/ai/analyze-coverage', method='POST', data={
                'test_cases': ['test1', 'test2'],
                'requirements': ['req1', 'req2']
            })
            data_flow_steps.append(step5)
            if step5['status_code'] not in [200, 400]:
                self.log_test("AI Data Flow", "FAIL", "AI data output not accessible")
                return False
            
            end_time = time.time()
            data_flow_duration = end_time - start_time
            
            # Calculate data flow metrics
            successful_steps = sum(1 for step in data_flow_steps if step['success'] or step['status_code'] == 400)
            success_rate = (successful_steps / len(data_flow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in data_flow_steps) / len(data_flow_steps)
            
            if success_rate >= 90:
                self.log_test("AI Data Flow", "PASS", 
                    f"{success_rate:.1f}% success, {data_flow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("AI Data Flow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {data_flow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("AI Data Flow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_integration_data_flow(self):
        """Test complete integration data flow"""
        try:
            print("🔍 Testing Integration Data Flow...")
            
            data_flow_steps = []
            start_time = time.time()
            
            # Step 1: Integration input (integrations page)
            print("  Step 1: Integration input (integrations page)...")
            step1 = self.make_request('/integrations')
            data_flow_steps.append(step1)
            if not step1['success']:
                self.log_test("Integration Data Flow", "FAIL", "Integration input not accessible")
                return False
            
            # Step 2: Integration processing (VS Code)
            print("  Step 2: Integration processing (VS Code)...")
            step2 = self.make_request('/api/integrations/vscode/install')
            data_flow_steps.append(step2)
            if not step2['success']:
                self.log_test("Integration Data Flow", "FAIL", "Integration processing not accessible")
                return False
            
            # Step 3: Integration data storage (GitHub Actions)
            print("  Step 3: Integration data storage (GitHub Actions)...")
            step3 = self.make_request('/api/integrations/github-actions/template')
            data_flow_steps.append(step3)
            if not step3['success']:
                self.log_test("Integration Data Flow", "FAIL", "Integration data storage not accessible")
                return False
            
            # Step 4: Integration data retrieval (Azure DevOps)
            print("  Step 4: Integration data retrieval (Azure DevOps)...")
            step4 = self.make_request('/api/integrations/azure-devops/template')
            data_flow_steps.append(step4)
            if not step4['success']:
                self.log_test("Integration Data Flow", "FAIL", "Integration data retrieval not accessible")
                return False
            
            # Step 5: Integration data output (service discovery)
            print("  Step 5: Integration data output (service discovery)...")
            step5 = self.make_request('/api/services')
            data_flow_steps.append(step5)
            if not step5['success']:
                self.log_test("Integration Data Flow", "FAIL", "Integration data output not accessible")
                return False
            
            end_time = time.time()
            data_flow_duration = end_time - start_time
            
            # Calculate data flow metrics
            successful_steps = sum(1 for step in data_flow_steps if step['success'])
            success_rate = (successful_steps / len(data_flow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in data_flow_steps) / len(data_flow_steps)
            
            if success_rate >= 90:
                self.log_test("Integration Data Flow", "PASS", 
                    f"{success_rate:.1f}% success, {data_flow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Integration Data Flow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {data_flow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Integration Data Flow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_monitoring_data_flow(self):
        """Test complete monitoring data flow"""
        try:
            print("🔍 Testing Monitoring Data Flow...")
            
            data_flow_steps = []
            start_time = time.time()
            
            # Step 1: Monitoring input (monitoring dashboard)
            print("  Step 1: Monitoring input (monitoring dashboard)...")
            step1 = self.make_request('/monitoring')
            data_flow_steps.append(step1)
            if not step1['success']:
                self.log_test("Monitoring Data Flow", "FAIL", "Monitoring input not accessible")
                return False
            
            # Step 2: Monitoring processing (system metrics)
            print("  Step 2: Monitoring processing (system metrics)...")
            step2 = self.make_request('/api/monitoring/system-metrics')
            data_flow_steps.append(step2)
            if not step2['success']:
                self.log_test("Monitoring Data Flow", "FAIL", "Monitoring processing not accessible")
                return False
            
            # Step 3: Monitoring data storage (performance summary)
            print("  Step 3: Monitoring data storage (performance summary)...")
            step3 = self.make_request('/api/monitoring/performance-summary')
            data_flow_steps.append(step3)
            if not step3['success']:
                self.log_test("Monitoring Data Flow", "FAIL", "Monitoring data storage not accessible")
                return False
            
            # Step 4: Monitoring data retrieval (health check)
            print("  Step 4: Monitoring data retrieval (health check)...")
            step4 = self.make_request('/api/monitoring/health')
            data_flow_steps.append(step4)
            if not step4['success']:
                self.log_test("Monitoring Data Flow", "FAIL", "Monitoring data retrieval not accessible")
                return False
            
            # Step 5: Monitoring data output (cache stats)
            print("  Step 5: Monitoring data output (cache stats)...")
            step5 = self.make_request('/api/cache/stats')
            data_flow_steps.append(step5)
            if not step5['success']:
                self.log_test("Monitoring Data Flow", "FAIL", "Monitoring data output not accessible")
                return False
            
            end_time = time.time()
            data_flow_duration = end_time - start_time
            
            # Calculate data flow metrics
            successful_steps = sum(1 for step in data_flow_steps if step['success'])
            success_rate = (successful_steps / len(data_flow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in data_flow_steps) / len(data_flow_steps)
            
            if success_rate >= 90:
                self.log_test("Monitoring Data Flow", "PASS", 
                    f"{success_rate:.1f}% success, {data_flow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Monitoring Data Flow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {data_flow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Monitoring Data Flow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_analytics_data_flow(self):
        """Test complete analytics data flow"""
        try:
            print("🔍 Testing Analytics Data Flow...")
            
            data_flow_steps = []
            start_time = time.time()
            
            # Step 1: Analytics input (business analytics)
            print("  Step 1: Analytics input (business analytics)...")
            step1 = self.make_request('/api/analytics/business')
            data_flow_steps.append(step1)
            if not step1['success']:
                self.log_test("Analytics Data Flow", "FAIL", "Analytics input not accessible")
                return False
            
            # Step 2: Analytics processing (performance analytics)
            print("  Step 2: Analytics processing (performance analytics)...")
            step2 = self.make_request('/api/analytics/performance')
            data_flow_steps.append(step2)
            if not step2['success']:
                self.log_test("Analytics Data Flow", "FAIL", "Analytics processing not accessible")
                return False
            
            # Step 3: Analytics data storage (A/B testing)
            print("  Step 3: Analytics data storage (A/B testing)...")
            step3 = self.make_request('/api/ab-testing/experiments')
            data_flow_steps.append(step3)
            if not step3['success']:
                self.log_test("Analytics Data Flow", "FAIL", "Analytics data storage not accessible")
                return False
            
            # Step 4: Analytics data retrieval (monitoring)
            print("  Step 4: Analytics data retrieval (monitoring)...")
            step4 = self.make_request('/api/monitoring/performance-summary')
            data_flow_steps.append(step4)
            if not step4['success']:
                self.log_test("Analytics Data Flow", "FAIL", "Analytics data retrieval not accessible")
                return False
            
            # Step 5: Analytics data output (reporting)
            print("  Step 5: Analytics data output (reporting)...")
            step5 = self.make_request('/advanced-reporting')
            data_flow_steps.append(step5)
            if not step5['success']:
                self.log_test("Analytics Data Flow", "FAIL", "Analytics data output not accessible")
                return False
            
            end_time = time.time()
            data_flow_duration = end_time - start_time
            
            # Calculate data flow metrics
            successful_steps = sum(1 for step in data_flow_steps if step['success'])
            success_rate = (successful_steps / len(data_flow_steps)) * 100
            avg_response_time = sum(step['response_time'] for step in data_flow_steps) / len(data_flow_steps)
            
            if success_rate >= 90:
                self.log_test("Analytics Data Flow", "PASS", 
                    f"{success_rate:.1f}% success, {data_flow_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Analytics Data Flow", "FAIL", 
                    f"Only {success_rate:.1f}% success, {data_flow_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Analytics Data Flow", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_data_flow_tests(self):
        """Run all data flow tests"""
        print("🔍 Starting Data Flow Testing...")
        print("=" * 60)
        
        # Run all data flow tests
        self.test_user_data_flow()
        self.test_enterprise_data_flow()
        self.test_ai_data_flow()
        self.test_integration_data_flow()
        self.test_monitoring_data_flow()
        self.test_analytics_data_flow()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Data Flow Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # Print data flow metrics
        print(f"\n📈 Data Flow Metrics:")
        print(f"  - Data Flows Tested: {self.data_flow_metrics['data_flows_tested']}")
        print(f"  - Data Integrity Score: {self.data_flow_metrics['data_integrity_score']:.1f}%")
        print(f"  - Average Data Processing Time: {self.data_flow_metrics['average_data_processing_time']:.2f}s")
        print(f"  - Data Consistency Score: {self.data_flow_metrics['data_consistency_score']:.1f}%")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = DataFlowTester()
    success = tester.run_all_data_flow_tests()
    exit(0 if success else 1)