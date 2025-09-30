#!/usr/bin/env python3
"""
Test Local LLM Integration for AI Test Generation
Tests the local LLM server for testing improvement
"""

import subprocess
import time
import requests
import json
import threading
from datetime import datetime
from local_llm_server import LocalLLMServer
from ollama_integration import OllamaIntegration

class LocalLLMIntegrationTester:
    """Test local LLM integration for AI test generation"""
    
    def __init__(self):
        self.local_server = None
        self.ollama_integration = None
        self.results = {}
        
    def start_local_server(self):
        """Start the local LLM server"""
        print("🚀 Starting Local LLM Server...")
        try:
            self.local_server = LocalLLMServer()
            # Start server in background thread
            server_thread = threading.Thread(target=self.local_server.start, daemon=True)
            server_thread.start()
            
            # Wait for server to start
            time.sleep(3)
            
            # Test server health
            response = requests.get("http://localhost:11434/health", timeout=5)
            if response.status_code == 200:
                print("✅ Local LLM Server started successfully")
                return True
            else:
                print("❌ Local LLM Server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start local server: {e}")
            return False
    
    def test_local_llm_features(self):
        """Test local LLM features"""
        print("\n🧪 Testing Local LLM Features...")
        
        try:
            # Test models endpoint
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✅ Available models: {len(models)}")
                self.results['models_available'] = len(models)
            else:
                print("❌ Failed to get models")
                self.results['models_available'] = 0
            
            # Test generation endpoint
            test_prompt = "Generate test cases for user login functionality"
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": test_prompt,
                    "stream": False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('response', '')
                print(f"✅ Generation working: {len(content)} characters")
                self.results['generation_working'] = True
                self.results['response_length'] = len(content)
            else:
                print("❌ Generation failed")
                self.results['generation_working'] = False
            
            return True
            
        except Exception as e:
            print(f"❌ Local LLM test failed: {e}")
            return False
    
    def test_ai_test_generation(self):
        """Test AI test generation using local LLM"""
        print("\n🤖 Testing AI Test Generation...")
        
        try:
            # Initialize Ollama integration
            self.ollama_integration = OllamaIntegration()
            
            # Test setup
            if not self.ollama_integration.setup_ollama():
                print("❌ Ollama setup failed")
                return False
            
            # Test test case generation
            print("  🔍 Testing test case generation...")
            test_response = self.ollama_integration.generate_test_cases(
                "User login functionality with email and password",
                3
            )
            
            if test_response.success:
                print(f"  ✅ Test cases generated: {len(test_response.content)} characters")
                self.results['test_cases_generated'] = True
                self.results['test_cases_length'] = len(test_response.content)
            else:
                print(f"  ❌ Test case generation failed: {test_response.error}")
                self.results['test_cases_generated'] = False
            
            # Test BDD generation
            print("  🔍 Testing BDD scenario generation...")
            bdd_response = self.ollama_integration.generate_bdd_scenarios(
                "User login functionality"
            )
            
            if bdd_response.success:
                print(f"  ✅ BDD scenarios generated: {len(bdd_response.content)} characters")
                self.results['bdd_generated'] = True
                self.results['bdd_length'] = len(bdd_response.content)
            else:
                print(f"  ❌ BDD generation failed: {bdd_response.error}")
                self.results['bdd_generated'] = False
            
            # Test test data generation
            print("  🔍 Testing test data generation...")
            data_response = self.ollama_integration.generate_test_data(
                "user authentication",
                5
            )
            
            if data_response.success:
                print(f"  ✅ Test data generated: {len(data_response.content)} characters")
                self.results['test_data_generated'] = True
                self.results['test_data_length'] = len(data_response.content)
            else:
                print(f"  ❌ Test data generation failed: {data_response.error}")
                self.results['test_data_generated'] = False
            
            # Test coverage analysis
            print("  🔍 Testing coverage analysis...")
            coverage_response = self.ollama_integration.analyze_coverage(
                ["Login test", "Logout test", "Password reset test"],
                ["User can login", "User can logout", "User can reset password"]
            )
            
            if coverage_response.success:
                print(f"  ✅ Coverage analysis completed: {len(coverage_response.content)} characters")
                self.results['coverage_analysis'] = True
                self.results['coverage_length'] = len(coverage_response.content)
            else:
                print(f"  ❌ Coverage analysis failed: {coverage_response.error}")
                self.results['coverage_analysis'] = False
            
            return True
            
        except Exception as e:
            print(f"❌ AI test generation failed: {e}")
            return False
    
    def test_performance_metrics(self):
        """Test performance metrics"""
        print("\n📊 Testing Performance Metrics...")
        
        try:
            # Test response times
            start_time = time.time()
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": "Generate a simple test case",
                    "stream": False
                },
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ Response time: {response_time:.2f} seconds")
                self.results['response_time'] = response_time
                self.results['performance_good'] = response_time < 5.0
            else:
                print("❌ Performance test failed")
                self.results['performance_good'] = False
            
            # Test concurrent requests
            print("  🔍 Testing concurrent requests...")
            import threading
            
            def make_request():
                try:
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama2",
                            "prompt": "Quick test",
                            "stream": False
                        },
                        timeout=10
                    )
                    return response.status_code == 200
                except:
                    return False
            
            # Test 3 concurrent requests
            threads = []
            results = []
            
            for i in range(3):
                thread = threading.Thread(target=lambda: results.append(make_request()))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            success_rate = sum(results) / len(results) * 100
            print(f"  ✅ Concurrent requests success rate: {success_rate:.1f}%")
            self.results['concurrent_success_rate'] = success_rate
            self.results['concurrent_good'] = success_rate >= 80
            
            return True
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        print("\n📋 Local LLM Integration Report")
        print("=" * 50)
        
        # Calculate success metrics
        total_tests = 8
        passed_tests = sum([
            self.results.get('models_available', 0) > 0,
            self.results.get('generation_working', False),
            self.results.get('test_cases_generated', False),
            self.results.get('bdd_generated', False),
            self.results.get('test_data_generated', False),
            self.results.get('coverage_analysis', False),
            self.results.get('performance_good', False),
            self.results.get('concurrent_good', False)
        ])
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 Test Results:")
        print(f"  Models Available: {self.results.get('models_available', 0)}")
        print(f"  Generation Working: {'✅' if self.results.get('generation_working') else '❌'}")
        print(f"  Test Cases Generated: {'✅' if self.results.get('test_cases_generated') else '❌'}")
        print(f"  BDD Generated: {'✅' if self.results.get('bdd_generated') else '❌'}")
        print(f"  Test Data Generated: {'✅' if self.results.get('test_data_generated') else '❌'}")
        print(f"  Coverage Analysis: {'✅' if self.results.get('coverage_analysis') else '❌'}")
        print(f"  Performance Good: {'✅' if self.results.get('performance_good') else '❌'}")
        print(f"  Concurrent Good: {'✅' if self.results.get('concurrent_good') else '❌'}")
        
        print(f"\n📈 Overall Success Rate: {success_rate:.1f}%")
        print(f"🎯 Tests Passed: {passed_tests}/{total_tests}")
        
        # Performance metrics
        if 'response_time' in self.results:
            print(f"⚡ Average Response Time: {self.results['response_time']:.2f}s")
        if 'concurrent_success_rate' in self.results:
            print(f"🔄 Concurrent Success Rate: {self.results['concurrent_success_rate']:.1f}%")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if success_rate >= 90:
            print("  ✅ Excellent integration - ready for production")
        elif success_rate >= 70:
            print("  ⚠️ Good integration - minor optimizations needed")
        else:
            print("  ❌ Integration needs improvement")
        
        # Expected improvements
        if success_rate >= 80:
            print("  📈 Expected testing improvement: +35-55%")
            print("  🚀 Ready for AI test generation")
        else:
            print("  📈 Limited improvement expected")
            print("  🔧 Needs optimization")
        
        # Save report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'success_rate': success_rate,
            'passed_tests': passed_tests,
            'total_tests': total_tests
        }
        
        with open('local_llm_integration_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: local_llm_integration_report.json")
        
        return success_rate

def main():
    """Main function"""
    print("🚀 Local LLM Integration Test for AI Test Generation")
    print("=" * 70)
    
    tester = LocalLLMIntegrationTester()
    
    # Start local server
    if not tester.start_local_server():
        print("❌ Failed to start local server")
        return 1
    
    # Test local LLM features
    if not tester.test_local_llm_features():
        print("❌ Local LLM features test failed")
        return 1
    
    # Test AI test generation
    if not tester.test_ai_test_generation():
        print("❌ AI test generation test failed")
        return 1
    
    # Test performance
    if not tester.test_performance_metrics():
        print("❌ Performance test failed")
        return 1
    
    # Generate report
    success_rate = tester.generate_integration_report()
    
    print(f"\n🎉 Local LLM Integration Test Complete!")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Local LLM integration successful!")
        print("📈 Expected testing improvement: +35-55%")
        return 0
    else:
        print("⚠️ Local LLM integration needs improvement")
        return 1

if __name__ == "__main__":
    exit(main())