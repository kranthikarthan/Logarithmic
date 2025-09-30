# Assertly Deployment Guide - Latest Version

## 🚀 **Complete Deployment Guide for Assertly**

This guide covers all deployment options for Assertly, from simple laptop deployment to enterprise production environments.

## 📋 **Prerequisites**

### **System Requirements**
- **Python**: 3.11+ (recommended 3.11 or 3.12)
- **Memory**: 2GB RAM minimum, 4GB+ recommended
- **Storage**: 1GB free space minimum
- **Network**: Internet access for AI providers (optional with local LLM)

### **Optional Dependencies**
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for multi-service deployment)
- **Redis**: 6.0+ (for caching and real-time features)
- **PostgreSQL**: 13+ (for production database)

## 🎯 **Deployment Options**

### **Option 1: Simple Python Deployment (Recommended for Development)**

**Best for**: Development, testing, laptop deployment

```bash
# 1. Clone the repository
git clone https://github.com/your-org/assertly.git
cd assertly

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (optional)
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY=your-secret-key-here

# 5. Run the application
python app.py

# 6. Access the application
open http://localhost:5000
```

**Features Available**:
- ✅ Core test management
- ✅ AI test generation (with local LLM or external APIs)
- ✅ Enterprise features (mock mode)
- ✅ Real-time features
- ✅ Basic monitoring

### **Option 2: Docker Monolithic Deployment**

**Best for**: Production deployment, easy scaling

```bash
# 1. Clone the repository
git clone https://github.com/your-org/assertly.git
cd assertly

# 2. Create environment file
cat > .env << EOF
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@db:5432/assertly
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token
EOF

# 3. Start services
docker-compose up -d

# 4. Access the application
open http://localhost:5000

# 5. Access monitoring
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
```

**Features Available**:
- ✅ All core features
- ✅ Full AI integration
- ✅ Enterprise features
- ✅ Real-time features
- ✅ Complete monitoring stack
- ✅ Production database

### **Option 3: Microservices Deployment (Enterprise)**

**Best for**: Large-scale production, enterprise environments

```bash
# 1. Clone the repository
git clone https://github.com/your-org/assertly.git
cd assertly

# 2. Create microservices environment
cat > .env.microservices << EOF
# API Gateway
GATEWAY_PORT=8000
GATEWAY_SECRET=your-gateway-secret

# User Service
USER_SERVICE_PORT=5001
USER_DB_URL=postgresql://user:pass@user-db:5432/users

# Test Service
TEST_SERVICE_PORT=5002
TEST_DB_URL=postgresql://user:pass@test-db:5432/tests

# AI Service
AI_SERVICE_PORT=5003
AI_OPENAI_KEY=sk-your-openai-key
AI_ANTHROPIC_KEY=your-anthropic-key

# Integration Service
INTEGRATION_SERVICE_PORT=5004
INTEGRATION_JIRA_URL=https://your-company.atlassian.net

# Notification Service
NOTIFICATION_SERVICE_PORT=5005
NOTIFICATION_REDIS_URL=redis://redis:6379/0
EOF

# 3. Start microservices stack
docker-compose -f docker-compose.microservices.yml up -d

# 4. Access API Gateway
open http://localhost:8000

# 5. Access individual services
# User Service: http://localhost:5001
# Test Service: http://localhost:5002
# AI Service: http://localhost:5003
# Integration Service: http://localhost:5004
# Notification Service: http://localhost:5005
```

**Features Available**:
- ✅ All features with microservices architecture
- ✅ Independent service scaling
- ✅ High availability
- ✅ Enterprise-grade performance
- ✅ Complete monitoring and observability

## 🔧 **Configuration Guide**

### **Environment Variables**

#### **Core Configuration**
```bash
# Application Settings
FLASK_APP=app.py
FLASK_ENV=production  # or development
SECRET_KEY=your-secret-key-here
DEBUG=False  # Set to True for development

# Database Configuration
DATABASE_URL=sqlite:///app.db  # Default SQLite
# DATABASE_URL=postgresql://user:pass@host:5432/db  # PostgreSQL

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0
```

#### **AI Provider Configuration**
```bash
# OpenAI (Optional)
OPENAI_API_KEY=sk-your-openai-key

# Anthropic (Optional)
ANTHROPIC_API_KEY=your-anthropic-key

# Google AI (Optional)
GOOGLE_AI_KEY=your-google-ai-key

# Azure OpenAI (Optional)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-azure-key

# Hugging Face (Optional)
HUGGINGFACE_API_KEY=hf_your-huggingface-key

# Local LLM (Recommended for Enterprise)
LOCAL_AI_URL=http://localhost:11434  # Ollama default
LOCAL_AI_MODEL=llama2  # or any Ollama model
```

#### **Jira Integration (Optional)**
```bash
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token
```

#### **Enterprise Configuration**
```bash
# Enterprise Settings
ENTERPRISE_MODE=True
AUDIT_LOGGING=True
DATA_ENCRYPTION=True
COMPLIANCE_MODE=standard  # or strict
OFFLINE_MODE=False  # Set to True for air-gapped environments
```

### **Database Configuration**

#### **SQLite (Default)**
```bash
# No additional configuration needed
# Database file: app.db (created automatically)
```

#### **PostgreSQL (Production)**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE assertly;
CREATE USER assertly_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE assertly TO assertly_user;
\q

# Set environment variable
export DATABASE_URL=postgresql://assertly_user:your_password@localhost:5432/assertly
```

### **Redis Configuration (Optional)**

#### **Local Redis**
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Set environment variable
export REDIS_URL=redis://localhost:6379/0
```

#### **Docker Redis**
```bash
# Start Redis container
docker run -d --name redis -p 6379:6379 redis:alpine

# Set environment variable
export REDIS_URL=redis://localhost:6379/0
```

## 🤖 **AI Provider Setup**

### **Option 1: External AI Providers**

#### **OpenAI Setup**
```bash
# Get API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY=sk-your-openai-key

# Test connection
curl -X POST http://localhost:5000/api/ai/generate-test-cases \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "description": "Test description"}'
```

#### **Anthropic Setup**
```bash
# Get API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY=your-anthropic-key

# Test connection
curl -X POST http://localhost:5000/api/ai/generate-test-cases \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "description": "Test description"}'
```

### **Option 2: Local LLM (Recommended for Enterprise)**

#### **Ollama Setup**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull a model (in another terminal)
ollama pull llama2
# or
ollama pull mistral
# or
ollama pull codellama

# Configure Assertly
export LOCAL_AI_URL=http://localhost:11434
export LOCAL_AI_MODEL=llama2

# Test connection
curl http://localhost:11434/api/tags
```

#### **Custom Local AI**
```bash
# Set custom local AI endpoint
export LOCAL_AI_URL=http://your-ai-server:8080/api
export LOCAL_AI_MODEL=your-model-name
```

## 🔌 **Integration Setup**

### **Jira Integration**
```bash
# Set Jira credentials
export JIRA_URL=https://your-company.atlassian.net
export JIRA_USERNAME=your-email@company.com
export JIRA_API_TOKEN=your-jira-api-token

# Test connection
curl http://localhost:5000/api/jira/projects
```

### **VS Code Extension**
```bash
# Install VS Code extension
code --install-extension assertly.vscode-extension

# Configure extension
# Open VS Code settings and add:
# "assertly.serverUrl": "http://localhost:5000"
# "assertly.apiKey": "your-api-key"
```

### **GitHub Actions Integration**
```yaml
# .github/workflows/assertly-test.yml
name: Assertly Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Assertly Tests
        uses: your-org/assertly-test-action@v1
        with:
          server-url: 'http://localhost:5000'
          api-key: ${{ secrets.ASSERTLY_API_KEY }}
```

## 📊 **Monitoring Setup**

### **Grafana Dashboard**
```bash
# Access Grafana
open http://localhost:3000

# Login credentials
Username: admin
Password: admin

# Import dashboards
# 1. Go to Dashboards > Import
# 2. Upload the dashboard JSON files from monitoring/grafana/dashboards/
```

### **Prometheus Metrics**
```bash
# Access Prometheus
open http://localhost:9090

# View metrics
# 1. Go to Status > Targets
# 2. Check that all targets are UP
# 3. Go to Graph and query metrics
```

### **Application Monitoring**
```bash
# Access application monitoring
open http://localhost:5000/monitoring

# View metrics
# - System metrics
# - Performance metrics
# - Cache statistics
# - Health status
```

## 🧪 **Testing Deployment**

### **Health Checks**
```bash
# Application health
curl http://localhost:5000/health

# Service discovery
curl http://localhost:5000/api/services

# Metrics endpoint
curl http://localhost:5000/metrics
```

### **Feature Testing**
```bash
# Test AI features
curl -X POST http://localhost:5000/api/ai/generate-test-cases \
  -H "Content-Type: application/json" \
  -d '{"title": "User Login", "description": "Test user login functionality"}'

# Test enterprise features
curl http://localhost:5000/api/enterprise/health

# Test integrations
curl http://localhost:5000/api/jira/projects
```

### **Comprehensive Testing**
```bash
# Run full test suite
python run_100_percent_tests.py

# Run specific test levels
python test_database_integration.py      # Level 1
python test_load_performance.py         # Level 2
python test_user_workflows.py           # Level 4
```

## 🚀 **Production Deployment**

### **Security Checklist**
- [ ] Change default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up backup procedures
- [ ] Enable audit logging
- [ ] Configure monitoring alerts

### **Performance Optimization**
- [ ] Configure Redis caching
- [ ] Optimize database queries
- [ ] Set up CDN for static assets
- [ ] Configure load balancing
- [ ] Enable compression

### **Monitoring Setup**
- [ ] Configure Prometheus alerts
- [ ] Set up Grafana dashboards
- [ ] Enable log aggregation
- [ ] Configure health checks
- [ ] Set up backup monitoring

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Application Won't Start**
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip install -r requirements.txt

# Check environment variables
echo $FLASK_APP
echo $SECRET_KEY
```

#### **Database Connection Issues**
```bash
# Check database URL
echo $DATABASE_URL

# Test database connection
python -c "import sqlite3; print('SQLite OK')"
# or
python -c "import psycopg2; print('PostgreSQL OK')"
```

#### **AI Provider Issues**
```bash
# Test OpenAI
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Test Anthropic
curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages

# Test Local LLM
curl http://localhost:11434/api/tags
```

#### **Redis Connection Issues**
```bash
# Check Redis
redis-cli ping  # Should return PONG

# Check Redis URL
echo $REDIS_URL
```

### **Log Analysis**
```bash
# Application logs
tail -f app.log

# Docker logs
docker-compose logs -f

# System logs
journalctl -u assertly -f
```

## 📞 **Support**

### **Documentation**
- **[README.md](README.md)** - Main documentation
- **[docs/README.md](docs/README.md)** - Enterprise documentation
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview

### **API Documentation**
- **[docs/api/enterprise-api.md](docs/api/enterprise-api.md)** - Complete API reference
- **[docs/user-guides/enterprise-user-guide.md](docs/user-guides/enterprise-user-guide.md)** - User manual

### **Community**
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Community support and questions
- **Wiki**: Additional documentation and guides

---

**Made with ❤️ by the Assertly Team**