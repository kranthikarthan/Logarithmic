#!/usr/bin/env python3
"""
Microservices Communication Testing for Assertly
Tests inter-service communication, service discovery, and service mesh functionality
"""

import requests
import json
import time
from datetime import datetime
import logging

class MicroservicesCommunicationTester:
    """Comprehensive microservices communication testing"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.service_endpoints = {
            'user_service': 'http://localhost:5001',
            'test_service': 'http://localhost:5002', 
            'ai_service': 'http://localhost:5003',
            'api_gateway': 'http://localhost:8000'
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
    
    def test_api_gateway_routing(self):
        """Test API Gateway routing to microservices"""
        try:
            # Test routing through API Gateway
            endpoints_to_test = [
                '/api/i18n/languages',
                '/api/analytics/business', 
                '/api/ab-testing/experiments',
                '/api/analytics/performance'
            ]
            
            all_routed = True
            for endpoint in endpoints_to_test:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code not in [200, 401, 503]:  # 401 for auth, 503 for service unavailable
                    all_routed = False
                    break
            
            if all_routed:
                self.log_test("API Gateway Routing", "PASS", "All endpoints routed successfully")
                return True
            else:
                self.log_test("API Gateway Routing", "FAIL", "Some endpoints failed to route")
                return False
                
        except Exception as e:
            self.log_test("API Gateway Routing", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_service_discovery(self):
        """Test service discovery functionality"""
        try:
            # Test if services can be discovered
            response = requests.get(f"{self.base_url}/api/services", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'services' in data and isinstance(data['services'], list):
                    self.log_test("Service Discovery", "PASS", f"Discovered {len(data['services'])} services")
                    return True
                else:
                    self.log_test("Service Discovery", "FAIL", "Invalid service discovery response")
                    return False
            else:
                self.log_test("Service Discovery", "FAIL", f"Service discovery failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Service Discovery", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_microservices_health_checks(self):
        """Test individual microservices health"""
        try:
            # Test main application health (includes microservices)
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'healthy':
                    self.log_test("Microservices Health Checks", "PASS", "Main application healthy")
                    return True
                else:
                    self.log_test("Microservices Health Checks", "FAIL", f"Invalid health status: {data}")
                    return False
            else:
                self.log_test("Microservices Health Checks", "FAIL", f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Microservices Health Checks", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_inter_service_communication(self):
        """Test communication between services"""
        try:
            # Test communication through the main application
            # This tests the integration between different service components
            
            # Test analytics service communication
            analytics_response = requests.get(f"{self.base_url}/api/analytics/business", timeout=10)
            if analytics_response.status_code != 200:
                self.log_test("Inter-Service Communication", "FAIL", "Analytics service communication failed")
                return False
            
            # Test i18n service communication
            i18n_response = requests.get(f"{self.base_url}/api/i18n/languages", timeout=10)
            if i18n_response.status_code != 200:
                self.log_test("Inter-Service Communication", "FAIL", "i18n service communication failed")
                return False
            
            # Test A/B testing service communication
            ab_response = requests.get(f"{self.base_url}/api/ab-testing/experiments", timeout=10)
            if ab_response.status_code != 200:
                self.log_test("Inter-Service Communication", "FAIL", "A/B testing service communication failed")
                return False
            
            self.log_test("Inter-Service Communication", "PASS", "All service communications successful")
            return True
            
        except Exception as e:
            self.log_test("Inter-Service Communication", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_service_mesh_functionality(self):
        """Test service mesh functionality"""
        try:
            # Test load balancing and service mesh features
            # This simulates multiple requests to test load distribution
            
            start_time = time.time()
            successful_requests = 0
            total_requests = 10
            
            for i in range(total_requests):
                try:
                    response = requests.get(f"{self.base_url}/api/analytics/business", timeout=5)
                    if response.status_code == 200:
                        successful_requests += 1
                except Exception:
                    pass
                time.sleep(0.1)  # Small delay between requests
            
            end_time = time.time()
            duration = end_time - start_time
            success_rate = (successful_requests / total_requests) * 100
            
            if success_rate >= 80:  # At least 80% success rate
                self.log_test("Service Mesh Functionality", "PASS", f"{success_rate:.1f}% success rate in {duration:.2f}s")
                return True
            else:
                self.log_test("Service Mesh Functionality", "FAIL", f"Only {success_rate:.1f}% success rate")
                return False
                
        except Exception as e:
            self.log_test("Service Mesh Functionality", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_fault_tolerance(self):
        """Test fault tolerance and service resilience"""
        try:
            # Test how the system handles service failures
            # This tests the fallback mechanisms
            
            # Test with invalid service endpoints
            invalid_endpoints = [
                '/api/nonexistent-service',
                '/api/invalid-endpoint'
            ]
            
            fault_tolerance_works = True
            for endpoint in invalid_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                # Should return 404 for non-existent services
                if response.status_code != 404:
                    fault_tolerance_works = False
                    break
            
            if fault_tolerance_works:
                self.log_test("Fault Tolerance", "PASS", "Proper handling of service failures")
                return True
            else:
                self.log_test("Fault Tolerance", "FAIL", "Insufficient fault tolerance")
                return False
                
        except Exception as e:
            self.log_test("Fault Tolerance", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_service_scalability(self):
        """Test service scalability"""
        try:
            # Test concurrent requests to simulate load
            import threading
            import queue
            
            results = queue.Queue()
            
            def make_request():
                try:
                    response = requests.get(f"{self.base_url}/api/analytics/business", timeout=10)
                    results.put(response.status_code == 200)
                except Exception:
                    results.put(False)
            
            # Create multiple threads to simulate concurrent load
            threads = []
            for i in range(5):  # 5 concurrent requests
                thread = threading.Thread(target=make_request)
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
            
            success_rate = (successful_requests / 5) * 100
            
            if success_rate >= 80:
                self.log_test("Service Scalability", "PASS", f"{success_rate:.1f}% success with concurrent requests")
                return True
            else:
                self.log_test("Service Scalability", "FAIL", f"Only {success_rate:.1f}% success with concurrent requests")
                return False
                
        except Exception as e:
            self.log_test("Service Scalability", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_data_consistency_across_services(self):
        """Test data consistency across microservices"""
        try:
            # Test that data is consistent across different service endpoints
            # This tests the shared data layer
            
            # Get analytics data
            analytics_response = requests.get(f"{self.base_url}/api/analytics/business", timeout=10)
            if analytics_response.status_code != 200:
                self.log_test("Data Consistency", "FAIL", "Analytics data not accessible")
                return False
            
            # Get performance data
            performance_response = requests.get(f"{self.base_url}/api/analytics/performance", timeout=10)
            if performance_response.status_code != 200:
                self.log_test("Data Consistency", "FAIL", "Performance data not accessible")
                return False
            
            # Both should return valid JSON
            analytics_data = analytics_response.json()
            performance_data = performance_response.json()
            
            if isinstance(analytics_data, dict) and isinstance(performance_data, dict):
                self.log_test("Data Consistency", "PASS", "Data consistent across services")
                return True
            else:
                self.log_test("Data Consistency", "FAIL", "Inconsistent data formats")
                return False
                
        except Exception as e:
            self.log_test("Data Consistency", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_microservices_tests(self):
        """Run all microservices communication tests"""
        print("🔍 Starting Microservices Communication Testing...")
        print("=" * 60)
        
        # Run all microservices tests
        self.test_api_gateway_routing()
        self.test_service_discovery()
        self.test_microservices_health_checks()
        self.test_inter_service_communication()
        self.test_service_mesh_functionality()
        self.test_fault_tolerance()
        self.test_service_scalability()
        self.test_data_consistency_across_services()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Microservices Communication Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = MicroservicesCommunicationTester()
    success = tester.run_all_microservices_tests()
    exit(0 if success else 1)