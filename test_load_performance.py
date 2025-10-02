#!/usr/bin/env python3
"""
Load Testing for Assertly
Tests system performance under normal and high load conditions
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

class LoadPerformanceTester:
    """Comprehensive load testing suite"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.performance_metrics = {
            'response_times': [],
            'throughput': 0,
            'error_rate': 0,
            'concurrent_users': 0
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
    
    def test_basic_load(self):
        """Test system under basic load (10 concurrent users)"""
        try:
            print("🔍 Testing Basic Load (10 concurrent users)...")
            
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
                    result = self.make_request(endpoint)
                    results.append(result)
                    time.sleep(0.1)  # Small delay between requests
            
            # Create 10 concurrent threads
            threads = []
            for i in range(10):
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
            
            self.performance_metrics['response_times'].extend([r['response_time'] for r in results])
            self.performance_metrics['throughput'] = throughput
            self.performance_metrics['error_rate'] = 100 - success_rate
            self.performance_metrics['concurrent_users'] = 10
            
            if success_rate >= 90 and avg_response_time < 2.0:
                self.log_test("Basic Load Testing", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {throughput:.1f} req/s")
                return True
            else:
                self.log_test("Basic Load Testing", "FAIL", 
                    f"Only {success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("Basic Load Testing", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_medium_load(self):
        """Test system under medium load (25 concurrent users)"""
        try:
            print("🔍 Testing Medium Load (25 concurrent users)...")
            
            endpoints = [
                '/',
                '/health',
                '/api/enterprise/health',
                '/api/analytics/business',
                '/api/i18n/languages',
                '/api/cache/stats',
                '/api/monitoring/system-metrics'
            ]
            
            results = []
            start_time = time.time()
            
            def worker():
                for endpoint in endpoints:
                    result = self.make_request(endpoint)
                    results.append(result)
                    time.sleep(0.05)  # Smaller delay for higher load
            
            # Create 25 concurrent threads
            threads = []
            for i in range(25):
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
            
            if success_rate >= 85 and avg_response_time < 3.0:
                self.log_test("Medium Load Testing", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {throughput:.1f} req/s")
                return True
            else:
                self.log_test("Medium Load Testing", "FAIL", 
                    f"Only {success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("Medium Load Testing", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_high_load(self):
        """Test system under high load (50 concurrent users)"""
        try:
            print("🔍 Testing High Load (50 concurrent users)...")
            
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
                    result = self.make_request(endpoint)
                    results.append(result)
                    time.sleep(0.02)  # Minimal delay for high load
            
            # Create 50 concurrent threads
            threads = []
            for i in range(50):
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
            
            if success_rate >= 80 and avg_response_time < 5.0:
                self.log_test("High Load Testing", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {throughput:.1f} req/s")
                return True
            else:
                self.log_test("High Load Testing", "FAIL", 
                    f"Only {success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("High Load Testing", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_response_time_distribution(self):
        """Test response time distribution under load"""
        try:
            print("🔍 Testing Response Time Distribution...")
            
            # Make 100 requests to various endpoints
            endpoints = ['/', '/health', '/api/enterprise/health', '/api/analytics/business']
            results = []
            
            for endpoint in endpoints:
                for i in range(25):  # 25 requests per endpoint
                    result = self.make_request(endpoint)
                    results.append(result)
                    time.sleep(0.01)
            
            response_times = [r['response_time'] for r in results if r['success']]
            
            if len(response_times) > 0:
                avg_time = statistics.mean(response_times)
                median_time = statistics.median(response_times)
                p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
                p99_time = sorted(response_times)[int(len(response_times) * 0.99)]
                
                if p95_time < 2.0 and p99_time < 3.0:
                    self.log_test("Response Time Distribution", "PASS", 
                        f"Avg: {avg_time:.3f}s, Median: {median_time:.3f}s, P95: {p95_time:.3f}s, P99: {p99_time:.3f}s")
                    return True
                else:
                    self.log_test("Response Time Distribution", "FAIL", 
                        f"P95: {p95_time:.3f}s, P99: {p99_time:.3f}s (too slow)")
                    return False
            else:
                self.log_test("Response Time Distribution", "FAIL", "No successful requests")
                return False
                
        except Exception as e:
            self.log_test("Response Time Distribution", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_concurrent_endpoints(self):
        """Test concurrent access to different endpoints"""
        try:
            print("🔍 Testing Concurrent Endpoints...")
            
            endpoints = [
                '/',
                '/health',
                '/api/enterprise/health',
                '/api/analytics/business',
                '/api/i18n/languages',
                '/api/cache/stats',
                '/api/monitoring/system-metrics',
                '/api/services'
            ]
            
            results = []
            start_time = time.time()
            
            def test_endpoint(endpoint):
                result = self.make_request(endpoint)
                results.append(result)
            
            # Test all endpoints concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(test_endpoint, endpoint) for endpoint in endpoints]
                concurrent.futures.wait(futures)
            
            end_time = time.time()
            duration = end_time - start_time
            
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            
            if success_rate >= 90 and avg_response_time < 2.0:
                self.log_test("Concurrent Endpoints", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response in {duration:.3f}s")
                return True
            else:
                self.log_test("Concurrent Endpoints", "FAIL", 
                    f"Only {success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("Concurrent Endpoints", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load"""
        try:
            print("🔍 Testing Memory Usage Under Load...")
            
            # This is a simplified memory test
            # In a real scenario, you'd use psutil or similar tools
            
            endpoints = ['/', '/health', '/api/enterprise/health']
            results = []
            
            # Make many requests to test memory usage
            for i in range(100):
                for endpoint in endpoints:
                    result = self.make_request(endpoint)
                    results.append(result)
                    time.sleep(0.01)
            
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            
            # Check if system is still responsive
            final_test = self.make_request('/health')
            
            if success_rate >= 90 and final_test['success']:
                self.log_test("Memory Usage Under Load", "PASS", 
                    f"{success_rate:.1f}% success, system remains responsive")
                return True
            else:
                self.log_test("Memory Usage Under Load", "FAIL", 
                    f"Only {success_rate:.1f}% success or system unresponsive")
                return False
                
        except Exception as e:
            self.log_test("Memory Usage Under Load", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_load_tests(self):
        """Run all load performance tests"""
        print("🔍 Starting Load Performance Testing...")
        print("=" * 60)
        
        # Run all load tests
        self.test_basic_load()
        self.test_medium_load()
        self.test_high_load()
        self.test_response_time_distribution()
        self.test_concurrent_endpoints()
        self.test_memory_usage_under_load()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Load Performance Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # Print performance metrics
        if self.performance_metrics['response_times']:
            avg_response = statistics.mean(self.performance_metrics['response_times'])
            print(f"\n📈 Performance Metrics:")
            print(f"  - Average Response Time: {avg_response:.3f}s")
            print(f"  - Throughput: {self.performance_metrics['throughput']:.1f} req/s")
            print(f"  - Error Rate: {self.performance_metrics['error_rate']:.1f}%")
            print(f"  - Concurrent Users: {self.performance_metrics['concurrent_users']}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = LoadPerformanceTester()
    success = tester.run_all_load_tests()
    exit(0 if success else 1)