# 📚 Assertly Enterprise Documentation

Welcome to the comprehensive documentation for Assertly Enterprise - the complete test management solution for enterprise environments with full data privacy and security compliance.

## 🚀 Quick Start

### For Administrators
- [Enterprise Deployment Guide](deployment/ENTERPRISE_DEPLOYMENT.md) - Complete deployment instructions
- [Installation Script](deployment/install-enterprise.sh) - One-command installation
- [Docker Configuration](deployment/docker-compose.enterprise.yml) - Enterprise Docker setup

### For Users
- [Enterprise User Guide](user-guides/enterprise-user-guide.md) - Complete user manual
- [API Documentation](api/enterprise-api.md) - REST API reference
- [Video Tutorials](tutorials/) - Step-by-step video guides

### For Developers
- [Developer Guide](developer/README.md) - Development setup and guidelines
- [API SDKs](sdk/) - Python, JavaScript, and other language SDKs
- [Integration Examples](integrations/) - Code examples and integrations

## 📖 Documentation Structure

### 🏢 Enterprise Features
- **Data Privacy**: Complete on-premise solution with no external dependencies
- **Security**: Enterprise-grade security with audit logging and compliance
- **AI Integration**: Local AI service integration with offline capabilities
- **Monitoring**: Comprehensive monitoring with Prometheus and Grafana
- **Scalability**: Production-ready architecture with horizontal scaling

### 🎯 Core Capabilities
- **AI Test Generation**: Generate test cases from user stories using AI
- **BDD Scenarios**: Create Gherkin scenarios for behavior-driven development
- **Test Data Generation**: Generate test data sets for various scenarios
- **Coverage Analysis**: Analyze test coverage and identify gaps
- **Test Management**: Organize and manage test cases and test suites

### 🔧 Technical Features
- **REST API**: Complete REST API for all functionality
- **Real-time Updates**: WebSocket support for real-time collaboration
- **Export/Import**: Support for various formats (JSON, CSV, Excel, XML)
- **Integrations**: Jira, GitHub, GitLab, CI/CD pipeline integrations
- **Customization**: Configurable workflows and custom fields

## 📋 Getting Started

### 1. Installation

#### Quick Installation
```bash
# One-command installation
curl -fsSL https://install.assertly.com/enterprise | sudo bash
```

#### Manual Installation
```bash
# Clone repository
git clone https://github.com/assertly/assertly-enterprise.git
cd assertly-enterprise

# Run installation script
sudo ./install-enterprise.sh
```

### 2. Configuration

#### Enterprise Settings
1. Navigate to Enterprise Settings
2. Configure your local AI service
3. Set up security policies
4. Configure audit logging

#### Local AI Service
```bash
# Configure AI service URL
LOCAL_AI_URL=http://internal-ai.company.com:8080/api
ENTERPRISE_MODEL=local-copilot
LOCAL_AI_API_KEY=your-internal-api-key
```

### 3. First Steps

#### Create Your First Test Case
1. Navigate to AI Test Generator
2. Enter your user story
3. Generate test cases
4. Review and customize
5. Save to your test repository

#### Generate BDD Scenarios
1. Access BDD Generator
2. Input your feature description
3. Generate Gherkin scenarios
4. Export to your BDD framework

## 🎨 User Interface

### Dashboard
- **Overview**: Key metrics and recent activity
- **Quick Actions**: Generate tests, view reports, access settings
- **Navigation**: Easy access to all features

### AI Test Generator
- **User Story Input**: Detailed form for user story information
- **Generation Options**: Configure test types and parameters
- **Results Review**: Review and customize generated test cases

### Test Management
- **Test Cases**: Organize and manage test cases
- **Test Suites**: Group related test cases
- **Execution**: Track test execution and results

### Reports and Analytics
- **Test Reports**: Execution results and coverage
- **AI Reports**: AI usage and generation statistics
- **Enterprise Reports**: Compliance and audit reports

## 🔒 Security and Compliance

### Data Privacy
- **Complete On-Premise**: All data stays within your network
- **No External Calls**: No internet access required
- **Local AI Only**: Uses your internal AI services
- **Encrypted Storage**: All data encrypted at rest

### Security Features
- **Authentication**: Multi-factor authentication support
- **Authorization**: Role-based access control
- **Audit Logging**: Complete activity tracking
- **Security Monitoring**: Real-time security event monitoring

### Compliance
- **Audit Reports**: Automated compliance reporting
- **Data Retention**: Configurable data retention policies
- **Access Control**: Granular permissions management
- **Security Policies**: Configurable security policies

## 🌐 API Reference

### Base URL
```
https://your-assertly-instance.com/api
```

### Authentication
```http
Authorization: Bearer <your-api-key>
Content-Type: application/json
```

### Key Endpoints

#### AI Generation
- `POST /api/ai/generate-test-cases` - Generate test cases
- `POST /api/ai/improve-test-case` - Improve existing test case
- `POST /api/ai/generate-bdd-scenarios` - Generate BDD scenarios
- `POST /api/ai/generate-test-data` - Generate test data

#### Enterprise Features
- `POST /api/enterprise/ai/configure` - Configure enterprise AI
- `GET /api/enterprise/ai/test-connection` - Test AI connection
- `GET /api/enterprise/audit/logs` - Get audit logs
- `POST /api/enterprise/compliance/report` - Generate compliance report

### SDK Examples

#### Python
```python
from assertly import AssertlyClient

client = AssertlyClient("https://your-instance.com", "your-api-key")

# Generate test cases
test_cases = client.generate_test_cases({
    "title": "User Login Test",
    "description": "As a user, I want to log in to my account",
    "acceptance_criteria": ["User can enter credentials", "User is logged in successfully"],
    "business_value": "Enables secure access to user accounts",
    "user_persona": "Registered user"
})
```

#### JavaScript
```javascript
const assertly = new AssertlyClient('https://your-instance.com', 'your-api-key');

// Generate test cases
const testCases = await assertly.generateTestCases({
    title: 'User Login Test',
    description: 'As a user, I want to log in to my account',
    acceptance_criteria: ['User can enter credentials', 'User is logged in successfully'],
    business_value: 'Enables secure access to user accounts',
    user_persona: 'Registered user'
});
```

## 🛠️ Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/assertly/assertly-enterprise.git
cd assertly-enterprise

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### Running Tests
```bash
# Run all tests
python run-comprehensive-tests.py

# Run specific test categories
python -m pytest tests/test_enterprise_features.py
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📊 Monitoring and Observability

### Metrics
- **Application Metrics**: Request rates, response times, error rates
- **AI Metrics**: Generation requests, success rates, latency
- **Security Metrics**: Security events, failed authentications
- **System Metrics**: CPU, memory, disk usage

### Dashboards
- **Grafana**: Comprehensive monitoring dashboards
- **Prometheus**: Metrics collection and alerting
- **Custom Dashboards**: Configurable enterprise dashboards

### Alerting
- **Service Health**: Automatic alerts for service issues
- **Security Events**: Real-time security event alerts
- **Performance**: Performance degradation alerts
- **Compliance**: Compliance violation alerts

## 🔧 Troubleshooting

### Common Issues

#### Service Not Starting
```bash
# Check service status
sudo systemctl status assertly-enterprise

# Check logs
sudo journalctl -u assertly-enterprise -f

# Check Docker logs
docker-compose -f docker-compose.enterprise.yml logs
```

#### AI Service Connection Issues
```bash
# Test AI service connection
curl http://localhost:5000/api/enterprise/ai/test-connection

# Check AI service logs
docker logs assertly-local-ai
```

#### Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Check database performance
docker exec assertly-postgres psql -U assertly -d assertly_enterprise -c "SELECT * FROM pg_stat_activity;"
```

### Log Locations
- **Application Logs**: `/var/log/assertly/`
- **Nginx Logs**: `/var/log/nginx/`
- **Docker Logs**: `docker logs <container-name>`
- **System Logs**: `sudo journalctl -u assertly-enterprise`

## 📞 Support

### Enterprise Support
- **Email**: enterprise-support@assertly.com
- **Phone**: +1-800-ASSERTLY
- **Documentation**: https://docs.assertly.com/enterprise
- **Community**: https://community.assertly.com

### Professional Services
- **Implementation**: Custom deployment assistance
- **Training**: Comprehensive training programs
- **Consulting**: Strategic consulting services
- **Custom Development**: Custom features and integrations

### Resources
- **Knowledge Base**: Comprehensive documentation
- **Video Tutorials**: Step-by-step video guides
- **Webinars**: Regular training sessions
- **Community Forum**: User community support

## 📄 License

Assertly Enterprise is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🏷️ Version Information

- **Current Version**: 1.0.0
- **Last Updated**: 2024-01-15
- **Documentation Version**: 1.0.0

---

**Need Help?** Check out our [FAQ](faq.md) or contact [enterprise-support@assertly.com](mailto:enterprise-support@assertly.com)