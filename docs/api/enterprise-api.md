# Assertly Enterprise API Documentation

## 🚀 **Complete API Reference for Assertly**

This document provides comprehensive API documentation for Assertly's enterprise features, AI integration, and core functionality.

## 📋 **Base URL**

```
Production: https://your-assertly-instance.com
Development: http://localhost:5000
```

## 🔐 **Authentication**

### **API Key Authentication**
```bash
# Add API key to headers
curl -H "Authorization: Bearer your-api-key" \
     -H "Content-Type: application/json" \
     https://your-assertly-instance.com/api/endpoint
```

### **Session Authentication**
```bash
# Login first
curl -X POST https://your-assertly-instance.com/login \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "password": "pass"}'

# Use session cookie for subsequent requests
curl -b cookies.txt https://your-assertly-instance.com/api/endpoint
```

## 🤖 **AI Test Generation API**

### **Generate Test Cases**
```http
POST /api/ai/generate-test-cases
Content-Type: application/json

{
  "title": "User Authentication",
  "description": "As a user, I want to login to the system",
  "acceptance_criteria": [
    "User can login with valid credentials",
    "User cannot login with invalid credentials"
  ],
  "business_value": "Secure access to the system",
  "user_persona": "End user"
}
```

**Response:**
```json
{
  "success": true,
  "test_cases": [
    {
      "title": "Valid Login Test",
      "description": "Test user login with valid credentials",
      "steps": [
        "1. Navigate to login page",
        "2. Enter valid username",
        "3. Enter valid password",
        "4. Click login button"
      ],
      "expected_result": "User should be successfully logged in",
      "test_type": "functional",
      "priority": "high",
      "tags": ["smoke", "regression"],
      "preconditions": ["User account exists"],
      "test_data": "Valid username and password",
      "acceptance_criteria": ["Login successful"]
    }
  ],
  "count": 1,
  "provider": "openai",
  "note": "Generated using OpenAI GPT-4"
}
```

### **Improve Test Case**
```http
POST /api/ai/improve-test-case
Content-Type: application/json

{
  "test_case": {
    "title": "Basic Login Test",
    "description": "Test user login",
    "steps": ["1. Login", "2. Verify"],
    "expected_result": "Login successful"
  },
  "improvement_prompts": [
    "Add security testing scenarios",
    "Include edge cases",
    "Add performance considerations"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "improved_test_case": {
    "title": "Enhanced Login Test with Security",
    "description": "Comprehensive login testing with security scenarios",
    "steps": [
      "1. Navigate to login page",
      "2. Enter valid username",
      "3. Enter valid password",
      "4. Click login button",
      "5. Verify successful login",
      "6. Test session timeout",
      "7. Test password complexity"
    ],
    "expected_result": "User should be successfully logged in with proper security",
    "test_type": "functional",
    "priority": "high",
    "tags": ["smoke", "regression", "security"],
    "preconditions": ["User account exists", "Security policies configured"],
    "test_data": "Valid credentials with security requirements",
    "acceptance_criteria": ["Login successful", "Security enforced"]
  },
  "provider": "openai",
  "note": "Enhanced using OpenAI GPT-4"
}
```

### **Generate BDD Scenarios**
```http
POST /api/ai/generate-bdd-scenarios
Content-Type: application/json

{
  "title": "User Registration",
  "description": "As a new user, I want to register for an account",
  "acceptance_criteria": [
    "User can create account with valid information",
    "User cannot create account with invalid information"
  ],
  "business_value": "User onboarding",
  "user_persona": "New user"
}
```

**Response:**
```json
{
  "success": true,
  "scenarios": [
    {
      "title": "Successful User Registration",
      "description": "Given a new user wants to register",
      "steps": [
        "Given the user is on the registration page",
        "When the user enters valid information",
        "Then the user should be successfully registered"
      ],
      "tags": ["smoke", "regression"],
      "examples": [
        {
          "name": "Valid registration",
          "data": {
            "email": "user@example.com",
            "password": "SecurePass123",
            "expected": "Registration successful"
          }
        }
      ]
    }
  ],
  "count": 1,
  "provider": "openai",
  "note": "Generated using OpenAI GPT-4"
}
```

### **Generate Test Data**
```http
POST /api/ai/generate-test-data
Content-Type: application/json

{
  "data_type": "user_credentials",
  "scenarios": ["valid", "invalid", "boundary"],
  "count": 10,
  "constraints": {
    "password_min_length": 8,
    "email_format": "valid"
  }
}
```

**Response:**
```json
{
  "success": true,
  "test_data": [
    {
      "scenario": "valid",
      "data": {
        "username": "testuser1",
        "email": "test1@example.com",
        "password": "SecurePass123"
      }
    },
    {
      "scenario": "invalid",
      "data": {
        "username": "",
        "email": "invalid-email",
        "password": "123"
      }
    }
  ],
  "count": 10,
  "provider": "openai",
  "note": "Generated using OpenAI GPT-4"
}
```

### **Analyze Test Coverage**
```http
POST /api/ai/analyze-coverage
Content-Type: application/json

{
  "test_cases": [
    {
      "title": "Login Test",
      "test_type": "functional",
      "priority": "high"
    }
  ],
  "requirements": [
    {
      "id": "REQ-001",
      "description": "User authentication",
      "priority": "high"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "coverage_analysis": {
    "overall_coverage": 85.5,
    "requirements_coverage": [
      {
        "requirement_id": "REQ-001",
        "coverage_percentage": 100.0,
        "test_cases": ["Login Test"]
      }
    ],
    "gaps": [
      {
        "requirement_id": "REQ-002",
        "description": "Password reset functionality",
        "coverage_percentage": 0.0,
        "recommendation": "Add test cases for password reset"
      }
    ],
    "recommendations": [
      "Add negative test cases for authentication",
      "Include performance testing for login",
      "Add security testing scenarios"
    ]
  },
  "provider": "openai",
  "note": "Analyzed using OpenAI GPT-4"
}
```

## 🔑 **API Key Management**

### **Get API Keys**
```http
GET /api/ai/keys
```

**Response:**
```json
{
  "success": true,
  "keys": {
    "openai": {
      "provider": "openai",
      "model": "gpt-4",
      "max_tokens": 4000,
      "temperature": 0.7,
      "timeout": 30,
      "retry_attempts": 3,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00",
      "last_used": "2024-01-01T12:00:00",
      "usage_count": 150,
      "monthly_limit": 10000,
      "cost_per_token": 0.00003
    }
  }
}
```

### **Add API Key**
```http
POST /api/ai/keys
Content-Type: application/json

{
  "provider": "openai",
  "apiKey": "sk-your-openai-key",
  "model": "gpt-4",
  "maxTokens": 4000,
  "temperature": 0.7,
  "timeout": 30,
  "retryAttempts": 3,
  "isActive": true,
  "monthlyLimit": 10000,
  "costPerToken": 0.00003
}
```

**Response:**
```json
{
  "success": true,
  "message": "API key added successfully"
}
```

### **Test API Key**
```http
POST /api/ai/keys/openai/test
```

**Response:**
```json
{
  "success": true,
  "model": "gpt-4",
  "tokens_used": 10,
  "response_time": 1.2
}
```

### **Update API Key**
```http
PATCH /api/ai/keys/openai
Content-Type: application/json

{
  "isActive": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "API key updated successfully"
}
```

### **Remove API Key**
```http
DELETE /api/ai/keys/openai
```

**Response:**
```json
{
  "success": true,
  "message": "API key removed successfully"
}
```

### **Get Usage Statistics**
```http
GET /api/ai/usage-stats
```

**Response:**
```json
{
  "total_requests": 150,
  "successful_requests": 145,
  "total_tokens": 15000,
  "total_cost": 0.45,
  "average_response_time": 1.2,
  "success_rate": 96.7
}
```

### **Get Available Providers**
```http
GET /api/ai/providers
```

**Response:**
```json
{
  "success": true,
  "providers": ["openai", "anthropic", "local"],
  "default_provider": "openai"
}
```

## 🏢 **Enterprise API**

### **Configure Enterprise AI**
```http
POST /api/enterprise/ai/configure
Content-Type: application/json

{
  "local_ai_url": "http://localhost:11434",
  "local_ai_model": "llama2",
  "local_api_key": "optional-api-key",
  "proxy_url": "http://proxy.company.com:8080",
  "cert_path": "/path/to/cert.pem",
  "verify_ssl": true,
  "audit_enabled": true,
  "data_encryption": true,
  "session_timeout": 3600,
  "data_retention_days": 365,
  "log_retention_days": 90,
  "compliance_mode": "standard",
  "offline_mode": false,
  "custom_models": true,
  "external_integrations": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Enterprise AI configured successfully"
}
```

### **Test Enterprise AI Connection**
```http
GET /api/enterprise/ai/test-connection
```

**Response:**
```json
{
  "success": true,
  "connection_status": "connected",
  "ai_provider": "local",
  "model": "llama2",
  "response_time": 0.5,
  "note": "Connected to local Ollama instance"
}
```

### **Generate Enterprise Test Cases**
```http
POST /api/enterprise/ai/generate-test-cases
Content-Type: application/json

{
  "title": "Enterprise User Management",
  "description": "As an enterprise admin, I need to manage user accounts",
  "acceptance_criteria": [
    "Admin can create user accounts",
    "Admin can modify user permissions",
    "Admin can deactivate user accounts"
  ],
  "business_value": "Enterprise user management",
  "user_persona": "Enterprise administrator"
}
```

**Response:**
```json
{
  "success": true,
  "test_cases": [
    {
      "title": "Create Enterprise User Account",
      "description": "Test admin creating new user account",
      "steps": [
        "1. Login as enterprise admin",
        "2. Navigate to user management",
        "3. Click create new user",
        "4. Fill in user details",
        "5. Set user permissions",
        "6. Save user account"
      ],
      "expected_result": "User account created successfully with proper permissions",
      "test_type": "functional",
      "priority": "high",
      "tags": ["enterprise", "admin", "user-management"],
      "preconditions": ["Admin logged in", "User management access"],
      "test_data": "Valid user information",
      "acceptance_criteria": ["User account created", "Permissions set correctly"]
    }
  ],
  "count": 1,
  "provider": "enterprise_local",
  "note": "Generated using enterprise local AI"
}
```

### **Get Enterprise Health**
```http
GET /api/enterprise/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "ai_provider": "healthy",
    "monitoring": "healthy"
  },
  "metrics": {
    "response_time": 0.05,
    "memory_usage": "256MB",
    "cpu_usage": "15%",
    "disk_usage": "2.1GB"
  },
  "enterprise_features": {
    "audit_logging": true,
    "data_encryption": true,
    "compliance_mode": "standard",
    "offline_mode": false
  }
}
```

### **Get Audit Logs**
```http
GET /api/enterprise/audit/logs?start_date=2024-01-01&end_date=2024-01-31&level=INFO
```

**Response:**
```json
{
  "success": true,
  "logs": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "level": "INFO",
      "user": "admin@company.com",
      "action": "ai_test_generation",
      "details": "Generated 5 test cases for user authentication",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "total_count": 150,
  "filtered_count": 25
}
```

### **Generate Compliance Report**
```http
POST /api/enterprise/compliance/report
Content-Type: application/json

{
  "report_type": "security_audit",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "include_details": true
}
```

**Response:**
```json
{
  "success": true,
  "report": {
    "report_type": "security_audit",
    "generated_at": "2024-01-31T23:59:59",
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "summary": {
      "total_activities": 1500,
      "security_events": 5,
      "compliance_score": 98.5
    },
    "findings": [
      {
        "severity": "low",
        "description": "Minor security configuration issue",
        "recommendation": "Update security settings",
        "status": "open"
      }
    ],
    "recommendations": [
      "Enable additional audit logging",
      "Review access control policies",
      "Update security configurations"
    ]
  }
}
```

## 🔗 **Jira Integration API**

### **Get Jira Projects**
```http
GET /api/jira/projects
```

**Response:**
```json
{
  "success": true,
  "projects": [
    {
      "id": "10001",
      "key": "TEST",
      "name": "Test Management",
      "projectTypeKey": "software",
      "lead": {
        "accountId": "user123",
        "displayName": "John Doe"
      }
    }
  ]
}
```

### **Sync with Jira**
```http
POST /api/jira/sync
Content-Type: application/json

{
  "project_key": "TEST",
  "sync_type": "test_cases",
  "direction": "bidirectional"
}
```

**Response:**
```json
{
  "success": true,
  "sync_result": {
    "test_cases_synced": 25,
    "issues_created": 5,
    "issues_updated": 20,
    "sync_duration": 2.5
  }
}
```

### **Get Jira Issues**
```http
GET /api/jira/issues?project=TEST&status=Open
```

**Response:**
```json
{
  "success": true,
  "issues": [
    {
      "id": "10001",
      "key": "TEST-123",
      "summary": "Test case for user login",
      "status": "Open",
      "assignee": "john.doe@company.com",
      "created": "2024-01-01T10:00:00",
      "updated": "2024-01-01T12:00:00"
    }
  ],
  "total_count": 1
}
```

## 📊 **Monitoring API**

### **Get System Metrics**
```http
GET /api/monitoring/metrics
```

**Response:**
```json
{
  "success": true,
  "metrics": {
    "system": {
      "cpu_usage": 15.5,
      "memory_usage": 256,
      "disk_usage": 2.1,
      "uptime": 86400
    },
    "application": {
      "response_time": 0.05,
      "throughput": 100,
      "error_rate": 0.01,
      "active_sessions": 25
    },
    "database": {
      "connection_pool": 10,
      "query_time": 0.02,
      "cache_hit_rate": 0.95
    }
  }
}
```

### **Get Health Status**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "ai_provider": "healthy"
  }
}
```

## 🚨 **Error Handling**

### **Error Response Format**
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "api_key",
    "message": "API key is required"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### **Common Error Codes**
- `VALIDATION_ERROR` - Request validation failed
- `AUTHENTICATION_ERROR` - Authentication failed
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `AI_PROVIDER_ERROR` - AI provider connection failed
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Internal server error

## 📝 **Rate Limiting**

### **Rate Limits**
- **AI Generation**: 10 requests/minute per user
- **API Key Management**: 5 requests/minute per user
- **Enterprise Operations**: 20 requests/minute per user
- **General API**: 100 requests/minute per user

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1640995200
```

## 🔧 **SDK Examples**

### **Python SDK**
```python
import requests

# Initialize client
base_url = "https://your-assertly-instance.com"
headers = {"Authorization": "Bearer your-api-key"}

# Generate test cases
response = requests.post(
    f"{base_url}/api/ai/generate-test-cases",
    headers=headers,
    json={
        "title": "User Login",
        "description": "Test user login functionality",
        "acceptance_criteria": ["User can login", "User cannot login with invalid credentials"]
    }
)

test_cases = response.json()["test_cases"]
```

### **JavaScript SDK**
```javascript
// Initialize client
const assertly = new AssertlyClient({
  baseUrl: 'https://your-assertly-instance.com',
  apiKey: 'your-api-key'
});

// Generate test cases
const testCases = await assertly.ai.generateTestCases({
  title: 'User Login',
  description: 'Test user login functionality',
  acceptance_criteria: ['User can login', 'User cannot login with invalid credentials']
});
```

## 📚 **Additional Resources**

- **[README.md](../README.md)** - Main documentation
- **[DEPLOYMENT_GUIDE_LATEST.md](../DEPLOYMENT_GUIDE_LATEST.md)** - Deployment guide
- **[docs/user-guides/enterprise-user-guide.md](user-guides/enterprise-user-guide.md)** - User manual

---

**Made with ❤️ by the Assertly Team**