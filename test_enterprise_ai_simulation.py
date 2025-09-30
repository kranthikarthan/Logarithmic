#!/usr/bin/env python3
"""
Test Enterprise AI Simulation with Ollama
Comprehensive testing of all AI features using local LLM
"""

import requests
import json
import time
from datetime import datetime

class EnterpriseAITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
    
    def make_request(self, endpoint, method='GET', data=None, timeout=30):
        """Make HTTP request"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else {},
                'response_time': response.elapsed.total_seconds()
            }
            
        except Exception as e:
            return {
                'status_code': 0,
                'success': False,
                'data': {},
                'error': str(e),
                'response_time': 0
            }
    
    def test_ai_test_generation(self):
        """Test AI test case generation"""
        print("\n🧪 Testing AI Test Case Generation...")
        
        test_data = {
            "title": "User Authentication System",
            "description": "As a user, I want to authenticate securely to access the application",
            "acceptance_criteria": [
                "User can login with valid credentials",
                "User can logout securely", 
                "Session timeout works correctly",
                "Password reset functionality works"
            ],
            "business_value": "Secure access to application features",
            "user_persona": "Registered application user",
            "test_types": ["functional", "security", "ui"],
            "num_cases": 5
        }
        
        response = self.make_request('/api/ai/generate-test-cases', 'POST', test_data, timeout=60)
        
        if response['success']:
            data = response['data']
            provider = data.get('provider', 'unknown')
            count = data.get('count', 0)
            note = data.get('note', '')
            
            if provider == 'local-llm':
                self.log_test("AI Test Generation", "PASS", f"Generated {count} test cases using local LLM")
                return True
            elif provider == 'mock-fallback':
                self.log_test("AI Test Generation", "FAIL", "Using mock fallback instead of local LLM")
                return False
            else:
                self.log_test("AI Test Generation", "PASS", f"Generated {count} test cases using {provider}")
                return True
        else:
            self.log_test("AI Test Generation", "FAIL", f"Request failed: {response.get('error', 'Unknown error')}")
            return False
    
    def test_ai_test_improvement(self):
        """Test AI test case improvement"""
        print("\n🔧 Testing AI Test Case Improvement...")
        
        improvement_data = {
            "test_case": {
                "title": "Basic User Login Test",
                "description": "Test user login functionality",
                "steps": [
                    "1. Navigate to login page",
                    "2. Enter valid username",
                    "3. Enter valid password", 
                    "4. Click login button"
                ],
                "expected_result": "User should be successfully logged in",
                "test_type": "functional",
                "priority": "high",
                "tags": ["smoke", "login"],
                "preconditions": ["User account exists", "Application is accessible"],
                "test_data": {"username": "testuser", "password": "testpass"},
                "acceptance_criteria": ["Login successful", "Redirect to dashboard"]
            },
            "improvement_prompts": [
                "Add security testing scenarios",
                "Include edge cases and boundary testing",
                "Add performance testing considerations",
                "Include accessibility testing"
            ]
        }
        
        response = self.make_request('/api/ai/improve-test-case', 'POST', improvement_data, timeout=60)
        
        if response['success']:
            data = response['data']
            provider = data.get('provider', 'unknown')
            note = data.get('note', '')
            
            if provider == 'local-llm':
                self.log_test("AI Test Improvement", "PASS", "Test case improved using local LLM")
                return True
            elif provider == 'mock-fallback':
                self.log_test("AI Test Improvement", "FAIL", "Using mock fallback instead of local LLM")
                return False
            else:
                self.log_test("AI Test Improvement", "PASS", f"Test case improved using {provider}")
                return True
        else:
            self.log_test("AI Test Improvement", "FAIL", f"Request failed: {response.get('error', 'Unknown error')}")
            return False
    
    def test_bdd_scenario_generation(self):
        """Test BDD scenario generation"""
        print("\n📋 Testing BDD Scenario Generation...")
        
        bdd_data = {
            "title": "User Registration Process",
            "description": "As a new user, I want to register for an account so I can access the application",
            "acceptance_criteria": [
                "User can fill registration form",
                "Email verification is sent",
                "Account is activated after verification",
                "User can login after registration"
            ],
            "business_value": "User acquisition and onboarding",
            "user_persona": "New user wanting to access the application",
            "num_scenarios": 3
        }
        
        response = self.make_request('/api/ai/generate-bdd-scenarios', 'POST', bdd_data, timeout=60)
        
        if response['success']:
            data = response['data']
            provider = data.get('provider', 'unknown')
            count = data.get('count', 0)
            note = data.get('note', '')
            
            if provider == 'local-llm':
                self.log_test("BDD Scenario Generation", "PASS", f"Generated {count} BDD scenarios using local LLM")
                return True
            elif provider == 'mock-fallback':
                self.log_test("BDD Scenario Generation", "FAIL", "Using mock fallback instead of local LLM")
                return False
            else:
                self.log_test("BDD Scenario Generation", "PASS", f"Generated {count} BDD scenarios using {provider}")
                return True
        else:
            self.log_test("BDD Scenario Generation", "FAIL", f"Request failed: {response.get('error', 'Unknown error')}")
            return False
    
    def test_ai_test_data_generation(self):
        """Test AI test data generation"""
        print("\n📊 Testing AI Test Data Generation...")
        
        test_data_request = {
            "test_type": "user_registration",
            "num_samples": 10,
            "data_types": ["valid", "invalid", "boundary", "edge_case"]
        }
        
        response = self.make_request('/api/ai/generate-test-data', 'POST', test_data_request, timeout=60)
        
        if response['success']:
            data = response['data']
            provider = data.get('provider', 'unknown')
            note = data.get('note', '')
            
            if provider == 'local-llm':
                self.log_test("AI Test Data Generation", "PASS", "Test data generated using local LLM")
                return True
            elif provider == 'mock-fallback':
                self.log_test("AI Test Data Generation", "PASS", "Using mock fallback (acceptable)")
                return True
            else:
                self.log_test("AI Test Data Generation", "PASS", f"Test data generated using {provider}")
                return True
        else:
            self.log_test("AI Test Data Generation", "FAIL", f"Request failed: {response.get('error', 'Unknown error')}")
            return False
    
    def test_ai_coverage_analysis(self):
        """Test AI coverage analysis"""
        print("\n📈 Testing AI Coverage Analysis...")
        
        coverage_data = {
            "test_cases": [
                {"title": "Login Test", "type": "functional"},
                {"title": "Logout Test", "type": "functional"},
                {"title": "Password Reset Test", "type": "functional"}
            ],
            "requirements": [
                {"id": "REQ-001", "title": "User Authentication"},
                {"id": "REQ-002", "title": "Session Management"},
                {"id": "REQ-003", "title": "Password Security"}
            ]
        }
        
        response = self.make_request('/api/ai/analyze-coverage', 'POST', coverage_data, timeout=60)
        
        if response['success']:
            data = response['data']
            provider = data.get('provider', 'unknown')
            note = data.get('note', '')
            
            if provider == 'local-llm':
                self.log_test("AI Coverage Analysis", "PASS", "Coverage analysis completed using local LLM")
                return True
            elif provider == 'mock-fallback':
                self.log_test("AI Coverage Analysis", "PASS", "Using mock fallback (acceptable)")
                return True
            else:
                self.log_test("AI Coverage Analysis", "PASS", f"Coverage analysis completed using {provider}")
                return True
        else:
            self.log_test("AI Coverage Analysis", "FAIL", f"Request failed: {response.get('error', 'Unknown error')}")
            return False
    
    def test_enterprise_ai_connection(self):
        """Test enterprise AI connection"""
        print("\n🏢 Testing Enterprise AI Connection...")
        
        response = self.make_request('/api/enterprise/ai/test-connection', timeout=30)
        
        if response['success']:
            data = response['data']
            success = data.get('success', False)
            message = data.get('message', '')
            provider = data.get('provider', 'unknown')
            
            if success:
                self.log_test("Enterprise AI Connection", "PASS", f"Connection successful: {message}")
                return True
            else:
                self.log_test("Enterprise AI Connection", "FAIL", f"Connection failed: {message}")
                return False
        else:
            self.log_test("Enterprise AI Connection", "FAIL", f"Request failed: {response.get('error', 'Unknown error')}")
            return False
    
    def test_enterprise_ai_generation(self):
        """Test enterprise AI test generation"""
        print("\n🏭 Testing Enterprise AI Test Generation...")
        
        enterprise_data = {
            "title": "Enterprise User Management",
            "description": "As an enterprise admin, I want to manage user accounts and permissions",
            "acceptance_criteria": [
                "Admin can create user accounts",
                "Admin can modify user permissions",
                "Admin can deactivate user accounts",
                "Audit trail is maintained"
            ],
            "business_value": "Enterprise user management and security",
            "user_persona": "Enterprise administrator"
        }
        
        response = self.make_request('/api/enterprise/ai/generate-test-cases', 'POST', enterprise_data, timeout=60)
        
        if response['success']:
            data = response['data']
            success = data.get('success', False)
            count = data.get('count', 0)
            provider = data.get('provider', 'unknown')
            
            if success:
                self.log_test("Enterprise AI Generation", "PASS", f"Generated {count} test cases using {provider}")
                return True
            else:
                self.log_test("Enterprise AI Generation", "FAIL", "Generation failed")
                return False
        else:
            self.log_test("Enterprise AI Generation", "FAIL", f"Request failed: {response.get('error', 'Unknown error')}")
            return False
    
    def run_all_tests(self):
        """Run all enterprise AI tests"""
        print("🎯 Enterprise AI Simulation Test Suite")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Test enterprise AI connection first
        connection_ok = self.test_enterprise_ai_connection()
        
        if not connection_ok:
            print("\n⚠️ Enterprise AI connection failed. Some tests may not work properly.")
        
        # Run all AI tests
        tests = [
            ("AI Test Generation", self.test_ai_test_generation),
            ("AI Test Improvement", self.test_ai_test_improvement),
            ("BDD Scenario Generation", self.test_bdd_scenario_generation),
            ("AI Test Data Generation", self.test_ai_test_data_generation),
            ("AI Coverage Analysis", self.test_ai_coverage_analysis),
            ("Enterprise AI Generation", self.test_enterprise_ai_generation)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, "FAIL", f"Test exception: {e}")
        
        # Generate report
        self.generate_report(passed, total)
        
        return passed, total
    
    def generate_report(self, passed, total):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 ENTERPRISE AI SIMULATION TEST REPORT")
        print("=" * 60)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"🧪 Test Results:")
        print(f"  Passed: {passed}")
        print(f"  Failed: {total - passed}")
        print(f"  Total: {total}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        print(f"\n📈 Provider Analysis:")
        local_llm_count = sum(1 for r in self.results if 'local LLM' in r.get('details', ''))
        mock_count = sum(1 for r in self.results if 'mock' in r.get('details', '').lower())
        other_count = total - local_llm_count - mock_count
        
        print(f"  Local LLM: {local_llm_count}")
        print(f"  Mock Fallback: {mock_count}")
        print(f"  Other: {other_count}")
        
        print(f"\n🎯 Enterprise AI Status:")
        if success_rate >= 80:
            print("  ✅ Enterprise AI simulation is working well")
        elif success_rate >= 60:
            print("  ⚠️ Enterprise AI simulation has some issues")
        else:
            print("  ❌ Enterprise AI simulation needs attention")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'passed': passed,
                'failed': total - passed,
                'total': total,
                'success_rate': success_rate
            },
            'provider_analysis': {
                'local_llm': local_llm_count,
                'mock_fallback': mock_count,
                'other': other_count
            },
            'test_results': self.results
        }
        
        with open('enterprise_ai_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: enterprise_ai_test_report.json")

def main():
    """Main test function"""
    print("🏢 Enterprise AI Simulation with Ollama")
    print("=" * 60)
    
    # Check if application is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Assertly application is not running")
            print("   Please start the application: python3 app.py &")
            return
    except:
        print("❌ Cannot connect to Assertly application")
        print("   Please start the application: python3 app.py &")
        return
    
    # Run tests
    tester = EnterpriseAITester()
    passed, total = tester.run_all_tests()
    
    print(f"\n🎉 Enterprise AI Simulation Complete!")
    print(f"   Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")

if __name__ == "__main__":
    main()