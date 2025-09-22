# Azure Container Registry and AKS Setup for Bank Interoperability Layer

## Azure Container Registry (ACR) Configuration

### 1. ACR Setup and Configuration
```bash
# Create Azure Container Registry
az acr create \
  --resource-group bank-interoperability-rg \
  --name bankregistry \
  --sku Premium \
  --admin-enabled true \
  --location eastus

# Get ACR credentials
az acr credential show --name bankregistry

# Configure ACR authentication
az aks update \
  --resource-group bank-interoperability-rg \
  --name bank-interoperability-aks \
  --attach-acr bankregistry
```

### 2. ACR Security Configuration
```yaml
# ACR security policies
apiVersion: v1
kind: ConfigMap
metadata:
  name: acr-security-config
  namespace: interoperability-core
data:
  security-policies.yaml: |
    # Content trust enabled
    contentTrust: true
    
    # Vulnerability scanning enabled
    vulnerabilityScanning: true
    
    # Image retention policies
    retentionPolicy:
      days: 30
      maxImages: 100
    
    # Access policies
    accessPolicies:
      - principalId: "<service-principal-id>"
        permissions: ["AcrPull", "AcrPush"]
      - principalId: "<aks-identity-id>"
        permissions: ["AcrPull"]
```

### 3. ACR Image Management
```bash
# Build and push images
docker build -t bankregistry.azurecr.io/bank-interoperability-api-gateway:latest ./src/api-gateway
docker push bankregistry.azurecr.io/bank-interoperability-api-gateway:latest

docker build -t bankregistry.azurecr.io/bank-interoperability-intelligent-router:latest ./src/intelligent-router
docker push bankregistry.azurecr.io/bank-interoperability-intelligent-router:latest

docker build -t bankregistry.azurecr.io/bank-interoperability-saga-orchestrator:latest ./src/saga-orchestrator
docker push bankregistry.azurecr.io/bank-interoperability-saga-orchestrator:latest
```

## Azure Kubernetes Service (AKS) Configuration

### 1. AKS Cluster Setup
```bash
# Create AKS cluster
az aks create \
  --resource-group bank-interoperability-rg \
  --name bank-interoperability-aks \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --enable-managed-identity \
  --attach-acr bankregistry \
  --network-plugin azure \
  --load-balancer-sku standard \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 10

# Get AKS credentials
az aks get-credentials --resource-group bank-interoperability-rg --name bank-interoperability-aks
```

### 2. AKS Node Pools Configuration
```yaml
# AKS node pools configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: aks-node-pools-config
  namespace: interoperability-core
data:
  node-pools.yaml: |
    # System node pool
    system:
      name: "system"
      vmSize: "Standard_D4s_v3"
      nodeCount: 3
      minCount: 1
      maxCount: 10
      enableAutoScaling: true
      osType: "Linux"
      mode: "System"
    
    # User node pool for workloads
    user:
      name: "user"
      vmSize: "Standard_D8s_v3"
      nodeCount: 2
      minCount: 1
      maxCount: 20
      enableAutoScaling: true
      osType: "Linux"
      mode: "User"
    
    # Spot node pool for non-critical workloads
    spot:
      name: "spot"
      vmSize: "Standard_D4s_v3"
      nodeCount: 1
      minCount: 0
      maxCount: 10
      enableAutoScaling: true
      osType: "Linux"
      mode: "User"
      priority: "Spot"
      evictionPolicy: "Delete"
```

### 3. AKS Networking Configuration
```yaml
# AKS networking configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: aks-networking-config
  namespace: interoperability-core
data:
  networking.yaml: |
    # Virtual network configuration
    vnet:
      name: "bank-interoperability-vnet"
      addressSpace: "10.0.0.0/16"
      subnets:
        - name: "aks-subnet"
          addressPrefix: "10.0.1.0/24"
        - name: "appgw-subnet"
          addressPrefix: "10.0.2.0/24"
    
    # Service CIDR
    serviceCidr: "10.1.0.0/16"
    dnsServiceIP: "10.1.0.10"
    
    # Pod CIDR
    podCidr: "10.244.0.0/16"
    
    # Network policies
    networkPolicy: "azure"
    loadBalancerSku: "standard"
```

## Istio Service Mesh Configuration

### 1. Istio Installation
```bash
# Install Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Install Istio on AKS
istioctl install --set values.defaultRevision=default

# Enable Istio injection for namespaces
kubectl label namespace interoperability-core istio-injection=enabled
kubectl label namespace interoperability-gateway istio-injection=enabled
kubectl label namespace interoperability-routing istio-injection=enabled
kubectl label namespace interoperability-saga istio-injection=enabled
```

### 2. Istio Gateway Configuration
```yaml
# Istio Gateway configuration
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: bank-interoperability-gateway
  namespace: interoperability-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "api.bank.com"
    - "dev-api.bank.com"
    - "staging-api.bank.com"
    tls:
      httpsRedirect: true
  - port:
      number: 443
      name: https
      protocol: HTTPS
    hosts:
    - "api.bank.com"
    - "dev-api.bank.com"
    - "staging-api.bank.com"
    tls:
      mode: SIMPLE
      credentialName: bank-interoperability-tls
```

### 3. Istio Virtual Service Configuration
```yaml
# Istio Virtual Service configuration
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: bank-interoperability-vs
  namespace: interoperability-gateway
spec:
  hosts:
  - "api.bank.com"
  - "dev-api.bank.com"
  - "staging-api.bank.com"
  gateways:
  - bank-interoperability-gateway
  http:
  - match:
    - uri:
        prefix: "/api/v1/process"
    route:
    - destination:
        host: api-gateway-service
        port:
          number: 8080
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
  - match:
    - uri:
        prefix: "/health"
    route:
    - destination:
        host: api-gateway-service
        port:
          number: 8080
```

## Kubernetes Namespaces Configuration

### 1. Core Namespaces
```yaml
# Core namespaces
apiVersion: v1
kind: Namespace
metadata:
  name: interoperability-core
  labels:
    environment: production
    component: core
    tier: infrastructure
    istio-injection: enabled
---
apiVersion: v1
kind: Namespace
metadata:
  name: interoperability-gateway
  labels:
    environment: production
    component: gateway
    tier: frontend
    istio-injection: enabled
---
apiVersion: v1
kind: Namespace
metadata:
  name: interoperability-routing
  labels:
    environment: production
    component: routing
    tier: middleware
    istio-injection: enabled
---
apiVersion: v1
kind: Namespace
metadata:
  name: interoperability-saga
  labels:
    environment: production
    component: saga
    tier: orchestration
    istio-injection: enabled
```

### 2. Domain Namespaces
```yaml
# Domain namespaces
apiVersion: v1
kind: Namespace
metadata:
  name: interoperability-payments
  labels:
    environment: production
    domain: payments
    tier: business
    istio-injection: enabled
---
apiVersion: v1
kind: Namespace
metadata:
  name: interoperability-loans
  labels:
    environment: production
    domain: loans
    tier: business
    istio-injection: enabled
---
apiVersion: v1
kind: Namespace
metadata:
  name: interoperability-cards
  labels:
    environment: production
    domain: cards
    tier: business
    istio-injection: enabled
```

## Network Policies Configuration

### 1. Core Network Policies
```yaml
# Core network policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: interoperability-core-policy
  namespace: interoperability-core
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: interoperability-gateway
    - namespaceSelector:
        matchLabels:
          name: interoperability-routing
    - namespaceSelector:
        matchLabels:
          name: interoperability-saga
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: interoperability-events
    - namespaceSelector:
        matchLabels:
          name: interoperability-monitoring
```

### 2. Gateway Network Policies
```yaml
# Gateway network policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: interoperability-gateway-policy
  namespace: interoperability-gateway
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from: []
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: interoperability-core
    - namespaceSelector:
        matchLabels:
          name: interoperability-routing
```

## Resource Quotas and Limits

### 1. Namespace Resource Quotas
```yaml
# Resource quotas for namespaces
apiVersion: v1
kind: ResourceQuota
metadata:
  name: interoperability-core-quota
  namespace: interoperability-core
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "50"
    services: "20"
    persistentvolumeclaims: "10"
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: interoperability-gateway-quota
  namespace: interoperability-gateway
spec:
  hard:
    requests.cpu: "2"
    requests.memory: "4Gi"
    limits.cpu: "4"
    limits.memory: "8Gi"
    pods: "20"
    services: "10"
    persistentvolumeclaims: "5"
```

### 2. Pod Resource Limits
```yaml
# Pod resource limits
apiVersion: v1
kind: LimitRange
metadata:
  name: interoperability-limits
  namespace: interoperability-core
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
  - default:
      cpu: "1"
      memory: "1Gi"
    defaultRequest:
      cpu: "200m"
      memory: "256Mi"
    type: Pod
```

## AKS Monitoring Configuration

### 1. Azure Monitor for Containers
```yaml
# Azure Monitor for containers configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: azure-monitor-config
  namespace: interoperability-monitoring
data:
  config.yaml: |
    # Azure Monitor configuration
    azureMonitor:
      enabled: true
      workspaceId: "<log-analytics-workspace-id>"
      workspaceKey: "<log-analytics-workspace-key>"
    
    # Prometheus configuration
    prometheus:
      enabled: true
      url: "http://prometheus:9090"
    
    # Grafana configuration
    grafana:
      enabled: true
      url: "http://grafana:3000"
```

### 2. Application Insights Configuration
```yaml
# Application Insights configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: application-insights-config
  namespace: interoperability-monitoring
data:
  config.yaml: |
    # Application Insights configuration
    applicationInsights:
      enabled: true
      instrumentationKey: "<app-insights-key>"
      connectionString: "<app-insights-connection-string>"
    
    # OpenTelemetry configuration
    openTelemetry:
      enabled: true
      jaegerEndpoint: "http://jaeger:14268/api/traces"
      prometheusEndpoint: "http://prometheus:9090"
```

## AKS Security Configuration

### 1. Pod Security Standards
```yaml
# Pod Security Standards
apiVersion: v1
kind: Namespace
metadata:
  name: interoperability-core
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 2. RBAC Configuration
```yaml
# RBAC configuration
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: interoperability-admin
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["*"]
- apiGroups: ["apps"]
  resources: ["*"]
  verbs: ["*"]
- apiGroups: ["networking.k8s.io"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: interoperability-admin-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: interoperability-admin
subjects:
- kind: ServiceAccount
  name: interoperability-admin
  namespace: interoperability-core
```

## AKS Backup and Disaster Recovery

### 1. Backup Configuration
```yaml
# Backup configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: backup-config
  namespace: interoperability-core
data:
  backup.yaml: |
    # Backup configuration
    backup:
      enabled: true
      schedule: "0 2 * * *"  # Daily at 2 AM
      retention: "30d"
      storage:
        type: "azure"
        account: "bankinteroperabilitybackup"
        container: "aks-backups"
    
    # Disaster recovery
    disasterRecovery:
      enabled: true
      region: "westus2"
      replication: "async"
```

### 2. Disaster Recovery Scripts
```bash
#!/bin/bash
# scripts/backup/backup-aks.sh

echo "Starting AKS backup..."

# Backup cluster configuration
kubectl get all --all-namespaces -o yaml > aks-backup-$(date +%Y%m%d-%H%M%S).yaml

# Backup persistent volumes
kubectl get pv -o yaml > pv-backup-$(date +%Y%m%d-%H%M%S).yaml

# Backup secrets
kubectl get secrets --all-namespaces -o yaml > secrets-backup-$(date +%Y%m%d-%H%M%S).yaml

echo "AKS backup completed!"
```

## AKS Performance Optimization

### 1. Horizontal Pod Autoscaler
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: interoperability-gateway
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Vertical Pod Autoscaler
```yaml
# Vertical Pod Autoscaler
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-gateway-vpa
  namespace: interoperability-gateway
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: api-gateway
      minAllowed:
        cpu: "100m"
        memory: "128Mi"
      maxAllowed:
        cpu: "2"
        memory: "4Gi"
```

This completes the Azure Container Registry and AKS setup. The next step would be to configure Azure Key Vault and security.