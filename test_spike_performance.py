#!/usr/bin/env python3
"""
Spike Testing for Assertly
Tests system response to sudden load spikes and traffic bursts
"""

import requests
import time
import threading
import statistics
from datetime import datetime
import json
import random

class SpikePerformanceTester:
    """Comprehensive spike testing suite"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.spike_metrics = {
            'spike_handling_capacity': 0,
            'recovery_time_after_spike': 0,
            'error_rate_during_spike': 0,
            'throughput_during_spike': 0
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
    
    def make_request(self, endpoint, method='GET', data=None, timeout=5):
        """Make a single request and return metrics"""
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", timeout=timeout)
            elif method == 'POST':
                response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=timeout)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': response.status_code in [200, 201, 202],
                'status_code': response.status_code,
                'response_time': response_time,
                'endpoint': endpoint,
                'method': method
            }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'status_code': 0,
                'response_time': end_time - start_time,
                'endpoint': endpoint,
                'method': method,
                'error': str(e)
            }
    
    def test_sudden_traffic_spike(self):
        """Test system response to sudden traffic spike"""
        try:
            print("🔍 Testing Sudden Traffic Spike...")
            
            endpoints = ['/', '/health', '/api/enterprise/health', '/api/analytics/business']
            results = []
            
            # Baseline: Normal load
            print("  Establishing baseline...")
            baseline_results = []
            for i in range(10):
                endpoint = random.choice(endpoints)
                result = self.make_request(endpoint)
                baseline_results.append(result)
                time.sleep(0.1)
            
            baseline_success = sum(1 for r in baseline_results if r['success'])
            baseline_rate = (baseline_success / len(baseline_results)) * 100
            
            # Spike: Sudden high load
            print("  Applying traffic spike...")
            spike_start = time.time()
            
            def spike_worker():
                spike_results = []
                for i in range(20):  # 20 requests per worker
                    endpoint = random.choice(endpoints)
                    result = self.make_request(endpoint, timeout=3)
                    spike_results.append(result)
                    time.sleep(0.01)  # Minimal delay
                return spike_results
            
            # Create 15 concurrent workers for spike
            threads = []
            for i in range(15):
                thread = threading.Thread(target=lambda: results.extend(spike_worker()))
                threads.append(thread)
                thread.start()
            
            # Wait for spike to complete
            for thread in threads:
                thread.join()
            
            spike_end = time.time()
            spike_duration = spike_end - spike_start
            
            # Calculate spike metrics
            spike_success = sum(1 for r in results if r['success'])
            spike_rate = (spike_success / len(results)) * 100
            spike_throughput = len(results) / spike_duration
            
            self.spike_metrics['spike_handling_capacity'] = len(results)
            self.spike_metrics['error_rate_during_spike'] = 100 - spike_rate
            self.spike_metrics['throughput_during_spike'] = spike_throughput
            
            if spike_rate >= 80 and spike_throughput >= 50:
                self.log_test("Sudden Traffic Spike", "PASS", 
                    f"Spike: {spike_rate:.1f}% success, {spike_throughput:.1f} req/s, {len(results)} requests")
                return True
            else:
                self.log_test("Sudden Traffic Spike", "FAIL", 
                    f"Spike: Only {spike_rate:.1f}% success, {spike_throughput:.1f} req/s")
                return False
                
        except Exception as e:
            self.log_test("Sudden Traffic Spike", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_multiple_spikes(self):
        """Test system with multiple consecutive spikes"""
        try:
            print("🔍 Testing Multiple Spikes...")
            
            endpoints = ['/', '/health', '/api/enterprise/health']
            all_results = []
            
            # Test 3 consecutive spikes
            for spike_num in range(1, 4):
                print(f"  Spike {spike_num}/3...")
                spike_results = []
                start_time = time.time()
                
                def spike_worker():
                    worker_results = []
                    for i in range(15):  # 15 requests per worker
                        endpoint = random.choice(endpoints)
                        result = self.make_request(endpoint, timeout=3)
                        worker_results.append(result)
                        time.sleep(0.01)
                    return worker_results
                
                # Create 8 concurrent workers for each spike
                threads = []
                for i in range(8):
                    thread = threading.Thread(target=lambda: spike_results.extend(spike_worker()))
                    threads.append(thread)
                    thread.start()
                
                # Wait for spike to complete
                for thread in threads:
                    thread.join()
                
                end_time = time.time()
                spike_duration = end_time - start_time
                
                # Calculate spike metrics
                spike_success = sum(1 for r in spike_results if r['success'])
                spike_rate = (spike_success / len(spike_results)) * 100
                spike_throughput = len(spike_results) / spike_duration
                
                all_results.extend(spike_results)
                
                print(f"    Spike {spike_num}: {spike_rate:.1f}% success, {spike_throughput:.1f} req/s")
                
                # Small delay between spikes
                time.sleep(1)
            
            # Calculate overall metrics
            total_success = sum(1 for r in all_results if r['success'])
            overall_rate = (total_success / len(all_results)) * 100
            
            if overall_rate >= 75:
                self.log_test("Multiple Spikes", "PASS", 
                    f"Overall: {overall_rate:.1f}% success across {len(all_results)} requests")
                return True
            else:
                self.log_test("Multiple Spikes", "FAIL", 
                    f"Overall: Only {overall_rate:.1f}% success across {len(all_results)} requests")
                return False
                
        except Exception as e:
            self.log_test("Multiple Spikes", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_spike_recovery(self):
        """Test system recovery after traffic spike"""
        try:
            print("🔍 Testing Spike Recovery...")
            
            endpoints = ['/', '/health', '/api/enterprise/health', '/api/analytics/business']
            
            # Apply spike
            print("  Applying traffic spike...")
            spike_results = []
            spike_start = time.time()
            
            def spike_worker():
                worker_results = []
                for i in range(25):  # 25 requests per worker
                    endpoint = random.choice(endpoints)
                    result = self.make_request(endpoint, timeout=3)
                    worker_results.append(result)
                    time.sleep(0.01)
                return worker_results
            
            # Create 10 concurrent workers for spike
            threads = []
            for i in range(10):
                thread = threading.Thread(target=lambda: spike_results.extend(spike_worker()))
                threads.append(thread)
                thread.start()
            
            # Wait for spike to complete
            for thread in threads:
                thread.join()
            
            spike_end = time.time()
            spike_duration = spike_end - spike_start
            
            # Wait for system to stabilize
            print("  Waiting for system stabilization...")
            time.sleep(2)
            
            # Test recovery
            print("  Testing system recovery...")
            recovery_start = time.time()
            recovery_results = []
            
            # Test normal load after spike
            for i in range(20):
                endpoint = random.choice(endpoints)
                result = self.make_request(endpoint, timeout=5)
                recovery_results.append(result)
                time.sleep(0.1)
            
            recovery_end = time.time()
            recovery_time = recovery_end - recovery_start
            
            # Calculate recovery metrics
            spike_success = sum(1 for r in spike_results if r['success'])
            spike_rate = (spike_success / len(spike_results)) * 100
            
            recovery_success = sum(1 for r in recovery_results if r['success'])
            recovery_rate = (recovery_success / len(recovery_results)) * 100
            
            self.spike_metrics['recovery_time_after_spike'] = recovery_time
            
            if recovery_rate >= 90:
                self.log_test("Spike Recovery", "PASS", 
                    f"Spike: {spike_rate:.1f}% success, Recovery: {recovery_rate:.1f}% success in {recovery_time:.2f}s")
                return True
            else:
                self.log_test("Spike Recovery", "FAIL", 
                    f"Recovery: Only {recovery_rate:.1f}% success after spike")
                return False
                
        except Exception as e:
            self.log_test("Spike Recovery", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_gradual_spike(self):
        """Test system with gradual traffic increase"""
        try:
            print("🔍 Testing Gradual Spike...")
            
            endpoints = ['/', '/health', '/api/enterprise/health']
            all_results = []
            
            # Gradually increase load
            load_levels = [5, 10, 20, 30, 40]  # Concurrent users
            
            for level in load_levels:
                print(f"  Load level: {level} concurrent users...")
                level_results = []
                start_time = time.time()
                
                def level_worker():
                    worker_results = []
                    for i in range(10):  # 10 requests per worker
                        endpoint = random.choice(endpoints)
                        result = self.make_request(endpoint, timeout=3)
                        worker_results.append(result)
                        time.sleep(0.02)
                    return worker_results
                
                # Create threads for current level
                threads = []
                for i in range(level):
                    thread = threading.Thread(target=lambda: level_results.extend(level_worker()))
                    threads.append(thread)
                    thread.start()
                
                # Wait for level to complete
                for thread in threads:
                    thread.join()
                
                end_time = time.time()
                level_duration = end_time - start_time
                
                # Calculate level metrics
                level_success = sum(1 for r in level_results if r['success'])
                level_rate = (level_success / len(level_results)) * 100
                level_throughput = len(level_results) / level_duration
                
                all_results.extend(level_results)
                
                print(f"    Level {level}: {level_rate:.1f}% success, {level_throughput:.1f} req/s")
                
                # Small delay between levels
                time.sleep(0.5)
            
            # Calculate overall metrics
            total_success = sum(1 for r in all_results if r['success'])
            overall_rate = (total_success / len(all_results)) * 100
            
            if overall_rate >= 80:
                self.log_test("Gradual Spike", "PASS", 
                    f"Overall: {overall_rate:.1f}% success across {len(all_results)} requests")
                return True
            else:
                self.log_test("Gradual Spike", "FAIL", 
                    f"Overall: Only {overall_rate:.1f}% success across {len(all_results)} requests")
                return False
                
        except Exception as e:
            self.log_test("Gradual Spike", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_spike_with_mixed_operations(self):
        """Test spike with mixed operation types"""
        try:
            print("🔍 Testing Spike with Mixed Operations...")
            
            # Mix of different operation types
            operations = [
                {'endpoint': '/', 'method': 'GET'},
                {'endpoint': '/health', 'method': 'GET'},
                {'endpoint': '/api/enterprise/health', 'method': 'GET'},
                {'endpoint': '/api/analytics/business', 'method': 'GET'},
                {'endpoint': '/api/i18n/set-language', 'method': 'POST', 'data': {'language': 'es'}},
                {'endpoint': '/api/i18n/languages', 'method': 'GET'},
                {'endpoint': '/api/cache/stats', 'method': 'GET'},
                {'endpoint': '/api/services', 'method': 'GET'}
            ]
            
            results = []
            start_time = time.time()
            
            def mixed_spike_worker():
                worker_results = []
                for i in range(15):  # 15 operations per worker
                    operation = random.choice(operations)
                    result = self.make_request(
                        operation['endpoint'],
                        method=operation['method'],
                        data=operation.get('data'),
                        timeout=3
                    )
                    worker_results.append(result)
                    time.sleep(0.01)
                return worker_results
            
            # Create 12 concurrent workers for mixed spike
            threads = []
            for i in range(12):
                thread = threading.Thread(target=lambda: results.extend(mixed_spike_worker()))
                threads.append(thread)
                thread.start()
            
            # Wait for spike to complete
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            spike_duration = end_time - start_time
            
            # Calculate metrics
            spike_success = sum(1 for r in results if r['success'])
            spike_rate = (spike_success / len(results)) * 100
            spike_throughput = len(results) / spike_duration
            
            if spike_rate >= 80 and spike_throughput >= 40:
                self.log_test("Mixed Operations Spike", "PASS", 
                    f"{spike_rate:.1f}% success, {spike_throughput:.1f} req/s, {len(results)} mixed operations")
                return True
            else:
                self.log_test("Mixed Operations Spike", "FAIL", 
                    f"Only {spike_rate:.1f}% success, {spike_throughput:.1f} req/s")
                return False
                
        except Exception as e:
            self.log_test("Mixed Operations Spike", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_spike_resilience(self):
        """Test system resilience during spikes"""
        try:
            print("🔍 Testing Spike Resilience...")
            
            endpoints = ['/', '/health', '/api/enterprise/health']
            
            # Test system resilience with repeated spikes
            resilience_results = []
            
            for spike_round in range(3):
                print(f"  Resilience round {spike_round + 1}/3...")
                round_results = []
                start_time = time.time()
                
                def resilience_worker():
                    worker_results = []
                    for i in range(20):  # 20 requests per worker
                        endpoint = random.choice(endpoints)
                        result = self.make_request(endpoint, timeout=2)
                        worker_results.append(result)
                        time.sleep(0.01)
                    return worker_results
                
                # Create 8 concurrent workers
                threads = []
                for i in range(8):
                    thread = threading.Thread(target=lambda: round_results.extend(resilience_worker()))
                    threads.append(thread)
                    thread.start()
                
                # Wait for round to complete
                for thread in threads:
                    thread.join()
                
                end_time = time.time()
                round_duration = end_time - start_time
                
                # Calculate round metrics
                round_success = sum(1 for r in round_results if r['success'])
                round_rate = (round_success / len(round_results)) * 100
                round_throughput = len(round_results) / round_duration
                
                resilience_results.extend(round_results)
                
                print(f"    Round {spike_round + 1}: {round_rate:.1f}% success, {round_throughput:.1f} req/s")
                
                # Short delay between rounds
                time.sleep(1)
            
            # Calculate overall resilience metrics
            total_success = sum(1 for r in resilience_results if r['success'])
            overall_rate = (total_success / len(resilience_results)) * 100
            
            if overall_rate >= 75:
                self.log_test("Spike Resilience", "PASS", 
                    f"Overall resilience: {overall_rate:.1f}% success across {len(resilience_results)} requests")
                return True
            else:
                self.log_test("Spike Resilience", "FAIL", 
                    f"Overall resilience: Only {overall_rate:.1f}% success")
                return False
                
        except Exception as e:
            self.log_test("Spike Resilience", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_spike_tests(self):
        """Run all spike performance tests"""
        print("🔍 Starting Spike Performance Testing...")
        print("=" * 60)
        
        # Run all spike tests
        self.test_sudden_traffic_spike()
        self.test_multiple_spikes()
        self.test_spike_recovery()
        self.test_gradual_spike()
        self.test_spike_with_mixed_operations()
        self.test_spike_resilience()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Spike Performance Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # Print spike metrics
        print(f"\n📈 Spike Metrics:")
        print(f"  - Spike Handling Capacity: {self.spike_metrics['spike_handling_capacity']} requests")
        print(f"  - Recovery Time After Spike: {self.spike_metrics['recovery_time_after_spike']:.2f}s")
        print(f"  - Error Rate During Spike: {self.spike_metrics['error_rate_during_spike']:.1f}%")
        print(f"  - Throughput During Spike: {self.spike_metrics['throughput_during_spike']:.1f} req/s")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = SpikePerformanceTester()
    success = tester.run_all_spike_tests()
    exit(0 if success else 1)