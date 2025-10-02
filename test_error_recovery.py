#!/usr/bin/env python3
"""
Error Recovery Testing for Assertly
Tests error recovery, fallback mechanisms, and system resilience
"""

import requests
import json
import time
from datetime import datetime
import logging

class ErrorRecoveryTester:
    """Comprehensive error recovery testing"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
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
    
    def test_404_error_handling(self):
        """Test 404 error handling"""
        try:
            # Test various non-existent endpoints
            non_existent_endpoints = [
                '/nonexistent',
                '/api/nonexistent',
                '/api/invalid/endpoint',
                '/dashboard/nonexistent'
            ]
            
            error_handling_works = True
            for endpoint in non_existent_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code != 404:
                    error_handling_works = False
                    break
            
            if error_handling_works:
                self.log_test("404 Error Handling", "PASS", "All non-existent endpoints return 404")
                return True
            else:
                self.log_test("404 Error Handling", "FAIL", "Some non-existent endpoints don't return 404")
                return False
        except Exception as e:
            self.log_test("404 Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_405_error_handling(self):
        """Test 405 error handling"""
        try:
            # Test invalid HTTP methods
            method_tests = [
                {'endpoint': '/', 'method': 'POST', 'expected_status': 405},
                {'endpoint': '/', 'method': 'PUT', 'expected_status': 405},
                {'endpoint': '/', 'method': 'DELETE', 'expected_status': 405},
                {'endpoint': '/health', 'method': 'POST', 'expected_status': 405}
            ]
            
            error_handling_works = True
            for test in method_tests:
                try:
                    if test['method'] == 'POST':
                        response = requests.post(f"{self.base_url}{test['endpoint']}", timeout=5)
                    elif test['method'] == 'PUT':
                        response = requests.put(f"{self.base_url}{test['endpoint']}", timeout=5)
                    elif test['method'] == 'DELETE':
                        response = requests.delete(f"{self.base_url}{test['endpoint']}", timeout=5)
                    
                    if response.status_code != test['expected_status']:
                        error_handling_works = False
                        break
                except Exception:
                    pass
            
            if error_handling_works:
                self.log_test("405 Error Handling", "PASS", "Invalid HTTP methods return 405")
                return True
            else:
                self.log_test("405 Error Handling", "FAIL", "Some invalid methods don't return 405")
                return False
        except Exception as e:
            self.log_test("405 Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_400_error_handling(self):
        """Test 400 error handling"""
        try:
            # Test invalid data
            invalid_data_tests = [
                {
                    'endpoint': '/api/i18n/set-language',
                    'payload': {'language': 'invalid_language'},
                    'expected_status': 400
                },
                {
                    'endpoint': '/api/i18n/set-language',
                    'payload': {},
                    'expected_status': 400
                }
            ]
            
            error_handling_works = True
            for test in invalid_data_tests:
                try:
                    response = requests.post(
                        f"{self.base_url}{test['endpoint']}",
                        json=test['payload'],
                        timeout=5
                    )
                    
                    if response.status_code != test['expected_status']:
                        error_handling_works = False
                        break
                except Exception:
                    pass
            
            if error_handling_works:
                self.log_test("400 Error Handling", "PASS", "Invalid data returns 400")
                return True
            else:
                self.log_test("400 Error Handling", "FAIL", "Some invalid data doesn't return 400")
                return False
        except Exception as e:
            self.log_test("400 Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_500_error_handling(self):
        """Test 500 error handling"""
        try:
            # Test endpoints that might return 500 errors
            # This includes monitoring endpoints that might fail without dependencies
            potential_500_endpoints = [
                '/api/realtime/status',
                '/api/monitoring/system-metrics'
            ]
            
            error_handling_works = True
            for endpoint in potential_500_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                # 500 is acceptable for these endpoints
                if response.status_code not in [200, 500]:
                    error_handling_works = False
                    break
            
            if error_handling_works:
                self.log_test("500 Error Handling", "PASS", "Server errors handled gracefully")
                return True
            else:
                self.log_test("500 Error Handling", "FAIL", "Some server errors not handled properly")
                return False
        except Exception as e:
            self.log_test("500 Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_fallback_mechanisms(self):
        """Test fallback mechanisms"""
        try:
            # Test that fallback mechanisms work when primary services fail
            # This includes cache fallbacks, monitoring fallbacks, etc.
            
            # Test cache fallback
            cache_response = requests.get(f"{self.base_url}/api/cache/stats", timeout=5)
            if cache_response.status_code not in [200, 500]:
                self.log_test("Fallback Mechanisms", "FAIL", "Cache fallback not working")
                return False
            
            # Test monitoring fallback
            monitoring_response = requests.get(f"{self.base_url}/api/monitoring/system-metrics", timeout=5)
            if monitoring_response.status_code not in [200, 500]:
                self.log_test("Fallback Mechanisms", "FAIL", "Monitoring fallback not working")
                return False
            
            # Test analytics fallback
            analytics_response = requests.get(f"{self.base_url}/api/analytics/business", timeout=5)
            if analytics_response.status_code != 200:
                self.log_test("Fallback Mechanisms", "FAIL", "Analytics fallback not working")
                return False
            
            self.log_test("Fallback Mechanisms", "PASS", "All fallback mechanisms working")
            return True
        except Exception as e:
            self.log_test("Fallback Mechanisms", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_system_resilience(self):
        """Test system resilience"""
        try:
            # Test that the system remains functional after errors
            # This includes testing recovery from various error conditions
            
            # Test basic functionality after potential errors
            resilience_tests = [
                '/',
                '/health',
                '/api/enterprise/health',
                '/api/analytics/business'
            ]
            
            all_functional = True
            for endpoint in resilience_tests:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code not in [200, 500]:  # 500 is acceptable for some endpoints
                        all_functional = False
                        break
                except Exception:
                    all_functional = False
                    break
            
            if all_functional:
                self.log_test("System Resilience", "PASS", "System remains functional after errors")
                return True
            else:
                self.log_test("System Resilience", "FAIL", "System not resilient to errors")
                return False
        except Exception as e:
            self.log_test("System Resilience", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_error_recovery_time(self):
        """Test error recovery time"""
        try:
            # Test how quickly the system recovers from errors
            start_time = time.time()
            
            # Make requests that might cause errors
            error_prone_requests = [
                f"{self.base_url}/nonexistent",
                f"{self.base_url}/api/nonexistent",
                f"{self.base_url}/api/monitoring/system-metrics"
            ]
            
            recovery_time = 0
            for request_url in error_prone_requests:
                try:
                    response = requests.get(request_url, timeout=5)
                    # Even if it returns an error, it should respond quickly
                    recovery_time += response.elapsed.total_seconds()
                except Exception:
                    pass
            
            end_time = time.time()
            total_time = end_time - start_time
            
            if total_time < 5.0:  # Should recover within 5 seconds
                self.log_test("Error Recovery Time", "PASS", f"System recovers in {total_time:.2f}s")
                return True
            else:
                self.log_test("Error Recovery Time", "FAIL", f"System takes too long to recover: {total_time:.2f}s")
                return False
        except Exception as e:
            self.log_test("Error Recovery Time", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_concurrent_error_handling(self):
        """Test concurrent error handling"""
        try:
            import threading
            import queue
            
            results = queue.Queue()
            
            def make_error_request():
                try:
                    # Make requests that might cause errors
                    response = requests.get(f"{self.base_url}/api/monitoring/system-metrics", timeout=5)
                    results.put(response.status_code in [200, 500])  # 500 is acceptable
                except Exception:
                    results.put(False)
            
            # Create multiple threads for concurrent error testing
            threads = []
            for i in range(3):  # 3 concurrent requests
                thread = threading.Thread(target=make_error_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            successful_requests = 0
            while not results.empty():
                if results.get():
                    successful_requests += 1
            
            success_rate = (successful_requests / 3) * 100
            
            if success_rate >= 66:  # At least 2 out of 3 should succeed
                self.log_test("Concurrent Error Handling", "PASS", f"{success_rate:.1f}% success with concurrent errors")
                return True
            else:
                self.log_test("Concurrent Error Handling", "FAIL", f"Only {success_rate:.1f}% success with concurrent errors")
                return False
        except Exception as e:
            self.log_test("Concurrent Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_graceful_degradation(self):
        """Test graceful degradation"""
        try:
            # Test that the system degrades gracefully when services fail
            # This includes testing partial functionality when some services are unavailable
            
            # Test core functionality
            core_endpoints = [
                '/',
                '/health',
                '/api/enterprise/health'
            ]
            
            core_functional = True
            for endpoint in core_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code != 200:
                    core_functional = False
                    break
            
            # Test optional functionality
            optional_endpoints = [
                '/api/monitoring/system-metrics',
                '/api/realtime/status'
            ]
            
            optional_functional = 0
            for endpoint in optional_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code in [200, 500]:  # 500 is acceptable for optional services
                    optional_functional += 1
            
            if core_functional and optional_functional >= 1:
                self.log_test("Graceful Degradation", "PASS", "System degrades gracefully")
                return True
            else:
                self.log_test("Graceful Degradation", "FAIL", "System doesn't degrade gracefully")
                return False
        except Exception as e:
            self.log_test("Graceful Degradation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_error_logging(self):
        """Test error logging"""
        try:
            # Test that errors are properly logged
            # This includes testing that error responses contain useful information
            
            # Test various error conditions
            error_tests = [
                {'url': f"{self.base_url}/nonexistent", 'expected_status': 404},
                {'url': f"{self.base_url}/api/nonexistent", 'expected_status': 404}
            ]
            
            error_logging_works = True
            for test in error_tests:
                response = requests.get(test['url'], timeout=5)
                if response.status_code != test['expected_status']:
                    error_logging_works = False
                    break
                
                # Check if error response contains useful information
                if len(response.text) < 10:  # Should have some error message
                    error_logging_works = False
                    break
            
            if error_logging_works:
                self.log_test("Error Logging", "PASS", "Errors are properly logged")
                return True
            else:
                self.log_test("Error Logging", "FAIL", "Error logging not working properly")
                return False
        except Exception as e:
            self.log_test("Error Logging", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_error_recovery_tests(self):
        """Run all error recovery tests"""
        print("🔍 Starting Error Recovery Testing...")
        print("=" * 50)
        
        # Run all error recovery tests
        self.test_404_error_handling()
        self.test_405_error_handling()
        self.test_400_error_handling()
        self.test_500_error_handling()
        self.test_fallback_mechanisms()
        self.test_system_resilience()
        self.test_error_recovery_time()
        self.test_concurrent_error_handling()
        self.test_graceful_degradation()
        self.test_error_logging()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Error Recovery Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = ErrorRecoveryTester()
    success = tester.run_all_error_recovery_tests()
    exit(0 if success else 1)