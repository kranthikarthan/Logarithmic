# Java Operator Deployment with Helm Charts

## Helm Chart Structure for Java Operators

### Chart Organization
```
helm-charts/
├── operators/                      # Main operators chart
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-staging.yaml
│   ├── values-prod.yaml
│   └── templates/
│       ├── _helpers.tpl
│       ├── namespace.yaml
│       ├── rbac/
│       ├── crd/
│       ├── interoperability-operator/
│       ├── saga-operator/
│       ├── routing-operator/
│       ├── security-operator/
│       └── monitoring-operator/
├── interoperability-operator/       # Individual operator chart
├── saga-operator/                  # Individual operator chart
├── routing-operator/               # Individual operator chart
├── security-operator/              # Individual operator chart
└── monitoring-operator/            # Individual operator chart
```

## Main Operators Chart

### 1. Chart.yaml
```yaml
# helm-charts/operators/Chart.yaml
apiVersion: v2
name: bank-interoperability-java-operators
description: Java-based Kubernetes Operators for Bank Interoperability Layer
version: 1.0.0
appVersion: "1.0.0"
home: https://github.com/bank/interoperability-java-operators
sources:
  - https://github.com/bank/interoperability-java-operators
maintainers:
  - name: Bank DevOps Team
    email: devops@bank.com
keywords:
  - banking
  - interoperability
  - operators
  - kubernetes
  - java
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
  - name: prometheus-operator
    version: "19.6.1"
    repository: "https://prometheus-community.github.io/helm-charts"
    condition: monitoring.prometheus.enabled
  - name: jaeger-operator
    version: "2.30.0"
    repository: "https://jaegertracing.github.io/helm-charts"
    condition: monitoring.jaeger.enabled
```

### 2. values.yaml
```yaml
# helm-charts/operators/values.yaml
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
      role: "interoperability-operator-role"
    rbac:
      enabled: true
      serviceAccount: "interoperability-operator"
  
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

# Interoperability Operator
interoperabilityOperator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/interoperability-operator"
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
  
  # Java operator configuration
  config:
    metricsBindAddress: ":8080"
    healthProbeBindAddress: ":8081"
    leaderElection: true
    leaderElectionID: "interoperability-operator.bank.com"
    leaderElectionNamespace: "interoperability-core"
    reconciliationInterval: 30000
    maxReconcileAttempts: 3
  
  # Environment variables
  env:
    - name: "SPRING_PROFILES_ACTIVE"
      value: "production"
    - name: "OPERATOR_NAMESPACE"
      value: "interoperability-core"
    - name: "LOG_LEVEL"
      value: "info"
    - name: "METRICS_ENABLED"
      value: "true"
    - name: "JAEGER_ENDPOINT"
      value: "http://jaeger:14268/api/traces"
    - name: "PROMETHEUS_ENDPOINT"
      value: "http://prometheus:9090"
  
  # Probes
  livenessProbe:
    httpGet:
      path: /actuator/health/liveness
      port: 8081
    initialDelaySeconds: 60
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  
  readinessProbe:
    httpGet:
      path: /actuator/health/readiness
      port: 8081
    initialDelaySeconds: 30
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 3

# Saga Operator
sagaOperator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/saga-operator"
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
  
  config:
    metricsBindAddress: ":8080"
    healthProbeBindAddress: ":8081"
    leaderElection: true
    leaderElectionID: "saga-operator.bank.com"
    leaderElectionNamespace: "interoperability-saga"
    reconciliationInterval: 30000
    maxReconcileAttempts: 3
  
  env:
    - name: "SPRING_PROFILES_ACTIVE"
      value: "production"
    - name: "OPERATOR_NAMESPACE"
      value: "interoperability-saga"
    - name: "TEMPORAL_ENDPOINT"
      value: "temporal.bank.com:7233"
    - name: "TEMPORAL_NAMESPACE"
      value: "bank-interoperability"

# Routing Operator
routingOperator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/routing-operator"
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
  
  config:
    metricsBindAddress: ":8080"
    healthProbeBindAddress: ":8081"
    leaderElection: true
    leaderElectionID: "routing-operator.bank.com"
    leaderElectionNamespace: "interoperability-routing"
    reconciliationInterval: 30000
    maxReconcileAttempts: 3
  
  env:
    - name: "SPRING_PROFILES_ACTIVE"
      value: "production"
    - name: "OPERATOR_NAMESPACE"
      value: "interoperability-routing"
    - name: "ML_MODEL_PATH"
      value: "/models"
    - name: "ROUTING_ALGORITHM"
      value: "intelligent"

# Security Operator
securityOperator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/security-operator"
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
  
  config:
    metricsBindAddress: ":8080"
    healthProbeBindAddress: ":8081"
    leaderElection: true
    leaderElectionID: "security-operator.bank.com"
    leaderElectionNamespace: "interoperability-security"
    reconciliationInterval: 30000
    maxReconcileAttempts: 3
  
  env:
    - name: "SPRING_PROFILES_ACTIVE"
      value: "production"
    - name: "OPERATOR_NAMESPACE"
      value: "interoperability-security"
    - name: "VAULT_URL"
      value: "https://vault.bank.com"
    - name: "VAULT_ROLE"
      value: "interoperability-operator"

# Monitoring Operator
monitoringOperator:
  enabled: true
  replicaCount: 1
  image:
    repository: "bankregistry.azurecr.io/monitoring-operator"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  service:
    type: "ClusterIP"
    port: 8080
    targetPort: 8080
  
  resources:
    requests:
      cpu: "200m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"
  
  config:
    metricsBindAddress: ":8080"
    healthProbeBindAddress: ":8081"
    leaderElection: false
    reconciliationInterval: 30000
    maxReconcileAttempts: 3
  
  env:
    - name: "SPRING_PROFILES_ACTIVE"
      value: "production"
    - name: "OPERATOR_NAMESPACE"
      value: "interoperability-monitoring"
    - name: "PROMETHEUS_URL"
      value: "http://prometheus:9090"
    - name: "GRAFANA_URL"
      value: "http://grafana:3000"

# CRD Configuration
crd:
  enabled: true
  crds:
    - name: "interoperabilityrequests"
      group: "interoperability.bank.com"
      version: "v1"
      scope: "Namespaced"
      plural: "interoperabilityrequests"
      singular: "interoperabilityrequest"
      shortNames: ["ir"]
    
    - name: "routingdecisions"
      group: "routing.bank.com"
      version: "v1"
      scope: "Namespaced"
      plural: "routingdecisions"
      singular: "routingdecision"
      shortNames: ["rd"]
    
    - name: "sagas"
      group: "saga.bank.com"
      version: "v1"
      scope: "Namespaced"
      plural: "sagas"
      singular: "saga"
      shortNames: ["saga"]
    
    - name: "securitypolicies"
      group: "security.bank.com"
      version: "v1"
      scope: "Namespaced"
      plural: "securitypolicies"
      singular: "securitypolicy"
      shortNames: ["sp"]

# RBAC Configuration
rbac:
  enabled: true
  serviceAccount:
    name: "interoperability-operator"
    namespace: "interoperability-core"
  
  clusterRoles:
    - name: "interoperability-operator"
      rules:
        - apiGroups: ["interoperability.bank.com"]
          resources: ["interoperabilityrequests"]
          verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
        - apiGroups: ["routing.bank.com"]
          resources: ["routingdecisions"]
          verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
        - apiGroups: ["saga.bank.com"]
          resources: ["sagas"]
          verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
        - apiGroups: ["security.bank.com"]
          resources: ["securitypolicies"]
          verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
        - apiGroups: ["apps"]
          resources: ["deployments"]
          verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
        - apiGroups: [""]
          resources: ["services", "configmaps", "secrets"]
          verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
        - apiGroups: ["networking.k8s.io"]
          resources: ["networkpolicies"]
          verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  
  roleBindings:
    - name: "interoperability-operator"
      namespace: "interoperability-core"
      roleRef:
        kind: "ClusterRole"
        name: "interoperability-operator"
      subjects:
        - kind: "ServiceAccount"
          name: "interoperability-operator"
          namespace: "interoperability-core"

# Monitoring Configuration
monitoring:
  prometheus:
    enabled: true
    serviceMonitor:
      enabled: true
      interval: "30s"
      scrapeTimeout: "10s"
  
  jaeger:
    enabled: true
    tracing:
      enabled: true
      endpoint: "http://jaeger-collector:14268/api/traces"
  
  grafana:
    enabled: true
    dashboards:
      - name: "interoperability-java-operators"
        title: "Bank Interoperability Java Operators"
        panels:
          - title: "Operator Health"
            type: "stat"
            query: "up{job=\"interoperability-operator\"}"
          - title: "Request Processing Rate"
            type: "graph"
            query: "rate(interoperability_requests_processed_total[5m])"
          - title: "Error Rate"
            type: "graph"
            query: "rate(interoperability_errors_total[5m])"
          - title: "JVM Memory Usage"
            type: "graph"
            query: "jvm_memory_used_bytes{job=\"interoperability-operator\"}"
```

## Operator Deployment Templates

### 1. Interoperability Operator Deployment
```yaml
# helm-charts/operators/templates/interoperability-operator/deployment.yaml
{{- if .Values.interoperabilityOperator.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "operators.fullname" . }}-interoperability-operator
  namespace: {{ .Values.namespace | default "interoperability-core" }}
  labels:
    {{- include "operators.labels" . | nindent 4 }}
    component: interoperability-operator
    operator-type: java
spec:
  replicas: {{ .Values.interoperabilityOperator.replicaCount }}
  selector:
    matchLabels:
      {{- include "operators.selectorLabels" . | nindent 6 }}
      component: interoperability-operator
  template:
    metadata:
      labels:
        {{- include "operators.selectorLabels" . | nindent 8 }}
        component: interoperability-operator
        operator-type: java
      annotations:
        sidecar.istio.io/inject: "true"
    spec:
      serviceAccountName: {{ include "operators.serviceAccountName" . }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
        - name: interoperability-operator
          image: "{{ .Values.global.imageRegistry }}/{{ .Values.interoperabilityOperator.image.repository }}:{{ .Values.interoperabilityOperator.image.tag }}"
          imagePullPolicy: {{ .Values.interoperabilityOperator.image.pullPolicy }}
          ports:
            - name: metrics
              containerPort: 8080
              protocol: TCP
            - name: health
              containerPort: 8081
              protocol: TCP
          args:
            - "--server.port=8080"
            - "--management.server.port=8081"
            - "--spring.profiles.active=production"
            - "--interoperability.operators.namespace=interoperability-core"
            - "--interoperability.operators.operator-type=java"
          env:
            {{- range .Values.interoperabilityOperator.env }}
            - name: {{ .name }}
              value: {{ .value | quote }}
            {{- end }}
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: JAVA_OPTS
              value: "-Xmx512m -Xms256m -XX:+UseG1GC -XX:+UseStringDeduplication"
          resources:
            {{- toYaml .Values.interoperabilityOperator.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: {{ .Values.interoperabilityOperator.livenessProbe.httpGet.path }}
              port: {{ .Values.interoperabilityOperator.livenessProbe.httpGet.port }}
            initialDelaySeconds: {{ .Values.interoperabilityOperator.livenessProbe.initialDelaySeconds }}
            periodSeconds: {{ .Values.interoperabilityOperator.livenessProbe.periodSeconds }}
            timeoutSeconds: {{ .Values.interoperabilityOperator.livenessProbe.timeoutSeconds }}
            failureThreshold: {{ .Values.interoperabilityOperator.livenessProbe.failureThreshold }}
          readinessProbe:
            httpGet:
              path: {{ .Values.interoperabilityOperator.readinessProbe.httpGet.path }}
              port: {{ .Values.interoperabilityOperator.readinessProbe.httpGet.port }}
            initialDelaySeconds: {{ .Values.interoperabilityOperator.readinessProbe.initialDelaySeconds }}
            periodSeconds: {{ .Values.interoperabilityOperator.readinessProbe.periodSeconds }}
            timeoutSeconds: {{ .Values.interoperabilityOperator.readinessProbe.timeoutSeconds }}
            failureThreshold: {{ .Values.interoperabilityOperator.readinessProbe.failureThreshold }}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: false
            runAsNonRoot: true
            runAsUser: 1000
            capabilities:
              drop:
                - ALL
      imagePullSecrets:
        {{- toYaml .Values.global.imagePullSecrets | nindent 8 }}
{{- end }}
```

### 2. CRD Templates
```yaml
# helm-charts/operators/templates/crd/interoperabilityrequest.yaml
{{- if .Values.crd.enabled }}
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: interoperabilityrequests.interoperability.bank.com
  labels:
    {{- include "operators.labels" . | nindent 4 }}
    operator-type: java
spec:
  group: interoperability.bank.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              requestId:
                type: string
              requestType:
                type: string
              payload:
                type: string
              routingStrategy:
                type: string
              dependencies:
                type: array
                items:
                  type: object
                  properties:
                    stepId:
                      type: string
                    dependsOn:
                      type: array
                      items:
                        type: string
              securityContext:
                type: object
                properties:
                  encryptionKey:
                    type: string
                  accessToken:
                    type: string
                  policies:
                    type: object
          status:
            type: object
            properties:
              phase:
                type: string
              message:
                type: string
              lastTransitionTime:
                type: string
                format: date-time
              steps:
                type: array
                items:
                  type: object
                  properties:
                    stepId:
                      type: string
                    status:
                      type: string
                    message:
                      type: string
                    startTime:
                      type: string
                      format: date-time
                    endTime:
                      type: string
                      format: date-time
              conditions:
                type: array
                items:
                  type: object
                  properties:
                    type:
                      type: string
                    status:
                      type: string
                    lastTransitionTime:
                      type: string
                      format: date-time
                    reason:
                      type: string
                    message:
                      type: string
  scope: Namespaced
  names:
    plural: interoperabilityrequests
    singular: interoperabilityrequest
    kind: InteroperabilityRequest
    shortNames:
    - ir
{{- end }}
```

### 3. RBAC Templates
```yaml
# helm-charts/operators/templates/rbac/serviceaccount.yaml
{{- if .Values.rbac.enabled }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ .Values.rbac.serviceAccount.name }}
  namespace: {{ .Values.rbac.serviceAccount.namespace }}
  labels:
    {{- include "operators.labels" . | nindent 4 }}
    operator-type: java
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: {{ .Values.rbac.clusterRoles[0].name }}
  labels:
    {{- include "operators.labels" . | nindent 4 }}
    operator-type: java
rules:
{{- toYaml .Values.rbac.clusterRoles[0].rules | nindent 2 }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ .Values.rbac.roleBindings[0].name }}
  namespace: {{ .Values.rbac.roleBindings[0].namespace }}
  labels:
    {{- include "operators.labels" . | nindent 4 }}
    operator-type: java
roleRef:
  kind: {{ .Values.rbac.roleBindings[0].roleRef.kind }}
  name: {{ .Values.rbac.roleBindings[0].roleRef.name }}
  apiGroup: rbac.authorization.k8s.io
subjects:
{{- toYaml .Values.rbac.roleBindings[0].subjects | nindent 2 }}
{{- end }}
```

## Operator Monitoring Templates

### 1. ServiceMonitor for Prometheus
```yaml
# helm-charts/operators/templates/monitoring/servicemonitor.yaml
{{- if .Values.monitoring.prometheus.enabled }}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "operators.fullname" . }}-java-operators
  namespace: {{ .Values.namespace | default "interoperability-monitoring" }}
  labels:
    {{- include "operators.labels" . | nindent 4 }}
    app.kubernetes.io/component: monitoring
    operator-type: java
spec:
  selector:
    matchLabels:
      {{- include "operators.selectorLabels" . | nindent 6 }}
      component: operator
      operator-type: java
  endpoints:
  - port: metrics
    interval: {{ .Values.monitoring.prometheus.serviceMonitor.interval }}
    scrapeTimeout: {{ .Values.monitoring.prometheus.serviceMonitor.scrapeTimeout }}
    path: /actuator/prometheus
{{- end }}
```

### 2. Grafana Dashboard
```yaml
# helm-charts/operators/templates/monitoring/grafana-dashboard.yaml
{{- if .Values.monitoring.grafana.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "operators.fullname" . }}-java-operators-dashboard
  namespace: {{ .Values.namespace | default "interoperability-monitoring" }}
  labels:
    {{- include "operators.labels" . | nindent 4 }}
    grafana_dashboard: "1"
    operator-type: java
data:
  java-operators-dashboard.json: |
    {
      "dashboard": {
        "title": "Bank Interoperability Java Operators",
        "panels": [
          {
            "title": "Operator Health",
            "type": "stat",
            "targets": [
              {
                "expr": "up{job=\"interoperability-operator\"}",
                "legendFormat": "Interoperability Operator"
              },
              {
                "expr": "up{job=\"saga-operator\"}",
                "legendFormat": "Saga Operator"
              },
              {
                "expr": "up{job=\"routing-operator\"}",
                "legendFormat": "Routing Operator"
              },
              {
                "expr": "up{job=\"security-operator\"}",
                "legendFormat": "Security Operator"
              }
            ]
          },
          {
            "title": "Request Processing Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(interoperability_requests_processed_total[5m])",
                "legendFormat": "{{request_type}} - {{status}}"
              }
            ]
          },
          {
            "title": "Error Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(interoperability_errors_total[5m])",
                "legendFormat": "{{error_type}} - {{operator}}"
              }
            ]
          },
          {
            "title": "JVM Memory Usage",
            "type": "graph",
            "targets": [
              {
                "expr": "jvm_memory_used_bytes{job=\"interoperability-operator\"}",
                "legendFormat": "Memory Used"
              }
            ]
          },
          {
            "title": "JVM GC Time",
            "type": "graph",
            "targets": [
              {
                "expr": "jvm_gc_pause_seconds_total{job=\"interoperability-operator\"}",
                "legendFormat": "GC Time"
              }
            ]
          }
        ]
      }
    }
{{- end }}
```

## Deployment Scripts

### 1. Java Operator Deployment Script
```bash
#!/bin/bash
# scripts/deployment/deploy-java-operators.sh

set -e

ENVIRONMENT=${1:-production}
NAMESPACE="interoperability-${ENVIRONMENT}"

echo "Deploying Bank Interoperability Java Operators to ${ENVIRONMENT} environment..."

# Create namespace if it doesn't exist
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Deploy operators using Helm
helm upgrade --install java-operators ./helm-charts/operators \
  --namespace ${NAMESPACE} \
  --create-namespace \
  --values ./helm-charts/operators/values-${ENVIRONMENT}.yaml \
  --set global.environment=${ENVIRONMENT} \
  --set global.operatorType=java \
  --wait \
  --timeout=10m

# Verify operator deployment
echo "Verifying Java operator deployment..."
kubectl get pods -n ${NAMESPACE} -l operator-type=java
kubectl get crd | grep interoperability

# Check operator health
echo "Checking operator health..."
kubectl get pods -n ${NAMESPACE} -l operator-type=java -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}'

echo "Java operator deployment completed successfully!"
```

### 2. Java Operator Rollback Script
```bash
#!/bin/bash
# scripts/deployment/rollback-java-operators.sh

set -e

ENVIRONMENT=${1:-production}
NAMESPACE="interoperability-${ENVIRONMENT}"

echo "Rolling back Bank Interoperability Java Operators in ${ENVIRONMENT} environment..."

# Rollback using Helm
helm rollback java-operators \
  --namespace ${NAMESPACE} \
  --wait \
  --timeout=10m

echo "Java operator rollback completed successfully!"
```

This completes the Java operator deployment with Helm charts!