# Azure Infrastructure Setup using Terraform

## Terraform Infrastructure Structure

### Directory Structure
```
infrastructure/
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
├── backend.tf
├── modules/
│   ├── aks/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── acr/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── key-vault/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── monitoring/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── networking/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    ├── dev/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── terraform.tfvars
    ├── staging/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── terraform.tfvars
    └── production/
        ├── main.tf
        ├── variables.tf
        └── terraform.tfvars
```

## Main Infrastructure Configuration

### 1. Backend Configuration (infrastructure/backend.tf)
```hcl
# infrastructure/backend.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "bank-terraform-state-rg"
    storage_account_name = "bankterraformstate"
    container_name       = "tfstate"
    key                  = "interoperability.tfstate"
  }
}
```

### 2. Main Configuration (infrastructure/main.tf)
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
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Data source for current client config
data "azurerm_client_config" "current" {}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
    CostCenter  = "IT-001"
    Owner       = "Bank IT Team"
  }
}

# Virtual Network
module "networking" {
  source = "./modules/networking"
  
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  vnet_name           = var.vnet_name
  address_space       = var.vnet_address_space
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Azure Container Registry
module "acr" {
  source = "./modules/acr"
  
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  acr_name            = var.acr_name
  acr_sku             = var.acr_sku
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Azure Key Vault
module "key_vault" {
  source = "./modules/key-vault"
  
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  key_vault_name      = var.key_vault_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  object_id            = data.azurerm_client_config.current.object_id
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Azure Kubernetes Service
module "aks" {
  source = "./modules/aks"
  
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  aks_name            = var.aks_name
  aks_dns_prefix      = var.aks_dns_prefix
  kubernetes_version  = var.kubernetes_version
  node_vm_size        = var.node_vm_size
  node_count          = var.node_count
  vnet_subnet_id      = module.networking.aks_subnet_id
  
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  
  tags = {
    Environment = var.environment
    Project     = "Bank Interoperability"
  }
}

# Monitoring
module "monitoring" {
  source = "./modules/monitoring"
  
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  log_analytics_name  = var.log_analytics_name
  app_insights_name   = var.app_insights_name
  
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
  administrator_password  = var.postgresql_admin_password
  
  sku_name   = var.postgresql_sku_name
  version    = var.postgresql_version
  storage_mb = var.postgresql_storage_mb
  
  backup_retention_days        = var.postgresql_backup_retention_days
  geo_redundant_backup_enabled = var.postgresql_geo_redundant_backup
  
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
  capacity            = var.redis_capacity
  family              = var.redis_family
  sku_name            = var.redis_sku_name
  enable_non_ssl_port = var.redis_enable_non_ssl_port
  minimum_tls_version = var.redis_minimum_tls_version
  
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

# Application Gateway
resource "azurerm_application_gateway" "main" {
  name                = var.app_gateway_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  
  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = var.app_gateway_capacity
  }
  
  gateway_ip_configuration {
    name      = "appGatewayIpConfig"
    subnet_id = module.networking.appgw_subnet_id
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
```

### 3. Variables (infrastructure/variables.tf)
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

# Networking variables
variable "vnet_name" {
  description = "Virtual network name"
  type        = string
  default     = "bank-interoperability-vnet"
}

variable "vnet_address_space" {
  description = "Virtual network address space"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

# ACR variables
variable "acr_name" {
  description = "Azure Container Registry name"
  type        = string
  default     = "bankregistry"
}

variable "acr_sku" {
  description = "Azure Container Registry SKU"
  type        = string
  default     = "Premium"
}

# Key Vault variables
variable "key_vault_name" {
  description = "Azure Key Vault name"
  type        = string
  default     = "bank-interoperability-kv"
}

# AKS variables
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

# Monitoring variables
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

# Database variables
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

variable "postgresql_sku_name" {
  description = "PostgreSQL SKU name"
  type        = string
  default     = "GP_Standard_D2s_v3"
}

variable "postgresql_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "13"
}

variable "postgresql_storage_mb" {
  description = "PostgreSQL storage in MB"
  type        = number
  default     = 32768
}

variable "postgresql_backup_retention_days" {
  description = "PostgreSQL backup retention days"
  type        = number
  default     = 7
}

variable "postgresql_geo_redundant_backup" {
  description = "PostgreSQL geo redundant backup"
  type        = bool
  default     = true
}

# Redis variables
variable "redis_name" {
  description = "Redis cache name"
  type        = string
  default     = "bank-interoperability-redis"
}

variable "redis_capacity" {
  description = "Redis capacity"
  type        = number
  default     = 1
}

variable "redis_family" {
  description = "Redis family"
  type        = string
  default     = "C"
}

variable "redis_sku_name" {
  description = "Redis SKU name"
  type        = string
  default     = "Standard"
}

variable "redis_enable_non_ssl_port" {
  description = "Redis enable non-SSL port"
  type        = bool
  default     = false
}

variable "redis_minimum_tls_version" {
  description = "Redis minimum TLS version"
  type        = string
  default     = "1.2"
}

# Cosmos DB variables
variable "cosmosdb_name" {
  description = "Cosmos DB account name"
  type        = string
  default     = "bank-interoperability-cosmos"
}

# Application Gateway variables
variable "app_gateway_name" {
  description = "Application Gateway name"
  type        = string
  default     = "bank-interoperability-appgw"
}

variable "app_gateway_capacity" {
  description = "Application Gateway capacity"
  type        = number
  default     = 2
}
```

### 4. Outputs (infrastructure/outputs.tf)
```hcl
# infrastructure/outputs.tf
output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Resource group location"
  value       = azurerm_resource_group.main.location
}

# AKS outputs
output "aks_name" {
  description = "AKS cluster name"
  value       = module.aks.aks_name
}

output "aks_fqdn" {
  description = "AKS cluster FQDN"
  value       = module.aks.aks_fqdn
}

output "aks_kube_config" {
  description = "AKS kube config"
  value       = module.aks.aks_kube_config
  sensitive   = true
}

# ACR outputs
output "acr_name" {
  description = "Azure Container Registry name"
  value       = module.acr.acr_name
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = module.acr.acr_login_server
}

# Key Vault outputs
output "key_vault_name" {
  description = "Azure Key Vault name"
  value       = module.key_vault.key_vault_name
}

output "key_vault_uri" {
  description = "Azure Key Vault URI"
  value       = module.key_vault.key_vault_uri
}

# Monitoring outputs
output "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID"
  value       = module.monitoring.log_analytics_workspace_id
}

output "application_insights_key" {
  description = "Application Insights instrumentation key"
  value       = module.monitoring.application_insights_key
}

output "application_insights_connection_string" {
  description = "Application Insights connection string"
  value       = module.monitoring.application_insights_connection_string
}

# Database outputs
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

# Networking outputs
output "vnet_name" {
  description = "Virtual network name"
  value       = module.networking.vnet_name
}

output "vnet_id" {
  description = "Virtual network ID"
  value       = module.networking.vnet_id
}

# Application Gateway outputs
output "app_gateway_name" {
  description = "Application Gateway name"
  value       = azurerm_application_gateway.main.name
}

output "app_gateway_public_ip" {
  description = "Application Gateway public IP"
  value       = azurerm_public_ip.appgw.ip_address
}
```

## Terraform Modules

### 1. AKS Module (infrastructure/modules/aks/main.tf)
```hcl
# infrastructure/modules/aks/main.tf
resource "azurerm_kubernetes_cluster" "main" {
  name                = var.aks_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.aks_dns_prefix
  kubernetes_version  = var.kubernetes_version
  
  default_node_pool {
    name                = "system"
    vm_size             = var.node_vm_size
    node_count          = var.node_count
    vnet_subnet_id      = var.vnet_subnet_id
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
      log_analytics_workspace_id = var.log_analytics_workspace_id
    }
    
    azure_policy {
      enabled = true
    }
  }
  
  tags = var.tags
}

# Get AKS credentials
data "azurerm_kubernetes_cluster" "main" {
  name                = azurerm_kubernetes_cluster.main.name
  resource_group_name = var.resource_group_name
  depends_on          = [azurerm_kubernetes_cluster.main]
}
```

### 2. ACR Module (infrastructure/modules/acr/main.tf)
```hcl
# infrastructure/modules/acr/main.tf
resource "azurerm_container_registry" "main" {
  name                = var.acr_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.acr_sku
  admin_enabled       = true
  
  identity {
    type = "SystemAssigned"
  }
  
  tags = var.tags
}
```

### 3. Key Vault Module (infrastructure/modules/key-vault/main.tf)
```hcl
# infrastructure/modules/key-vault/main.tf
resource "azurerm_key_vault" "main" {
  name                = var.key_vault_name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  sku_name           = "premium"
  
  access_policy {
    tenant_id = var.tenant_id
    object_id = var.object_id
    
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
  
  tags = var.tags
}
```

### 4. Monitoring Module (infrastructure/modules/monitoring/main.tf)
```hcl
# infrastructure/modules/monitoring/main.tf
# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  
  tags = var.tags
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = var.app_insights_name
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  
  tags = var.tags
}
```

### 5. Networking Module (infrastructure/modules/networking/main.tf)
```hcl
# infrastructure/modules/networking/main.tf
# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = var.vnet_name
  address_space       = var.address_space
  location            = var.location
  resource_group_name = var.resource_group_name
  
  tags = var.tags
}

# Subnet for AKS
resource "azurerm_subnet" "aks_subnet" {
  name                 = "aks-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Subnet for Application Gateway
resource "azurerm_subnet" "appgw_subnet" {
  name                 = "appgw-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Network Security Group for AKS
resource "azurerm_network_security_group" "aks_nsg" {
  name                = "aks-nsg"
  location            = var.location
  resource_group_name = var.resource_group_name
  
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
  
  tags = var.tags
}
```

## Environment-Specific Configurations

### 1. Development Environment (infrastructure/environments/dev/terraform.tfvars)
```hcl
# infrastructure/environments/dev/terraform.tfvars
environment = "development"
location = "East US"
resource_group_name = "bank-interoperability-dev-rg"

# AKS configuration
aks_name = "bank-interoperability-dev-aks"
aks_dns_prefix = "bank-interop-dev"
node_count = 2
node_vm_size = "Standard_D2s_v3"

# Database configuration
postgresql_name = "bank-interoperability-dev-postgres"
postgresql_sku_name = "GP_Standard_D2s_v3"
postgresql_storage_mb = 16384

# Redis configuration
redis_name = "bank-interoperability-dev-redis"
redis_sku_name = "Basic"
redis_capacity = 0

# Cosmos DB configuration
cosmosdb_name = "bank-interoperability-dev-cosmos"

# Application Gateway configuration
app_gateway_name = "bank-interoperability-dev-appgw"
app_gateway_capacity = 1
```

### 2. Production Environment (infrastructure/environments/production/terraform.tfvars)
```hcl
# infrastructure/environments/production/terraform.tfvars
environment = "production"
location = "East US"
resource_group_name = "bank-interoperability-rg"

# AKS configuration
aks_name = "bank-interoperability-aks"
aks_dns_prefix = "bank-interop"
node_count = 3
node_vm_size = "Standard_D4s_v3"

# Database configuration
postgresql_name = "bank-interoperability-postgres"
postgresql_sku_name = "GP_Standard_D4s_v3"
postgresql_storage_mb = 32768

# Redis configuration
redis_name = "bank-interoperability-redis"
redis_sku_name = "Standard"
redis_capacity = 1

# Cosmos DB configuration
cosmosdb_name = "bank-interoperability-cosmos"

# Application Gateway configuration
app_gateway_name = "bank-interoperability-appgw"
app_gateway_capacity = 2
```

## Deployment Scripts

### 1. Infrastructure Deployment Script (scripts/deployment/deploy-infrastructure.sh)
```bash
#!/bin/bash
# scripts/deployment/deploy-infrastructure.sh

set -e

echo "Deploying Azure infrastructure for Bank Interoperability Layer..."

# Set environment
ENVIRONMENT=${1:-production}
echo "Deploying to environment: $ENVIRONMENT"

# Change to infrastructure directory
cd infrastructure

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Plan deployment
echo "Planning deployment..."
terraform plan -var-file="environments/$ENVIRONMENT/terraform.tfvars" -out="tfplan"

# Apply deployment
echo "Applying deployment..."
terraform apply "tfplan"

# Get outputs
echo "Getting deployment outputs..."
terraform output -json > "../outputs/$ENVIRONMENT-outputs.json"

echo "Infrastructure deployment completed successfully!"
```

### 2. Infrastructure Cleanup Script (scripts/deployment/cleanup-infrastructure.sh)
```bash
#!/bin/bash
# scripts/deployment/cleanup-infrastructure.sh

set -e

echo "Cleaning up Azure infrastructure for Bank Interoperability Layer..."

# Set environment
ENVIRONMENT=${1:-production}
echo "Cleaning up environment: $ENVIRONMENT"

# Change to infrastructure directory
cd infrastructure

# Plan destruction
echo "Planning destruction..."
terraform plan -destroy -var-file="environments/$ENVIRONMENT/terraform.tfvars" -out="destroy.tfplan"

# Apply destruction
echo "Applying destruction..."
terraform apply "destroy.tfplan"

echo "Infrastructure cleanup completed successfully!"
```

This completes the Azure infrastructure setup using Terraform. The next step would be to configure the Azure DevOps pipelines.