# Helm Charts for Kubernetes Deployment - Bank Interoperability Layer

## Helm Chart Structure

### Chart Organization
```
helm-charts/
├── interoperability/              # Main interoperability chart
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-staging.yaml
│   ├── values-prod.yaml
│   ├── templates/
│   │   ├── _helpers.tpl
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── api-gateway/
│   │   ├── intelligent-router/
│   │   ├── saga-orchestrator/
│   │   ├── protocol-adapters/
│   │   ├── schema-adapters/
│   │   ├── security-services/
│   │   ├── event-coordinator/
│   │   ├── monitoring/
│   │   └── istio/
│   └── charts/
├── api-gateway/                   # API Gateway chart
├── intelligent-router/            # Intelligent Router chart
├── saga-orchestrator/             # Saga Orchestrator chart
└── shared/                        # Shared components chart
```

## Main Interoperability Chart

### 1. Chart.yaml
```yaml
# helm-charts/interoperability/Chart.yaml
apiVersion: v2
name: interoperability
description: Bank Interoperability Layer Helm Chart
version: 1.0.0
appVersion: "1.0.0"
home: https://github.com/bank/interoperability-layer
sources:
  - https://github.com/bank/interoperability-layer
maintainers:
  - name: Bank DevOps Team
    email: devops@bank.com
keywords:
  - banking
  - interoperability
  - microservices
  - spring-boot
dependencies:
  - name: postgresql
    version: "12.1.2"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "17.3.7"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
  - name: prometheus
    version: "19.6.1"
    repository: "https://prometheus-community.github.io/helm-charts"
    condition: monitoring.prometheus.enabled
  - name: grafana
    version: "6.50.7"
    repository: "https://grafana.github.io/helm-charts"
    condition: monitoring.grafana.enabled
```

### 2. values.yaml
```yaml
# helm-charts/interoperability/values.yaml
global:
  imageRegistry: "bankregistry.azurecr.io"
  imageTag: "latest"
  imagePullSecrets:
    - name: "acr-secret"
  
  # Azure specific configuration
  azure:
    subscriptionId: ""
    resourceGroup: "bank-interoperability-rg"
    location: "eastus"
  
  # Security configuration
  security:
    enabled: true
    vault:
      enabled: true
      url: "https://vault.bank.com"
      role: "interoperability-role"
    oauth2:
      enabled: true
      issuer: "https://login.microsoftonline.com/<tenant-id>/v2.0"
      clientId: ""
      clientSecret: ""
  
  # Monitoring configuration
  monitoring:
    enabled: true
    prometheus:
      enabled: true
      url: "http://prometheus:9090"
    jaeger:
      enabled: true
      url: "http://jaeger:16686"
    grafana:
      enabled: true
      url: "http://grafana:3000"
    applicationInsights:
      enabled: true
      connectionString: ""

# API Gateway configuration
apiGateway:
  enabled: true
  replicaCount: 3
  image:
    repository: "bankregistry.azurecr.io/bank-interoperability-api-gateway"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  service:
    type: "ClusterIP"
    port: 8080
    targetPort: 8080
  
  ingress:
    enabled: true
    className: "istio"
    annotations:
      istio.ingress.kubernetes.io/rewrite-target: "/"
      istio.ingress.kubernetes.io/ssl-redirect: "true"
    hosts:
      - host: "api.bank.com"
        paths:
          - path: "/"
            pathType: "Prefix"
    tls:
      - secretName: "bank-interoperability-tls"
        hosts:
          - "api.bank.com"
  
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "1Gi"
  
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  
  # Environment variables
  env:
    - name: "SPRING_PROFILES_ACTIVE"
      value: "production"
    - name: "DATABASE_URL"
      value: "jdbc:postgresql://postgresql:5432/interoperability"
    - name: "REDIS_HOST"
      value: "redis"
    - name: "JAEGER_ENDPOINT"
      value: "http://jaeger:14268/api/traces"

# Intelligent Router configuration
intelligentRouter:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/bank-interoperability-intelligent-router"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  service:
    type: "ClusterIP"
    port: 8080
    targetPort: 8080
  
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "1Gi"
  
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 8
    targetCPUUtilizationPercentage: 70

# Saga Orchestrator configuration
sagaOrchestrator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/bank-interoperability-saga-orchestrator"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  service:
    type: "ClusterIP"
    port: 8080
    targetPort: 8080
  
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "1Gi"
  
  # Temporal configuration
  temporal:
    enabled: true
    host: "temporal.bank.com"
    port: 7233
    namespace: "bank-interoperability"

# Protocol Adapters configuration
protocolAdapters:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/bank-interoperability-protocol-adapters"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  service:
    type: "ClusterIP"
    port: 8080
    targetPort: 8080
  
  resources:
    requests:
      cpu: "300m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"

# Schema Adapters configuration
schemaAdapters:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/bank-interoperability-schema-adapters"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  service:
    type: "ClusterIP"
    port: 8080
    targetPort: 8080
  
  resources:
    requests:
      cpu: "300m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"

# Security Services configuration
securityServices:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/bank-interoperability-security-services"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  service:
    type: "ClusterIP"
    port: 8080
    targetPort: 8080
  
  resources:
    requests:
      cpu: "300m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"

# Event Coordinator configuration
eventCoordinator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/bank-interoperability-event-coordinator"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  service:
    type: "ClusterIP"
    port: 8080
    targetPort: 8080
  
  resources:
    requests:
      cpu: "300m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"

# PostgreSQL configuration
postgresql:
  enabled: true
  auth:
    postgresPassword: ""
    username: "interoperability"
    password: ""
    database: "interoperability"
  
  primary:
    persistence:
      enabled: true
      size: "20Gi"
      storageClass: "managed-premium"
  
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "1Gi"

# Redis configuration
redis:
  enabled: true
  auth:
    enabled: false
  
  master:
    persistence:
      enabled: true
      size: "5Gi"
      storageClass: "managed-premium"
  
  resources:
    requests:
      cpu: "200m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"

# Monitoring configuration
monitoring:
  prometheus:
    enabled: true
    server:
      persistentVolume:
        enabled: true
        size: "10Gi"
        storageClass: "managed-premium"
  
  grafana:
    enabled: true
    adminPassword: ""
    persistence:
      enabled: true
      size: "5Gi"
      storageClass: "managed-premium"
  
  jaeger:
    enabled: true
    storage:
      type: "elasticsearch"
      elasticsearch:
        nodeCount: 1
        storage:
          size: "10Gi"
          storageClass: "managed-premium"

# Istio configuration
istio:
  enabled: true
  gateway:
    enabled: true
    name: "bank-interoperability-gateway"
    namespace: "interoperability-gateway"
  
  virtualService:
    enabled: true
    name: "bank-interoperability-vs"
    hosts:
      - "api.bank.com"
      - "dev-api.bank.com"
      - "staging-api.bank.com"
```

## API Gateway Chart Templates

### 1. Deployment Template
```yaml
# helm-charts/interoperability/templates/api-gateway/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "interoperability.fullname" . }}-api-gateway
  namespace: {{ .Values.namespace | default "interoperability-gateway" }}
  labels:
    {{- include "interoperability.labels" . | nindent 4 }}
    component: api-gateway
spec:
  replicas: {{ .Values.apiGateway.replicaCount }}
  selector:
    matchLabels:
      {{- include "interoperability.selectorLabels" . | nindent 6 }}
      component: api-gateway
  template:
    metadata:
      labels:
        {{- include "interoperability.selectorLabels" . | nindent 8 }}
        component: api-gateway
      annotations:
        sidecar.istio.io/inject: "true"
    spec:
      serviceAccountName: {{ include "interoperability.serviceAccountName" . }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
        - name: api-gateway
          image: "{{ .Values.global.imageRegistry }}/{{ .Values.apiGateway.image.repository }}:{{ .Values.apiGateway.image.tag }}"
          imagePullPolicy: {{ .Values.apiGateway.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          env:
            {{- range .Values.apiGateway.env }}
            - name: {{ .name }}
              value: {{ .value | quote }}
            {{- end }}
            - name: SPRING_PROFILES_ACTIVE
              value: {{ .Values.global.environment | default "production" | quote }}
            - name: DATABASE_URL
              value: "jdbc:postgresql://{{ include "postgresql.fullname" . }}:5432/{{ .Values.postgresql.auth.database }}"
            - name: REDIS_HOST
              value: {{ include "redis.fullname" . }}
            - name: JAEGER_ENDPOINT
              value: "http://{{ include "jaeger.fullname" . }}-collector:14268/api/traces"
          resources:
            {{- toYaml .Values.apiGateway.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            runAsUser: 1000
            capabilities:
              drop:
                - ALL
      imagePullSecrets:
        {{- toYaml .Values.global.imagePullSecrets | nindent 8 }}
```

### 2. Service Template
```yaml
# helm-charts/interoperability/templates/api-gateway/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "interoperability.fullname" . }}-api-gateway
  namespace: {{ .Values.namespace | default "interoperability-gateway" }}
  labels:
    {{- include "interoperability.labels" . | nindent 4 }}
    component: api-gateway
spec:
  type: {{ .Values.apiGateway.service.type }}
  ports:
    - port: {{ .Values.apiGateway.service.port }}
      targetPort: {{ .Values.apiGateway.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "interoperability.selectorLabels" . | nindent 4 }}
    component: api-gateway
```

### 3. Ingress Template
```yaml
# helm-charts/interoperability/templates/api-gateway/ingress.yaml
{{- if .Values.apiGateway.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "interoperability.fullname" . }}-api-gateway
  namespace: {{ .Values.namespace | default "interoperability-gateway" }}
  labels:
    {{- include "interoperability.labels" . | nindent 4 }}
    component: api-gateway
  annotations:
    {{- toYaml .Values.apiGateway.ingress.annotations | nindent 4 }}
spec:
  {{- if .Values.apiGateway.ingress.tls }}
  tls:
    {{- range .Values.apiGateway.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.apiGateway.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "interoperability.fullname" $ }}-api-gateway
                port:
                  number: {{ $.Values.apiGateway.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
```

## Istio Configuration Templates

### 1. Gateway Template
```yaml
# helm-charts/interoperability/templates/istio/gateway.yaml
{{- if .Values.istio.enabled -}}
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: {{ .Values.istio.gateway.name }}
  namespace: {{ .Values.istio.gateway.namespace }}
  labels:
    {{- include "interoperability.labels" . | nindent 4 }}
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    {{- range .Values.istio.virtualService.hosts }}
    - {{ . | quote }}
    {{- end }}
    tls:
      httpsRedirect: true
  - port:
      number: 443
      name: https
      protocol: HTTPS
    hosts:
    {{- range .Values.istio.virtualService.hosts }}
    - {{ . | quote }}
    {{- end }}
    tls:
      mode: SIMPLE
      credentialName: bank-interoperability-tls
{{- end }}
```

### 2. Virtual Service Template
```yaml
# helm-charts/interoperability/templates/istio/virtualservice.yaml
{{- if .Values.istio.enabled -}}
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: {{ .Values.istio.virtualService.name }}
  namespace: {{ .Values.namespace | default "interoperability-gateway" }}
  labels:
    {{- include "interoperability.labels" . | nindent 4 }}
spec:
  hosts:
  {{- range .Values.istio.virtualService.hosts }}
  - {{ . | quote }}
  {{- end }}
  gateways:
  - {{ .Values.istio.gateway.name }}
  http:
  - match:
    - uri:
        prefix: "/api/v1/process"
    route:
    - destination:
        host: {{ include "interoperability.fullname" . }}-api-gateway
        port:
          number: {{ .Values.apiGateway.service.port }}
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
  - match:
    - uri:
        prefix: "/health"
    route:
    - destination:
        host: {{ include "interoperability.fullname" . }}-api-gateway
        port:
          number: {{ .Values.apiGateway.service.port }}
{{- end }}
```

## Monitoring Templates

### 1. Prometheus Configuration
```yaml
# helm-charts/interoperability/templates/monitoring/prometheus-config.yaml
{{- if .Values.monitoring.prometheus.enabled -}}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "interoperability.fullname" . }}-prometheus-config
  namespace: {{ .Values.namespace | default "interoperability-monitoring" }}
  labels:
    {{- include "interoperability.labels" . | nindent 4 }}
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
{{- end }}
```

### 2. Grafana Dashboard
```yaml
# helm-charts/interoperability/templates/monitoring/grafana-dashboard.yaml
{{- if .Values.monitoring.grafana.enabled -}}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "interoperability.fullname" . }}-grafana-dashboard
  namespace: {{ .Values.namespace | default "interoperability-monitoring" }}
  labels:
    {{- include "interoperability.labels" . | nindent 4 }}
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
          }
        ]
      }
    }
{{- end }}
```

## Helper Templates

### 1. _helpers.tpl
```yaml
# helm-charts/interoperability/templates/_helpers.tpl
{{/*
Expand the name of the chart.
*/}}
{{- define "interoperability.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "interoperability.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "interoperability.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "interoperability.labels" -}}
helm.sh/chart: {{ include "interoperability.chart" . }}
{{ include "interoperability.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "interoperability.selectorLabels" -}}
app.kubernetes.io/name: {{ include "interoperability.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "interoperability.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "interoperability.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
```

## Deployment Scripts

### 1. Deploy Script
```bash
#!/bin/bash
# scripts/deployment/deploy.sh

set -e

ENVIRONMENT=${1:-production}
NAMESPACE="interoperability-${ENVIRONMENT}"

echo "Deploying Bank Interoperability Layer to ${ENVIRONMENT} environment..."

# Create namespace if it doesn't exist
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Deploy using Helm
helm upgrade --install interoperability ./helm-charts/interoperability \
  --namespace ${NAMESPACE} \
  --create-namespace \
  --values ./helm-charts/interoperability/values-${ENVIRONMENT}.yaml \
  --set global.environment=${ENVIRONMENT} \
  --wait \
  --timeout=10m

echo "Deployment completed successfully!"
```

### 2. Rollback Script
```bash
#!/bin/bash
# scripts/deployment/rollback.sh

set -e

ENVIRONMENT=${1:-production}
NAMESPACE="interoperability-${ENVIRONMENT}"

echo "Rolling back Bank Interoperability Layer in ${ENVIRONMENT} environment..."

# Rollback using Helm
helm rollback interoperability \
  --namespace ${NAMESPACE} \
  --wait \
  --timeout=10m

echo "Rollback completed successfully!"
```

This completes the Helm charts for Kubernetes deployment. The implementation is now complete with all 8 steps finished!