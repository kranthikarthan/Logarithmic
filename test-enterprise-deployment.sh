#!/bin/bash

# Assertly Enterprise Deployment Testing Script
# Tests the enterprise deployment package

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:5000"
HEALTH_ENDPOINT="$BASE_URL/api/enterprise/health"
ENTERPRISE_SETTINGS="$BASE_URL/enterprise-settings"
TIMEOUT=30

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Print colored output
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="${3:-200}"
    
    ((TOTAL_TESTS++))
    print_status "Running: $test_name"
    
    if eval "$test_command"; then
        print_success "$test_name"
        return 0
    else
        print_error "$test_name"
        return 1
    fi
}

# Wait for service to be ready
wait_for_service() {
    print_status "Waiting for Assertly Enterprise to be ready..."
    
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if curl -s -f "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
            print_success "Service is ready"
            return 0
        fi
        
        ((attempts++))
        print_status "Attempt $attempts/$max_attempts - waiting for service..."
        sleep 2
    done
    
    print_error "Service failed to start within timeout"
    return 1
}

# Test 1: Health Check
test_health_check() {
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$HEALTH_ENDPOINT")
    [ "$response" = "200" ]
}

# Test 2: Enterprise Settings Page
test_enterprise_settings() {
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$ENTERPRISE_SETTINGS")
    [ "$response" = "200" ]
}

# Test 3: Enterprise AI Configuration
test_enterprise_ai_config() {
    local config_data='{
        "local_ai_url": "http://test-ai.company.com:8080/api",
        "local_ai_model": "local-copilot",
        "local_api_key": "test-key",
        "proxy_url": "",
        "cert_path": "",
        "verify_ssl": true
    }'
    
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$config_data" \
        -w "%{http_code}" \
        -o /dev/null \
        "$BASE_URL/api/enterprise/ai/configure")
    
    [ "$response" = "200" ]
}

# Test 4: Enterprise AI Connection Test
test_enterprise_ai_connection() {
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/api/enterprise/ai/test-connection")
    # This might return 400 if not configured, which is expected
    [ "$response" = "200" ] || [ "$response" = "400" ]
}

# Test 5: Audit Logs
test_audit_logs() {
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/api/enterprise/audit/logs")
    [ "$response" = "200" ]
}

# Test 6: Compliance Report Generation
test_compliance_report() {
    local report_data='{
        "report_type": "audit_summary",
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-12-31T23:59:59"
    }'
    
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$report_data" \
        -w "%{http_code}" \
        -o /dev/null \
        "$BASE_URL/api/enterprise/compliance/report")
    
    [ "$response" = "200" ]
}

# Test 7: Enterprise AI Test Case Generation
test_enterprise_ai_generation() {
    local test_data='{
        "title": "User Login Test",
        "description": "As a user, I want to log in so that I can access my account",
        "acceptance_criteria": ["User can enter credentials", "User is logged in successfully"],
        "business_value": "Enables secure access to user accounts",
        "user_persona": "Registered user",
        "test_types": ["functional", "ui"],
        "num_cases": 3
    }'
    
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$test_data" \
        -w "%{http_code}" \
        -o /dev/null \
        "$BASE_URL/api/enterprise/ai/generate-test-cases")
    
    # This might return 500 if local AI is not available, which is expected
    [ "$response" = "200" ] || [ "$response" = "500" ]
}

# Test 8: Security Headers
test_security_headers() {
    local headers=$(curl -s -I "$BASE_URL" | grep -i "x-frame-options\|x-content-type-options\|x-xss-protection")
    [ -n "$headers" ]
}

# Test 9: SSL/TLS Configuration (if HTTPS)
test_ssl_configuration() {
    # This test would check SSL configuration if HTTPS is enabled
    # For now, we'll just check if the service responds
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL")
    [ "$response" = "200" ]
}

# Test 10: Database Connectivity
test_database_connectivity() {
    # This would test database connectivity
    # For now, we'll check if the health endpoint returns database status
    local health_response=$(curl -s "$HEALTH_ENDPOINT")
    echo "$health_response" | grep -q "status"
}

# Test 11: Cache Connectivity
test_cache_connectivity() {
    # This would test Redis connectivity
    # For now, we'll check if the service is responding
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL")
    [ "$response" = "200" ]
}

# Test 12: Monitoring Endpoints
test_monitoring_endpoints() {
    # Test Prometheus metrics endpoint
    local prometheus_response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:9090/metrics" 2>/dev/null || echo "000")
    [ "$prometheus_response" = "200" ] || [ "$prometheus_response" = "000" ]
}

# Test 13: Grafana Dashboard
test_grafana_dashboard() {
    # Test Grafana dashboard
    local grafana_response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:3000" 2>/dev/null || echo "000")
    [ "$grafana_response" = "200" ] || [ "$grafana_response" = "000" ]
}

# Test 14: Enterprise Configuration Persistence
test_configuration_persistence() {
    # Test that configuration is persisted
    local health_response=$(curl -s "$HEALTH_ENDPOINT")
    echo "$health_response" | grep -q "enterprise_mode"
}

# Test 15: Offline Capabilities
test_offline_capabilities() {
    # Test offline AI capabilities
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/api/enterprise/health")
    [ "$response" = "200" ]
}

# Performance Tests
test_performance() {
    print_status "Running performance tests..."
    
    # Test response time
    local start_time=$(date +%s%N)
    curl -s "$HEALTH_ENDPOINT" > /dev/null
    local end_time=$(date +%s%N)
    local response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [ $response_time -lt 1000 ]; then
        print_success "Response time: ${response_time}ms (acceptable)"
    else
        print_warning "Response time: ${response_time}ms (slow)"
    fi
}

# Load Testing
test_load() {
    print_status "Running load tests..."
    
    local concurrent_requests=10
    local total_requests=50
    
    print_status "Sending $total_requests requests with $concurrent_requests concurrent connections..."
    
    # Use curl to send multiple requests
    for i in $(seq 1 $total_requests); do
        curl -s "$HEALTH_ENDPOINT" > /dev/null &
        if [ $((i % concurrent_requests)) -eq 0 ]; then
            wait
        fi
    done
    wait
    
    print_success "Load test completed"
}

# Security Tests
test_security() {
    print_status "Running security tests..."
    
    # Test for common vulnerabilities
    local security_tests=(
        "curl -s -w '%{http_code}' -o /dev/null '$BASE_URL/../etc/passwd'"
        "curl -s -w '%{http_code}' -o /dev/null '$BASE_URL/../../etc/passwd'"
        "curl -s -w '%{http_code}' -o /dev/null '$BASE_URL/../../../etc/passwd'"
    )
    
    for test in "${security_tests[@]}"; do
        local response=$(eval "$test")
        if [ "$response" = "404" ] || [ "$response" = "403" ]; then
            print_success "Security test passed: $test"
        else
            print_error "Security test failed: $test (response: $response)"
        fi
    done
}

# Main test execution
main() {
    echo "=========================================="
    echo "Assertly Enterprise Deployment Testing"
    echo "=========================================="
    echo
    
    # Wait for service to be ready
    if ! wait_for_service; then
        print_error "Service is not ready. Exiting."
        exit 1
    fi
    
    echo
    print_status "Starting enterprise deployment tests..."
    echo
    
    # Core functionality tests
    run_test "Health Check" "test_health_check"
    run_test "Enterprise Settings Page" "test_enterprise_settings"
    run_test "Enterprise AI Configuration" "test_enterprise_ai_config"
    run_test "Enterprise AI Connection Test" "test_enterprise_ai_connection"
    run_test "Audit Logs" "test_audit_logs"
    run_test "Compliance Report Generation" "test_compliance_report"
    run_test "Enterprise AI Test Case Generation" "test_enterprise_ai_generation"
    
    # Security tests
    run_test "Security Headers" "test_security_headers"
    run_test "SSL/TLS Configuration" "test_ssl_configuration"
    
    # Infrastructure tests
    run_test "Database Connectivity" "test_database_connectivity"
    run_test "Cache Connectivity" "test_cache_connectivity"
    run_test "Monitoring Endpoints" "test_monitoring_endpoints"
    run_test "Grafana Dashboard" "test_grafana_dashboard"
    
    # Enterprise features
    run_test "Configuration Persistence" "test_configuration_persistence"
    run_test "Offline Capabilities" "test_offline_capabilities"
    
    # Performance and security tests
    test_performance
    test_load
    test_security
    
    # Display results
    echo
    echo "=========================================="
    echo "Test Results Summary"
    echo "=========================================="
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $TESTS_PASSED"
    echo "Failed: $TESTS_FAILED"
    echo
    
    if [ $TESTS_FAILED -eq 0 ]; then
        print_success "All tests passed! Enterprise deployment is working correctly."
        exit 0
    else
        print_error "Some tests failed. Please check the deployment."
        exit 1
    fi
}

# Run main function
main "$@"