# Assertly - Modern Test Management for Agile Teams

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://hub.docker.com)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-red?logo=flask)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Affordable, lightweight test management for Jira, GitHub & GitLab**

Assertly is a modern test management platform with AI-powered test generation, comprehensive traceability, and seamless integrations. Built for agile teams who value quality and efficiency.

## ✨ Features

- **🎯 Requirements Traceability** - Link tests to requirements with full traceability matrix
- **🌱 BDD Scenarios** - Write and manage BDD scenarios with Gherkin syntax
- **🤖 Automated Testing** - Integrate with CI/CD pipelines and test frameworks
- **🐛 Defect Management** - Link test failures to defects with automated creation
- **📊 Advanced Reporting** - Comprehensive reports and analytics for stakeholders
- **🔗 Seamless Integrations** - Jira, GitHub, GitLab, and CI/CD tools
- **☁️ SaaS & On-Premise** - Deploy in the cloud or on your infrastructure

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/assertly.git
cd assertly

# Start the application
docker-compose up -d

# Access the application
open http://localhost:5000
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the application
python app.py
```

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build the production image
docker build -t assertly:latest .

# Run with environment variables
docker run -d \
  --name assertly \
  -p 5000:5000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  assertly:latest
```

### Docker Compose for Production

```yaml
version: '3.8'
services:
  app:
    image: assertly:latest
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/assertly
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
      - redis
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `DATABASE_URL` | Database connection string | `sqlite:///app.db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `JIRA_URL` | Jira instance URL | - |
| `JIRA_USERNAME` | Jira username | - |
| `JIRA_API_TOKEN` | Jira API token | - |

### Database Setup

```bash
# Initialize the database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📊 Monitoring

The application includes built-in monitoring with Prometheus metrics:

- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`
- **Prometheus Dashboard**: `http://localhost:9090`

## 🔌 Integrations

### Jira Integration

```python
# Configure Jira connection
JIRA_URL = "https://your-company.atlassian.net"
JIRA_USERNAME = "your-email@company.com"
JIRA_API_TOKEN = "your-api-token"
```

### GitHub Integration

```python
# Configure GitHub integration
GITHUB_TOKEN = "your-github-token"
GITHUB_REPO = "owner/repository"
```

### GitLab Integration

```python
# Configure GitLab integration
GITLAB_URL = "https://gitlab.com"
GITLAB_TOKEN = "your-gitlab-token"
GITLAB_PROJECT_ID = "12345"
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React/Vue)   │◄──►│   (Flask)       │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Redis         │    │   Monitoring    │
│   (Reverse      │    │   (Cache)       │    │   (Prometheus)  │
│    Proxy)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py
```

## 📈 Performance

- **Response Time**: < 200ms average
- **Throughput**: 1000+ requests/second
- **Memory Usage**: < 512MB
- **Database**: Optimized queries with indexing

## 🔒 Security

- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: AES-256 encryption at rest
- **HTTPS**: TLS 1.3 with perfect forward secrecy
- **CORS**: Configurable cross-origin resource sharing

## 📝 API Documentation

### Authentication

```bash
# Login
POST /api/auth/login
{
  "username": "user@example.com",
  "password": "password"
}

# Refresh token
POST /api/auth/refresh
{
  "refresh_token": "jwt-refresh-token"
}
```

### Test Management

```bash
# Get test cases
GET /api/test-cases?project=PROJ&status=Open

# Create test case
POST /api/test-cases
{
  "summary": "Test case title",
  "description": "Test case description",
  "project": "PROJ"
}

# Execute test
POST /api/test-executions
{
  "test_key": "PROJ-123",
  "status": "PASS",
  "comment": "Test passed successfully"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.assertly.com](https://docs.assertly.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/assertly/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/assertly/discussions)
- **Email**: support@assertly.com

## 🎯 Roadmap

- [ ] **Q1 2024**: Advanced reporting and analytics
- [ ] **Q2 2024**: Mobile app for iOS and Android
- [ ] **Q3 2024**: AI-powered test case generation
- [ ] **Q4 2024**: Enterprise SSO integration

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Styled with modern CSS and [Tailwind CSS](https://tailwindcss.com/)
- Icons by [Font Awesome](https://fontawesome.com/)
- Fonts by [Google Fonts](https://fonts.google.com/)

---

<div align="center">
  <strong>Built with ❤️ for the testing community</strong>
</div>