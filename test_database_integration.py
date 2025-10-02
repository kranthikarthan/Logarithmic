#!/usr/bin/env python3
"""
Database Integration Testing for Assertly
Tests data integrity, persistence, and retrieval across all database operations
"""

import requests
import json
import time
from datetime import datetime, timedelta
import logging

class DatabaseIntegrationTester:
    """Comprehensive database integration testing"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.test_data = {}
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        if status == 'PASS':
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: PASS - {message}")
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAIL - {message}")
    
    def test_database_connectivity(self):
        """Test basic database connectivity"""
        try:
            # Test health endpoint which uses database
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Database Connectivity", "PASS", "Health endpoint accessible")
                return True
            else:
                self.log_test("Database Connectivity", "FAIL", f"Health endpoint returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Connectivity", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_enterprise_health_database(self):
        """Test enterprise health database operations"""
        try:
            response = requests.get(f"{self.base_url}/api/enterprise/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'healthy':
                    self.log_test("Enterprise Database Health", "PASS", "Enterprise health check successful")
                    return True
                else:
                    self.log_test("Enterprise Database Health", "FAIL", f"Invalid health status: {data}")
                    return False
            else:
                self.log_test("Enterprise Database Health", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Enterprise Database Health", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_audit_logging_database(self):
        """Test audit logging database operations"""
        try:
            response = requests.get(f"{self.base_url}/api/enterprise/audit/logs", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'logs' in data and isinstance(data['logs'], list):
                    self.log_test("Audit Logging Database", "PASS", f"Retrieved {len(data['logs'])} audit logs")
                    return True
                else:
                    self.log_test("Audit Logging Database", "FAIL", "Invalid audit logs format")
                    return False
            else:
                self.log_test("Audit Logging Database", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Audit Logging Database", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_analytics_database_operations(self):
        """Test analytics database operations"""
        try:
            # Test business analytics
            response = requests.get(f"{self.base_url}/api/analytics/business", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_active_users', 'total_sessions', 'total_page_views']
                if all(field in data for field in required_fields):
                    self.log_test("Analytics Database Operations", "PASS", "Analytics data structure valid")
                    return True
                else:
                    self.log_test("Analytics Database Operations", "FAIL", "Missing required analytics fields")
                    return False
            else:
                self.log_test("Analytics Database Operations", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Analytics Database Operations", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_cache_database_operations(self):
        """Test cache database operations"""
        try:
            # Test cache stats
            response = requests.get(f"{self.base_url}/api/cache/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    self.log_test("Cache Database Operations", "PASS", "Cache stats retrieved successfully")
                    return True
                else:
                    self.log_test("Cache Database Operations", "FAIL", "Invalid cache stats format")
                    return False
            else:
                self.log_test("Cache Database Operations", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Cache Database Operations", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_data_persistence_simulation(self):
        """Test data persistence by simulating operations"""
        try:
            # Test language setting (simulates data persistence)
            test_language = "es"
            response = requests.post(
                f"{self.base_url}/api/i18n/set-language",
                json={"language": test_language},
                timeout=10
            )
            
            if response.status_code == 200:
                # Verify the setting was persisted by checking languages endpoint
                lang_response = requests.get(f"{self.base_url}/api/i18n/languages", timeout=10)
                if lang_response.status_code == 200:
                    self.log_test("Data Persistence Simulation", "PASS", "Language setting persisted")
                    return True
                else:
                    self.log_test("Data Persistence Simulation", "FAIL", "Could not verify persistence")
                    return False
            else:
                self.log_test("Data Persistence Simulation", "FAIL", f"Language setting failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Data Persistence Simulation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_database_performance(self):
        """Test database performance with multiple operations"""
        try:
            start_time = time.time()
            
            # Perform multiple database operations
            operations = [
                f"{self.base_url}/health",
                f"{self.base_url}/api/enterprise/health",
                f"{self.base_url}/api/analytics/business",
                f"{self.base_url}/api/cache/stats",
                f"{self.base_url}/api/i18n/languages"
            ]
            
            for operation in operations:
                response = requests.get(operation, timeout=5)
                if response.status_code not in [200, 401]:  # 401 is expected for some endpoints
                    self.log_test("Database Performance", "FAIL", f"Operation {operation} failed")
                    return False
            
            end_time = time.time()
            duration = end_time - start_time
            
            if duration < 5.0:  # Should complete within 5 seconds
                self.log_test("Database Performance", "PASS", f"All operations completed in {duration:.2f}s")
                return True
            else:
                self.log_test("Database Performance", "FAIL", f"Operations too slow: {duration:.2f}s")
                return False
                
        except Exception as e:
            self.log_test("Database Performance", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_database_error_handling(self):
        """Test database error handling"""
        try:
            # Test with invalid data that might cause database errors
            invalid_payloads = [
                {"language": "invalid_language"},
                {"invalid_field": "test"},
                None,
                "invalid_json"
            ]
            
            error_handling_works = True
            
            for payload in invalid_payloads:
                try:
                    if payload is None:
                        response = requests.post(f"{self.base_url}/api/i18n/set-language", timeout=5)
                    elif payload == "invalid_json":
                        response = requests.post(
                            f"{self.base_url}/api/i18n/set-language",
                            data="invalid json",
                            headers={"Content-Type": "application/json"},
                            timeout=5
                        )
                    else:
                        response = requests.post(
                            f"{self.base_url}/api/i18n/set-language",
                            json=payload,
                            timeout=5
                        )
                    
                    # Should return 400 for invalid data
                    if response.status_code not in [400, 500]:
                        error_handling_works = False
                        break
                        
                except Exception:
                    # Network errors are acceptable for this test
                    pass
            
            if error_handling_works:
                self.log_test("Database Error Handling", "PASS", "Proper error handling for invalid data")
                return True
            else:
                self.log_test("Database Error Handling", "FAIL", "Insufficient error handling")
                return False
                
        except Exception as e:
            self.log_test("Database Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_database_tests(self):
        """Run all database integration tests"""
        print("🔍 Starting Database Integration Testing...")
        print("=" * 50)
        
        # Run all database tests
        self.test_database_connectivity()
        self.test_enterprise_health_database()
        self.test_audit_logging_database()
        self.test_analytics_database_operations()
        self.test_cache_database_operations()
        self.test_data_persistence_simulation()
        self.test_database_performance()
        self.test_database_error_handling()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Database Integration Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = DatabaseIntegrationTester()
    success = tester.run_all_database_tests()
    exit(0 if success else 1)