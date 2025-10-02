#!/usr/bin/env python3
"""
Client Configuration Generator for Assertly
Generates configuration files for different deployment scenarios
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ClientConfig:
    """Client configuration for Assertly deployment"""
    # Basic Information
    client_name: str
    deployment_type: str  # 'cloud', 'on-premises', 'hybrid'
    ai_provider: str
    api_key: str
    
    # AI Configuration
    ai_settings: Dict[str, Any]
    
    # Security Settings
    security_settings: Dict[str, Any]
    
    # Feature Flags
    features: Dict[str, bool]
    
    # Cost Management
    cost_limits: Dict[str, Any]
    
    # Monitoring
    monitoring: Dict[str, Any]
    
    # Created timestamp
    created_at: str

class ClientConfigGenerator:
    """Generates client configurations for different scenarios"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load configuration templates for different scenarios"""
        return {
            'enterprise_on_premises': {
                'deployment_type': 'on-premises',
                'ai_provider': 'local',
                'ai_settings': {
                    'local_ai_url': 'http://localhost:11434',
                    'local_ai_model': 'llama2',
                    'offline_mode': True,
                    'custom_models': True
                },
                'security_settings': {
                    'data_encryption': True,
                    'audit_logging': True,
                    'access_control': True,
                    'data_retention_days': 365
                },
                'features': {
                    'ai_test_generation': True,
                    'ai_test_improvement': True,
                    'bdd_scenario_generation': True,
                    'test_data_generation': True,
                    'coverage_analysis': True,
                    'enterprise_features': True,
                    'offline_operation': True
                },
                'cost_limits': {
                    'monthly_budget': 0,
                    'cost_per_request': 0,
                    'usage_alerts': False
                },
                'monitoring': {
                    'performance_monitoring': True,
                    'usage_tracking': True,
                    'error_logging': True,
                    'health_checks': True
                }
            },
            
            'startup_cloud': {
                'deployment_type': 'cloud',
                'ai_provider': 'openai',
                'ai_settings': {
                    'model': 'gpt-4',
                    'max_tokens': 4000,
                    'temperature': 0.7,
                    'timeout': 30,
                    'retry_attempts': 3
                },
                'security_settings': {
                    'data_encryption': True,
                    'audit_logging': True,
                    'access_control': False,
                    'data_retention_days': 90
                },
                'features': {
                    'ai_test_generation': True,
                    'ai_test_improvement': True,
                    'bdd_scenario_generation': True,
                    'test_data_generation': True,
                    'coverage_analysis': True,
                    'enterprise_features': False,
                    'offline_operation': False
                },
                'cost_limits': {
                    'monthly_budget': 100,
                    'cost_per_request': 0.01,
                    'usage_alerts': True
                },
                'monitoring': {
                    'performance_monitoring': True,
                    'usage_tracking': True,
                    'error_logging': True,
                    'health_checks': True
                }
            },
            
            'enterprise_hybrid': {
                'deployment_type': 'hybrid',
                'ai_provider': 'anthropic',
                'ai_settings': {
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 4000,
                    'temperature': 0.7,
                    'timeout': 30,
                    'retry_attempts': 3,
                    'fallback_to_local': True
                },
                'security_settings': {
                    'data_encryption': True,
                    'audit_logging': True,
                    'access_control': True,
                    'data_retention_days': 365
                },
                'features': {
                    'ai_test_generation': True,
                    'ai_test_improvement': True,
                    'bdd_scenario_generation': True,
                    'test_data_generation': True,
                    'coverage_analysis': True,
                    'enterprise_features': True,
                    'offline_operation': True
                },
                'cost_limits': {
                    'monthly_budget': 500,
                    'cost_per_request': 0.02,
                    'usage_alerts': True
                },
                'monitoring': {
                    'performance_monitoring': True,
                    'usage_tracking': True,
                    'error_logging': True,
                    'health_checks': True
                }
            }
        }
    
    def generate_config(self, client_name: str, scenario: str, 
                       custom_settings: Optional[Dict[str, Any]] = None) -> ClientConfig:
        """Generate client configuration for a specific scenario"""
        
        if scenario not in self.templates:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        template = self.templates[scenario].copy()
        
        # Apply custom settings if provided
        if custom_settings:
            for key, value in custom_settings.items():
                if key in template:
                    template[key].update(value)
                else:
                    template[key] = value
        
        # Generate API key based on provider
        api_key = self._generate_api_key(template['ai_provider'])
        
        config = ClientConfig(
            client_name=client_name,
            deployment_type=template['deployment_type'],
            ai_provider=template['ai_provider'],
            api_key=api_key,
            ai_settings=template['ai_settings'],
            security_settings=template['security_settings'],
            features=template['features'],
            cost_limits=template['cost_limits'],
            monitoring=template['monitoring'],
            created_at=datetime.now().isoformat()
        )
        
        return config
    
    def _generate_api_key(self, provider: str) -> str:
        """Generate a sample API key for the provider"""
        import secrets
        
        if provider == 'openai':
            return f"sk-{secrets.token_hex(32)}"
        elif provider == 'anthropic':
            return f"sk-ant-{secrets.token_hex(32)}"
        elif provider == 'google':
            return f"AIza{secrets.token_hex(32)}"
        elif provider == 'azure':
            return f"az-{secrets.token_hex(32)}"
        elif provider == 'huggingface':
            return f"hf_{secrets.token_hex(32)}"
        elif provider == 'local':
            return "local-llm-key"
        else:
            return f"custom-{secrets.token_hex(16)}"
    
    def generate_deployment_package(self, config: ClientConfig) -> Dict[str, str]:
        """Generate deployment package files"""
        files = {}
        
        # Main configuration file
        files['assertly_config.json'] = json.dumps(asdict(config), indent=2)
        
        # Docker Compose file
        files['docker-compose.yml'] = self._generate_docker_compose(config)
        
        # Environment file
        files['.env'] = self._generate_env_file(config)
        
        # Deployment script
        files['deploy.sh'] = self._generate_deployment_script(config)
        
        # API key configuration
        files['api_keys.json'] = self._generate_api_keys_config(config)
        
        # Monitoring configuration
        files['monitoring.yml'] = self._generate_monitoring_config(config)
        
        return files
    
    def _generate_docker_compose(self, config: ClientConfig) -> str:
        """Generate Docker Compose configuration"""
        if config.deployment_type == 'on-premises':
            return f"""version: '3.8'

services:
  assertly:
    image: assertly:latest
    ports:
      - "5000:5000"
    environment:
      - AI_PROVIDER={config.ai_provider}
      - AI_API_KEY={config.api_key}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres
      - ollama

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=assertly
      - POSTGRES_USER=assertly
      - POSTGRES_PASSWORD=assertly123
    volumes:
      - postgres_data:/var/lib/postgresql/data

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  ollama_data:
"""
        else:
            return f"""version: '3.8'

services:
  assertly:
    image: assertly:latest
    ports:
      - "5000:5000"
    environment:
      - AI_PROVIDER={config.ai_provider}
      - AI_API_KEY={config.api_key}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=assertly
      - POSTGRES_USER=assertly
      - POSTGRES_PASSWORD=assertly123
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
    
    def _generate_env_file(self, config: ClientConfig) -> str:
        """Generate environment file"""
        env_content = f"""# Assertly Configuration
ASSERTLY_ENV=production
ASSERTLY_CLIENT={config.client_name}
ASSERTLY_DEPLOYMENT={config.deployment_type}

# AI Configuration
AI_PROVIDER={config.ai_provider}
AI_API_KEY={config.api_key}
AI_MODEL={config.ai_settings.get('model', 'default')}
AI_MAX_TOKENS={config.ai_settings.get('max_tokens', 4000)}
AI_TEMPERATURE={config.ai_settings.get('temperature', 0.7)}

# Security Settings
DATA_ENCRYPTION={str(config.security_settings.get('data_encryption', True)).lower()}
AUDIT_LOGGING={str(config.security_settings.get('audit_logging', True)).lower()}
DATA_RETENTION_DAYS={config.security_settings.get('data_retention_days', 365)}

# Cost Management
MONTHLY_BUDGET={config.cost_limits.get('monthly_budget', 0)}
COST_PER_REQUEST={config.cost_limits.get('cost_per_request', 0)}
USAGE_ALERTS={str(config.cost_limits.get('usage_alerts', False)).lower()}

# Monitoring
PERFORMANCE_MONITORING={str(config.monitoring.get('performance_monitoring', True)).lower()}
USAGE_TRACKING={str(config.monitoring.get('usage_tracking', True)).lower()}
ERROR_LOGGING={str(config.monitoring.get('error_logging', True)).lower()}
"""
        return env_content
    
    def _generate_deployment_script(self, config: ClientConfig) -> str:
        """Generate deployment script"""
        return f"""#!/bin/bash
# Assertly Deployment Script for {config.client_name}

echo "🚀 Deploying Assertly for {config.client_name}"
echo "   Deployment Type: {config.deployment_type}"
echo "   AI Provider: {config.ai_provider}"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✅ Prerequisites met"

# Create directories
echo "📁 Creating directories..."
mkdir -p data logs

# Set permissions
echo "🔐 Setting permissions..."
chmod 755 data logs

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Assertly is running"
else
    echo "❌ Assertly is not responding"
    exit 1
fi

echo ""
echo "🎉 Deployment complete!"
echo "   Access Assertly at: http://localhost:5000"
echo "   Client: {config.client_name}"
echo "   AI Provider: {config.ai_provider}"
echo ""
echo "📋 Next steps:"
echo "   1. Configure your AI provider API keys"
echo "   2. Set up user accounts"
echo "   3. Configure integrations"
echo "   4. Start using Assertly!"
"""
    
    def _generate_api_keys_config(self, config: ClientConfig) -> str:
        """Generate API keys configuration"""
        api_keys_config = {
            config.ai_provider: {
                "api_key": config.api_key,
                "model": config.ai_settings.get('model', 'default'),
                "max_tokens": config.ai_settings.get('max_tokens', 4000),
                "temperature": config.ai_settings.get('temperature', 0.7),
                "timeout": config.ai_settings.get('timeout', 30),
                "retry_attempts": config.ai_settings.get('retry_attempts', 3),
                "is_active": True,
                "created_at": config.created_at,
                "usage_count": 0,
                "monthly_limit": config.cost_limits.get('monthly_budget'),
                "cost_per_token": config.cost_limits.get('cost_per_request')
            }
        }
        
        return json.dumps(api_keys_config, indent=2)
    
    def _generate_monitoring_config(self, config: ClientConfig) -> str:
        """Generate monitoring configuration"""
        return f"""# Assertly Monitoring Configuration
# Client: {config.client_name}
# Generated: {config.created_at}

monitoring:
  enabled: true
  client: "{config.client_name}"
  
  # Performance Monitoring
  performance:
    enabled: {str(config.monitoring.get('performance_monitoring', True)).lower()}
    metrics:
      - response_time
      - throughput
      - error_rate
      - resource_usage
    
  # Usage Tracking
  usage:
    enabled: {str(config.monitoring.get('usage_tracking', True)).lower()}
    track:
      - api_calls
      - token_usage
      - cost_tracking
      - user_activity
    
  # Error Logging
  errors:
    enabled: {str(config.monitoring.get('error_logging', True)).lower()}
    levels:
      - ERROR
      - WARNING
      - INFO
    
  # Health Checks
  health:
    enabled: {str(config.monitoring.get('health_checks', True)).lower()}
    endpoints:
      - /health
      - /api/ai/providers
      - /api/ai/usage-stats
    
  # Alerts
  alerts:
    enabled: {str(config.cost_limits.get('usage_alerts', False)).lower()}
    thresholds:
      monthly_budget: {config.cost_limits.get('monthly_budget', 0)}
      error_rate: 5%
      response_time: 5s
"""

def main():
    """Main function for testing client configuration generation"""
    print("🏢 Client Configuration Generator")
    print("=" * 50)
    
    generator = ClientConfigGenerator()
    
    # Generate configurations for different scenarios
    scenarios = [
        ('Acme Corp', 'enterprise_on_premises'),
        ('StartupXYZ', 'startup_cloud'),
        ('GlobalCorp', 'enterprise_hybrid')
    ]
    
    for client_name, scenario in scenarios:
        print(f"\n📋 Generating configuration for {client_name} ({scenario})")
        
        try:
            config = generator.generate_config(client_name, scenario)
            files = generator.generate_deployment_package(config)
            
            print(f"✅ Configuration generated")
            print(f"   Client: {config.client_name}")
            print(f"   Deployment: {config.deployment_type}")
            print(f"   AI Provider: {config.ai_provider}")
            print(f"   Features: {sum(config.features.values())} enabled")
            print(f"   Files: {len(files)} generated")
            
            # Save files
            client_dir = f"deployments/{client_name.lower().replace(' ', '_')}"
            os.makedirs(client_dir, exist_ok=True)
            
            for filename, content in files.items():
                filepath = os.path.join(client_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"   📄 {filename}")
            
        except Exception as e:
            print(f"❌ Error generating configuration: {e}")
    
    print(f"\n🎉 Client configuration generation complete!")
    print(f"   Check the 'deployments/' directory for generated files")

if __name__ == "__main__":
    main()