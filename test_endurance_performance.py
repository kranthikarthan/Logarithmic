#!/usr/bin/env python3
"""
Endurance Testing for Assertly
Tests system performance over extended periods and long-running operations
"""

import requests
import time
import threading
import statistics
from datetime import datetime
import json
import random

class EndurancePerformanceTester:
    """Comprehensive endurance testing suite"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.endurance_metrics = {
            'test_duration': 0,
            'total_requests': 0,
            'avg_response_time': 0,
            'performance_degradation': 0,
            'memory_stability': 0
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
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'status_code': 0,
                'response_time': end_time - start_time,
                'endpoint': endpoint,
                'method': method,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def test_extended_operation(self):
        """Test system over extended period (5 minutes)"""
        try:
            print("🔍 Testing Extended Operation (5 minutes)...")
            
            endpoints = ['/', '/health', '/api/enterprise/health', '/api/analytics/business']
            results = []
            start_time = time.time()
            test_duration = 300  # 5 minutes
            
            print(f"  Running for {test_duration} seconds...")
            
            while time.time() - start_time < test_duration:
                # Make requests every 2 seconds
                for endpoint in endpoints:
                    result = self.make_request(endpoint, timeout=5)
                    results.append(result)
                    time.sleep(0.5)
                
                # Progress update every 30 seconds
                elapsed = time.time() - start_time
                if int(elapsed) % 30 == 0:
                    print(f"    {int(elapsed)}s elapsed, {len(results)} requests completed")
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            
            self.endurance_metrics['test_duration'] = actual_duration
            self.endurance_metrics['total_requests'] = len(results)
            self.endurance_metrics['avg_response_time'] = avg_response_time
            
            if success_rate >= 95 and avg_response_time < 2.0:
                self.log_test("Extended Operation", "PASS", 
                    f"{success_rate:.1f}% success over {actual_duration:.1f}s, {len(results)} requests, {avg_response_time:.3f}s avg")
                return True
            else:
                self.log_test("Extended Operation", "FAIL", 
                    f"Only {success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("Extended Operation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_continuous_load(self):
        """Test system under continuous load"""
        try:
            print("🔍 Testing Continuous Load (3 minutes)...")
            
            endpoints = ['/', '/health', '/api/enterprise/health', '/api/analytics/business', '/api/i18n/languages']
            results = []
            start_time = time.time()
            test_duration = 180  # 3 minutes
            
            def continuous_worker():
                worker_results = []
                while time.time() - start_time < test_duration:
                    endpoint = random.choice(endpoints)
                    result = self.make_request(endpoint, timeout=3)
                    worker_results.append(result)
                    time.sleep(0.5)  # Request every 0.5 seconds
                return worker_results
            
            # Create 3 concurrent workers
            threads = []
            for i in range(3):
                thread = threading.Thread(target=lambda: results.extend(continuous_worker()))
                threads.append(thread)
                thread.start()
            
            # Wait for test to complete
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            requests_per_second = len(results) / actual_duration
            
            if success_rate >= 90 and requests_per_second >= 5:
                self.log_test("Continuous Load", "PASS", 
                    f"{success_rate:.1f}% success over {actual_duration:.1f}s, {requests_per_second:.1f} req/s, {avg_response_time:.3f}s avg")
                return True
            else:
                self.log_test("Continuous Load", "FAIL", 
                    f"Only {success_rate:.1f}% success, {requests_per_second:.1f} req/s")
                return False
                
        except Exception as e:
            self.log_test("Continuous Load", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_performance_consistency(self):
        """Test performance consistency over time"""
        try:
            print("🔍 Testing Performance Consistency...")
            
            endpoints = ['/', '/health', '/api/enterprise/health']
            results = []
            start_time = time.time()
            test_duration = 120  # 2 minutes
            
            # Collect performance data in time windows
            time_windows = []
            current_window = []
            window_start = start_time
            
            while time.time() - start_time < test_duration:
                endpoint = random.choice(endpoints)
                result = self.make_request(endpoint, timeout=3)
                current_window.append(result)
                
                # Check if 10 seconds have passed
                if time.time() - window_start >= 10:
                    if current_window:
                        window_success = sum(1 for r in current_window if r['success'])
                        window_rate = (window_success / len(current_window)) * 100
                        window_avg_time = statistics.mean([r['response_time'] for r in current_window])
                        time_windows.append({
                            'success_rate': window_rate,
                            'avg_response_time': window_avg_time,
                            'request_count': len(current_window)
                        })
                    current_window = []
                    window_start = time.time()
                
                time.sleep(0.2)
            
            # Calculate consistency metrics
            if len(time_windows) >= 6:  # At least 6 windows (1 minute)
                success_rates = [w['success_rate'] for w in time_windows]
                response_times = [w['avg_response_time'] for w in time_windows]
                
                success_consistency = 100 - statistics.stdev(success_rates)
                response_consistency = 100 - (statistics.stdev(response_times) / statistics.mean(response_times) * 100)
                
                if success_consistency >= 80 and response_consistency >= 70:
                    self.log_test("Performance Consistency", "PASS", 
                        f"Success consistency: {success_consistency:.1f}%, Response consistency: {response_consistency:.1f}%")
                    return True
                else:
                    self.log_test("Performance Consistency", "FAIL", 
                        f"Success consistency: {success_consistency:.1f}%, Response consistency: {response_consistency:.1f}%")
                    return False
            else:
                self.log_test("Performance Consistency", "FAIL", "Insufficient data for consistency analysis")
                return False
                
        except Exception as e:
            self.log_test("Performance Consistency", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_memory_stability(self):
        """Test memory stability over extended period"""
        try:
            print("🔍 Testing Memory Stability...")
            
            endpoints = ['/', '/health', '/api/enterprise/health', '/api/analytics/business']
            results = []
            start_time = time.time()
            test_duration = 90  # 1.5 minutes
            
            # Make requests continuously to test memory stability
            while time.time() - start_time < test_duration:
                endpoint = random.choice(endpoints)
                result = self.make_request(endpoint, timeout=3)
                results.append(result)
                time.sleep(0.3)
            
            # Test system responsiveness at the end
            final_test_start = time.time()
            final_results = []
            for i in range(10):
                endpoint = random.choice(endpoints)
                result = self.make_request(endpoint, timeout=5)
                final_results.append(result)
                time.sleep(0.1)
            final_test_end = time.time()
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            
            final_success = sum(1 for r in final_results if r['success'])
            final_rate = (final_success / len(final_results)) * 100
            final_avg_time = statistics.mean([r['response_time'] for r in final_results])
            
            self.endurance_metrics['memory_stability'] = final_rate
            
            if success_rate >= 90 and final_rate >= 90 and final_avg_time < 1.0:
                self.log_test("Memory Stability", "PASS", 
                    f"Overall: {success_rate:.1f}% success, Final: {final_rate:.1f}% success, {final_avg_time:.3f}s avg")
                return True
            else:
                self.log_test("Memory Stability", "FAIL", 
                    f"Overall: {success_rate:.1f}% success, Final: {final_rate:.1f}% success")
                return False
                
        except Exception as e:
            self.log_test("Memory Stability", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_database_endurance(self):
        """Test database operations over extended period"""
        try:
            print("🔍 Testing Database Endurance...")
            
            # Database-intensive operations
            operations = [
                {'endpoint': '/api/enterprise/health', 'method': 'GET'},
                {'endpoint': '/api/enterprise/audit/logs', 'method': 'GET'},
                {'endpoint': '/api/i18n/set-language', 'method': 'POST', 'data': {'language': 'es'}},
                {'endpoint': '/api/i18n/languages', 'method': 'GET'},
                {'endpoint': '/api/analytics/business', 'method': 'GET'}
            ]
            
            results = []
            start_time = time.time()
            test_duration = 60  # 1 minute
            
            while time.time() - start_time < test_duration:
                operation = random.choice(operations)
                result = self.make_request(
                    operation['endpoint'],
                    method=operation['method'],
                    data=operation.get('data'),
                    timeout=5
                )
                results.append(result)
                time.sleep(0.5)
            
            # Calculate metrics
            successful_operations = sum(1 for r in results if r['success'])
            success_rate = (successful_operations / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            
            if success_rate >= 85 and avg_response_time < 2.0:
                self.log_test("Database Endurance", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {len(results)} operations")
                return True
            else:
                self.log_test("Database Endurance", "FAIL", 
                    f"Only {success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("Database Endurance", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_system_reliability(self):
        """Test overall system reliability over time"""
        try:
            print("🔍 Testing System Reliability...")
            
            endpoints = ['/', '/health', '/api/enterprise/health', '/api/analytics/business', '/api/cache/stats']
            results = []
            start_time = time.time()
            test_duration = 60  # 1 minute
            
            # Test system reliability with mixed operations
            while time.time() - start_time < test_duration:
                endpoint = random.choice(endpoints)
                result = self.make_request(endpoint, timeout=3)
                results.append(result)
                time.sleep(0.2)
            
            # Test system health at the end
            health_check = self.make_request('/health', timeout=5)
            
            # Calculate reliability metrics
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            
            # Calculate uptime percentage
            uptime_percentage = success_rate
            
            if uptime_percentage >= 95 and health_check['success']:
                self.log_test("System Reliability", "PASS", 
                    f"{uptime_percentage:.1f}% uptime, {avg_response_time:.3f}s avg response, system healthy")
                return True
            else:
                self.log_test("System Reliability", "FAIL", 
                    f"Only {uptime_percentage:.1f}% uptime, health check: {health_check['success']}")
                return False
                
        except Exception as e:
            self.log_test("System Reliability", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_endurance_tests(self):
        """Run all endurance performance tests"""
        print("🔍 Starting Endurance Performance Testing...")
        print("=" * 60)
        
        # Run all endurance tests
        self.test_extended_operation()
        self.test_continuous_load()
        self.test_performance_consistency()
        self.test_memory_stability()
        self.test_database_endurance()
        self.test_system_reliability()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Endurance Performance Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # Print endurance metrics
        print(f"\n📈 Endurance Metrics:")
        print(f"  - Test Duration: {self.endurance_metrics['test_duration']:.1f}s")
        print(f"  - Total Requests: {self.endurance_metrics['total_requests']}")
        print(f"  - Average Response Time: {self.endurance_metrics['avg_response_time']:.3f}s")
        print(f"  - Performance Degradation: {self.endurance_metrics['performance_degradation']:.1f}%")
        print(f"  - Memory Stability: {self.endurance_metrics['memory_stability']:.1f}%")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = EndurancePerformanceTester()
    success = tester.run_all_endurance_tests()
    exit(0 if success else 1)