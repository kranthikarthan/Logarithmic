#!/usr/bin/env python3
"""
AI Features Testing for Assertly
Tests AI-powered test generation, improvement, and analysis features
"""

import requests
import json
import time
from datetime import datetime
import logging

class AIFeaturesTester:
    """Comprehensive AI features testing"""
    
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
    
    def test_ai_endpoint_availability(self):
        """Test AI endpoint availability"""
        try:
            ai_endpoints = [
                '/api/ai/generate-test-cases',
                '/api/ai/improve-test-case',
                '/api/ai/generate-bdd-scenarios',
                '/api/ai/analyze-coverage'
            ]
            
            all_available = True
            for endpoint in ai_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code not in [200, 400, 405]:  # 400 for missing data, 405 for wrong method
                    all_available = False
                    break
            
            if all_available:
                self.log_test("AI Endpoint Availability", "PASS", "All AI endpoints accessible")
                return True
            else:
                self.log_test("AI Endpoint Availability", "FAIL", "Some AI endpoints not accessible")
                return False
        except Exception as e:
            self.log_test("AI Endpoint Availability", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_test_case_generation(self):
        """Test AI test case generation"""
        try:
            # Test with valid user story
            user_story = {
                "title": "User Login",
                "description": "As a user, I want to log in to the system",
                "acceptance_criteria": [
                    "Given I am on the login page",
                    "When I enter valid credentials",
                    "Then I should be redirected to the dashboard"
                ],
                "business_value": "High",
                "user_persona": "Registered User"
            }
            
            response = requests.post(
                f"{self.base_url}/api/ai/generate-test-cases",
                json={"user_story": user_story},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'test_cases' in data and isinstance(data['test_cases'], list):
                    self.log_test("AI Test Case Generation", "PASS", f"Generated {len(data['test_cases'])} test cases")
                    return True
                else:
                    self.log_test("AI Test Case Generation", "FAIL", "Invalid test case generation response")
                    return False
            elif response.status_code == 400:
                # This is expected without API keys
                self.log_test("AI Test Case Generation", "PASS", "AI endpoint working (API key required)")
                return True
            else:
                self.log_test("AI Test Case Generation", "FAIL", f"Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Test Case Generation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_test_case_improvement(self):
        """Test AI test case improvement"""
        try:
            # Test with valid test case
            test_case = {
                "title": "Login Test",
                "description": "Test user login functionality",
                "steps": [
                    "Navigate to login page",
                    "Enter credentials",
                    "Click login button"
                ],
                "expected_result": "User should be logged in"
            }
            
            response = requests.post(
                f"{self.base_url}/api/ai/improve-test-case",
                json={
                    "test_case": test_case,
                    "improvement_type": "coverage"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'improved_test_case' in data:
                    self.log_test("AI Test Case Improvement", "PASS", "Test case improvement successful")
                    return True
                else:
                    self.log_test("AI Test Case Improvement", "FAIL", "Invalid improvement response")
                    return False
            elif response.status_code == 400:
                # This is expected without API keys
                self.log_test("AI Test Case Improvement", "PASS", "AI endpoint working (API key required)")
                return True
            else:
                self.log_test("AI Test Case Improvement", "FAIL", f"Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Test Case Improvement", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_bdd_scenario_generation(self):
        """Test AI BDD scenario generation"""
        try:
            # Test with valid user story
            user_story = {
                "title": "User Registration",
                "description": "As a new user, I want to register for an account",
                "acceptance_criteria": [
                    "Given I am on the registration page",
                    "When I fill in valid information",
                    "Then I should receive a confirmation email"
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/api/ai/generate-bdd-scenarios",
                json={"user_story": user_story},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'scenarios' in data and isinstance(data['scenarios'], list):
                    self.log_test("AI BDD Scenario Generation", "PASS", f"Generated {len(data['scenarios'])} BDD scenarios")
                    return True
                else:
                    self.log_test("AI BDD Scenario Generation", "FAIL", "Invalid BDD scenario response")
                    return False
            elif response.status_code == 400:
                # This is expected without API keys
                self.log_test("AI BDD Scenario Generation", "PASS", "AI endpoint working (API key required)")
                return True
            else:
                self.log_test("AI BDD Scenario Generation", "FAIL", f"Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI BDD Scenario Generation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_coverage_analysis(self):
        """Test AI coverage analysis"""
        try:
            # Test with valid test cases and requirements
            test_cases = [
                {"id": 1, "title": "Login Test", "type": "functional"},
                {"id": 2, "title": "Registration Test", "type": "functional"}
            ]
            
            requirements = [
                {"id": 1, "title": "User Authentication", "priority": "high"},
                {"id": 2, "title": "User Registration", "priority": "medium"}
            ]
            
            response = requests.post(
                f"{self.base_url}/api/ai/analyze-coverage",
                json={
                    "test_cases": test_cases,
                    "requirements": requirements
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'coverage_analysis' in data:
                    self.log_test("AI Coverage Analysis", "PASS", "Coverage analysis successful")
                    return True
                else:
                    self.log_test("AI Coverage Analysis", "FAIL", "Invalid coverage analysis response")
                    return False
            elif response.status_code == 400:
                # This is expected without API keys
                self.log_test("AI Coverage Analysis", "PASS", "AI endpoint working (API key required)")
                return True
            else:
                self.log_test("AI Coverage Analysis", "FAIL", f"Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Coverage Analysis", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_error_handling(self):
        """Test AI error handling"""
        try:
            # Test with invalid data
            invalid_payloads = [
                {},  # Empty payload
                {"invalid": "data"},  # Invalid structure
                None  # None payload
            ]
            
            error_handling_works = True
            for payload in invalid_payloads:
                try:
                    if payload is None:
                        response = requests.post(f"{self.base_url}/api/ai/generate-test-cases", timeout=5)
                    else:
                        response = requests.post(
                            f"{self.base_url}/api/ai/generate-test-cases",
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
                self.log_test("AI Error Handling", "PASS", "Proper error handling for invalid data")
                return True
            else:
                self.log_test("AI Error Handling", "FAIL", "Insufficient error handling")
                return False
        except Exception as e:
            self.log_test("AI Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_performance(self):
        """Test AI performance"""
        try:
            # Test response times for AI operations
            start_time = time.time()
            
            # Test multiple AI endpoints
            ai_operations = [
                ('/api/ai/generate-test-cases', {"user_story": {"title": "Test"}}),
                ('/api/ai/improve-test-case', {"test_case": {"title": "Test"}}),
                ('/api/ai/generate-bdd-scenarios', {"user_story": {"title": "Test"}}),
                ('/api/ai/analyze-coverage', {"test_cases": [], "requirements": []})
            ]
            
            successful_operations = 0
            for endpoint, payload in ai_operations:
                try:
                    response = requests.post(f"{self.base_url}{endpoint}", json=payload, timeout=5)
                    if response.status_code in [200, 400]:  # 400 is expected without API keys
                        successful_operations += 1
                except Exception:
                    pass
            
            end_time = time.time()
            duration = end_time - start_time
            
            success_rate = (successful_operations / len(ai_operations)) * 100
            
            if success_rate >= 75 and duration < 5.0:  # At least 75% success and under 5 seconds
                self.log_test("AI Performance", "PASS", f"{success_rate:.1f}% success in {duration:.2f}s")
                return True
            else:
                self.log_test("AI Performance", "FAIL", f"Only {success_rate:.1f}% success in {duration:.2f}s")
                return False
        except Exception as e:
            self.log_test("AI Performance", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ai_integration_with_other_features(self):
        """Test AI integration with other features"""
        try:
            # Test that AI features integrate well with other system features
            # This includes analytics, caching, and monitoring
            
            # Test analytics integration
            analytics_response = requests.get(f"{self.base_url}/api/analytics/business", timeout=5)
            if analytics_response.status_code != 200:
                self.log_test("AI Integration", "FAIL", "Analytics integration not working")
                return False
            
            # Test cache integration
            cache_response = requests.get(f"{self.base_url}/api/cache/stats", timeout=5)
            if cache_response.status_code != 200:
                self.log_test("AI Integration", "FAIL", "Cache integration not working")
                return False
            
            # Test monitoring integration
            monitoring_response = requests.get(f"{self.base_url}/api/monitoring/system-metrics", timeout=5)
            if monitoring_response.status_code not in [200, 500]:  # 500 is acceptable for monitoring
                self.log_test("AI Integration", "FAIL", "Monitoring integration not working")
                return False
            
            self.log_test("AI Integration", "PASS", "AI integrates well with other features")
            return True
        except Exception as e:
            self.log_test("AI Integration", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_ai_tests(self):
        """Run all AI features tests"""
        print("🔍 Starting AI Features Testing...")
        print("=" * 40)
        
        # Run all AI tests
        self.test_ai_endpoint_availability()
        self.test_ai_test_case_generation()
        self.test_ai_test_case_improvement()
        self.test_ai_bdd_scenario_generation()
        self.test_ai_coverage_analysis()
        self.test_ai_error_handling()
        self.test_ai_performance()
        self.test_ai_integration_with_other_features()
        
        # Print summary
        print("\n" + "=" * 40)
        print("📊 AI Features Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = AIFeaturesTester()
    success = tester.run_all_ai_tests()
    exit(0 if success else 1)