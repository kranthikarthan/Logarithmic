# Azure Monitor and Application Insights Setup for Bank Interoperability Layer

## Azure Monitor Configuration

### 1. Log Analytics Workspace Setup
```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group bank-interoperability-rg \
  --workspace-name bank-interoperability-logs \
  --location eastus \
  --sku PerGB2018 \
  --retention-time 30

# Get workspace ID and key
az monitor log-analytics workspace show \
  --resource-group bank-interoperability-rg \
  --workspace-name bank-interoperability-logs \
  --query customerId -o tsv

az monitor log-analytics workspace get-shared-keys \
  --resource-group bank-interoperability-rg \
  --workspace-name bank-interoperability-logs
```

### 2. Application Insights Setup
```bash
# Create Application Insights
az monitor app-insights component create \
  --resource-group bank-interoperability-rg \
  --app bank-interoperability-insights \
  --location eastus \
  --kind web \
  --application-type web \
  --workspace bank-interoperability-logs

# Get instrumentation key and connection string
az monitor app-insights component show \
  --resource-group bank-interoperability-rg \
  --app bank-interoperability-insights \
  --query instrumentationKey -o tsv

az monitor app-insights component show \
  --resource-group bank-interoperability-rg \
  --app bank-interoperability-insights \
  --query connectionString -o tsv
```

## Azure Monitor for Containers

### 1. Container Insights Configuration
```yaml
# Container Insights configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: container-insights-config
  namespace: interoperability-monitoring
data:
  config.yaml: |
    # Container Insights configuration
    containerInsights:
      enabled: true
      workspaceId: "<log-analytics-workspace-id>"
      workspaceKey: "<log-analytics-workspace-key>"
      
      # Metrics collection
      metrics:
        enabled: true
        interval: "60s"
        namespaces:
          - "interoperability-core"
          - "interoperability-gateway"
          - "interoperability-routing"
          - "interoperability-saga"
      
      # Log collection
      logs:
        enabled: true
        sources:
          - "stdout"
          - "stderr"
          - "application"
          - "system"
      
      # Performance monitoring
      performance:
        enabled: true
        cpu: true
        memory: true
        disk: true
        network: true
```

### 2. Prometheus Integration
```yaml
# Prometheus integration
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: interoperability-monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name
```

## Application Insights Configuration

### 1. Application Insights SDK Configuration
```yaml
# Application Insights SDK configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: application-insights-config
  namespace: interoperability-monitoring
data:
  applicationinsights.json: |
    {
      "instrumentation": {
        "key": "<instrumentation-key>",
        "connectionString": "<connection-string>"
      },
      "sampling": {
        "percentage": 100,
        "excludedTypes": ["Dependency", "Exception"]
      },
      "telemetryProcessors": [
        {
          "type": "Microsoft.ApplicationInsights.WindowsServer.TelemetryChannel.TelemetryChannel"
        }
      ],
      "performanceCounters": {
        "enabled": true
      },
      "dependencyTracking": {
        "enabled": true
      },
      "requestTracking": {
        "enabled": true
      },
      "exceptionTracking": {
        "enabled": true
      }
    }
```

### 2. Custom Metrics Configuration
```yaml
# Custom metrics configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: custom-metrics-config
  namespace: interoperability-monitoring
data:
  metrics.yaml: |
    # Custom metrics
    customMetrics:
      - name: "banking_requests_total"
        type: "counter"
        description: "Total number of banking requests"
        labels:
          - "request_type"
          - "status"
          - "environment"
      
      - name: "banking_request_duration_seconds"
        type: "histogram"
        description: "Duration of banking requests"
        buckets: [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        labels:
          - "request_type"
          - "status"
      
      - name: "saga_execution_duration_seconds"
        type: "histogram"
        description: "Duration of saga execution"
        buckets: [1.0, 5.0, 10.0, 30.0, 60.0, 300.0]
        labels:
          - "saga_type"
          - "status"
      
      - name: "active_sagas_total"
        type: "gauge"
        description: "Number of active sagas"
        labels:
          - "saga_type"
          - "environment"
```

## OpenTelemetry Integration

### 1. OpenTelemetry Configuration
```yaml
# OpenTelemetry configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: opentelemetry-config
  namespace: interoperability-monitoring
data:
  otel-config.yaml: |
    # OpenTelemetry configuration
    opentelemetry:
      enabled: true
      serviceName: "bank-interoperability"
      serviceVersion: "1.0.0"
      
      # Exporters
      exporters:
        - name: "jaeger"
          endpoint: "http://jaeger-collector:14250"
          protocol: "grpc"
        - name: "prometheus"
          endpoint: "http://prometheus:9090"
          protocol: "http"
        - name: "azure-monitor"
          connectionString: "<app-insights-connection-string>"
      
      # Sampling
      sampling:
        type: "traceidratio"
        ratio: 1.0
      
      # Resource attributes
      resource:
        service.name: "bank-interoperability"
        service.version: "1.0.0"
        deployment.environment: "production"
        cloud.provider: "azure"
        cloud.region: "eastus"
```

### 2. Jaeger Configuration
```yaml
# Jaeger configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: jaeger-config
  namespace: interoperability-monitoring
data:
  jaeger.yaml: |
    # Jaeger configuration
    jaeger:
      enabled: true
      collector:
        endpoint: "http://jaeger-collector:14268/api/traces"
        timeout: "30s"
      query:
        endpoint: "http://jaeger-query:16686"
      agent:
        endpoint: "jaeger-agent:6831"
        protocol: "udp"
```

## Grafana Dashboards

### 1. Main Dashboard Configuration
```yaml
# Grafana dashboard configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard
  namespace: interoperability-monitoring
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Bank Interoperability Dashboard",
        "panels": [
          {
            "title": "Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(banking_requests_total[5m])",
                "legendFormat": "{{request_type}} - {{status}}"
              }
            ]
          },
          {
            "title": "Response Time",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(banking_request_duration_seconds_bucket[5m]))",
                "legendFormat": "95th Percentile"
              },
              {
                "expr": "histogram_quantile(0.50, rate(banking_request_duration_seconds_bucket[5m]))",
                "legendFormat": "50th Percentile"
              }
            ]
          },
          {
            "title": "Saga Success Rate",
            "type": "stat",
            "targets": [
              {
                "expr": "rate(banking_requests_total{status=\"success\"}[5m]) / rate(banking_requests_total[5m]) * 100",
                "legendFormat": "Success Rate %"
              }
            ]
          },
          {
            "title": "Active Sagas",
            "type": "gauge",
            "targets": [
              {
                "expr": "active_sagas_total",
                "legendFormat": "Active Sagas"
              }
            ]
          }
        ]
      }
    }
```

### 2. Security Dashboard
```yaml
# Security dashboard configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-dashboard
  namespace: interoperability-monitoring
data:
  security-dashboard.json: |
    {
      "dashboard": {
        "title": "Security Dashboard",
        "panels": [
          {
            "title": "Security Events",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(security_events_total[5m])",
                "legendFormat": "{{event_type}}"
              }
            ]
          },
          {
            "title": "Failed Logins",
            "type": "stat",
            "targets": [
              {
                "expr": "rate(failed_logins_total[5m])",
                "legendFormat": "Failed Logins/min"
              }
            ]
          },
          {
            "title": "Active Threats",
            "type": "table",
            "targets": [
              {
                "expr": "active_threats",
                "legendFormat": "{{threat_type}} - {{severity}}"
              }
            ]
          }
        ]
      }
    }
```

## Azure Monitor Alerts

### 1. Alert Rules Configuration
```yaml
# Alert rules configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: alert-rules
  namespace: interoperability-monitoring
data:
  alert-rules.yaml: |
    # Alert rules
    alerts:
      - name: "High Error Rate"
        condition: "rate(banking_requests_total{status=\"error\"}[5m]) > 0.1"
        severity: "Critical"
        description: "High error rate detected"
        actions:
          - "Send email notification"
          - "Create incident ticket"
      
      - name: "High Response Time"
        condition: "histogram_quantile(0.95, rate(banking_request_duration_seconds_bucket[5m])) > 2"
        severity: "Warning"
        description: "High response time detected"
        actions:
          - "Send email notification"
      
      - name: "Low Success Rate"
        condition: "rate(banking_requests_total{status=\"success\"}[5m]) / rate(banking_requests_total[5m]) < 0.95"
        severity: "Critical"
        description: "Low success rate detected"
        actions:
          - "Send email notification"
          - "Create incident ticket"
      
      - name: "High Memory Usage"
        condition: "container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.8"
        severity: "Warning"
        description: "High memory usage detected"
        actions:
          - "Send email notification"
```

### 2. Alert Action Groups
```yaml
# Alert action groups
apiVersion: v1
kind: ConfigMap
metadata:
  name: alert-action-groups
  namespace: interoperability-monitoring
data:
  action-groups.yaml: |
    # Alert action groups
    actionGroups:
      - name: "Critical Alerts"
        emailReceivers:
          - "devops-team@bank.com"
          - "on-call@bank.com"
        smsReceivers:
          - "+1234567890"
        webhookReceivers:
          - "https://bank.webhook.office.com/webhookb2/..."
      
      - name: "Warning Alerts"
        emailReceivers:
          - "devops-team@bank.com"
        webhookReceivers:
          - "https://bank.webhook.office.com/webhookb2/..."
```

## Log Analytics Queries

### 1. Custom Log Analytics Queries
```yaml
# Log Analytics queries
apiVersion: v1
kind: ConfigMap
metadata:
  name: log-analytics-queries
  namespace: interoperability-monitoring
data:
  queries.yaml: |
    # Log Analytics queries
    queries:
      - name: "Request Performance"
        query: |
          requests
          | where timestamp > ago(1h)
          | summarize avg(duration), count() by bin(timestamp, 5m)
          | render timechart
      
      - name: "Error Analysis"
        query: |
          exceptions
          | where timestamp > ago(1h)
          | summarize count() by type, outerMessage
          | order by count_ desc
      
      - name: "Dependency Performance"
        query: |
          dependencies
          | where timestamp > ago(1h)
          | summarize avg(duration), count() by name
          | order by avg_duration desc
      
      - name: "Custom Events"
        query: |
          customEvents
          | where timestamp > ago(1h)
          | summarize count() by name
          | order by count_ desc
```

### 2. KQL Workbooks
```yaml
# KQL workbooks
apiVersion: v1
kind: ConfigMap
metadata:
  name: kql-workbooks
  namespace: interoperability-monitoring
data:
  workbooks.yaml: |
    # KQL workbooks
    workbooks:
      - name: "Bank Interoperability Performance"
        queries:
          - name: "Request Rate"
            query: |
              requests
              | where timestamp > ago(24h)
              | summarize count() by bin(timestamp, 1h)
              | render timechart
          
          - name: "Response Time"
            query: |
              requests
              | where timestamp > ago(24h)
              | summarize avg(duration) by bin(timestamp, 1h)
              | render timechart
      
      - name: "Security Analysis"
        queries:
          - name: "Security Events"
            query: |
              securityEvents
              | where timestamp > ago(24h)
              | summarize count() by EventID, Computer
              | order by count_ desc
```

## Monitoring Scripts

### 1. Health Check Script
```bash
#!/bin/bash
# scripts/monitoring/health-check.sh

echo "Running health checks..."

# Check AKS cluster health
echo "Checking AKS cluster health..."
kubectl get nodes
kubectl get pods --all-namespaces

# Check application health
echo "Checking application health..."
curl -f http://api-gateway-service:8080/health || echo "API Gateway health check failed"
curl -f http://intelligent-router-service:8080/health || echo "Intelligent Router health check failed"
curl -f http://saga-orchestrator-service:8080/health || echo "Saga Orchestrator health check failed"

# Check monitoring components
echo "Checking monitoring components..."
kubectl get pods -n interoperability-monitoring

# Check metrics
echo "Checking metrics..."
kubectl top nodes
kubectl top pods --all-namespaces

echo "Health checks completed!"
```

### 2. Performance Test Script
```bash
#!/bin/bash
# scripts/monitoring/performance-test.sh

echo "Running performance tests..."

# Load test API Gateway
echo "Load testing API Gateway..."
for i in {1..100}; do
  curl -s http://api-gateway-service:8080/api/v1/process \
    -H "Content-Type: application/json" \
    -d '{"requestType":"test","payload":"test"}' &
done
wait

# Load test Intelligent Router
echo "Load testing Intelligent Router..."
for i in {1..50}; do
  curl -s http://intelligent-router-service:8080/route \
    -H "Content-Type: application/json" \
    -d '{"requestType":"test","payload":"test"}' &
done
wait

echo "Performance tests completed!"
```

## Monitoring Best Practices

### 1. Monitoring Strategy
```yaml
# Monitoring strategy
apiVersion: v1
kind: ConfigMap
metadata:
  name: monitoring-strategy
  namespace: interoperability-monitoring
data:
  strategy.yaml: |
    # Monitoring strategy
    monitoring:
      # Metrics collection
      metrics:
        - "Application metrics"
        - "Infrastructure metrics"
        - "Business metrics"
        - "Security metrics"
      
      # Logging
      logging:
        - "Application logs"
        - "System logs"
        - "Security logs"
        - "Audit logs"
      
      # Tracing
      tracing:
        - "Distributed tracing"
        - "Request flow tracing"
        - "Performance tracing"
      
      # Alerting
      alerting:
        - "Critical alerts"
        - "Warning alerts"
        - "Info alerts"
```

### 2. Monitoring SLAs
```yaml
# Monitoring SLAs
apiVersion: v1
kind: ConfigMap
metadata:
  name: monitoring-slas
  namespace: interoperability-monitoring
data:
  slas.yaml: |
    # Monitoring SLAs
    slas:
      availability: "99.9%"
      responseTime: "2s"
      errorRate: "< 0.1%"
      throughput: "1000 req/s"
      
      # Alerting SLAs
      alerting:
        critical: "5 minutes"
        warning: "15 minutes"
        info: "1 hour"
```

This completes the Azure Monitor and Application Insights setup. The next step would be to create the Spring Boot microservices structure.