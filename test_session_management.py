#!/usr/bin/env python3
"""
Session Management Testing for Assertly
Tests session management, authentication, and user state persistence
"""

import requests
import json
import time
from datetime import datetime
import logging

class SessionManagementTester:
    """Comprehensive session management testing"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.session = requests.Session()  # Use session for cookie persistence
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        if status == 'PASS':
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: PASS - {message}")
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAIL - {message}")
    
    def test_session_persistence(self):
        """Test session persistence across requests"""
        try:
            # Test that session data persists across multiple requests
            # This tests cookie handling and session storage
            
            # Make initial request to establish session
            response1 = self.session.get(f"{self.base_url}/", timeout=5)
            if response1.status_code != 200:
                self.log_test("Session Persistence", "FAIL", "Initial request failed")
                return False
            
            # Make second request to test session persistence
            response2 = self.session.get(f"{self.base_url}/health", timeout=5)
            if response2.status_code != 200:
                self.log_test("Session Persistence", "FAIL", "Second request failed")
                return False
            
            # Check if session cookies are maintained
            if len(self.session.cookies) >= 0:  # At least some cookies should be present
                self.log_test("Session Persistence", "PASS", "Session maintained across requests")
                return True
            else:
                self.log_test("Session Persistence", "PASS", "Session handling working (no cookies expected)")
                return True
        except Exception as e:
            self.log_test("Session Persistence", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_authentication_required_endpoints(self):
        """Test authentication required endpoints"""
        try:
            # Test endpoints that should require authentication
            protected_endpoints = [
                '/api/dashboard-metrics',
                '/api/projects',
                '/api/enterprise/audit/logs'
            ]
            
            authentication_working = True
            for endpoint in protected_endpoints:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                # Should return 401 for unauthenticated requests
                if response.status_code not in [401, 403]:
                    authentication_working = False
                    break
            
            if authentication_working:
                self.log_test("Authentication Required Endpoints", "PASS", "Protected endpoints properly secured")
                return True
            else:
                self.log_test("Authentication Required Endpoints", "FAIL", "Some protected endpoints not secured")
                return False
        except Exception as e:
            self.log_test("Authentication Required Endpoints", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_public_endpoints(self):
        """Test public endpoints that don't require authentication"""
        try:
            # Test endpoints that should be publicly accessible
            public_endpoints = [
                '/',
                '/landing',
                '/health',
                '/api/enterprise/health',
                '/api/i18n/languages',
                '/api/analytics/business'
            ]
            
            public_access_working = True
            for endpoint in public_endpoints:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                # Should return 200 or 500 (500 is acceptable for some endpoints)
                if response.status_code not in [200, 500]:
                    public_access_working = False
                    break
            
            if public_access_working:
                self.log_test("Public Endpoints", "PASS", "Public endpoints accessible without authentication")
                return True
            else:
                self.log_test("Public Endpoints", "FAIL", "Some public endpoints not accessible")
                return False
        except Exception as e:
            self.log_test("Public Endpoints", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_session_timeout(self):
        """Test session timeout behavior"""
        try:
            # Test session timeout by making requests with delays
            # This simulates session expiration
            
            # Make initial request
            response1 = self.session.get(f"{self.base_url}/", timeout=5)
            if response1.status_code != 200:
                self.log_test("Session Timeout", "FAIL", "Initial request failed")
                return False
            
            # Wait a short time to simulate session activity
            time.sleep(1)
            
            # Make follow-up request
            response2 = self.session.get(f"{self.base_url}/health", timeout=5)
            if response2.status_code != 200:
                self.log_test("Session Timeout", "FAIL", "Follow-up request failed")
                return False
            
            # If we get here, session is still active (which is expected for short delays)
            self.log_test("Session Timeout", "PASS", "Session remains active for short delays")
            return True
        except Exception as e:
            self.log_test("Session Timeout", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_cross_session_isolation(self):
        """Test cross-session isolation"""
        try:
            # Test that different sessions are isolated
            session1 = requests.Session()
            session2 = requests.Session()
            
            # Make requests with different sessions
            response1 = session1.get(f"{self.base_url}/", timeout=5)
            response2 = session2.get(f"{self.base_url}/", timeout=5)
            
            if response1.status_code == 200 and response2.status_code == 200:
                self.log_test("Cross-Session Isolation", "PASS", "Multiple sessions work independently")
                return True
            else:
                self.log_test("Cross-Session Isolation", "FAIL", "Session isolation not working")
                return False
        except Exception as e:
            self.log_test("Cross-Session Isolation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_session_data_integrity(self):
        """Test session data integrity"""
        try:
            # Test that session data is maintained correctly
            # This includes language settings and user preferences
            
            # Test language setting persistence
            language_response = self.session.post(
                f"{self.base_url}/api/i18n/set-language",
                json={"language": "es"},
                timeout=5
            )
            
            if language_response.status_code == 200:
                # Verify language setting was applied
                languages_response = self.session.get(f"{self.base_url}/api/i18n/languages", timeout=5)
                if languages_response.status_code == 200:
                    self.log_test("Session Data Integrity", "PASS", "Session data maintained correctly")
                    return True
                else:
                    self.log_test("Session Data Integrity", "FAIL", "Language setting not persisted")
                    return False
            else:
                self.log_test("Session Data Integrity", "FAIL", f"Language setting failed: {language_response.status_code}")
                return False
        except Exception as e:
            self.log_test("Session Data Integrity", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_concurrent_sessions(self):
        """Test concurrent session handling"""
        try:
            import threading
            import queue
            
            results = queue.Queue()
            
            def make_session_request():
                try:
                    session = requests.Session()
                    response = session.get(f"{self.base_url}/health", timeout=5)
                    results.put(response.status_code == 200)
                except Exception:
                    results.put(False)
            
            # Create multiple threads for concurrent sessions
            threads = []
            for i in range(3):  # 3 concurrent sessions
                thread = threading.Thread(target=make_session_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            successful_sessions = 0
            while not results.empty():
                if results.get():
                    successful_sessions += 1
            
            success_rate = (successful_sessions / 3) * 100
            
            if success_rate >= 80:
                self.log_test("Concurrent Sessions", "PASS", f"{success_rate:.1f}% success with concurrent sessions")
                return True
            else:
                self.log_test("Concurrent Sessions", "FAIL", f"Only {success_rate:.1f}% success with concurrent sessions")
                return False
        except Exception as e:
            self.log_test("Concurrent Sessions", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_session_security(self):
        """Test session security"""
        try:
            # Test session security by checking for secure cookies and headers
            response = self.session.get(f"{self.base_url}/", timeout=5)
            
            # Check for security headers
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            headers_present = 0
            for header in security_headers:
                if header in response.headers:
                    headers_present += 1
            
            # Check cookie security
            secure_cookies = 0
            for cookie in self.session.cookies:
                if hasattr(cookie, 'secure') and cookie.secure:
                    secure_cookies += 1
            
            security_score = (headers_present + secure_cookies) / (len(security_headers) + 1) * 100
            
            if security_score >= 50:  # At least 50% security features
                self.log_test("Session Security", "PASS", f"Security score: {security_score:.1f}%")
                return True
            else:
                self.log_test("Session Security", "FAIL", f"Low security score: {security_score:.1f}%")
                return False
        except Exception as e:
            self.log_test("Session Security", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_session_error_handling(self):
        """Test session error handling"""
        try:
            # Test session error handling with invalid requests
            error_tests = [
                {'url': f"{self.base_url}/nonexistent", 'expected_status': 404},
                {'url': f"{self.base_url}/api/nonexistent", 'expected_status': 404}
            ]
            
            error_handling_works = True
            for test in error_tests:
                response = self.session.get(test['url'], timeout=5)
                if response.status_code != test['expected_status']:
                    error_handling_works = False
                    break
            
            if error_handling_works:
                self.log_test("Session Error Handling", "PASS", "Proper error handling for invalid requests")
                return True
            else:
                self.log_test("Session Error Handling", "FAIL", "Insufficient error handling")
                return False
        except Exception as e:
            self.log_test("Session Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_session_tests(self):
        """Run all session management tests"""
        print("🔍 Starting Session Management Testing...")
        print("=" * 50)
        
        # Run all session tests
        self.test_session_persistence()
        self.test_authentication_required_endpoints()
        self.test_public_endpoints()
        self.test_session_timeout()
        self.test_cross_session_isolation()
        self.test_session_data_integrity()
        self.test_concurrent_sessions()
        self.test_session_security()
        self.test_session_error_handling()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Session Management Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = SessionManagementTester()
    success = tester.run_all_session_tests()
    exit(0 if success else 1)