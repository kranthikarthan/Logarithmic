# 🧪 Jira Integration Testing

## Overview

This directory contains Jira integration testing tools to improve test coverage and validate Jira integration features.

## Files

### **Core Testing Files**
- `jira_stub.py` - Mock Jira server for testing
- `test_jira_integration.py` - Comprehensive Jira integration tests
- `improve_test_coverage.py` - Test coverage improvement tool
- `run_jira_tests.py` - Quick test runner

## 🚀 Quick Start

### **1. Run Jira Integration Tests**
```bash
# Quick test run
python3 run_jira_tests.py

# Or run comprehensive tests
python3 test_jira_integration.py
```

### **2. Improve Test Coverage**
```bash
# Run coverage improvement
python3 improve_test_coverage.py
```

### **3. Start Jira Stub Server**
```bash
# Start mock Jira server
python3 jira_stub.py
```

## 📊 Test Coverage Improvement

### **Available Test Suites**
1. **Database Integration** - `test_database_integration.py`
2. **Load Performance** - `test_load_performance.py`
3. **Stress Performance** - `test_stress_performance.py`
4. **User Workflows** - `test_user_workflows.py`
5. **AI Workflows** - `test_ai_workflows.py`
6. **Enterprise Workflows** - `test_enterprise_workflows.py`
7. **Data Flow** - `test_data_flow.py`
8. **Error Scenarios** - `test_error_scenarios.py`
9. **Jira Integration** - `test_jira_integration.py`

### **Coverage Metrics**
- **Target Success Rate**: 80%+
- **Target Code Coverage**: 80%+
- **Test Types**: Unit, Integration, Performance, E2E

## 🔧 Jira Stub Server

### **Endpoints Available**
- `GET /rest/api/3/project` - List projects
- `GET /rest/api/3/project/{key}` - Get project
- `GET /rest/api/3/search` - Search issues
- `GET /rest/api/3/issue/{key}` - Get issue
- `POST /rest/api/3/issue` - Create issue
- `GET /rest/api/3/issue/{key}/links` - Get issue links
- `POST /rest/api/3/issueLink` - Create issue link
- `GET /rest/api/3/myself` - Get user info
- `GET /health` - Health check

### **Mock Data**
- **Projects**: TEST, DEMO, QA
- **Issues**: Test cases with various statuses
- **Links**: Issue relationships and traceability

## 📈 Expected Results

### **Test Success Rate**
- **Excellent**: 90%+
- **Good**: 80-89%
- **Needs Improvement**: <80%

### **Code Coverage**
- **Excellent**: 90%+
- **Good**: 80-89%
- **Needs Improvement**: <80%

## 🎯 Usage Examples

### **Test Jira Integration**
```bash
# Start Jira stub server
python3 jira_stub.py &
# Server runs on http://localhost:8080

# Run integration tests
python3 test_jira_integration.py
```

### **Improve Coverage**
```bash
# Run all test suites
python3 improve_test_coverage.py

# Check coverage report
cat test_coverage_report.json
```

### **Quick Test**
```bash
# Run quick Jira test
python3 run_jira_tests.py
```

## 📊 Reports Generated

### **Test Coverage Report**
- `test_coverage_report.json` - Detailed coverage analysis
- `coverage.json` - Pytest coverage data
- `htmlcov/` - HTML coverage report

### **Test Results**
- Console output with pass/fail status
- Detailed error messages for failed tests
- Performance metrics and timing

## 🔍 Troubleshooting

### **Common Issues**
1. **Port conflicts** - Ensure ports 5000 and 8080 are available
2. **Dependencies** - Install required Python packages
3. **Timeout errors** - Increase timeout values for slow tests

### **Debug Mode**
```bash
# Run with debug output
python3 test_jira_integration.py --debug

# Check Jira stub server logs
python3 jira_stub.py --verbose
```

## ✅ Success Criteria

### **Test Coverage Goals**
- ✅ **80%+ Test Success Rate**
- ✅ **80%+ Code Coverage**
- ✅ **All Critical Paths Tested**
- ✅ **Integration Tests Passing**
- ✅ **Performance Tests Within Limits**

### **Jira Integration Goals**
- ✅ **Jira Stub Server Healthy**
- ✅ **Projects API Working**
- ✅ **Issues API Working**
- ✅ **Issue Creation Working**
- ✅ **Assertly Integration Working**

---

**Status**: ✅ **READY FOR TESTING**  
**Usage**: Run `python3 run_jira_tests.py` to start  
**Coverage**: Use `python3 improve_test_coverage.py` for comprehensive testing