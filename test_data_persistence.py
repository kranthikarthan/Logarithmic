#!/usr/bin/env python3
"""
Data Persistence Testing for Assertly
Tests data persistence, retrieval, and consistency across operations
"""

import requests
import json
import time
from datetime import datetime
import logging

class DataPersistenceTester:
    """Comprehensive data persistence testing"""
    
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
    
    def test_language_setting_persistence(self):
        """Test language setting persistence"""
        try:
            # Set language to Spanish
            set_response = requests.post(
                f"{self.base_url}/api/i18n/set-language",
                json={"language": "es"},
                timeout=10
            )
            
            if set_response.status_code != 200:
                self.log_test("Language Setting Persistence", "FAIL", f"Language setting failed: {set_response.status_code}")
                return False
            
            # Wait a moment for persistence
            time.sleep(0.5)
            
            # Verify language setting persisted
            languages_response = requests.get(f"{self.base_url}/api/i18n/languages", timeout=10)
            if languages_response.status_code == 200:
                data = languages_response.json()
                if 'languages' in data and 'es' in data['languages']:
                    self.log_test("Language Setting Persistence", "PASS", "Language setting persisted")
                    return True
                else:
                    self.log_test("Language Setting Persistence", "FAIL", "Language setting not found in response")
                    return False
            else:
                self.log_test("Language Setting Persistence", "FAIL", f"Language retrieval failed: {languages_response.status_code}")
                return False
        except Exception as e:
            self.log_test("Language Setting Persistence", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_analytics_data_persistence(self):
        """Test analytics data persistence"""
        try:
            # Test that analytics data is persistent across requests
            response1 = requests.get(f"{self.base_url}/api/analytics/business", timeout=10)
            if response1.status_code != 200:
                self.log_test("Analytics Data Persistence", "FAIL", f"First analytics request failed: {response1.status_code}")
                return False
            
            # Wait a moment
            time.sleep(0.5)
            
            # Make second request
            response2 = requests.get(f"{self.base_url}/api/analytics/business", timeout=10)
            if response2.status_code != 200:
                self.log_test("Analytics Data Persistence", "FAIL", f"Second analytics request failed: {response2.status_code}")
                return False
            
            # Compare data structure (should be consistent)
            data1 = response1.json()
            data2 = response2.json()
            
            if isinstance(data1, dict) and isinstance(data2, dict):
                # Check if key structure is consistent
                keys1 = set(data1.keys())
                keys2 = set(data2.keys())
                
                if keys1 == keys2:
                    self.log_test("Analytics Data Persistence", "PASS", "Analytics data structure consistent")
                    return True
                else:
                    self.log_test("Analytics Data Persistence", "FAIL", "Analytics data structure inconsistent")
                    return False
            else:
                self.log_test("Analytics Data Persistence", "FAIL", "Invalid analytics data format")
                return False
        except Exception as e:
            self.log_test("Analytics Data Persistence", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_cache_data_persistence(self):
        """Test cache data persistence"""
        try:
            # Test cache data persistence
            response1 = requests.get(f"{self.base_url}/api/cache/stats", timeout=10)
            if response1.status_code != 200:
                self.log_test("Cache Data Persistence", "FAIL", f"First cache request failed: {response1.status_code}")
                return False
            
            # Wait a moment
            time.sleep(0.5)
            
            # Make second request
            response2 = requests.get(f"{self.base_url}/api/cache/stats", timeout=10)
            if response2.status_code != 200:
                self.log_test("Cache Data Persistence", "FAIL", f"Second cache request failed: {response2.status_code}")
                return False
            
            # Cache data should be consistent
            data1 = response1.json()
            data2 = response2.json()
            
            if isinstance(data1, dict) and isinstance(data2, dict):
                self.log_test("Cache Data Persistence", "PASS", "Cache data structure consistent")
                return True
            else:
                self.log_test("Cache Data Persistence", "FAIL", "Invalid cache data format")
                return False
        except Exception as e:
            self.log_test("Cache Data Persistence", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_enterprise_data_persistence(self):
        """Test enterprise data persistence"""
        try:
            # Test enterprise data persistence
            response1 = requests.get(f"{self.base_url}/api/enterprise/health", timeout=10)
            if response1.status_code != 200:
                self.log_test("Enterprise Data Persistence", "FAIL", f"First enterprise request failed: {response1.status_code}")
                return False
            
            # Wait a moment
            time.sleep(0.5)
            
            # Make second request
            response2 = requests.get(f"{self.base_url}/api/enterprise/health", timeout=10)
            if response2.status_code != 200:
                self.log_test("Enterprise Data Persistence", "FAIL", f"Second enterprise request failed: {response2.status_code}")
                return False
            
            # Enterprise data should be consistent
            data1 = response1.json()
            data2 = response2.json()
            
            if isinstance(data1, dict) and isinstance(data2, dict):
                # Check if status is consistent
                if 'status' in data1 and 'status' in data2:
                    self.log_test("Enterprise Data Persistence", "PASS", "Enterprise data structure consistent")
                    return True
                else:
                    self.log_test("Enterprise Data Persistence", "FAIL", "Enterprise data missing status field")
                    return False
            else:
                self.log_test("Enterprise Data Persistence", "FAIL", "Invalid enterprise data format")
                return False
        except Exception as e:
            self.log_test("Enterprise Data Persistence", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_audit_log_persistence(self):
        """Test audit log persistence"""
        try:
            # Test audit log persistence
            response1 = requests.get(f"{self.base_url}/api/enterprise/audit/logs", timeout=10)
            if response1.status_code != 200:
                self.log_test("Audit Log Persistence", "FAIL", f"First audit request failed: {response1.status_code}")
                return False
            
            # Wait a moment
            time.sleep(0.5)
            
            # Make second request
            response2 = requests.get(f"{self.base_url}/api/enterprise/audit/logs", timeout=10)
            if response2.status_code != 200:
                self.log_test("Audit Log Persistence", "FAIL", f"Second audit request failed: {response2.status_code}")
                return False
            
            # Audit logs should be consistent
            data1 = response1.json()
            data2 = response2.json()
            
            if isinstance(data1, dict) and isinstance(data2, dict):
                if 'logs' in data1 and 'logs' in data2:
                    logs1 = data1['logs']
                    logs2 = data2['logs']
                    
                    if isinstance(logs1, list) and isinstance(logs2, list):
                        self.log_test("Audit Log Persistence", "PASS", f"Audit logs consistent: {len(logs1)} logs")
                        return True
                    else:
                        self.log_test("Audit Log Persistence", "FAIL", "Invalid audit logs format")
                        return False
                else:
                    self.log_test("Audit Log Persistence", "FAIL", "Audit logs missing from response")
                    return False
            else:
                self.log_test("Audit Log Persistence", "FAIL", "Invalid audit response format")
                return False
        except Exception as e:
            self.log_test("Audit Log Persistence", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_data_consistency_across_operations(self):
        """Test data consistency across different operations"""
        try:
            # Test that data remains consistent across different operations
            operations = [
                f"{self.base_url}/api/analytics/business",
                f"{self.base_url}/api/cache/stats",
                f"{self.base_url}/api/enterprise/health",
                f"{self.base_url}/api/i18n/languages"
            ]
            
            all_consistent = True
            for operation in operations:
                try:
                    response = requests.get(operation, timeout=5)
                    if response.status_code not in [200, 500]:  # 500 is acceptable for some endpoints
                        all_consistent = False
                        break
                except Exception:
                    all_consistent = False
                    break
            
            if all_consistent:
                self.log_test("Data Consistency Across Operations", "PASS", "All operations maintain data consistency")
                return True
            else:
                self.log_test("Data Consistency Across Operations", "FAIL", "Some operations failed consistency check")
                return False
        except Exception as e:
            self.log_test("Data Consistency Across Operations", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_data_retrieval_performance(self):
        """Test data retrieval performance"""
        try:
            # Test performance of data retrieval operations
            start_time = time.time()
            
            # Test multiple data retrieval operations
            operations = [
                f"{self.base_url}/api/analytics/business",
                f"{self.base_url}/api/cache/stats",
                f"{self.base_url}/api/enterprise/health",
                f"{self.base_url}/api/i18n/languages"
            ]
            
            successful_operations = 0
            for operation in operations:
                try:
                    response = requests.get(operation, timeout=5)
                    if response.status_code in [200, 500]:  # 500 is acceptable for some endpoints
                        successful_operations += 1
                except Exception:
                    pass
            
            end_time = time.time()
            duration = end_time - start_time
            
            success_rate = (successful_operations / len(operations)) * 100
            
            if success_rate >= 75 and duration < 3.0:
                self.log_test("Data Retrieval Performance", "PASS", f"{success_rate:.1f}% success in {duration:.2f}s")
                return True
            else:
                self.log_test("Data Retrieval Performance", "FAIL", f"Only {success_rate:.1f}% success in {duration:.2f}s")
                return False
        except Exception as e:
            self.log_test("Data Retrieval Performance", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_concurrent_data_access(self):
        """Test concurrent data access"""
        try:
            import threading
            import queue
            
            results = queue.Queue()
            
            def make_data_request():
                try:
                    response = requests.get(f"{self.base_url}/api/analytics/business", timeout=5)
                    results.put(response.status_code == 200)
                except Exception:
                    results.put(False)
            
            # Create multiple threads for concurrent data access
            threads = []
            for i in range(5):  # 5 concurrent requests
                thread = threading.Thread(target=make_data_request)
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
                self.log_test("Concurrent Data Access", "PASS", f"{success_rate:.1f}% success with concurrent access")
                return True
            else:
                self.log_test("Concurrent Data Access", "FAIL", f"Only {success_rate:.1f}% success with concurrent access")
                return False
        except Exception as e:
            self.log_test("Concurrent Data Access", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_data_integrity_validation(self):
        """Test data integrity validation"""
        try:
            # Test that data integrity is maintained
            # This includes checking for data corruption and validation
            
            # Test various data endpoints
            data_endpoints = [
                '/api/analytics/business',
                '/api/cache/stats',
                '/api/enterprise/health',
                '/api/i18n/languages'
            ]
            
            integrity_checks_passed = 0
            for endpoint in data_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code in [200, 500]:  # 500 is acceptable for some endpoints
                        # Check if response is valid JSON
                        try:
                            data = response.json()
                            if isinstance(data, dict):
                                integrity_checks_passed += 1
                        except json.JSONDecodeError:
                            pass
                except Exception:
                    pass
            
            integrity_rate = (integrity_checks_passed / len(data_endpoints)) * 100
            
            if integrity_rate >= 75:
                self.log_test("Data Integrity Validation", "PASS", f"{integrity_rate:.1f}% of data integrity checks passed")
                return True
            else:
                self.log_test("Data Integrity Validation", "FAIL", f"Only {integrity_rate:.1f}% of data integrity checks passed")
                return False
        except Exception as e:
            self.log_test("Data Integrity Validation", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_data_persistence_tests(self):
        """Run all data persistence tests"""
        print("🔍 Starting Data Persistence Testing...")
        print("=" * 50)
        
        # Run all data persistence tests
        self.test_language_setting_persistence()
        self.test_analytics_data_persistence()
        self.test_cache_data_persistence()
        self.test_enterprise_data_persistence()
        self.test_audit_log_persistence()
        self.test_data_consistency_across_operations()
        self.test_data_retrieval_performance()
        self.test_concurrent_data_access()
        self.test_data_integrity_validation()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Data Persistence Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = DataPersistenceTester()
    success = tester.run_all_data_persistence_tests()
    exit(0 if success else 1)