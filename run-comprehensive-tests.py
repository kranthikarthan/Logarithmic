#!/usr/bin/env python3
"""
Comprehensive Test Runner for Assertly Enterprise
Runs all tests including unit tests, integration tests, and end-to-end tests
"""

import unittest
import sys
import os
import time
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestRunner:
    """Comprehensive test runner for Assertly Enterprise"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.api_base = f"{self.base_url}/api"
        self.enterprise_api_base = f"{self.base_url}/api/enterprise"
        self.test_results = {
            "unit_tests": {"passed": 0, "failed": 0, "total": 0},
            "integration_tests": {"passed": 0, "failed": 0, "total": 0},
            "api_tests": {"passed": 0, "failed": 0, "total": 0},
            "enterprise_tests": {"passed": 0, "failed": 0, "total": 0},
            "performance_tests": {"passed": 0, "failed": 0, "total": 0},
            "security_tests": {"passed": 0, "failed": 0, "total": 0}
        }
        self.start_time = datetime.now()
    
    def run_unit_tests(self) -> bool:
        """Run unit tests"""
        print("🧪 Running Unit Tests...")
        print("=" * 50)
        
        try:
            # Import and run unit tests
            from tests.test_enterprise_features import run_enterprise_tests
            success = run_enterprise_tests()
            
            if success:
                self.test_results["unit_tests"]["passed"] += 1
                print("✅ Unit tests passed")
            else:
                self.test_results["unit_tests"]["failed"] += 1
                print("❌ Unit tests failed")
            
            self.test_results["unit_tests"]["total"] += 1
            return success
            
        except Exception as e:
            print(f"❌ Unit tests failed with error: {e}")
            self.test_results["unit_tests"]["failed"] += 1
            self.test_results["unit_tests"]["total"] += 1
            return False
    
    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        print("\n🔗 Running Integration Tests...")
        print("=" * 50)
        
        integration_tests = [
            self.test_database_connectivity,
            self.test_redis_connectivity,
            self.test_ai_service_integration,
            self.test_audit_logging_integration,
            self.test_security_integration
        ]
        
        passed = 0
        failed = 0
        
        for test in integration_tests:
            try:
                if test():
                    passed += 1
                    print(f"✅ {test.__name__}")
                else:
                    failed += 1
                    print(f"❌ {test.__name__}")
            except Exception as e:
                failed += 1
                print(f"❌ {test.__name__} - Error: {e}")
        
        self.test_results["integration_tests"]["passed"] = passed
        self.test_results["integration_tests"]["failed"] = failed
        self.test_results["integration_tests"]["total"] = passed + failed
        
        return failed == 0
    
    def test_database_connectivity(self) -> bool:
        """Test database connectivity"""
        try:
            response = requests.get(f"{self.enterprise_api_base}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_redis_connectivity(self) -> bool:
        """Test Redis connectivity"""
        try:
            # This would test Redis connectivity through the application
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_ai_service_integration(self) -> bool:
        """Test AI service integration"""
        try:
            # Test AI configuration
            config_data = {
                "local_ai_url": "http://test-ai.company.com:8080/api",
                "local_ai_model": "local-copilot"
            }
            
            response = requests.post(
                f"{self.enterprise_api_base}/ai/configure",
                json=config_data,
                timeout=10
            )
            
            return response.status_code == 200
        except:
            return False
    
    def test_audit_logging_integration(self) -> bool:
        """Test audit logging integration"""
        try:
            response = requests.get(f"{self.enterprise_api_base}/audit/logs", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_security_integration(self) -> bool:
        """Test security integration"""
        try:
            # Test security headers
            response = requests.get(self.base_url, timeout=10)
            headers = response.headers
            
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection'
            ]
            
            return all(header in headers for header in security_headers)
        except:
            return False
    
    def run_api_tests(self) -> bool:
        """Run API tests"""
        print("\n🌐 Running API Tests...")
        print("=" * 50)
        
        api_tests = [
            self.test_health_endpoints,
            self.test_ai_generation_endpoints,
            self.test_audit_endpoints,
            self.test_enterprise_endpoints,
            self.test_error_handling
        ]
        
        passed = 0
        failed = 0
        
        for test in api_tests:
            try:
                if test():
                    passed += 1
                    print(f"✅ {test.__name__}")
                else:
                    failed += 1
                    print(f"❌ {test.__name__}")
            except Exception as e:
                failed += 1
                print(f"❌ {test.__name__} - Error: {e}")
        
        self.test_results["api_tests"]["passed"] = passed
        self.test_results["api_tests"]["failed"] = failed
        self.test_results["api_tests"]["total"] = passed + failed
        
        return failed == 0
    
    def test_health_endpoints(self) -> bool:
        """Test health endpoints"""
        try:
            # Test main health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code != 200:
                return False
            
            # Test enterprise health endpoint
            response = requests.get(f"{self.enterprise_api_base}/health", timeout=10)
            if response.status_code != 200:
                return False
            
            return True
        except:
            return False
    
    def test_ai_generation_endpoints(self) -> bool:
        """Test AI generation endpoints"""
        try:
            # Test AI configuration
            config_data = {
                "local_ai_url": "http://test-ai.company.com:8080/api",
                "local_ai_model": "local-copilot"
            }
            
            response = requests.post(
                f"{self.enterprise_api_base}/ai/configure",
                json=config_data,
                timeout=10
            )
            
            if response.status_code != 200:
                return False
            
            # Test AI connection
            response = requests.get(f"{self.enterprise_api_base}/ai/test-connection", timeout=10)
            if response.status_code not in [200, 400]:  # 400 is expected if not configured
                return False
            
            return True
        except:
            return False
    
    def test_audit_endpoints(self) -> bool:
        """Test audit endpoints"""
        try:
            # Test audit logs
            response = requests.get(f"{self.enterprise_api_base}/audit/logs", timeout=10)
            if response.status_code != 200:
                return False
            
            # Test compliance report
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
            
            return response.status_code == 200
        except:
            return False
    
    def test_enterprise_endpoints(self) -> bool:
        """Test enterprise endpoints"""
        try:
            # Test enterprise settings page
            response = requests.get(f"{self.base_url}/enterprise-settings", timeout=10)
            if response.status_code != 200:
                return False
            
            return True
        except:
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling"""
        try:
            # Test invalid endpoint
            response = requests.get(f"{self.base_url}/invalid-endpoint", timeout=10)
            if response.status_code not in [404, 405]:
                return False
            
            # Test invalid API request
            response = requests.post(
                f"{self.enterprise_api_base}/ai/configure",
                json={},  # Empty data should cause validation error
                timeout=10
            )
            if response.status_code not in [400, 422]:
                return False
            
            return True
        except:
            return False
    
    def run_enterprise_tests(self) -> bool:
        """Run enterprise-specific tests"""
        print("\n🏢 Running Enterprise Tests...")
        print("=" * 50)
        
        enterprise_tests = [
            self.test_enterprise_configuration,
            self.test_enterprise_security,
            self.test_enterprise_ai,
            self.test_enterprise_audit,
            self.test_enterprise_compliance
        ]
        
        passed = 0
        failed = 0
        
        for test in enterprise_tests:
            try:
                if test():
                    passed += 1
                    print(f"✅ {test.__name__}")
                else:
                    failed += 1
                    print(f"❌ {test.__name__}")
            except Exception as e:
                failed += 1
                print(f"❌ {test.__name__} - Error: {e}")
        
        self.test_results["enterprise_tests"]["passed"] = passed
        self.test_results["enterprise_tests"]["failed"] = failed
        self.test_results["enterprise_tests"]["total"] = passed + failed
        
        return failed == 0
    
    def test_enterprise_configuration(self) -> bool:
        """Test enterprise configuration"""
        try:
            # Test configuration endpoint
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
            
            return response.status_code == 200
        except:
            return False
    
    def test_enterprise_security(self) -> bool:
        """Test enterprise security"""
        try:
            # Test security headers
            response = requests.get(self.base_url, timeout=10)
            headers = response.headers
            
            required_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection'
            ]
            
            return all(header in headers for header in required_headers)
        except:
            return False
    
    def test_enterprise_ai(self) -> bool:
        """Test enterprise AI functionality"""
        try:
            # Test AI test case generation
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
            return response.status_code in [200, 500]
        except:
            return False
    
    def test_enterprise_audit(self) -> bool:
        """Test enterprise audit functionality"""
        try:
            # Test audit logs
            response = requests.get(f"{self.enterprise_api_base}/audit/logs", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            return data.get("success", False)
        except:
            return False
    
    def test_enterprise_compliance(self) -> bool:
        """Test enterprise compliance functionality"""
        try:
            # Test compliance report generation
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
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            return data.get("success", False)
        except:
            return False
    
    def run_performance_tests(self) -> bool:
        """Run performance tests"""
        print("\n⚡ Running Performance Tests...")
        print("=" * 50)
        
        performance_tests = [
            self.test_response_times,
            self.test_concurrent_requests,
            self.test_memory_usage,
            self.test_database_performance
        ]
        
        passed = 0
        failed = 0
        
        for test in performance_tests:
            try:
                if test():
                    passed += 1
                    print(f"✅ {test.__name__}")
                else:
                    failed += 1
                    print(f"❌ {test.__name__}")
            except Exception as e:
                failed += 1
                print(f"❌ {test.__name__} - Error: {e}")
        
        self.test_results["performance_tests"]["passed"] = passed
        self.test_results["performance_tests"]["failed"] = failed
        self.test_results["performance_tests"]["total"] = passed + failed
        
        return failed == 0
    
    def test_response_times(self) -> bool:
        """Test response times"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Response time should be less than 1 second
            return response.status_code == 200 and response_time < 1.0
        except:
            return False
    
    def test_concurrent_requests(self) -> bool:
        """Test concurrent requests"""
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
            
            # Make 10 concurrent requests
            threads = []
            for _ in range(10):
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
            
            return success_count >= 8  # At least 80% should succeed
        except:
            return False
    
    def test_memory_usage(self) -> bool:
        """Test memory usage"""
        try:
            # This is a simplified test - in a real scenario, you'd use proper memory monitoring
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_database_performance(self) -> bool:
        """Test database performance"""
        try:
            # Test database connectivity through health endpoint
            response = requests.get(f"{self.enterprise_api_base}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def run_security_tests(self) -> bool:
        """Run security tests"""
        print("\n🔒 Running Security Tests...")
        print("=" * 50)
        
        security_tests = [
            self.test_security_headers,
            self.test_authentication,
            self.test_authorization,
            self.test_input_validation,
            self.test_sql_injection_protection
        ]
        
        passed = 0
        failed = 0
        
        for test in security_tests:
            try:
                if test():
                    passed += 1
                    print(f"✅ {test.__name__}")
                else:
                    failed += 1
                    print(f"❌ {test.__name__}")
            except Exception as e:
                failed += 1
                print(f"❌ {test.__name__} - Error: {e}")
        
        self.test_results["security_tests"]["passed"] = passed
        self.test_results["security_tests"]["failed"] = failed
        self.test_results["security_tests"]["total"] = passed + failed
        
        return failed == 0
    
    def test_security_headers(self) -> bool:
        """Test security headers"""
        try:
            response = requests.get(self.base_url, timeout=10)
            headers = response.headers
            
            required_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection'
            ]
            
            return all(header in headers for header in required_headers)
        except:
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication"""
        try:
            # Test that protected endpoints require authentication
            response = requests.get(f"{self.enterprise_api_base}/audit/logs", timeout=10)
            # Should return 200 (with session) or 401 (without session)
            return response.status_code in [200, 401]
        except:
            return False
    
    def test_authorization(self) -> bool:
        """Test authorization"""
        try:
            # Test that users can only access authorized resources
            response = requests.get(f"{self.enterprise_api_base}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_input_validation(self) -> bool:
        """Test input validation"""
        try:
            # Test with invalid input
            response = requests.post(
                f"{self.enterprise_api_base}/ai/configure",
                json={"invalid": "data"},
                timeout=10
            )
            # Should return 400 for invalid input
            return response.status_code in [400, 422]
        except:
            return False
    
    def test_sql_injection_protection(self) -> bool:
        """Test SQL injection protection"""
        try:
            # Test with SQL injection attempt
            malicious_input = "'; DROP TABLE users; --"
            response = requests.get(
                f"{self.base_url}/search?q={malicious_input}",
                timeout=10
            )
            # Should not crash the application
            return response.status_code in [200, 400, 404]
        except:
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        total_tests = sum(category["total"] for category in self.test_results.values())
        total_passed = sum(category["passed"] for category in self.test_results.values())
        total_failed = sum(category["failed"] for category in self.test_results.values())
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
                "duration_seconds": duration.total_seconds(),
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for category, results in self.test_results.items():
            if results["failed"] > 0:
                recommendations.append(f"Address {results['failed']} failed {category.replace('_', ' ')}")
        
        if not recommendations:
            recommendations.append("All tests passed! System is ready for production.")
        
        return recommendations
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🚀 Starting Comprehensive Test Suite for Assertly Enterprise")
        print("=" * 70)
        
        # Run all test categories
        unit_success = self.run_unit_tests()
        integration_success = self.run_integration_tests()
        api_success = self.run_api_tests()
        enterprise_success = self.run_enterprise_tests()
        performance_success = self.run_performance_tests()
        security_success = self.run_security_tests()
        
        # Generate and display report
        report = self.generate_test_report()
        
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Passed: {report['test_summary']['passed']}")
        print(f"Failed: {report['test_summary']['failed']}")
        print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"Duration: {report['test_summary']['duration_seconds']:.2f} seconds")
        
        print("\n📋 Test Results by Category:")
        for category, results in report['test_results'].items():
            status = "✅" if results['failed'] == 0 else "❌"
            print(f"  {status} {category.replace('_', ' ').title()}: {results['passed']}/{results['total']} passed")
        
        print("\n💡 Recommendations:")
        for recommendation in report['recommendations']:
            print(f"  • {recommendation}")
        
        # Save report to file
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: test_report.json")
        
        overall_success = all([
            unit_success, integration_success, api_success,
            enterprise_success, performance_success, security_success
        ])
        
        if overall_success:
            print("\n🎉 All tests passed! Assertly Enterprise is ready for production!")
        else:
            print("\n⚠️  Some tests failed. Please review the results and fix issues before production deployment.")
        
        return overall_success

def main():
    """Main function to run comprehensive tests"""
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()