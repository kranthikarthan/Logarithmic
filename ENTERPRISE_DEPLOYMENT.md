# 🏢 Assertly Enterprise Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying Assertly Enterprise in on-premise environments with complete data privacy and security compliance.

## 🚀 Quick Start

### Prerequisites

- **Operating System**: Ubuntu 20.04+, CentOS 8+, or RHEL 8+
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: Minimum 10GB free disk space
- **Docker**: Version 20.10+ with Docker Compose
- **Network**: Internal network access (no external internet required)

### One-Command Installation

```bash
# Download and run the enterprise installer
curl -fsSL https://install.assertly.com/enterprise | sudo bash
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/assertly/assertly-enterprise.git
cd assertly-enterprise

# Run the installation script
sudo ./install-enterprise.sh
```

## 📋 Installation Process

### 1. System Requirements Check

The installer automatically checks:
- ✅ Operating system compatibility
- ✅ Docker and Docker Compose availability
- ✅ Memory and disk space requirements
- ✅ Network connectivity

### 2. User and Directory Creation

Creates:
- System user: `assertly`
- Installation directory: `/opt/assertly-enterprise`
- Configuration directory: `/etc/assertly`
- Data directory: `/var/lib/assertly`
- Log directory: `/var/log/assertly`

### 3. Docker Images Installation

Downloads and builds:
- ✅ Assertly Enterprise application
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Nginx reverse proxy
- ✅ Prometheus monitoring
- ✅ Grafana dashboard

### 4. Configuration Generation

Creates:
- ✅ Environment configuration (`.env`)
- ✅ Nginx configuration
- ✅ Prometheus configuration
- ✅ SSL certificates (self-signed)
- ✅ Security policies

### 5. Service Startup

Starts all services using Docker Compose with health checks.

## 🔧 Configuration

### Environment Variables

Key configuration options in `/etc/assertly/.env`:

```bash
# Security
SECRET_KEY=your-secret-key
POSTGRES_PASSWORD=your-db-password
REDIS_PASSWORD=your-redis-password

# Enterprise AI Configuration
LOCAL_AI_URL=http://local-ai-service:8080/api
ENTERPRISE_MODEL=local-copilot
LOCAL_AI_API_KEY=your-ai-api-key

# Network Configuration
PROXY_URL=http://proxy.company.com:8080
CERT_PATH=/path/to/company-cert.pem
VERIFY_SSL=true

# Security Settings
AUDIT_ENABLED=true
DATA_ENCRYPTION=true
SESSION_TIMEOUT=3600

# Compliance Settings
DATA_RETENTION_DAYS=365
LOG_RETENTION_DAYS=90
COMPLIANCE_MODE=standard
```

### Local AI Service Configuration

1. **Configure your local AI service URL**:
   ```bash
   # Edit the configuration
   sudo nano /etc/assertly/.env
   
   # Update the LOCAL_AI_URL
   LOCAL_AI_URL=http://your-ai-service.company.com:8080/api
   ```

2. **Test the connection**:
   ```bash
   curl http://localhost:5000/api/enterprise/ai/test-connection
   ```

### SSL Certificate Configuration

For production environments, replace the self-signed certificates:

```bash
# Copy your certificates
sudo cp your-cert.pem /opt/assertly-enterprise/enterprise-certs/cert.pem
sudo cp your-key.pem /opt/assertly-enterprise/enterprise-certs/key.pem

# Set proper permissions
sudo chown assertly:assertly /opt/assertly-enterprise/enterprise-certs/*
sudo chmod 600 /opt/assertly-enterprise/enterprise-certs/key.pem
sudo chmod 644 /opt/assertly-enterprise/enterprise-certs/cert.pem

# Restart services
sudo systemctl restart assertly-enterprise
```

## 🌐 Access URLs

After installation, access the following services:

- **Main Application**: https://localhost
- **Enterprise Settings**: https://localhost/enterprise-settings
- **API Documentation**: https://localhost/api/docs
- **Monitoring Dashboard**: http://localhost:3000 (Grafana)
- **Metrics**: http://localhost:9090 (Prometheus)

### Default Credentials

- **Grafana**: admin / `<generated-password>`
  - Password is generated during installation and shown in the summary

## 🔒 Security Features

### Data Privacy
- ✅ **Complete On-Premise**: All data stays within your network
- ✅ **No External Calls**: No internet access required
- ✅ **Local AI Processing**: All AI operations use your internal AI service
- ✅ **Encrypted Storage**: All sensitive data is encrypted at rest

### Audit and Compliance
- ✅ **Comprehensive Logging**: All activities are logged for compliance
- ✅ **Security Events**: Real-time security monitoring
- ✅ **Access Control**: Role-based access control
- ✅ **Data Retention**: Configurable data retention policies

### Network Security
- ✅ **Internal Network Only**: No external internet access
- ✅ **SSL/TLS Encryption**: All communications encrypted
- ✅ **Security Headers**: Comprehensive security headers
- ✅ **Rate Limiting**: Protection against abuse

## 📊 Monitoring and Alerting

### Grafana Dashboards

Access the monitoring dashboard at http://localhost:3000:

- **Application Health**: Service status and performance
- **Enterprise AI**: AI service metrics and latency
- **Security Events**: Security monitoring and alerts
- **System Resources**: CPU, memory, and disk usage
- **Database Performance**: PostgreSQL metrics
- **Cache Performance**: Redis metrics

### Prometheus Metrics

Available metrics at http://localhost:9090:

- `assertly_requests_total`: Total HTTP requests
- `assertly_request_duration_seconds`: Request latency
- `enterprise_ai_requests_total`: AI service requests
- `security_events_total`: Security events
- `database_connections`: Database connections
- `cache_hits`: Cache hit rate

### Alerting Rules

Pre-configured alerts for:
- Service downtime
- High error rates
- Security violations
- Resource usage
- Performance degradation

## 🛠️ Management Commands

### Service Management

```bash
# Start services
sudo systemctl start assertly-enterprise

# Stop services
sudo systemctl stop assertly-enterprise

# Restart services
sudo systemctl restart assertly-enterprise

# Check status
sudo systemctl status assertly-enterprise

# View logs
sudo journalctl -u assertly-enterprise -f
```

### Docker Management

```bash
# View running containers
docker ps

# View logs
docker-compose -f /opt/assertly-enterprise/docker-compose.enterprise.yml logs

# Restart specific service
docker-compose -f /opt/assertly-enterprise/docker-compose.enterprise.yml restart assertly-enterprise
```

### Database Management

```bash
# Connect to database
docker exec -it assertly-postgres psql -U assertly -d assertly_enterprise

# Backup database
docker exec assertly-postgres pg_dump -U assertly assertly_enterprise > backup.sql

# Restore database
docker exec -i assertly-postgres psql -U assertly assertly_enterprise < backup.sql
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Service Not Starting

```bash
# Check service status
sudo systemctl status assertly-enterprise

# Check logs
sudo journalctl -u assertly-enterprise -f

# Check Docker logs
docker-compose -f /opt/assertly-enterprise/docker-compose.enterprise.yml logs
```

#### 2. Database Connection Issues

```bash
# Check database status
docker exec assertly-postgres pg_isready -U assertly

# Check database logs
docker logs assertly-postgres
```

#### 3. AI Service Connection Issues

```bash
# Test AI service connection
curl http://localhost:5000/api/enterprise/ai/test-connection

# Check AI service logs
docker logs assertly-local-ai
```

#### 4. SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in /opt/assertly-enterprise/enterprise-certs/cert.pem -text -noout

# Regenerate self-signed certificates
sudo /opt/assertly-enterprise/scripts/generate-ssl-certs.sh
```

### Log Locations

- **Application Logs**: `/var/log/assertly/`
- **Nginx Logs**: `/var/log/nginx/`
- **Docker Logs**: `docker logs <container-name>`
- **System Logs**: `sudo journalctl -u assertly-enterprise`

### Performance Optimization

#### 1. Resource Allocation

```bash
# Edit Docker Compose file
sudo nano /opt/assertly-enterprise/docker-compose.enterprise.yml

# Add resource limits
services:
  assertly-enterprise:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

#### 2. Database Optimization

```bash
# Connect to database
docker exec -it assertly-postgres psql -U assertly -d assertly_enterprise

# Check database size
SELECT pg_size_pretty(pg_database_size('assertly_enterprise'));

# Optimize database
VACUUM ANALYZE;
```

## 📈 Scaling and High Availability

### Horizontal Scaling

To scale the application:

```bash
# Edit Docker Compose file
sudo nano /opt/assertly-enterprise/docker-compose.enterprise.yml

# Add multiple instances
services:
  assertly-enterprise:
    deploy:
      replicas: 3
```

### Load Balancing

Configure Nginx for load balancing:

```nginx
upstream assertly_backend {
    server assertly-enterprise-1:5000;
    server assertly-enterprise-2:5000;
    server assertly-enterprise-3:5000;
}
```

### Database Clustering

For high availability, configure PostgreSQL clustering:

```bash
# Configure primary-replica setup
# See PostgreSQL documentation for clustering setup
```

## 🔄 Backup and Recovery

### Automated Backups

```bash
# Create backup script
sudo nano /opt/assertly-enterprise/scripts/backup.sh

#!/bin/bash
BACKUP_DIR="/opt/assertly-enterprise/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker exec assertly-postgres pg_dump -U assertly assertly_enterprise > "$BACKUP_DIR/db_$DATE.sql"

# Configuration backup
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" /etc/assertly/

# Data backup
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" /var/lib/assertly/
```

### Recovery Process

```bash
# Stop services
sudo systemctl stop assertly-enterprise

# Restore database
docker exec -i assertly-postgres psql -U assertly assertly_enterprise < backup.sql

# Restore configuration
tar -xzf config_backup.tar.gz -C /

# Start services
sudo systemctl start assertly-enterprise
```

## 📞 Support

### Enterprise Support

For enterprise support and custom configurations:

- **Email**: enterprise-support@assertly.com
- **Documentation**: https://docs.assertly.com/enterprise
- **Community**: https://community.assertly.com

### Professional Services

Available services:
- Custom deployment assistance
- Security audit and hardening
- Performance optimization
- Training and workshops
- 24/7 support contracts

## 📄 License

Assertly Enterprise is licensed under the MIT License. See LICENSE file for details.

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0