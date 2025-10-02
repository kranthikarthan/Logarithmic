#!/usr/bin/env python3
"""
Stress Testing for Assertly
Tests system behavior under extreme load conditions and breaking points
"""

import requests
import time
import threading
import statistics
from datetime import datetime
import json
import queue
import concurrent.futures
from collections import defaultdict
import random

class StressPerformanceTester:
    """Comprehensive stress testing suite"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.stress_metrics = {
            'max_concurrent_users': 0,
            'breaking_point': 0,
            'recovery_time': 0,
            'error_rate_at_peak': 0
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
    
    def make_request(self, endpoint, method='GET', data=None, timeout=5):
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
                'method': method
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
    
    def test_extreme_concurrent_users(self):
        """Test system with extreme concurrent users (100+)"""
        try:
            print("🔍 Testing Extreme Concurrent Users (100 users)...")
            
            endpoints = [
                '/',
                '/health',
                '/api/enterprise/health',
                '/api/analytics/business',
                '/api/i18n/languages'
            ]
            
            results = []
            start_time = time.time()
            
            def worker():
                for endpoint in endpoints:
                    result = self.make_request(endpoint, timeout=3)
                    results.append(result)
                    time.sleep(0.01)  # Minimal delay
            
            # Create 100 concurrent threads
            threads = []
            for i in range(100):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            total_requests = len(results)
            success_rate = (successful_requests / total_requests) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            throughput = total_requests / duration
            
            self.stress_metrics['max_concurrent_users'] = 100
            self.stress_metrics['error_rate_at_peak'] = 100 - success_rate
            
            if success_rate >= 70:  # Lower threshold for stress testing
                self.log_test("Extreme Concurrent Users", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {throughput:.1f} req/s")
                return True
            else:
                self.log_test("Extreme Concurrent Users", "FAIL", 
                    f"Only {success_rate:.1f}% success, system overwhelmed")
                return False
                
        except Exception as e:
            self.log_test("Extreme Concurrent Users", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_breaking_point(self):
        """Test system breaking point with increasing load"""
        try:
            print("🔍 Testing Breaking Point (Increasing Load)...")
            
            endpoints = ['/', '/health', '/api/enterprise/health']
            breaking_point = 0
            max_success_rate = 0
            
            # Test with increasing concurrent users
            for concurrent_users in [50, 75, 100, 125, 150]:
                print(f"  Testing with {concurrent_users} concurrent users...")
                
                results = []
                start_time = time.time()
                
                def worker():
                    for endpoint in endpoints:
                        result = self.make_request(endpoint, timeout=2)
                        results.append(result)
                        time.sleep(0.005)
                
                # Create concurrent threads
                threads = []
                for i in range(concurrent_users):
                    thread = threading.Thread(target=worker)
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Calculate success rate
                successful_requests = sum(1 for r in results if r['success'])
                total_requests = len(results)
                success_rate = (successful_requests / total_requests) * 100
                
                if success_rate >= 80:
                    breaking_point = concurrent_users
                    max_success_rate = success_rate
                else:
                    break
            
            self.stress_metrics['breaking_point'] = breaking_point
            
            if breaking_point >= 75:
                self.log_test("Breaking Point", "PASS", 
                    f"System handles up to {breaking_point} concurrent users with {max_success_rate:.1f}% success")
                return True
            else:
                self.log_test("Breaking Point", "FAIL", 
                    f"System breaks at only {breaking_point} concurrent users")
                return False
                
        except Exception as e:
            self.log_test("Breaking Point", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_rapid_fire_requests(self):
        """Test system with rapid-fire requests"""
        try:
            print("🔍 Testing Rapid-Fire Requests...")
            
            endpoints = ['/', '/health', '/api/enterprise/health']
            results = []
            start_time = time.time()
            
            # Make requests as fast as possible
            for i in range(200):  # 200 rapid requests
                endpoint = random.choice(endpoints)
                result = self.make_request(endpoint, timeout=1)
                results.append(result)
                time.sleep(0.001)  # Minimal delay
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            throughput = len(results) / duration
            
            if success_rate >= 80 and avg_response_time < 1.0:
                self.log_test("Rapid-Fire Requests", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {throughput:.1f} req/s")
                return True
            else:
                self.log_test("Rapid-Fire Requests", "FAIL", 
                    f"Only {success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("Rapid-Fire Requests", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_mixed_workload_stress(self):
        """Test system with mixed workload under stress"""
        try:
            print("🔍 Testing Mixed Workload Stress...")
            
            # Mix of different request types
            requests_config = [
                {'endpoint': '/', 'method': 'GET', 'count': 20},
                {'endpoint': '/health', 'method': 'GET', 'count': 20},
                {'endpoint': '/api/enterprise/health', 'method': 'GET', 'count': 20},
                {'endpoint': '/api/i18n/set-language', 'method': 'POST', 'data': {'language': 'es'}, 'count': 10},
                {'endpoint': '/api/i18n/languages', 'method': 'GET', 'count': 20}
            ]
            
            results = []
            start_time = time.time()
            
            def worker(config):
                for i in range(config['count']):
                    result = self.make_request(
                        config['endpoint'], 
                        method=config['method'], 
                        data=config.get('data'),
                        timeout=3
                    )
                    results.append(result)
                    time.sleep(0.01)
            
            # Create threads for each request type
            threads = []
            for config in requests_config:
                thread = threading.Thread(target=worker, args=(config,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            throughput = len(results) / duration
            
            if success_rate >= 75:
                self.log_test("Mixed Workload Stress", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {throughput:.1f} req/s")
                return True
            else:
                self.log_test("Mixed Workload Stress", "FAIL", 
                    f"Only {success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("Mixed Workload Stress", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_system_recovery(self):
        """Test system recovery after stress"""
        try:
            print("🔍 Testing System Recovery After Stress...")
            
            # First, apply stress
            print("  Applying stress load...")
            endpoints = ['/', '/health', '/api/enterprise/health']
            stress_results = []
            
            def stress_worker():
                for endpoint in endpoints:
                    result = self.make_request(endpoint, timeout=2)
                    stress_results.append(result)
                    time.sleep(0.01)
            
            # Create high load
            threads = []
            for i in range(80):  # High load
                thread = threading.Thread(target=stress_worker)
                threads.append(thread)
                thread.start()
            
            # Wait for stress to complete
            for thread in threads:
                thread.join()
            
            # Wait for system to stabilize
            time.sleep(2)
            
            # Test recovery
            print("  Testing system recovery...")
            recovery_start = time.time()
            recovery_results = []
            
            # Test normal load after stress
            for endpoint in endpoints:
                for i in range(10):  # Normal load
                    result = self.make_request(endpoint, timeout=5)
                    recovery_results.append(result)
                    time.sleep(0.1)
            
            recovery_end = time.time()
            recovery_time = recovery_end - recovery_start
            
            # Calculate recovery metrics
            successful_recovery = sum(1 for r in recovery_results if r['success'])
            recovery_success_rate = (successful_recovery / len(recovery_results)) * 100
            avg_recovery_time = statistics.mean([r['response_time'] for r in recovery_results])
            
            self.stress_metrics['recovery_time'] = recovery_time
            
            if recovery_success_rate >= 90 and avg_recovery_time < 2.0:
                self.log_test("System Recovery", "PASS", 
                    f"{recovery_success_rate:.1f}% success after {recovery_time:.2f}s recovery, {avg_recovery_time:.3f}s avg response")
                return True
            else:
                self.log_test("System Recovery", "FAIL", 
                    f"Only {recovery_success_rate:.1f}% success after stress, {avg_recovery_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("System Recovery", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_resource_exhaustion(self):
        """Test system behavior under resource exhaustion"""
        try:
            print("🔍 Testing Resource Exhaustion...")
            
            # Test with very short timeouts to simulate resource exhaustion
            endpoints = ['/', '/health', '/api/enterprise/health']
            results = []
            start_time = time.time()
            
            def resource_worker():
                for endpoint in endpoints:
                    # Very short timeout to simulate resource exhaustion
                    result = self.make_request(endpoint, timeout=0.5)
                    results.append(result)
                    time.sleep(0.001)  # Minimal delay
            
            # Create many threads with short timeouts
            threads = []
            for i in range(60):  # Moderate load with short timeouts
                thread = threading.Thread(target=resource_worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            timeout_requests = sum(1 for r in results if not r['success'] and 'timeout' in str(r.get('error', '')).lower())
            success_rate = (successful_requests / len(results)) * 100
            
            if success_rate >= 60:  # Lower threshold due to short timeouts
                self.log_test("Resource Exhaustion", "PASS", 
                    f"{success_rate:.1f}% success under resource constraints, {timeout_requests} timeouts")
                return True
            else:
                self.log_test("Resource Exhaustion", "FAIL", 
                    f"Only {success_rate:.1f}% success under resource constraints")
                return False
                
        except Exception as e:
            self.log_test("Resource Exhaustion", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_stress_tests(self):
        """Run all stress performance tests"""
        print("🔍 Starting Stress Performance Testing...")
        print("=" * 60)
        
        # Run all stress tests
        self.test_extreme_concurrent_users()
        self.test_breaking_point()
        self.test_rapid_fire_requests()
        self.test_mixed_workload_stress()
        self.test_system_recovery()
        self.test_resource_exhaustion()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Stress Performance Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # Print stress metrics
        print(f"\n📈 Stress Metrics:")
        print(f"  - Max Concurrent Users: {self.stress_metrics['max_concurrent_users']}")
        print(f"  - Breaking Point: {self.stress_metrics['breaking_point']} users")
        print(f"  - Recovery Time: {self.stress_metrics['recovery_time']:.2f}s")
        print(f"  - Error Rate at Peak: {self.stress_metrics['error_rate_at_peak']:.1f}%")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = StressPerformanceTester()
    success = tester.run_all_stress_tests()
    exit(0 if success else 1)