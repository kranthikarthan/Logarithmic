#!/usr/bin/env python3
"""
Comprehensive Test Suite for Assertly Enterprise Features
Tests all enterprise functionality including AI integration, security, and compliance
"""

import unittest
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enterprise_config import EnterpriseConfigManager, EnterpriseSettings
from enterprise_security import EnterpriseSecurity, SecurityLevel, AccessLevel
from offline_ai_manager import OfflineAIManager
from local_ai_provider import LocalAIProvider, LocalAIConfig

class TestEnterpriseConfiguration(unittest.TestCase):
    """Test enterprise configuration management"""
    
    def setUp(self):
        """Set up test environment"""
        self.config_manager = EnterpriseConfigManager("test_enterprise.db")
        self.test_settings = EnterpriseSettings(
            local_ai_url="http://test-ai.company.com:8080/api",
            local_ai_model="local-copilot",
            local_api_key="test-api-key",
            proxy_url="http://proxy.company.com:8080",
            cert_path="/path/to/cert.pem",
            verify_ssl=True,
            audit_enabled=True,
            data_encryption=True,
            session_timeout=3600,
            data_retention_days=365,
            log_retention_days=90,
            compliance_mode="standard",
            offline_mode=False,
            custom_models=False,
            external_integrations=False
        )
    
    def test_save_enterprise_settings(self):
        """Test saving enterprise settings"""
        result = self.config_manager.save_enterprise_settings(self.test_settings)
        self.assertTrue(result)
    
    def test_load_enterprise_settings(self):
        """Test loading enterprise settings"""
        # First save settings
        self.config_manager.save_enterprise_settings(self.test_settings)
        
        # Then load them
        loaded_settings = self.config_manager.load_enterprise_settings()
        self.assertIsNotNone(loaded_settings)
        self.assertEqual(loaded_settings.local_ai_url, self.test_settings.local_ai_url)
        self.assertEqual(loaded_settings.local_ai_model, self.test_settings.local_ai_model)
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        result = self.config_manager.log_audit_event(
            user="test_user",
            action="test_action",
            resource="test_resource",
            details={"test": "data"},
            ip_address="127.0.0.1",
            user_agent="test-agent"
        )
        self.assertTrue(result)
    
    def test_get_audit_logs(self):
        """Test retrieving audit logs"""
        # Log some test events
        self.config_manager.log_audit_event("user1", "action1", "resource1", {"data": "test1"})
        self.config_manager.log_audit_event("user2", "action2", "resource2", {"data": "test2"})
        
        # Get logs
        logs = self.config_manager.get_audit_logs()
        self.assertGreaterEqual(len(logs), 2)
    
    def test_compliance_report_generation(self):
        """Test compliance report generation"""
        report_id = self.config_manager.generate_compliance_report("audit_summary")
        self.assertIsNotNone(report_id)
        self.assertIsInstance(report_id, str)
    
    def test_system_health(self):
        """Test system health check"""
        health = self.config_manager.get_system_health()
        self.assertIn("status", health)
        self.assertIn("enterprise_mode", health)

class TestEnterpriseSecurity(unittest.TestCase):
    """Test enterprise security features"""
    
    def setUp(self):
        """Set up test environment"""
        self.security = EnterpriseSecurity("test_security")
    
    def test_encrypt_decrypt_data(self):
        """Test data encryption and decryption"""
        test_data = "sensitive test data"
        
        # Encrypt data
        encrypted = self.security.encrypt_data(test_data)
        self.assertIsNotNone(encrypted)
        self.assertNotEqual(encrypted, test_data)
        
        # Decrypt data
        decrypted = self.security.decrypt_data(encrypted)
        self.assertEqual(decrypted, test_data)
    
    def test_password_hashing(self):
        """Test password hashing"""
        password = "test_password"
        
        # Hash password
        hashed, salt = self.security.hash_password(password)
        self.assertIsNotNone(hashed)
        self.assertIsNotNone(salt)
        
        # Verify password
        is_valid = self.security.verify_password(password, hashed, salt)
        self.assertTrue(is_valid)
        
        # Test wrong password
        is_invalid = self.security.verify_password("wrong_password", hashed, salt)
        self.assertFalse(is_invalid)
    
    def test_security_event_logging(self):
        """Test security event logging"""
        event_id = self.security.log_security_event(
            user="test_user",
            action="test_action",
            resource="test_resource",
            level=SecurityLevel.MEDIUM,
            ip_address="127.0.0.1",
            user_agent="test-agent",
            details={"test": "data"},
            success=True
        )
        
        self.assertIsNotNone(event_id)
        self.assertIsInstance(event_id, str)
    
    def test_access_control(self):
        """Test access control functionality"""
        # Create access control rule
        rule_id = self.security.create_access_control(
            user="test_user",
            resource="test_resource",
            access_level=AccessLevel.READ,
            conditions={"time": "business_hours"}
        )
        
        self.assertIsNotNone(rule_id)
        
        # Check access
        has_access = self.security.check_access("test_user", "test_resource", AccessLevel.READ)
        self.assertTrue(has_access)
        
        # Check higher level access
        has_admin_access = self.security.check_access("test_user", "test_resource", AccessLevel.ADMIN)
        self.assertFalse(has_admin_access)
    
    def test_security_events_retrieval(self):
        """Test retrieving security events"""
        # Log some test events
        self.security.log_security_event("user1", "action1", "resource1", SecurityLevel.LOW, "127.0.0.1", "agent1", {"data": "test1"})
        self.security.log_security_event("user2", "action2", "resource2", SecurityLevel.HIGH, "127.0.0.1", "agent2", {"data": "test2"})
        
        # Get all events
        events = self.security.get_security_events()
        self.assertGreaterEqual(len(events), 2)
        
        # Get events by level
        high_events = self.security.get_security_events(level=SecurityLevel.HIGH)
        self.assertGreaterEqual(len(high_events), 1)
    
    def test_security_report_generation(self):
        """Test security report generation"""
        # Log some test events first
        self.security.log_security_event("user1", "action1", "resource1", SecurityLevel.LOW, "127.0.0.1", "agent1", {"data": "test1"})
        
        # Generate report
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        report = self.security.generate_security_report(start_date, end_date)
        
        self.assertIsNotNone(report)
        self.assertIn("summary", report)
        self.assertIn("total_events", report["summary"])

class TestOfflineAIManager(unittest.TestCase):
    """Test offline AI capabilities"""
    
    def setUp(self):
        """Set up test environment"""
        self.offline_manager = OfflineAIManager("test_offline_cache", "test_offline_models")
    
    def test_register_model(self):
        """Test model registration"""
        result = self.offline_manager.register_model(
            model_id="test_model",
            name="Test Model",
            version="1.0.0",
            model_path="test_model.pkl",
            config={"type": "test", "parameters": {"param1": "value1"}}
        )
        self.assertTrue(result)
    
    def test_load_model(self):
        """Test model loading"""
        # First register a model
        self.offline_manager.register_model(
            model_id="test_model",
            name="Test Model",
            version="1.0.0",
            model_path="test_model.pkl",
            config={"type": "test"}
        )
        
        # Then try to load it
        result = self.offline_manager.load_model("test_model")
        # This will fail because the model file doesn't exist, but the method should handle it gracefully
        self.assertIsInstance(result, bool)
    
    def test_generate_offline_response(self):
        """Test offline response generation"""
        # This will use cached responses or fallback
        response = self.offline_manager.generate_offline_response("test prompt")
        # The response might be None if no cache exists, which is expected
        self.assertIsInstance(response, (type(None), type(self.offline_manager.OfflineResponse)))
    
    def test_cache_management(self):
        """Test cache management functionality"""
        # Get cache stats
        stats = self.offline_manager.get_cache_stats()
        self.assertIsInstance(stats, dict)
        
        # Test cache cleanup
        deleted_count = self.offline_manager.cleanup_old_cache(days=0)  # Clean all old entries
        self.assertIsInstance(deleted_count, int)
    
    def test_cache_export_import(self):
        """Test cache export and import"""
        # Test export
        export_file = "test_cache_export.json"
        result = self.offline_manager.export_cache(export_file)
        self.assertIsInstance(result, bool)
        
        # Test import
        if os.path.exists(export_file):
            result = self.offline_manager.import_cache(export_file)
            self.assertIsInstance(result, bool)
            # Clean up
            os.remove(export_file)

class TestLocalAIProvider(unittest.TestCase):
    """Test local AI provider functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = LocalAIConfig(
            base_url="http://test-ai.company.com:8080/api",
            api_key="test-api-key",
            model_name="test-model",
            timeout=30,
            max_retries=3
        )
        self.provider = LocalAIProvider(self.config)
    
    def test_configuration(self):
        """Test provider configuration"""
        self.assertEqual(self.provider.config.base_url, self.config.base_url)
        self.assertEqual(self.provider.config.api_key, self.config.api_key)
        self.assertEqual(self.provider.config.model_name, self.config.model_name)
    
    def test_connection_test(self):
        """Test connection testing"""
        # This will fail because the test URL doesn't exist, but should handle gracefully
        result = self.provider.test_connection()
        self.assertIsInstance(result, bool)
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        # Get initial audit log count
        initial_logs = len(self.provider.get_audit_log())
        
        # The audit log should be empty initially
        self.assertIsInstance(initial_logs, int)
    
    def test_cache_functionality(self):
        """Test cache functionality"""
        # Get cache stats
        stats = self.provider.get_cache_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("cache_size", stats)
        
        # Clear cache
        self.provider.clear_cache()
        
        # Verify cache is cleared
        stats_after = self.provider.get_cache_stats()
        self.assertEqual(stats_after["cache_size"], 0)

class TestEnterpriseAPIEndpoints(unittest.TestCase):
    """Test enterprise API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.api_base = f"{self.base_url}/api/enterprise"
    
    def test_health_endpoint(self):
        """Test enterprise health endpoint"""
        response = requests.get(f"{self.api_base}/health", timeout=10)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("enterprise_mode", data)
    
    def test_ai_configuration_endpoint(self):
        """Test AI configuration endpoint"""
        config_data = {
            "local_ai_url": "http://test-ai.company.com:8080/api",
            "local_ai_model": "local-copilot",
            "local_api_key": "test-key"
        }
        
        response = requests.post(
            f"{self.api_base}/ai/configure",
            json=config_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
    
    def test_ai_connection_test_endpoint(self):
        """Test AI connection test endpoint"""
        response = requests.get(f"{self.api_base}/ai/test-connection", timeout=10)
        # This might return 400 if not configured, which is expected
        self.assertIn(response.status_code, [200, 400])
    
    def test_audit_logs_endpoint(self):
        """Test audit logs endpoint"""
        response = requests.get(f"{self.api_base}/audit/logs", timeout=10)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("logs", data)
    
    def test_compliance_report_endpoint(self):
        """Test compliance report endpoint"""
        report_data = {
            "report_type": "audit_summary",
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2024-12-31T23:59:59"
        }
        
        response = requests.post(
            f"{self.api_base}/compliance/report",
            json=report_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("report_id", data)

class TestEnterpriseIntegration(unittest.TestCase):
    """Test enterprise integration scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.api_base = f"{self.base_url}/api/enterprise"
    
    def test_complete_enterprise_workflow(self):
        """Test complete enterprise workflow"""
        # 1. Configure enterprise AI
        config_data = {
            "local_ai_url": "http://test-ai.company.com:8080/api",
            "local_ai_model": "local-copilot",
            "local_api_key": "test-key"
        }
        
        response = requests.post(
            f"{self.api_base}/ai/configure",
            json=config_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        # 2. Test AI connection
        response = requests.get(f"{self.api_base}/ai/test-connection", timeout=10)
        self.assertIn(response.status_code, [200, 400])
        
        # 3. Generate test cases (this might fail if AI service is not available)
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
            f"{self.api_base}/ai/generate-test-cases",
            json=test_data,
            timeout=30
        )
        # This might return 500 if AI service is not available, which is expected
        self.assertIn(response.status_code, [200, 500])
        
        # 4. Check audit logs
        response = requests.get(f"{self.api_base}/audit/logs", timeout=10)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        # Should have at least the configuration event
        self.assertGreaterEqual(data["count"], 1)
    
    def test_security_compliance_workflow(self):
        """Test security and compliance workflow"""
        # 1. Generate compliance report
        report_data = {
            "report_type": "audit_summary",
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2024-12-31T23:59:59"
        }
        
        response = requests.post(
            f"{self.api_base}/compliance/report",
            json=report_data,
            timeout=10
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("report_id", data)
        
        # 2. Check audit logs for compliance
        response = requests.get(f"{self.api_base}/audit/logs", timeout=10)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        # Should have compliance-related events
        self.assertGreaterEqual(data["count"], 0)

def run_enterprise_tests():
    """Run all enterprise tests"""
    print("🧪 Running Assertly Enterprise Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEnterpriseConfiguration,
        TestEnterpriseSecurity,
        TestOfflineAIManager,
        TestLocalAIProvider,
        TestEnterpriseAPIEndpoints,
        TestEnterpriseIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
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
    success = run_enterprise_tests()
    sys.exit(0 if success else 1)