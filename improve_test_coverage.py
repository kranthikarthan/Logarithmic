#!/usr/bin/env python3
"""
Test Coverage Improvement Script
Runs comprehensive tests to improve test coverage percentage
"""

import subprocess
import sys
import os
import time
import json
from datetime import datetime

class TestCoverageImprover:
    def __init__(self):
        self.test_results = {}
        self.coverage_reports = {}
        
    def run_test_suite(self, test_name, test_file):
        """Run a specific test suite"""
        print(f"\n🧪 Running {test_name}...")
        try:
            result = subprocess.run(
                ['python3', test_file],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            self.test_results[test_name] = {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                print(f"   Error: {result.stderr}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name}: TIMEOUT")
            self.test_results[test_name] = {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Test timed out after 5 minutes'
            }
            return False
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            self.test_results[test_name] = {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }
            return False
    
    def run_coverage_analysis(self):
        """Run coverage analysis"""
        print("\n📊 Running Coverage Analysis...")
        try:
            # Run pytest with coverage
            result = subprocess.run([
                'python3', '-m', 'pytest', 
                '--cov=app',
                '--cov-report=json',
                '--cov-report=html',
                '--cov-report=term'
            ], capture_output=True, text=True, timeout=600)
            
            # Parse coverage report
            if os.path.exists('coverage.json'):
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
                    total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                    self.coverage_reports['pytest'] = {
                        'coverage': total_coverage,
                        'success': result.returncode == 0
                    }
                    print(f"✅ Coverage: {total_coverage:.1f}%")
                    return total_coverage
            else:
                print("❌ Coverage report not generated")
                return 0
                
        except Exception as e:
            print(f"❌ Coverage analysis failed: {e}")
            return 0
    
    def run_comprehensive_tests(self):
        """Run all available test suites"""
        print("🚀 Starting Comprehensive Test Coverage Improvement")
        print("=" * 60)
        
        # Test suites to run
        test_suites = [
            ("Database Integration", "test_database_integration.py"),
            ("Load Performance", "test_load_performance.py"),
            ("Stress Performance", "test_stress_performance.py"),
            ("User Workflows", "test_user_workflows.py"),
            ("AI Workflows", "test_ai_workflows.py"),
            ("Enterprise Workflows", "test_enterprise_workflows.py"),
            ("Data Flow", "test_data_flow.py"),
            ("Error Scenarios", "test_error_scenarios.py"),
            ("Jira Integration", "test_jira_integration.py")
        ]
        
        # Run each test suite
        results = {}
        for test_name, test_file in test_suites:
            if os.path.exists(test_file):
                success = self.run_test_suite(test_name, test_file)
                results[test_name] = success
            else:
                print(f"⚠️ {test_name}: Test file not found ({test_file})")
                results[test_name] = False
        
        # Run coverage analysis
        coverage = self.run_coverage_analysis()
        
        # Calculate overall results
        total_tests = len(results)
        passed_tests = sum(results.values())
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Generate report
        self.generate_coverage_report(results, coverage, success_rate)
        
        return success_rate, coverage
    
    def generate_coverage_report(self, results, coverage, success_rate):
        """Generate comprehensive coverage report"""
        print("\n" + "=" * 60)
        print("📊 TEST COVERAGE IMPROVEMENT REPORT")
        print("=" * 60)
        
        # Test results summary
        print(f"\n🧪 TEST SUITE RESULTS:")
        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  {test_name}: {status}")
        
        print(f"\n📈 OVERALL METRICS:")
        print(f"  Test Success Rate: {success_rate:.1f}%")
        print(f"  Code Coverage: {coverage:.1f}%")
        print(f"  Total Test Suites: {len(results)}")
        print(f"  Passed Tests: {sum(results.values())}")
        print(f"  Failed Tests: {len(results) - sum(results.values())}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate < 80:
            print("  ⚠️ Test success rate is below 80% - focus on fixing failing tests")
        if coverage < 80:
            print("  ⚠️ Code coverage is below 80% - add more test cases")
        if success_rate >= 80 and coverage >= 80:
            print("  ✅ Excellent test coverage achieved!")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'test_results': results,
            'coverage': coverage,
            'success_rate': success_rate,
            'recommendations': self.get_recommendations(success_rate, coverage)
        }
        
        with open('test_coverage_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: test_coverage_report.json")
    
    def get_recommendations(self, success_rate, coverage):
        """Get improvement recommendations"""
        recommendations = []
        
        if success_rate < 70:
            recommendations.append("Focus on fixing failing test suites")
        if coverage < 70:
            recommendations.append("Add more unit tests for uncovered code")
        if success_rate < 90:
            recommendations.append("Improve test reliability and stability")
        if coverage < 90:
            recommendations.append("Add integration tests for edge cases")
        
        if success_rate >= 90 and coverage >= 90:
            recommendations.append("Excellent test coverage achieved!")
        
        return recommendations

def main():
    """Main function"""
    print("🎯 Test Coverage Improvement Tool")
    print("Improving test coverage percentage for Assertly")
    print("=" * 60)
    
    improver = TestCoverageImprover()
    success_rate, coverage = improver.run_comprehensive_tests()
    
    print(f"\n🎉 Test Coverage Improvement Complete!")
    print(f"📊 Final Results:")
    print(f"  Test Success Rate: {success_rate:.1f}%")
    print(f"  Code Coverage: {coverage:.1f}%")
    
    if success_rate >= 80 and coverage >= 80:
        print("✅ Excellent test coverage achieved!")
        return 0
    else:
        print("⚠️ Test coverage needs improvement")
        return 1

if __name__ == "__main__":
    exit(main())