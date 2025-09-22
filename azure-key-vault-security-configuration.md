# Azure Key Vault and Security Configuration for Bank Interoperability Layer

## Azure Key Vault Setup

### 1. Key Vault Creation and Configuration
```bash
# Create Azure Key Vault
az keyvault create \
  --name bank-interoperability-kv \
  --resource-group bank-interoperability-rg \
  --location eastus \
  --sku premium \
  --enable-rbac-authorization true \
  --enable-soft-delete true \
  --soft-delete-retention-days 90 \
  --enable-purge-protection true

# Enable access logging
az monitor diagnostic-settings create \
  --name "KeyVaultAccessLogs" \
  --resource "/subscriptions/<subscription-id>/resourceGroups/bank-interoperability-rg/providers/Microsoft.KeyVault/vaults/bank-interoperability-kv" \
  --logs '[{"category": "AuditEvent", "enabled": true}]' \
  --workspace "/subscriptions/<subscription-id>/resourceGroups/bank-interoperability-rg/providers/Microsoft.OperationalInsights/workspaces/bank-interoperability-logs"
```

### 2. Key Vault Access Policies
```yaml
# Key Vault access policies
apiVersion: v1
kind: ConfigMap
metadata:
  name: key-vault-access-policies
  namespace: interoperability-security
data:
  access-policies.yaml: |
    # Service Principal access
    servicePrincipal:
      objectId: "<service-principal-object-id>"
      permissions:
        keys: ["Get", "List", "Create", "Delete", "Update", "Import", "Backup", "Restore", "Recover"]
        secrets: ["Get", "List", "Set", "Delete", "Backup", "Restore", "Recover"]
        certificates: ["Get", "List", "Create", "Delete", "Update", "Import", "Backup", "Restore", "Recover"]
    
    # AKS managed identity access
    aksIdentity:
      objectId: "<aks-managed-identity-object-id>"
      permissions:
        secrets: ["Get", "List"]
        keys: ["Get", "List"]
    
    # DevOps service connection access
    devopsService:
      objectId: "<devops-service-connection-object-id>"
      permissions:
        secrets: ["Get", "List"]
        keys: ["Get", "List"]
```

### 3. Key Vault Secrets Management
```bash
# Create secrets in Key Vault
az keyvault secret set \
  --vault-name bank-interoperability-kv \
  --name "postgresql-admin-password" \
  --value "$(openssl rand -base64 32)"

az keyvault secret set \
  --vault-name bank-interoperability-kv \
  --name "redis-access-key" \
  --value "$(openssl rand -base64 32)"

az keyvault secret set \
  --vault-name bank-interoperability-kv \
  --name "cosmosdb-primary-key" \
  --value "$(openssl rand -base64 32)"

az keyvault secret set \
  --vault-name bank-interoperability-kv \
  --name "jwt-secret" \
  --value "$(openssl rand -base64 64)"

az keyvault secret set \
  --vault-name bank-interoperability-kv \
  --name "encryption-key" \
  --value "$(openssl rand -base64 32)"

# Create certificates
az keyvault certificate create \
  --vault-name bank-interoperability-kv \
  --name "bank-interoperability-tls" \
  --policy @certificate-policy.json
```

## Azure Active Directory Integration

### 1. Azure AD Application Registration
```bash
# Create Azure AD application
az ad app create \
  --display-name "Bank Interoperability Layer" \
  --identifier-uris "https://api.bank.com/interoperability" \
  --reply-urls "https://api.bank.com/auth/callback" \
  --required-resource-accesses @app-permissions.json

# Create service principal
az ad sp create --id <app-id>

# Assign roles
az role assignment create \
  --assignee <service-principal-id> \
  --role "Key Vault Secrets User" \
  --scope "/subscriptions/<subscription-id>/resourceGroups/bank-interoperability-rg/providers/Microsoft.KeyVault/vaults/bank-interoperability-kv"
```

### 2. OAuth2/OIDC Configuration
```yaml
# OAuth2/OIDC configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: oauth2-config
  namespace: interoperability-security
data:
  oauth2-config.yaml: |
    # OAuth2 configuration
    oauth2:
      enabled: true
      issuer: "https://login.microsoftonline.com/<tenant-id>/v2.0"
      clientId: "<client-id>"
      clientSecret: "<client-secret>"
      scopes:
        - "openid"
        - "profile"
        - "email"
        - "banking:read"
        - "banking:write"
        - "banking:admin"
    
    # JWT configuration
    jwt:
      enabled: true
      secret: "<jwt-secret>"
      expiration: "3600"  # 1 hour
      refreshExpiration: "86400"  # 24 hours
      algorithm: "HS256"
    
    # RBAC configuration
    rbac:
      enabled: true
      roles:
        - name: "admin"
          permissions: ["*"]
        - name: "user"
          permissions: ["banking:read", "banking:write"]
        - name: "viewer"
          permissions: ["banking:read"]
```

## Istio Security Configuration

### 1. Istio Security Policies
```yaml
# Istio security policies
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: bank-interoperability-mtls
  namespace: interoperability-core
spec:
  mtls:
    mode: STRICT
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: bank-interoperability-rbac
  namespace: interoperability-core
spec:
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/interoperability-gateway/sa/gateway-service"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/process"]
  - from:
    - source:
        principals: ["cluster.local/ns/interoperability-gateway/sa/gateway-service"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/health"]
```

### 2. Istio Request Authentication
```yaml
# Istio request authentication
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: bank-interoperability-jwt
  namespace: interoperability-core
spec:
  jwtRules:
  - issuer: "https://login.microsoftonline.com/<tenant-id>/v2.0"
    jwksUri: "https://login.microsoftonline.com/<tenant-id>/discovery/v2.0/keys"
    audiences:
    - "api://bank-interoperability"
    - "https://api.bank.com/interoperability"
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: bank-interoperability-jwt-rbac
  namespace: interoperability-core
spec:
  rules:
  - from:
    - source:
        requestPrincipals: ["*"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/process"]
    when:
    - key: request.auth.claims[aud]
      values: ["api://bank-interoperability"]
```

## Network Security Configuration

### 1. Network Security Groups
```yaml
# Network Security Groups
apiVersion: v1
kind: ConfigMap
metadata:
  name: network-security-groups
  namespace: interoperability-security
data:
  nsg-rules.yaml: |
    # AKS NSG rules
    aks-nsg:
      name: "aks-nsg"
      rules:
        - name: "AllowHTTPS"
          priority: 100
          direction: "Inbound"
          access: "Allow"
          protocol: "Tcp"
          sourcePortRange: "*"
          destinationPortRange: "443"
          sourceAddressPrefix: "*"
          destinationAddressPrefix: "*"
        
        - name: "AllowHTTP"
          priority: 110
          direction: "Inbound"
          access: "Allow"
          protocol: "Tcp"
          sourcePortRange: "*"
          destinationPortRange: "80"
          sourceAddressPrefix: "*"
          destinationAddressPrefix: "*"
        
        - name: "AllowSSH"
          priority: 120
          direction: "Inbound"
          access: "Allow"
          protocol: "Tcp"
          sourcePortRange: "*"
          destinationPortRange: "22"
          sourceAddressPrefix: "10.0.0.0/16"
          destinationAddressPrefix: "*"
        
        - name: "DenyAllInbound"
          priority: 1000
          direction: "Inbound"
          access: "Deny"
          protocol: "*"
          sourcePortRange: "*"
          destinationPortRange: "*"
          sourceAddressPrefix: "*"
          destinationAddressPrefix: "*"
```

### 2. Application Gateway Security
```yaml
# Application Gateway security configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-gateway-security
  namespace: interoperability-security
data:
  security-config.yaml: |
    # WAF configuration
    waf:
      enabled: true
      mode: "Prevention"
      ruleSetType: "OWASP"
      ruleSetVersion: "3.2"
      disabledRuleGroups:
        - ruleGroupName: "REQUEST-942-APPLICATION-ATTACK-SQLI"
          rules: []
    
    # SSL/TLS configuration
    ssl:
      enabled: true
      protocol: "TLSv1_2"
      cipherSuites:
        - "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
        - "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
    
    # Rate limiting
    rateLimiting:
      enabled: true
      requestsPerMinute: 1000
      burstSize: 100
```

## Kubernetes Security Configuration

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
---
apiVersion: v1
kind: Namespace
metadata:
  name: interoperability-gateway
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 2. Security Context Constraints
```yaml
# Security Context Constraints
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-context-constraints
  namespace: interoperability-security
data:
  scc.yaml: |
    # Security context constraints
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      runAsGroup: 1000
      fsGroup: 1000
      seccompProfile:
        type: RuntimeDefault
      capabilities:
        drop:
          - ALL
        add:
          - NET_BIND_SERVICE
    
    # Pod security context
    podSecurityContext:
      runAsNonRoot: true
      runAsUser: 1000
      runAsGroup: 1000
      fsGroup: 1000
      seccompProfile:
        type: RuntimeDefault
```

### 3. Network Policies
```yaml
# Network policies for security
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: interoperability-security-policy
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
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: interoperability-events
    - namespaceSelector:
        matchLabels:
          name: interoperability-monitoring
    ports:
    - protocol: TCP
      port: 9090
    - protocol: TCP
      port: 14268
```

## Azure Security Center Configuration

### 1. Security Center Policies
```yaml
# Security Center policies
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-center-policies
  namespace: interoperability-security
data:
  policies.yaml: |
    # Security Center policies
    securityCenter:
      enabled: true
      pricingTier: "Standard"
      autoProvisioning:
        logAnalyticsAgent: true
        vulnerabilityAssessment: true
        securityAgent: true
      
      # Security recommendations
      recommendations:
        - name: "Enable Azure Defender for Kubernetes"
          status: "Enabled"
        - name: "Enable Azure Defender for Container Registries"
          status: "Enabled"
        - name: "Enable Azure Defender for Key Vault"
          status: "Enabled"
        - name: "Enable Azure Defender for Storage"
          status: "Enabled"
```

### 2. Security Alerts Configuration
```yaml
# Security alerts configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-alerts
  namespace: interoperability-security
data:
  alerts.yaml: |
    # Security alerts
    alerts:
      - name: "Suspicious Activity Detected"
        severity: "High"
        description: "Unusual activity detected in the system"
        actions:
          - "Send email notification"
          - "Create incident ticket"
          - "Block suspicious IP"
      
      - name: "Failed Authentication Attempts"
        severity: "Medium"
        description: "Multiple failed authentication attempts"
        actions:
          - "Send email notification"
          - "Log security event"
      
      - name: "Privilege Escalation Attempt"
        severity: "Critical"
        description: "Attempted privilege escalation detected"
        actions:
          - "Send immediate alert"
          - "Block user account"
          - "Create incident ticket"
```

## Compliance and Audit Configuration

### 1. Audit Logging
```yaml
# Audit logging configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: audit-logging
  namespace: interoperability-security
data:
  audit-config.yaml: |
    # Audit logging
    audit:
      enabled: true
      logLevel: "INFO"
      destinations:
        - "Azure Monitor"
        - "Log Analytics"
        - "Azure Storage"
      
      # Audit events
      events:
        - "Authentication"
        - "Authorization"
        - "Data Access"
        - "Configuration Changes"
        - "Security Events"
      
      # Retention
      retention:
        days: 90
        archive: true
```

### 2. Compliance Reporting
```yaml
# Compliance reporting configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: compliance-reporting
  namespace: interoperability-security
data:
  compliance.yaml: |
    # Compliance reporting
    compliance:
      enabled: true
      standards:
        - "PCI DSS"
        - "SOX"
        - "GDPR"
        - "HIPAA"
      
      # Reporting schedule
      reports:
        - name: "Security Assessment"
          frequency: "Monthly"
          format: "PDF"
        - name: "Compliance Report"
          frequency: "Quarterly"
          format: "Excel"
        - name: "Audit Report"
          frequency: "Annually"
          format: "PDF"
```

## Security Monitoring and Alerting

### 1. Security Monitoring Dashboard
```yaml
# Security monitoring dashboard
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-monitoring
  namespace: interoperability-security
data:
  dashboard.yaml: |
    # Security monitoring dashboard
    dashboard:
      title: "Bank Interoperability Security Dashboard"
      panels:
        - title: "Security Events"
          type: "graph"
          query: "security_events_total"
        - title: "Failed Logins"
          type: "stat"
          query: "failed_logins_total"
        - title: "Active Threats"
          type: "table"
          query: "active_threats"
        - title: "Compliance Status"
          type: "gauge"
          query: "compliance_score"
```

### 2. Security Alerting Rules
```yaml
# Security alerting rules
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-alerting
  namespace: interoperability-security
data:
  alerting.yaml: |
    # Security alerting rules
    alerting:
      rules:
        - name: "High Security Risk"
          condition: "security_risk_score > 8"
          severity: "Critical"
          actions:
            - "Send email"
            - "Create incident"
            - "Block access"
        
        - name: "Multiple Failed Logins"
          condition: "failed_logins > 5"
          severity: "High"
          actions:
            - "Send email"
            - "Log event"
        
        - name: "Unusual Activity"
          condition: "unusual_activity_detected"
          severity: "Medium"
          actions:
            - "Send notification"
            - "Log event"
```

## Security Testing and Validation

### 1. Security Testing Scripts
```bash
#!/bin/bash
# scripts/security/security-test.sh

echo "Running security tests..."

# Test Key Vault access
echo "Testing Key Vault access..."
az keyvault secret list --vault-name bank-interoperability-kv

# Test network connectivity
echo "Testing network connectivity..."
kubectl get networkpolicies --all-namespaces

# Test RBAC
echo "Testing RBAC..."
kubectl auth can-i create pods --as=system:serviceaccount:interoperability-core:default

# Test security contexts
echo "Testing security contexts..."
kubectl get pods -o jsonpath='{.items[*].spec.securityContext}' --all-namespaces

echo "Security tests completed!"
```

### 2. Vulnerability Scanning
```yaml
# Vulnerability scanning configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: vulnerability-scanning
  namespace: interoperability-security
data:
  scanning.yaml: |
    # Vulnerability scanning
    vulnerabilityScanning:
      enabled: true
      schedule: "0 2 * * *"  # Daily at 2 AM
      tools:
        - "Trivy"
        - "Snyk"
        - "Clair"
      
      # Scan targets
      targets:
        - "Container images"
        - "Dependencies"
        - "Infrastructure"
        - "Configuration files"
      
      # Reporting
      reporting:
        format: "JSON"
        destination: "Azure Monitor"
        retention: "30 days"
```

This completes the Azure Key Vault and security configuration. The next step would be to set up Azure Monitor and Application Insights.