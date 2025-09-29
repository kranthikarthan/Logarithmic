#!/bin/bash

# Assertly Enterprise Installation Script
# Version: 1.0.0
# License: MIT

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/assertly-enterprise"
CONFIG_DIR="/etc/assertly"
DATA_DIR="/var/lib/assertly"
LOG_DIR="/var/log/assertly"
SERVICE_USER="assertly"
SERVICE_GROUP="assertly"

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check OS
    if [[ ! -f /etc/os-release ]]; then
        print_error "Unsupported operating system"
        exit 1
    fi
    
    source /etc/os-release
    case $ID in
        ubuntu|debian)
            print_status "Detected Ubuntu/Debian system"
            ;;
        centos|rhel|fedora)
            print_status "Detected CentOS/RHEL/Fedora system"
            ;;
        *)
            print_warning "Unsupported OS: $ID"
            ;;
    esac
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check available memory
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $MEMORY_GB -lt 4 ]]; then
        print_warning "Recommended minimum 4GB RAM. Detected: ${MEMORY_GB}GB"
    fi
    
    # Check available disk space
    DISK_GB=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
    if [[ $DISK_GB -lt 10 ]]; then
        print_warning "Recommended minimum 10GB free disk space. Detected: ${DISK_GB}GB"
    fi
    
    print_success "System requirements check completed"
}

# Create system user and directories
create_user_and_directories() {
    print_status "Creating system user and directories..."
    
    # Create user and group
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
        print_status "Created user: $SERVICE_USER"
    else
        print_status "User $SERVICE_USER already exists"
    fi
    
    # Create directories
    mkdir -p "$INSTALL_DIR" "$CONFIG_DIR" "$DATA_DIR" "$LOG_DIR"
    mkdir -p "$INSTALL_DIR/enterprise-config" "$INSTALL_DIR/enterprise-certs" "$INSTALL_DIR/enterprise-data"
    mkdir -p "$INSTALL_DIR/enterprise-logs" "$INSTALL_DIR/ai-models" "$INSTALL_DIR/monitoring"
    
    # Set permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR"
    chmod 755 "$INSTALL_DIR" "$CONFIG_DIR" "$DATA_DIR" "$LOG_DIR"
    
    print_success "User and directories created"
}

# Install Docker images
install_docker_images() {
    print_status "Installing Docker images..."
    
    # Build enterprise image
    cd "$INSTALL_DIR"
    docker build -f Dockerfile.enterprise -t assertly-enterprise:latest .
    
    # Pull required images
    docker pull postgres:15-alpine
    docker pull redis:7-alpine
    docker pull nginx:alpine
    docker pull prom/prometheus:latest
    docker pull grafana/grafana:latest
    
    print_success "Docker images installed"
}

# Generate configuration files
generate_configuration() {
    print_status "Generating configuration files..."
    
    # Generate environment file
    cat > "$CONFIG_DIR/.env" << EOF
# Assertly Enterprise Configuration
# Generated on $(date)

# Security
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
GRAFANA_PASSWORD=$(openssl rand -hex 16)

# Enterprise AI Configuration
LOCAL_AI_URL=http://local-ai-service:8080/api
ENTERPRISE_MODEL=local-copilot
LOCAL_AI_API_KEY=$(openssl rand -hex 16)

# Network Configuration
PROXY_URL=
CERT_PATH=
VERIFY_SSL=true

# Security Configuration
AUDIT_ENABLED=true
DATA_ENCRYPTION=true
SESSION_TIMEOUT=3600

# Compliance Configuration
DATA_RETENTION_DAYS=365
LOG_RETENTION_DAYS=90
COMPLIANCE_MODE=standard

# Feature Flags
OFFLINE_MODE=false
CUSTOM_MODELS=false
EXTERNAL_INTEGRATIONS=false
EOF
    
    # Generate Nginx configuration
    cat > "$INSTALL_DIR/nginx/nginx.enterprise.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream assertly {
        server assertly-enterprise:5000;
    }
    
    upstream local-ai {
        server local-ai-service:8080;
    }
    
    server {
        listen 80;
        server_name _;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name _;
        
        # SSL Configuration
        ssl_certificate /etc/nginx/certs/cert.pem;
        ssl_certificate_key /etc/nginx/certs/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # Main application
        location / {
            proxy_pass http://assertly;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Local AI service
        location /ai/ {
            proxy_pass http://local-ai/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
    
    # Generate Prometheus configuration
    cat > "$INSTALL_DIR/monitoring/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'assertly-enterprise'
    static_configs:
      - targets: ['assertly-enterprise:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
    
    print_success "Configuration files generated"
}

# Generate SSL certificates
generate_ssl_certificates() {
    print_status "Generating SSL certificates..."
    
    cd "$INSTALL_DIR/enterprise-certs"
    
    # Generate self-signed certificate for development
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
        -subj "/C=US/ST=Enterprise/L=Internal/O=Assertly/OU=IT/CN=assertly-enterprise.local"
    
    # Set permissions
    chmod 600 key.pem
    chmod 644 cert.pem
    chown "$SERVICE_USER:$SERVICE_GROUP" *.pem
    
    print_success "SSL certificates generated"
}

# Create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/assertly-enterprise.service << EOF
[Unit]
Description=Assertly Enterprise Test Management
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/docker-compose -f docker-compose.enterprise.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.enterprise.yml down
TimeoutStartSec=0
User=$SERVICE_USER
Group=$SERVICE_GROUP

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable assertly-enterprise.service
    
    print_success "Systemd service created"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    cd "$INSTALL_DIR"
    
    # Start with Docker Compose
    docker-compose -f docker-compose.enterprise.yml up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check service health
    if curl -f http://localhost:5000/api/enterprise/health > /dev/null 2>&1; then
        print_success "Assertly Enterprise is running"
    else
        print_error "Failed to start Assertly Enterprise"
        exit 1
    fi
    
    print_success "Services started successfully"
}

# Display installation summary
display_summary() {
    print_success "Assertly Enterprise installation completed!"
    
    echo
    echo "=========================================="
    echo "Installation Summary"
    echo "=========================================="
    echo "Installation Directory: $INSTALL_DIR"
    echo "Configuration Directory: $CONFIG_DIR"
    echo "Data Directory: $DATA_DIR"
    echo "Log Directory: $LOG_DIR"
    echo
    echo "Service Management:"
    echo "  Start:   systemctl start assertly-enterprise"
    echo "  Stop:    systemctl stop assertly-enterprise"
    echo "  Status:  systemctl status assertly-enterprise"
    echo "  Logs:    journalctl -u assertly-enterprise -f"
    echo
    echo "Access URLs:"
    echo "  Application: https://localhost"
    echo "  Enterprise Settings: https://localhost/enterprise-settings"
    echo "  Monitoring: http://localhost:3000 (Grafana)"
    echo "  Metrics: http://localhost:9090 (Prometheus)"
    echo
    echo "Default Credentials:"
    echo "  Grafana: admin / $(grep GRAFANA_PASSWORD $CONFIG_DIR/.env | cut -d'=' -f2)"
    echo
    echo "Next Steps:"
    echo "1. Configure your local AI service"
    echo "2. Set up enterprise certificates"
    echo "3. Configure proxy settings if needed"
    echo "4. Access the application and complete setup"
    echo
}

# Main installation function
main() {
    echo "=========================================="
    echo "Assertly Enterprise Installation"
    echo "=========================================="
    echo
    
    check_root
    check_requirements
    create_user_and_directories
    install_docker_images
    generate_configuration
    generate_ssl_certificates
    create_systemd_service
    start_services
    display_summary
}

# Run main function
main "$@"