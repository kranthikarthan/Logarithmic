# Azure Infrastructure Configuration for Bank Interoperability Layer

## Azure Resource Architecture

### Resource Group Structure
```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Resource Groups                        │
├─────────────────────────────────────────────────────────────────┤
│ bank-interoperability-rg (Production)                           │
│ ├── AKS Cluster: bank-interoperability-aks                      │
│ ├── ACR: bankregistry                                          │
│ ├── Key Vault: bank-interoperability-kv                        │
│ ├── Storage: bankinteroperabilitystorage                       │
│ └── Monitor: bank-interoperability-monitor                      │
├─────────────────────────────────────────────────────────────────┤
│ bank-interoperability-dev-rg (Development)                     │
│ ├── AKS Cluster: bank-interoperability-dev-aks                  │
│ ├── ACR: bankregistry                                          │
│ ├── Key Vault: bank-interoperability-dev-kv                    │
│ └── Storage: bankinteroperabilitydevstorage                    │
└─────────────────────────────────────────────────────────────────┘
```

## Terraform Infrastructure as Code

### 1. Main Infrastructure (infrastructure/main.tf)
```hcl
# infrastructure/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }
  
  backend "azurerm" {
    resource_group_name  = "bank-terraform-state-rg"
    storage_account_name = "bankterraformstate"
    container_name       = "tfstate"
    key                  = "interoperability.tfstate"
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
    CostCenter  = "IT-001"
  }
}

# Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Premium"
  admin_enabled       = true
  
  identity {
    type = "SystemAssigned"
  }
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Azure Key Vault
resource "azurerm_key_vault" "kv" {
  name                = var.key_vault_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name           = "premium"
  
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    
    key_permissions = [
      "Get", "List", "Create", "Delete", "Update", "Import", "Backup", "Restore", "Recover"
    ]
    
    secret_permissions = [
      "Get", "List", "Set", "Delete", "Backup", "Restore", "Recover"
    ]
    
    certificate_permissions = [
      "Get", "List", "Create", "Delete", "Update", "Import", "Backup", "Restore", "Recover"
    ]
  }
  
  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Azure Kubernetes Service
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.aks_dns_prefix
  kubernetes_version  = var.kubernetes_version
  
  default_node_pool {
    name                = "system"
    vm_size             = var.node_vm_size
    node_count          = var.node_count
    vnet_subnet_id      = azurerm_subnet.aks_subnet.id
    enable_auto_scaling = true
    min_count           = 1
    max_count           = 10
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = "10.1.0.0/16"
    dns_service_ip    = "10.1.0.10"
  }
  
  addon_profile {
    oms_agent {
      enabled                    = true
      log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
    }
    
    azure_policy {
      enabled = true
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = var.app_insights_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = var.vnet_name
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Subnet for AKS
resource "azurerm_subnet" "aks_subnet" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Subnet for Application Gateway
resource "azurerm_subnet" "appgw_subnet" {
  name                 = "appgw-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Application Gateway
resource "azurerm_application_gateway" "main" {
  name                = var.app_gateway_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  
  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }
  
  gateway_ip_configuration {
    name      = "appGatewayIpConfig"
    subnet_id = azurerm_subnet.appgw_subnet.id
  }
  
  frontend_port {
    name = "frontendPort"
    port = 80
  }
  
  frontend_ip_configuration {
    name                 = "frontendIP"
    public_ip_address_id = azurerm_public_ip.appgw.id
  }
  
  backend_address_pool {
    name = "backendPool"
  }
  
  backend_http_settings {
    name                  = "backendSettings"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 60
  }
  
  http_listener {
    name                           = "listener"
    frontend_ip_configuration_name = "frontendIP"
    frontend_port_name             = "frontendPort"
    protocol                       = "Http"
  }
  
  request_routing_rule {
    name                       = "routingRule"
    rule_type                  = "Basic"
    http_listener_name         = "listener"
    backend_address_pool_name  = "backendPool"
    backend_http_settings_name = "backendSettings"
    priority                   = 100
  }
  
  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Public IP for Application Gateway
resource "azurerm_public_ip" "appgw" {
  name                = "appgw-public-ip"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
  sku                 = "Standard"
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Azure Database for PostgreSQL
resource "azurerm_postgresql_flexible_server" "main" {
  name                = var.postgresql_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  
  administrator_login    = var.postgresql_admin_login
  administrator_password = var.postgresql_admin_password
  
  sku_name   = "GP_Standard_D2s_v3"
  version    = "13"
  storage_mb = 32768
  
  backup_retention_days        = 7
  geo_redundant_backup_enabled = true
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Azure Cache for Redis
resource "azurerm_redis_cache" "main" {
  name                = var.redis_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 1
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Azure Cosmos DB
resource "azurerm_cosmosdb_account" "main" {
  name                = var.cosmosdb_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  
  consistency_policy {
    consistency_level = "Session"
  }
  
  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
  
  capabilities {
    name = "EnableCassandra"
  }
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Data source for current client config
data "azurerm_client_config" "current" {}
```

### 2. Variables (infrastructure/variables.tf)
```hcl
# infrastructure/variables.tf
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
  default     = "bank-interoperability-rg"
}

variable "acr_name" {
  description = "Azure Container Registry name"
  type        = string
  default     = "bankregistry"
}

variable "key_vault_name" {
  description = "Azure Key Vault name"
  type        = string
  default     = "bank-interoperability-kv"
}

variable "aks_name" {
  description = "AKS cluster name"
  type        = string
  default     = "bank-interoperability-aks"
}

variable "aks_dns_prefix" {
  description = "AKS DNS prefix"
  type        = string
  default     = "bank-interop"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.27"
}

variable "node_vm_size" {
  description = "Node VM size"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "node_count" {
  description = "Number of nodes"
  type        = number
  default     = 3
}

variable "log_analytics_name" {
  description = "Log Analytics workspace name"
  type        = string
  default     = "bank-interoperability-logs"
}

variable "app_insights_name" {
  description = "Application Insights name"
  type        = string
  default     = "bank-interoperability-insights"
}

variable "vnet_name" {
  description = "Virtual network name"
  type        = string
  default     = "bank-interoperability-vnet"
}

variable "app_gateway_name" {
  description = "Application Gateway name"
  type        = string
  default     = "bank-interoperability-appgw"
}

variable "postgresql_name" {
  description = "PostgreSQL server name"
  type        = string
  default     = "bank-interoperability-postgres"
}

variable "postgresql_admin_login" {
  description = "PostgreSQL admin login"
  type        = string
  default     = "postgresadmin"
}

variable "postgresql_admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "redis_name" {
  description = "Redis cache name"
  type        = string
  default     = "bank-interoperability-redis"
}

variable "cosmosdb_name" {
  description = "Cosmos DB account name"
  type        = string
  default     = "bank-interoperability-cosmos"
}
```

### 3. Outputs (infrastructure/outputs.tf)
```hcl
# infrastructure/outputs.tf
output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "aks_name" {
  description = "AKS cluster name"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "aks_fqdn" {
  description = "AKS cluster FQDN"
  value       = azurerm_kubernetes_cluster.aks.fqdn
}

output "acr_name" {
  description = "Azure Container Registry name"
  value       = azurerm_container_registry.acr.name
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = azurerm_container_registry.acr.login_server
}

output "key_vault_name" {
  description = "Azure Key Vault name"
  value       = azurerm_key_vault.kv.name
}

output "key_vault_uri" {
  description = "Azure Key Vault URI"
  value       = azurerm_key_vault.kv.vault_uri
}

output "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID"
  value       = azurerm_log_analytics_workspace.main.id
}

output "application_insights_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.main.instrumentation_key
}

output "application_insights_connection_string" {
  description = "Application Insights connection string"
  value       = azurerm_application_insights.main.connection_string
}

output "postgresql_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "redis_hostname" {
  description = "Redis cache hostname"
  value       = azurerm_redis_cache.main.hostname
}

output "cosmosdb_endpoint" {
  description = "Cosmos DB endpoint"
  value       = azurerm_cosmosdb_account.main.endpoint
}
```

## Azure DevOps Service Connections

### 1. Azure Service Connection
```yaml
# Azure service connection configuration
name: Bank-Azure-Subscription
type: AzureRM
subscriptionId: <subscription-id>
subscriptionName: Bank Azure Subscription
resourceGroupName: bank-interoperability-rg
```

### 2. Container Registry Service Connection
```yaml
# Container registry service connection
name: Bank-Container-Registry
type: DockerRegistry
registry: bankregistry.azurecr.io
username: <acr-username>
password: <acr-password>
```

### 3. Azure Key Vault Service Connection
```yaml
# Key Vault service connection
name: Bank-Key-Vault
type: AzureKeyVault
vaultName: bank-interoperability-kv
resourceGroupName: bank-interoperability-rg
```

## Azure Monitor Configuration

### 1. Log Analytics Workspace
```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group bank-interoperability-rg \
  --workspace-name bank-interoperability-logs \
  --location eastus
```

### 2. Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
  --resource-group bank-interoperability-rg \
  --app bank-interoperability-insights \
  --location eastus \
  --kind web
```

### 3. Azure Monitor Alerts
```yaml
# Azure Monitor alert configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: azure-monitor-alerts
  namespace: interoperability-monitoring
data:
  alert-rules.yaml: |
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
    
    - alert: HighResponseTime
      expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High response time detected"
```

## Azure Security Configuration

### 1. Azure Security Center
```bash
# Enable Security Center
az security pricing create \
  --name "VirtualMachines" \
  --tier "Standard"
```

### 2. Azure Policy
```yaml
# Azure Policy for compliance
apiVersion: v1
kind: ConfigMap
metadata:
  name: azure-policy-config
  namespace: interoperability-security
data:
  policy-rules.yaml: |
    - name: "Require HTTPS"
      description: "Require HTTPS for all services"
      rules:
        - apiVersion: networking.istio.io/v1beta1
          kind: VirtualService
          spec:
            http:
              - match:
                  - port: 80
                redirect:
                  uri: "https://"
                  authority: "{{ .Host }}"
```

### 3. Network Security Groups
```hcl
# Network Security Group for AKS
resource "azurerm_network_security_group" "aks_nsg" {
  name                = "aks-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "AllowHTTP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}
```

This comprehensive Azure infrastructure configuration provides a complete foundation for your bank interoperability layer with enterprise-grade security, monitoring, and scalability.