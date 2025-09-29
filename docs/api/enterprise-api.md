# 🏢 Assertly Enterprise API Documentation

## Overview

The Assertly Enterprise API provides comprehensive test management capabilities for enterprise environments with complete data privacy and security compliance.

## Base URL

```
https://your-assertly-instance.com/api/enterprise
```

## Authentication

All API requests require authentication using session-based authentication or API keys.

### Headers

```http
Content-Type: application/json
Authorization: Bearer <your-api-key>
```

## Enterprise AI Configuration

### Configure Enterprise AI

Configure the local AI service for enterprise use.

**Endpoint:** `POST /api/enterprise/ai/configure`

**Request Body:**
```json
{
  "local_ai_url": "http://internal-ai.company.com:8080/api",
  "local_ai_model": "local-copilot",
  "local_api_key": "your-internal-api-key",
  "proxy_url": "http://proxy.company.com:8080",
  "cert_path": "/path/to/company-cert.pem",
  "verify_ssl": true,
  "audit_enabled": true,
  "data_encryption": true,
  "session_timeout": 3600,
  "data_retention_days": 365,
  "log_retention_days": 90,
  "compliance_mode": "standard",
  "offline_mode": false,
  "custom_models": false,
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

### Test Enterprise AI Connection

Test the connection to the local AI service.

**Endpoint:** `GET /api/enterprise/ai/test-connection`

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "url": "http://internal-ai.company.com:8080/api",
  "model": "local-copilot"
}
```

### Generate Test Cases with Enterprise AI

Generate test cases using the enterprise/local AI service.

**Endpoint:** `POST /api/enterprise/ai/generate-test-cases`

**Request Body:**
```json
{
  "title": "User Login Test",
  "description": "As a user, I want to log in so that I can access my account",
  "acceptance_criteria": [
    "User can enter credentials",
    "User is logged in successfully"
  ],
  "business_value": "Enables secure access to user accounts",
  "user_persona": "Registered user",
  "epic": "Authentication",
  "story_points": 5,
  "test_types": ["functional", "ui", "api"],
  "num_cases": 5,
  "additional_prompts": [
    "Include edge cases for invalid credentials",
    "Test session timeout scenarios"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "test_cases": [
    {
      "title": "Valid User Login",
      "description": "Test successful login with valid credentials",
      "steps": [
        "Navigate to login page",
        "Enter valid username",
        "Enter valid password",
        "Click login button"
      ],
      "expected_result": "User is logged in successfully",
      "test_type": "functional",
      "priority": "high",
      "tags": ["authentication", "login", "positive"],
      "preconditions": ["User account exists", "User is not already logged in"],
      "test_data": {
        "username": "testuser@company.com",
        "password": "SecurePassword123"
      },
      "acceptance_criteria": ["User is redirected to dashboard", "Welcome message is displayed"]
    }
  ],
  "count": 5,
  "provider": "enterprise_local"
}
```

## Audit and Compliance

### Get Audit Logs

Retrieve audit logs with optional filtering.

**Endpoint:** `GET /api/enterprise/audit/logs`

**Query Parameters:**
- `start_date` (optional): Start date in ISO format
- `end_date` (optional): End date in ISO format
- `user` (optional): Filter by user
- `action` (optional): Filter by action

**Example:**
```
GET /api/enterprise/audit/logs?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59&user=admin
```

**Response:**
```json
{
  "success": true,
  "logs": [
    {
      "log_id": "evt_20240115_143022_abc12345",
      "timestamp": "2024-01-15T14:30:22.123456",
      "user": "admin",
      "action": "configure_enterprise_ai",
      "resource": "enterprise_settings",
      "details": {
        "local_ai_url": "http://internal-ai.company.com:8080/api"
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
  ],
  "count": 1
}
```

### Generate Compliance Report

Generate compliance reports for audit and regulatory purposes.

**Endpoint:** `POST /api/enterprise/compliance/report`

**Request Body:**
```json
{
  "report_type": "audit_summary",
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-12-31T23:59:59"
}
```

**Response:**
```json
{
  "success": true,
  "report_id": "rpt_20240115_143022_xyz789",
  "report_type": "audit_summary"
}
```

## System Health

### Get Enterprise Health

Get comprehensive system health information.

**Endpoint:** `GET /api/enterprise/health`

**Response:**
```json
{
  "status": "healthy",
  "enterprise_mode": true,
  "settings_configured": true,
  "last_updated": "2024-01-15T14:30:22.123456",
  "security_policies": {
    "audit_enabled": true,
    "data_encryption": true,
    "session_timeout": 3600,
    "compliance_mode": "standard"
  },
  "recent_activity": 15,
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "ai_service": "healthy",
    "monitoring": "healthy"
  },
  "metrics": {
    "uptime_seconds": 86400,
    "total_requests": 1250,
    "error_rate": 0.02,
    "average_response_time": 150
  }
}
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": "Error message describing what went wrong",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_CONFIGURATION` | Invalid enterprise configuration |
| `AI_SERVICE_UNAVAILABLE` | Local AI service is not available |
| `AUTHENTICATION_FAILED` | Authentication failed |
| `PERMISSION_DENIED` | Insufficient permissions |
| `VALIDATION_ERROR` | Request validation failed |
| `INTERNAL_ERROR` | Internal server error |

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **General API**: 100 requests per minute per IP
- **AI Generation**: 10 requests per minute per user
- **Audit Logs**: 50 requests per minute per user

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642252800
```

## Security Features

### Data Encryption

All sensitive data is encrypted at rest and in transit:

- **At Rest**: AES-256 encryption for stored data
- **In Transit**: TLS 1.2+ for all communications
- **API Keys**: Hashed and salted storage

### Audit Logging

All API activities are logged for compliance:

- **Authentication Events**: Login/logout activities
- **Configuration Changes**: Enterprise settings modifications
- **Data Access**: Who accessed what data when
- **Security Events**: Failed authentication attempts, suspicious activities

### Access Control

Role-based access control for enterprise features:

- **Admin**: Full access to all enterprise features
- **Manager**: Access to reports and configuration
- **User**: Limited access to AI generation
- **Auditor**: Read-only access to audit logs

## Examples

### Complete Enterprise Setup

```bash
# 1. Configure enterprise AI
curl -X POST https://your-assertly-instance.com/api/enterprise/ai/configure \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "local_ai_url": "http://internal-ai.company.com:8080/api",
    "local_ai_model": "local-copilot",
    "local_api_key": "your-internal-api-key"
  }'

# 2. Test connection
curl -X GET https://your-assertly-instance.com/api/enterprise/ai/test-connection \
  -H "Authorization: Bearer your-api-key"

# 3. Generate test cases
curl -X POST https://your-assertly-instance.com/api/enterprise/ai/generate-test-cases \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "title": "User Login Test",
    "description": "As a user, I want to log in so that I can access my account",
    "acceptance_criteria": ["User can enter credentials", "User is logged in successfully"],
    "business_value": "Enables secure access to user accounts",
    "user_persona": "Registered user",
    "test_types": ["functional", "ui"],
    "num_cases": 5
  }'
```

### Audit and Compliance

```bash
# Get audit logs for the last 30 days
curl -X GET "https://your-assertly-instance.com/api/enterprise/audit/logs?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59" \
  -H "Authorization: Bearer your-api-key"

# Generate compliance report
curl -X POST https://your-assertly-instance.com/api/enterprise/compliance/report \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "report_type": "audit_summary",
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-12-31T23:59:59"
  }'
```

## SDK Examples

### Python SDK

```python
import requests

class AssertlyEnterprise:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def configure_ai(self, local_ai_url, local_ai_model, **kwargs):
        data = {
            "local_ai_url": local_ai_url,
            "local_ai_model": local_ai_model,
            **kwargs
        }
        response = requests.post(
            f"{self.base_url}/api/enterprise/ai/configure",
            json=data,
            headers=self.headers
        )
        return response.json()
    
    def generate_test_cases(self, user_story):
        response = requests.post(
            f"{self.base_url}/api/enterprise/ai/generate-test-cases",
            json=user_story,
            headers=self.headers
        )
        return response.json()
    
    def get_audit_logs(self, **filters):
        params = {k: v for k, v in filters.items() if v is not None}
        response = requests.get(
            f"{self.base_url}/api/enterprise/audit/logs",
            params=params,
            headers=self.headers
        )
        return response.json()

# Usage
client = AssertlyEnterprise("https://your-assertly-instance.com", "your-api-key")

# Configure AI
result = client.configure_ai(
    local_ai_url="http://internal-ai.company.com:8080/api",
    local_ai_model="local-copilot"
)

# Generate test cases
test_cases = client.generate_test_cases({
    "title": "User Login Test",
    "description": "As a user, I want to log in so that I can access my account",
    "acceptance_criteria": ["User can enter credentials", "User is logged in successfully"],
    "business_value": "Enables secure access to user accounts",
    "user_persona": "Registered user",
    "test_types": ["functional", "ui"],
    "num_cases": 5
})
```

### JavaScript SDK

```javascript
class AssertlyEnterprise {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        };
    }
    
    async configureAI(localAiUrl, localAiModel, options = {}) {
        const data = {
            local_ai_url: localAiUrl,
            local_ai_model: localAiModel,
            ...options
        };
        
        const response = await fetch(`${this.baseUrl}/api/enterprise/ai/configure`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    async generateTestCases(userStory) {
        const response = await fetch(`${this.baseUrl}/api/enterprise/ai/generate-test-cases`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(userStory)
        });
        
        return await response.json();
    }
    
    async getAuditLogs(filters = {}) {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                params.append(key, value);
            }
        });
        
        const response = await fetch(`${this.baseUrl}/api/enterprise/audit/logs?${params}`, {
            headers: this.headers
        });
        
        return await response.json();
    }
}

// Usage
const client = new AssertlyEnterprise('https://your-assertly-instance.com', 'your-api-key');

// Configure AI
const result = await client.configureAI(
    'http://internal-ai.company.com:8080/api',
    'local-copilot'
);

// Generate test cases
const testCases = await client.generateTestCases({
    title: 'User Login Test',
    description: 'As a user, I want to log in so that I can access my account',
    acceptance_criteria: ['User can enter credentials', 'User is logged in successfully'],
    business_value: 'Enables secure access to user accounts',
    user_persona: 'Registered user',
    test_types: ['functional', 'ui'],
    num_cases: 5
});
```

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release of Enterprise API
- Enterprise AI configuration and testing
- Audit logging and compliance reporting
- System health monitoring
- Security and access control features

---

**Last Updated**: 2024-01-15  
**API Version**: 1.0.0  
**Contact**: enterprise-support@assertly.com