#!/usr/bin/env python3
"""
Volume Testing for Assertly
Tests system performance with large amounts of data and high data volumes
"""

import requests
import time
import threading
import statistics
from datetime import datetime
import json
import random
import string

class VolumePerformanceTester:
    """Comprehensive volume testing suite"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.volume_metrics = {
            'max_data_size': 0,
            'max_requests_per_second': 0,
            'data_processing_time': 0,
            'memory_usage_peak': 0
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
    
    def make_request(self, endpoint, method='GET', data=None, timeout=10):
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
                'method': method,
                'response_size': len(response.content) if hasattr(response, 'content') else 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'status_code': 0,
                'response_time': end_time - start_time,
                'endpoint': endpoint,
                'method': method,
                'error': str(e),
                'response_size': 0
            }
    
    def generate_large_data(self, size_kb):
        """Generate large data payload"""
        # Generate random string data
        data_size = size_kb * 1024
        random_data = ''.join(random.choices(string.ascii_letters + string.digits, k=data_size))
        
        return {
            'title': f'Large Test Data {size_kb}KB',
            'description': random_data,
            'content': random_data,
            'metadata': {
                'size': data_size,
                'timestamp': datetime.now().isoformat(),
                'type': 'volume_test'
            }
        }
    
    def test_large_payload_handling(self):
        """Test system with large payloads"""
        try:
            print("🔍 Testing Large Payload Handling...")
            
            # Test with different payload sizes
            payload_sizes = [1, 5, 10, 25, 50]  # KB
            results = []
            
            for size_kb in payload_sizes:
                print(f"  Testing {size_kb}KB payload...")
                large_data = self.generate_large_data(size_kb)
                
                # Test with language setting (simulates large data processing)
                result = self.make_request(
                    '/api/i18n/set-language',
                    method='POST',
                    data={'language': 'en', 'large_data': large_data},
                    timeout=15
                )
                results.append(result)
                
                # Test with analytics (simulates large data analysis)
                result = self.make_request('/api/analytics/business', timeout=15)
                results.append(result)
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            max_payload_size = max(payload_sizes)
            
            self.volume_metrics['max_data_size'] = max_payload_size
            
            if success_rate >= 80 and avg_response_time < 10.0:
                self.log_test("Large Payload Handling", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, up to {max_payload_size}KB")
                return True
            else:
                self.log_test("Large Payload Handling", "FAIL", 
                    f"Only {success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
                return False
                
        except Exception as e:
            self.log_test("Large Payload Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_high_volume_requests(self):
        """Test system with high volume of requests"""
        try:
            print("🔍 Testing High Volume Requests...")
            
            endpoints = [
                '/',
                '/health',
                '/api/enterprise/health',
                '/api/analytics/business',
                '/api/i18n/languages',
                '/api/cache/stats',
                '/api/services'
            ]
            
            results = []
            start_time = time.time()
            
            # Make 500 requests rapidly
            for i in range(500):
                endpoint = random.choice(endpoints)
                result = self.make_request(endpoint, timeout=5)
                results.append(result)
                time.sleep(0.01)  # Small delay
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            requests_per_second = len(results) / duration
            
            self.volume_metrics['max_requests_per_second'] = requests_per_second
            
            if success_rate >= 90 and requests_per_second >= 50:
                self.log_test("High Volume Requests", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {requests_per_second:.1f} req/s")
                return True
            else:
                self.log_test("High Volume Requests", "FAIL", 
                    f"Only {success_rate:.1f}% success, {requests_per_second:.1f} req/s")
                return False
                
        except Exception as e:
            self.log_test("High Volume Requests", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_data_processing_volume(self):
        """Test data processing with high volume"""
        try:
            print("🔍 Testing Data Processing Volume...")
            
            # Simulate high volume data processing
            processing_tasks = []
            start_time = time.time()
            
            # Create multiple data processing tasks
            for i in range(100):
                # Simulate analytics processing
                result = self.make_request('/api/analytics/business', timeout=10)
                processing_tasks.append(result)
                
                # Simulate cache operations
                result = self.make_request('/api/cache/stats', timeout=10)
                processing_tasks.append(result)
                
                # Simulate enterprise operations
                result = self.make_request('/api/enterprise/health', timeout=10)
                processing_tasks.append(result)
                
                time.sleep(0.02)  # Small delay between tasks
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_tasks = sum(1 for r in processing_tasks if r['success'])
            success_rate = (successful_tasks / len(processing_tasks)) * 100
            avg_processing_time = statistics.mean([r['response_time'] for r in processing_tasks])
            tasks_per_second = len(processing_tasks) / duration
            
            self.volume_metrics['data_processing_time'] = duration
            
            if success_rate >= 85 and tasks_per_second >= 10:
                self.log_test("Data Processing Volume", "PASS", 
                    f"{success_rate:.1f}% success, {avg_processing_time:.3f}s avg processing, {tasks_per_second:.1f} tasks/s")
                return True
            else:
                self.log_test("Data Processing Volume", "FAIL", 
                    f"Only {success_rate:.1f}% success, {tasks_per_second:.1f} tasks/s")
                return False
                
        except Exception as e:
            self.log_test("Data Processing Volume", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_concurrent_volume_processing(self):
        """Test concurrent volume processing"""
        try:
            print("🔍 Testing Concurrent Volume Processing...")
            
            results = []
            start_time = time.time()
            
            def volume_worker(worker_id):
                worker_results = []
                for i in range(20):  # 20 tasks per worker
                    # Mix of different volume operations
                    operations = [
                        '/api/analytics/business',
                        '/api/cache/stats',
                        '/api/enterprise/health',
                        '/api/i18n/languages',
                        '/api/services'
                    ]
                    
                    endpoint = random.choice(operations)
                    result = self.make_request(endpoint, timeout=8)
                    worker_results.append(result)
                    time.sleep(0.05)
                
                results.extend(worker_results)
            
            # Create 10 concurrent workers
            threads = []
            for i in range(10):
                thread = threading.Thread(target=volume_worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all workers to complete
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_requests = sum(1 for r in results if r['success'])
            success_rate = (successful_requests / len(results)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            concurrent_throughput = len(results) / duration
            
            if success_rate >= 80 and concurrent_throughput >= 20:
                self.log_test("Concurrent Volume Processing", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {concurrent_throughput:.1f} req/s")
                return True
            else:
                self.log_test("Concurrent Volume Processing", "FAIL", 
                    f"Only {success_rate:.1f}% success, {concurrent_throughput:.1f} req/s")
                return False
                
        except Exception as e:
            self.log_test("Concurrent Volume Processing", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_memory_usage_volume(self):
        """Test memory usage with high volume"""
        try:
            print("🔍 Testing Memory Usage with High Volume...")
            
            # Simulate memory-intensive operations
            memory_operations = []
            start_time = time.time()
            
            # Create many concurrent operations to test memory usage
            for i in range(200):
                # Operations that might use memory
                result = self.make_request('/api/analytics/business', timeout=5)
                memory_operations.append(result)
                
                result = self.make_request('/api/cache/stats', timeout=5)
                memory_operations.append(result)
                
                time.sleep(0.01)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_operations = sum(1 for r in memory_operations if r['success'])
            success_rate = (successful_operations / len(memory_operations)) * 100
            
            # Test system responsiveness after memory operations
            final_test = self.make_request('/health', timeout=5)
            
            if success_rate >= 85 and final_test['success']:
                self.log_test("Memory Usage Volume", "PASS", 
                    f"{success_rate:.1f}% success, system remains responsive after {len(memory_operations)} operations")
                return True
            else:
                self.log_test("Memory Usage Volume", "FAIL", 
                    f"Only {success_rate:.1f}% success or system unresponsive")
                return False
                
        except Exception as e:
            self.log_test("Memory Usage Volume", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_database_volume_operations(self):
        """Test database operations with high volume"""
        try:
            print("🔍 Testing Database Volume Operations...")
            
            # Test database-intensive operations
            db_operations = []
            start_time = time.time()
            
            # Simulate high volume database operations
            for i in range(150):
                # Operations that involve database
                result = self.make_request('/api/enterprise/audit/logs', timeout=8)
                db_operations.append(result)
                
                result = self.make_request('/api/enterprise/health', timeout=8)
                db_operations.append(result)
                
                # Simulate language setting (database write)
                if i % 10 == 0:  # Every 10th operation
                    result = self.make_request(
                        '/api/i18n/set-language',
                        method='POST',
                        data={'language': 'es'},
                        timeout=8
                    )
                    db_operations.append(result)
                
                time.sleep(0.02)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_operations = sum(1 for r in db_operations if r['success'])
            success_rate = (successful_operations / len(db_operations)) * 100
            avg_response_time = statistics.mean([r['response_time'] for r in db_operations])
            operations_per_second = len(db_operations) / duration
            
            if success_rate >= 80 and operations_per_second >= 5:
                self.log_test("Database Volume Operations", "PASS", 
                    f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response, {operations_per_second:.1f} ops/s")
                return True
            else:
                self.log_test("Database Volume Operations", "FAIL", 
                    f"Only {success_rate:.1f}% success, {operations_per_second:.1f} ops/s")
                return False
                
        except Exception as e:
            self.log_test("Database Volume Operations", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_volume_tests(self):
        """Run all volume performance tests"""
        print("🔍 Starting Volume Performance Testing...")
        print("=" * 60)
        
        # Run all volume tests
        self.test_large_payload_handling()
        self.test_high_volume_requests()
        self.test_data_processing_volume()
        self.test_concurrent_volume_processing()
        self.test_memory_usage_volume()
        self.test_database_volume_operations()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Volume Performance Test Results:")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n❌ Errors Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        # Print volume metrics
        print(f"\n📈 Volume Metrics:")
        print(f"  - Max Data Size: {self.volume_metrics['max_data_size']}KB")
        print(f"  - Max Requests/Second: {self.volume_metrics['max_requests_per_second']:.1f}")
        print(f"  - Data Processing Time: {self.volume_metrics['data_processing_time']:.2f}s")
        print(f"  - Memory Usage Peak: {self.volume_metrics['memory_usage_peak']}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = VolumePerformanceTester()
    success = tester.run_all_volume_tests()
    exit(0 if success else 1)