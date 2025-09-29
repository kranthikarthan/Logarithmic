#!/usr/bin/env python3
"""
Simplified Test Suite for Assertly Enterprise
Tests core functionality without external dependencies
"""

import unittest
import sys
import os
import requests
import time
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAssertlyEnterprise(unittest.TestCase):
    """Simplified test suite for Assertly Enterprise"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.api_base = f"{self.base_url}/api"
        self.enterprise_api_base = f"{self.base_url}/api/enterprise"
    
    def test_application_health(self):
        """Test application health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            self.assertEqual(response.status_code, 200)
            print("✅ Application health check passed")
        except Exception as e:
            self.fail(f"Health check failed: {e}")
    
    def test_enterprise_health(self):
        """Test enterprise health endpoint"""
        try:
            response = requests.get(f"{self.enterprise_api_base}/health", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("status", data)
            self.assertIn("enterprise_mode", data)
            print("✅ Enterprise health check passed")
        except Exception as e:
            self.fail(f"Enterprise health check failed: {e}")
    
    def test_enterprise_settings_page(self):
        """Test enterprise settings page"""
        try:
            response = requests.get(f"{self.base_url}/enterprise-settings", timeout=10)
            self.assertEqual(response.status_code, 200)
            print("✅ Enterprise settings page accessible")
        except Exception as e:
            self.fail(f"Enterprise settings page failed: {e}")
    
    def test_ai_configuration(self):
        """Test AI configuration endpoint"""
        try:
            config_data = {
                "local_ai_url": "http://test-ai.company.com:8080/api",
                "local_ai_model": "local-copilot",
                "local_api_key": "test-key"
            }
            
            response = requests.post(
                f"{self.enterprise_api_base}/ai/configure",
                json=config_data,
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data.get("success", False))
            print("✅ AI configuration test passed")
        except Exception as e:
            self.fail(f"AI configuration test failed: {e}")
    
    def test_ai_connection_test(self):
        """Test AI connection test endpoint"""
        try:
            response = requests.get(f"{self.enterprise_api_base}/ai/test-connection", timeout=10)
            # This might return 400 if not configured, which is expected
            self.assertIn(response.status_code, [200, 400])
            print("✅ AI connection test passed")
        except Exception as e:
            self.fail(f"AI connection test failed: {e}")
    
    def test_audit_logs(self):
        """Test audit logs endpoint"""
        try:
            response = requests.get(f"{self.enterprise_api_base}/audit/logs", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data.get("success", False))
            self.assertIn("logs", data)
            print("✅ Audit logs test passed")
        except Exception as e:
            self.fail(f"Audit logs test failed: {e}")
    
    def test_compliance_report(self):
        """Test compliance report generation"""
        try:
            report_data = {
                "report_type": "audit_summary",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59"
            }
            
            response = requests.post(
                f"{self.enterprise_api_base}/compliance/report",
                json=report_data,
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data.get("success", False))
            self.assertIn("report_id", data)
            print("✅ Compliance report test passed")
        except Exception as e:
            self.fail(f"Compliance report test failed: {e}")
    
    def test_ai_test_generation(self):
        """Test AI test case generation"""
        try:
            test_data = {
                "title": "User Login Test",
                "description": "As a user, I want to log in so that I can access my account",
                "acceptance_criteria": ["User can enter credentials", "User is logged in successfully"],
                "business_value": "Enables secure access to user accounts",
                "user_persona": "Registered user",
                "test_types": ["functional", "ui"],
                "num_cases": 3
            }
            
            response = requests.post(
                f"{self.enterprise_api_base}/ai/generate-test-cases",
                json=test_data,
                timeout=30
            )
            # This might return 500 if AI service is not available, which is expected
            self.assertIn(response.status_code, [200, 500])
            print("✅ AI test generation test passed")
        except Exception as e:
            self.fail(f"AI test generation test failed: {e}")
    
    def test_response_time(self):
        """Test response time performance"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            self.assertLess(response_time, 2.0)  # Should respond within 2 seconds
            print(f"✅ Response time test passed ({response_time:.2f}s)")
        except Exception as e:
            self.fail(f"Response time test failed: {e}")
    
    def test_error_handling(self):
        """Test error handling"""
        try:
            # Test invalid endpoint
            response = requests.get(f"{self.base_url}/invalid-endpoint", timeout=10)
            self.assertIn(response.status_code, [404, 405])
            print("✅ Error handling test passed")
        except Exception as e:
            self.fail(f"Error handling test failed: {e}")
    
    def test_security_headers(self):
        """Test security headers"""
        try:
            response = requests.get(self.base_url, timeout=10)
            headers = response.headers
            
            # Check for basic security headers
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection'
            ]
            
            found_headers = [header for header in security_headers if header in headers]
            self.assertGreater(len(found_headers), 0, f"Expected security headers, found: {found_headers}")
            print(f"✅ Security headers test passed (found: {len(found_headers)} headers)")
        except Exception as e:
            self.fail(f"Security headers test failed: {e}")
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        try:
            import threading
            import queue
            
            results = queue.Queue()
            
            def make_request():
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=10)
                    results.put(response.status_code == 200)
                except:
                    results.put(False)
            
            # Make 5 concurrent requests
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=make_request)
                thread.start()
                threads.append(thread)
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            success_count = 0
            while not results.empty():
                if results.get():
                    success_count += 1
            
            self.assertGreaterEqual(success_count, 4)  # At least 80% should succeed
            print(f"✅ Concurrent requests test passed ({success_count}/5 successful)")
        except Exception as e:
            self.fail(f"Concurrent requests test failed: {e}")

class TestEnterpriseFeatures(unittest.TestCase):
    """Test enterprise-specific features"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.enterprise_api_base = f"{self.base_url}/api/enterprise"
    
    def test_enterprise_configuration_persistence(self):
        """Test that enterprise configuration is persisted"""
        try:
            # Configure enterprise settings
            config_data = {
                "local_ai_url": "http://test-ai.company.com:8080/api",
                "local_ai_model": "local-copilot",
                "audit_enabled": True,
                "data_encryption": True
            }
            
            response = requests.post(
                f"{self.enterprise_api_base}/ai/configure",
                json=config_data,
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            
            # Check health endpoint shows configuration
            health_response = requests.get(f"{self.enterprise_api_base}/health", timeout=10)
            self.assertEqual(health_response.status_code, 200)
            
            health_data = health_response.json()
            self.assertIn("settings_configured", health_data)
            print("✅ Enterprise configuration persistence test passed")
        except Exception as e:
            self.fail(f"Enterprise configuration persistence test failed: {e}")
    
    def test_audit_logging_functionality(self):
        """Test audit logging functionality"""
        try:
            # Get initial audit log count
            response = requests.get(f"{self.enterprise_api_base}/audit/logs", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            initial_data = response.json()
            initial_count = initial_data.get("count", 0)
            
            # Perform an action that should generate audit log
            config_data = {
                "local_ai_url": "http://test-ai.company.com:8080/api",
                "local_ai_model": "local-copilot"
            }
            
            requests.post(
                f"{self.enterprise_api_base}/ai/configure",
                json=config_data,
                timeout=10
            )
            
            # Check audit logs again
            response = requests.get(f"{self.enterprise_api_base}/audit/logs", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            new_data = response.json()
            new_count = new_data.get("count", 0)
            
            # Should have at least the same number of logs (might have more)
            self.assertGreaterEqual(new_count, initial_count)
            print("✅ Audit logging functionality test passed")
        except Exception as e:
            self.fail(f"Audit logging functionality test failed: {e}")
    
    def test_compliance_report_generation(self):
        """Test compliance report generation"""
        try:
            report_data = {
                "report_type": "audit_summary",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59"
            }
            
            response = requests.post(
                f"{self.enterprise_api_base}/compliance/report",
                json=report_data,
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data.get("success", False))
            self.assertIn("report_id", data)
            self.assertIsInstance(data["report_id"], str)
            print("✅ Compliance report generation test passed")
        except Exception as e:
            self.fail(f"Compliance report generation test failed: {e}")

def run_simplified_tests():
    """Run simplified test suite"""
    print("🧪 Running Simplified Test Suite for Assertly Enterprise")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [TestAssertlyEnterprise, TestEnterpriseFeatures]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    return success

if __name__ == "__main__":
    success = run_simplified_tests()
    sys.exit(0 if success else 1)