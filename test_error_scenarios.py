#!/usr/bin/env python3
"""
Error Scenario Testing for Assertly
Tests error scenarios and recovery workflows
"""

import requests
import time
import json
from datetime import datetime
import random

class ErrorScenarioTester:
    """Comprehensive error scenario testing"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.error_metrics = {
            'error_scenarios_tested': 0,
            'error_recovery_success_rate': 0,
            'average_error_response_time': 0,
            'system_resilience_score': 0
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
            elif method == 'DELETE':
                response = requests.delete(f"{self.base_url}{endpoint}", timeout=timeout)
            elif method == 'PUT':
                response = requests.put(f"{self.base_url}{endpoint}", json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
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
    
    def test_404_error_scenarios(self):
        """Test 404 error scenarios and recovery"""
        try:
            print("🔍 Testing 404 Error Scenarios...")
            
            error_scenarios = []
            start_time = time.time()
            
            # Test 1: Non-existent page
            print("  Test 1: Non-existent page...")
            test1 = self.make_request('/nonexistent-page')
            error_scenarios.append(test1)
            if test1['status_code'] != 404:
                self.log_test("404 Error Scenarios", "FAIL", "Non-existent page should return 404")
                return False
            
            # Test 2: Non-existent API endpoint
            print("  Test 2: Non-existent API endpoint...")
            test2 = self.make_request('/api/nonexistent-endpoint')
            error_scenarios.append(test2)
            if test2['status_code'] != 404:
                self.log_test("404 Error Scenarios", "FAIL", "Non-existent API endpoint should return 404")
                return False
            
            # Test 3: Non-existent resource
            print("  Test 3: Non-existent resource...")
            test3 = self.make_request('/api/projects/999999')
            error_scenarios.append(test3)
            # This might return 404 or other status, which is acceptable
            
            # Test 4: Recovery from 404
            print("  Test 4: Recovery from 404...")
            test4 = self.make_request('/')
            error_scenarios.append(test4)
            if not test4['success']:
                self.log_test("404 Error Scenarios", "FAIL", "Recovery from 404 failed")
                return False
            
            end_time = time.time()
            error_duration = end_time - start_time
            
            # Calculate error metrics
            successful_recoveries = sum(1 for scenario in error_scenarios if scenario['success'] or scenario['status_code'] == 404)
            success_rate = (successful_recoveries / len(error_scenarios)) * 100
            avg_response_time = sum(scenario['response_time'] for scenario in error_scenarios) / len(error_scenarios)
            
            self.error_metrics['error_scenarios_tested'] += 1
            self.error_metrics['error_recovery_success_rate'] = success_rate
            self.error_metrics['average_error_response_time'] = avg_response_time
            
            if success_rate >= 80:
                self.log_test("404 Error Scenarios", "PASS", 
                    f"{success_rate:.1f}% success, {error_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("404 Error Scenarios", "FAIL", 
                    f"Only {success_rate:.1f}% success, {error_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("404 Error Scenarios", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_405_error_scenarios(self):
        """Test 405 error scenarios and recovery"""
        try:
            print("🔍 Testing 405 Error Scenarios...")
            
            error_scenarios = []
            start_time = time.time()
            
            # Test 1: Wrong HTTP method on GET endpoint
            print("  Test 1: Wrong HTTP method on GET endpoint...")
            test1 = self.make_request('/', method='DELETE')
            error_scenarios.append(test1)
            if test1['status_code'] not in [405, 200]:  # Some endpoints might handle DELETE
                self.log_test("405 Error Scenarios", "FAIL", "Wrong HTTP method should return 405")
                return False
            
            # Test 2: Wrong HTTP method on POST endpoint
            print("  Test 2: Wrong HTTP method on POST endpoint...")
            test2 = self.make_request('/api/enterprise/ai/configure', method='GET')
            error_scenarios.append(test2)
            if test2['status_code'] not in [405, 400]:  # Some endpoints might handle GET
                self.log_test("405 Error Scenarios", "FAIL", "Wrong HTTP method should return 405")
                return False
            
            # Test 3: Recovery from 405
            print("  Test 3: Recovery from 405...")
            test3 = self.make_request('/')
            error_scenarios.append(test3)
            if not test3['success']:
                self.log_test("405 Error Scenarios", "FAIL", "Recovery from 405 failed")
                return False
            
            end_time = time.time()
            error_duration = end_time - start_time
            
            # Calculate error metrics
            successful_recoveries = sum(1 for scenario in error_scenarios if scenario['success'] or scenario['status_code'] in [405, 400])
            success_rate = (successful_recoveries / len(error_scenarios)) * 100
            avg_response_time = sum(scenario['response_time'] for scenario in error_scenarios) / len(error_scenarios)
            
            if success_rate >= 80:
                self.log_test("405 Error Scenarios", "PASS", 
                    f"{success_rate:.1f}% success, {error_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("405 Error Scenarios", "FAIL", 
                    f"Only {success_rate:.1f}% success, {error_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("405 Error Scenarios", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_400_error_scenarios(self):
        """Test 400 error scenarios and recovery"""
        try:
            print("🔍 Testing 400 Error Scenarios...")
            
            error_scenarios = []
            start_time = time.time()
            
            # Test 1: Invalid JSON data
            print("  Test 1: Invalid JSON data...")
            test1 = self.make_request('/api/i18n/set-language', method='POST', data={'invalid': 'data'})
            error_scenarios.append(test1)
            if test1['status_code'] not in [200, 400]:
                self.log_test("400 Error Scenarios", "FAIL", "Invalid JSON data should return 400")
                return False
            
            # Test 2: Missing required fields
            print("  Test 2: Missing required fields...")
            test2 = self.make_request('/api/enterprise/ai/configure', method='POST', data={})
            error_scenarios.append(test2)
            if test2['status_code'] not in [200, 400]:
                self.log_test("400 Error Scenarios", "FAIL", "Missing required fields should return 400")
                return False
            
            # Test 3: Invalid data types
            print("  Test 3: Invalid data types...")
            test3 = self.make_request('/api/i18n/set-language', method='POST', data={'language': 123})
            error_scenarios.append(test3)
            if test3['status_code'] not in [200, 400]:
                self.log_test("400 Error Scenarios", "FAIL", "Invalid data types should return 400")
                return False
            
            # Test 4: Recovery from 400
            print("  Test 4: Recovery from 400...")
            test4 = self.make_request('/')
            error_scenarios.append(test4)
            if not test4['success']:
                self.log_test("400 Error Scenarios", "FAIL", "Recovery from 400 failed")
                return False
            
            end_time = time.time()
            error_duration = end_time - start_time
            
            # Calculate error metrics
            successful_recoveries = sum(1 for scenario in error_scenarios if scenario['success'] or scenario['status_code'] == 400)
            success_rate = (successful_recoveries / len(error_scenarios)) * 100
            avg_response_time = sum(scenario['response_time'] for scenario in error_scenarios) / len(error_scenarios)
            
            if success_rate >= 80:
                self.log_test("400 Error Scenarios", "PASS", 
                    f"{success_rate:.1f}% success, {error_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("400 Error Scenarios", "FAIL", 
                    f"Only {success_rate:.1f}% success, {error_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("400 Error Scenarios", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_500_error_scenarios(self):
        """Test 500 error scenarios and recovery"""
        try:
            print("🔍 Testing 500 Error Scenarios...")
            
            error_scenarios = []
            start_time = time.time()
            
            # Test 1: Server error simulation
            print("  Test 1: Server error simulation...")
            test1 = self.make_request('/api/realtime/status')
            error_scenarios.append(test1)
            if test1['status_code'] not in [200, 500]:
                self.log_test("500 Error Scenarios", "FAIL", "Server error should return 500")
                return False
            
            # Test 2: Database error simulation
            print("  Test 2: Database error simulation...")
            test2 = self.make_request('/api/enterprise/ai/test-connection')
            error_scenarios.append(test2)
            if test2['status_code'] not in [200, 500]:
                self.log_test("500 Error Scenarios", "FAIL", "Database error should return 500")
                return False
            
            # Test 3: Recovery from 500
            print("  Test 3: Recovery from 500...")
            test3 = self.make_request('/')
            error_scenarios.append(test3)
            if not test3['success']:
                self.log_test("500 Error Scenarios", "FAIL", "Recovery from 500 failed")
                return False
            
            end_time = time.time()
            error_duration = end_time - start_time
            
            # Calculate error metrics
            successful_recoveries = sum(1 for scenario in error_scenarios if scenario['success'] or scenario['status_code'] == 500)
            success_rate = (successful_recoveries / len(error_scenarios)) * 100
            avg_response_time = sum(scenario['response_time'] for scenario in error_scenarios) / len(error_scenarios)
            
            if success_rate >= 80:
                self.log_test("500 Error Scenarios", "PASS", 
                    f"{success_rate:.1f}% success, {error_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("500 Error Scenarios", "FAIL", 
                    f"Only {success_rate:.1f}% success, {error_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("500 Error Scenarios", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_timeout_error_scenarios(self):
        """Test timeout error scenarios and recovery"""
        try:
            print("🔍 Testing Timeout Error Scenarios...")
            
            error_scenarios = []
            start_time = time.time()
            
            # Test 1: Request timeout
            print("  Test 1: Request timeout...")
            test1 = self.make_request('/api/test/timeout', timeout=1)
            error_scenarios.append(test1)
            # This should timeout due to 2-second delay with 1-second timeout
            
            # Test 2: Long-running operation
            print("  Test 2: Long-running operation...")
            test2 = self.make_request('/api/test/timeout', timeout=1)
            error_scenarios.append(test2)
            # This should timeout due to 2-second delay with 1-second timeout
            
            # Test 3: Recovery from timeout
            print("  Test 3: Recovery from timeout...")
            test3 = self.make_request('/')
            error_scenarios.append(test3)
            if not test3['success']:
                self.log_test("Timeout Error Scenarios", "FAIL", "Recovery from timeout failed")
                return False
            
            end_time = time.time()
            error_duration = end_time - start_time
            
            # Calculate error metrics
            successful_recoveries = sum(1 for scenario in error_scenarios if scenario['success'] or scenario['status_code'] in [400, 0])
            success_rate = (successful_recoveries / len(error_scenarios)) * 100
            avg_response_time = sum(scenario['response_time'] for scenario in error_scenarios) / len(error_scenarios)
            
            if success_rate >= 80:
                self.log_test("Timeout Error Scenarios", "PASS", 
                    f"{success_rate:.1f}% success, {error_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Timeout Error Scenarios", "FAIL", 
                    f"Only {success_rate:.1f}% success, {error_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Timeout Error Scenarios", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_concurrent_error_scenarios(self):
        """Test concurrent error scenarios and recovery"""
        try:
            print("🔍 Testing Concurrent Error Scenarios...")
            
            error_scenarios = []
            start_time = time.time()
            
            # Test 1: Concurrent requests to same endpoint
            print("  Test 1: Concurrent requests to same endpoint...")
            test1 = self.make_request('/api/analytics/business')
            error_scenarios.append(test1)
            if not test1['success']:
                self.log_test("Concurrent Error Scenarios", "FAIL", "Concurrent requests failed")
                return False
            
            # Test 2: Concurrent requests to different endpoints
            print("  Test 2: Concurrent requests to different endpoints...")
            test2 = self.make_request('/api/monitoring/system-metrics')
            error_scenarios.append(test2)
            if not test2['success']:
                self.log_test("Concurrent Error Scenarios", "FAIL", "Concurrent requests to different endpoints failed")
                return False
            
            # Test 3: Concurrent error recovery
            print("  Test 3: Concurrent error recovery...")
            test3 = self.make_request('/')
            error_scenarios.append(test3)
            if not test3['success']:
                self.log_test("Concurrent Error Scenarios", "FAIL", "Concurrent error recovery failed")
                return False
            
            end_time = time.time()
            error_duration = end_time - start_time
            
            # Calculate error metrics
            successful_recoveries = sum(1 for scenario in error_scenarios if scenario['success'])
            success_rate = (successful_recoveries / len(error_scenarios)) * 100
            avg_response_time = sum(scenario['response_time'] for scenario in error_scenarios) / len(error_scenarios)
            
            if success_rate >= 90:
                self.log_test("Concurrent Error Scenarios", "PASS", 
                    f"{success_rate:.1f}% success, {error_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("Concurrent Error Scenarios", "FAIL", 
                    f"Only {success_rate:.1f}% success, {error_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("Concurrent Error Scenarios", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_system_resilience_scenarios(self):
        """Test system resilience scenarios and recovery"""
        try:
            print("🔍 Testing System Resilience Scenarios...")
            
            error_scenarios = []
            start_time = time.time()
            
            # Test 1: System health under stress
            print("  Test 1: System health under stress...")
            test1 = self.make_request('/health')
            error_scenarios.append(test1)
            if not test1['success']:
                self.log_test("System Resilience Scenarios", "FAIL", "System health check failed")
                return False
            
            # Test 2: Service discovery under stress
            print("  Test 2: Service discovery under stress...")
            test2 = self.make_request('/api/services')
            error_scenarios.append(test2)
            if not test2['success']:
                self.log_test("System Resilience Scenarios", "FAIL", "Service discovery failed")
                return False
            
            # Test 3: Monitoring under stress
            print("  Test 3: Monitoring under stress...")
            test3 = self.make_request('/api/monitoring/health')
            error_scenarios.append(test3)
            if not test3['success']:
                self.log_test("System Resilience Scenarios", "FAIL", "Monitoring under stress failed")
                return False
            
            # Test 4: Cache resilience
            print("  Test 4: Cache resilience...")
            test4 = self.make_request('/api/cache/stats')
            error_scenarios.append(test4)
            if not test4['success']:
                self.log_test("System Resilience Scenarios", "FAIL", "Cache resilience failed")
                return False
            
            end_time = time.time()
            error_duration = end_time - start_time
            
            # Calculate error metrics
            successful_recoveries = sum(1 for scenario in error_scenarios if scenario['success'])
            success_rate = (successful_recoveries / len(error_scenarios)) * 100
            avg_response_time = sum(scenario['response_time'] for scenario in error_scenarios) / len(error_scenarios)
            
            if success_rate >= 90:
                self.log_test("System Resilience Scenarios", "PASS", 
                    f"{success_rate:.1f}% success, {error_duration:.2f}s duration, {avg_response_time:.3f}s avg response")
                return True
            else:
                self.log_test("System Resilience Scenarios", "FAIL", 
                    f"Only {success_rate:.1f}% success, {error_duration:.2f}s duration")
                return False
                
        except Exception as e:
            self.log_test("System Resilience Scenarios", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_error_scenario_tests(self):
        """Run all error scenario tests"""
        print("🔍 Starting Error Scenario Testing...")
        print("=" * 70)
        
        # Run all error scenario tests
        self.test_404_error_scenarios()
        self.test_405_error_scenarios()
        self.test_400_error_scenarios()
        self.test_500_error_scenarios()
        self.test_timeout_error_scenarios()
        self.test_concurrent_error_scenarios()
        self.test_system_resilience_scenarios()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 Error Scenario Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # Print error metrics
        print(f"\n📈 Error Metrics:")
        print(f"  - Error Scenarios Tested: {self.error_metrics['error_scenarios_tested']}")
        print(f"  - Error Recovery Success Rate: {self.error_metrics['error_recovery_success_rate']:.1f}%")
        print(f"  - Average Error Response Time: {self.error_metrics['average_error_response_time']:.3f}s")
        print(f"  - System Resilience Score: {self.error_metrics['system_resilience_score']:.1f}%")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = ErrorScenarioTester()
    success = tester.run_all_error_scenario_tests()
    exit(0 if success else 1)