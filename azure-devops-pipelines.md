# Azure DevOps Pipelines for Bank Interoperability Layer

## Azure DevOps Pipeline Architecture

### Pipeline Structure
```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure DevOps Pipeline Structure              │
├─────────────────────────────────────────────────────────────────┤
│ Build Pipeline → Test Pipeline → Security Scan → Deploy Pipeline│
│     ↓              ↓              ↓              ↓                │
│  Artifacts → Unit Tests → SAST/DAST → AKS Deployment           │
│     ↓              ↓              ↓              ↓                │
│  Container → Integration → Security → Monitoring                │
│  Registry      Tests       Gates      Setup                     │
└─────────────────────────────────────────────────────────────────┘
```

## Azure DevOps Pipeline YAML Files

### 1. Main Build Pipeline (azure-pipelines.yml)
```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
    - main
    - develop
    - feature/*
  paths:
    exclude:
    - README.md
    - docs/*

variables:
  buildConfiguration: 'Release'
  dockerRegistry: 'bankregistry.azurecr.io'
  imageRepository: 'bank-interoperability'
  containerRegistry: 'bankregistry.azurecr.io'
  dockerfilePath: '$(Build.SourcesDirectory)/Dockerfile'
  tag: '$(Build.BuildId)'
  vmImageName: 'ubuntu-latest'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: Build
    displayName: 'Build'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: Docker@2
      displayName: 'Build and push image'
      inputs:
        command: buildAndPush
        repository: $(imageRepository)
        dockerfile: $(dockerfilePath)
        containerRegistry: $(containerRegistry)
        tags: |
          $(tag)
          latest

    - task: PublishBuildArtifacts@1
      displayName: 'Publish Artifacts'
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)'
        ArtifactName: 'drop'
        publishLocation: 'Container'

- stage: Test
  displayName: 'Test'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - job: UnitTests
    displayName: 'Unit Tests'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: Maven@3
      displayName: 'Run Unit Tests'
      inputs:
        mavenPomFile: 'pom.xml'
        goals: 'test'
        publishJUnitResults: true
        testResultsFiles: '**/surefire-reports/TEST-*.xml'

  - job: IntegrationTests
    displayName: 'Integration Tests'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: Maven@3
      displayName: 'Run Integration Tests'
      inputs:
        mavenPomFile: 'pom.xml'
        goals: 'verify'
        publishJUnitResults: true
        testResultsFiles: '**/failsafe-reports/TEST-*.xml'

- stage: Security
  displayName: 'Security Scan'
  dependsOn: Test
  condition: succeeded()
  jobs:
  - job: SecurityScan
    displayName: 'Security Scan'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: SonarCloudPrepare@1
      displayName: 'Prepare SonarCloud analysis'
      inputs:
        SonarCloud: 'BankInteroperability'
        organization: 'bank-org'
        scannerMode: 'Other'

    - task: SonarCloudAnalyze@1
      displayName: 'Run SonarCloud analysis'

    - task: SonarCloudPublish@1
      displayName: 'Publish SonarCloud results'

    - task: SnykSecurityScan@1
      displayName: 'Snyk Security Scan'
      inputs:
        serviceConnectionEndpoint: 'SnykServiceConnection'
        testType: 'app'
        severityThreshold: 'high'

- stage: Deploy
  displayName: 'Deploy to AKS'
  dependsOn: Security
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToAKS
    displayName: 'Deploy to AKS'
    environment: 'production'
    pool:
      vmImage: $(vmImageName)
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            displayName: 'Deploy to AKS'
            inputs:
              azureSubscription: 'Bank-Azure-Subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                # Deploy to AKS
                az aks get-credentials --resource-group bank-interoperability-rg --name bank-interoperability-aks
                helm upgrade --install interoperability ./helm-charts/interoperability --namespace interoperability-core
```

### 2. Feature Branch Pipeline (feature-pipeline.yml)
```yaml
# feature-pipeline.yml
trigger:
  branches:
    include:
    - feature/*
  paths:
    exclude:
    - README.md
    - docs/*

variables:
  buildConfiguration: 'Debug'
  dockerRegistry: 'bankregistry.azurecr.io'
  imageRepository: 'bank-interoperability'
  containerRegistry: 'bankregistry.azurecr.io'
  dockerfilePath: '$(Build.SourcesDirectory)/Dockerfile'
  tag: '$(Build.BuildId)-$(Build.SourceBranchName)'
  vmImageName: 'ubuntu-latest'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: Build
    displayName: 'Build'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: Docker@2
      displayName: 'Build and push image'
      inputs:
        command: buildAndPush
        repository: $(imageRepository)
        dockerfile: $(dockerfilePath)
        containerRegistry: $(containerRegistry)
        tags: |
          $(tag)
          latest

- stage: Test
  displayName: 'Test'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - job: UnitTests
    displayName: 'Unit Tests'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: Maven@3
      displayName: 'Run Unit Tests'
      inputs:
        mavenPomFile: 'pom.xml'
        goals: 'test'
        publishJUnitResults: true
        testResultsFiles: '**/surefire-reports/TEST-*.xml'

- stage: Deploy
  displayName: 'Deploy to Dev AKS'
  dependsOn: Test
  condition: succeeded()
  jobs:
  - deployment: DeployToDevAKS
    displayName: 'Deploy to Dev AKS'
    environment: 'development'
    pool:
      vmImage: $(vmImageName)
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            displayName: 'Deploy to Dev AKS'
            inputs:
              azureSubscription: 'Bank-Azure-Subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                # Deploy to Dev AKS
                az aks get-credentials --resource-group bank-interoperability-dev-rg --name bank-interoperability-dev-aks
                helm upgrade --install interoperability ./helm-charts/interoperability --namespace interoperability-dev --set image.tag=$(tag)
```

### 3. Infrastructure Pipeline (infrastructure-pipeline.yml)
```yaml
# infrastructure-pipeline.yml
trigger:
  branches:
    include:
    - main
  paths:
    include:
    - infrastructure/*

variables:
  vmImageName: 'ubuntu-latest'
  terraformVersion: '1.5.0'

stages:
- stage: Plan
  displayName: 'Terraform Plan'
  jobs:
  - job: Plan
    displayName: 'Plan Infrastructure'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: TerraformInstaller@0
      displayName: 'Install Terraform'
      inputs:
        terraformVersion: $(terraformVersion)

    - task: TerraformTaskV3@3
      displayName: 'Terraform Plan'
      inputs:
        provider: 'azurerm'
        command: 'plan'
        workingDirectory: '$(Build.SourcesDirectory)/infrastructure'
        environmentServiceNameAzureRM: 'Bank-Azure-Subscription'

- stage: Deploy
  displayName: 'Deploy Infrastructure'
  dependsOn: Plan
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployInfrastructure
    displayName: 'Deploy Infrastructure'
    environment: 'production'
    pool:
      vmImage: $(vmImageName)
    strategy:
      runOnce:
        deploy:
          steps:
          - task: TerraformInstaller@0
            displayName: 'Install Terraform'
            inputs:
              terraformVersion: $(terraformVersion)

          - task: TerraformTaskV3@3
            displayName: 'Terraform Apply'
            inputs:
              provider: 'azurerm'
              command: 'apply'
              workingDirectory: '$(Build.SourcesDirectory)/infrastructure'
              environmentServiceNameAzureRM: 'Bank-Azure-Subscription'
```

## Azure-Specific Infrastructure Configuration

### 1. Azure Resource Group Setup
```bash
# Create resource groups
az group create --name bank-interoperability-rg --location eastus
az group create --name bank-interoperability-dev-rg --location eastus
az group create --name bank-interoperability-staging-rg --location eastus
```

### 2. Azure Container Registry
```bash
# Create Azure Container Registry
az acr create --resource-group bank-interoperability-rg --name bankregistry --sku Premium --admin-enabled true

# Get ACR credentials
az acr credential show --name bankregistry
```

### 3. Azure Kubernetes Service (AKS)
```bash
# Create AKS cluster
az aks create \
  --resource-group bank-interoperability-rg \
  --name bank-interoperability-aks \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --enable-managed-identity \
  --attach-acr bankregistry
```

## Azure DevOps Service Connections

### 1. Azure Service Connection
```yaml
# Service connection configuration
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

## Azure-Specific Helm Charts

### 1. Azure AKS Helm Chart (helm-charts/interoperability/values.yaml)
```yaml
# Azure-specific values
global:
  imageRegistry: "bankregistry.azurecr.io"
  imageTag: "latest"
  
azure:
  subscriptionId: "<subscription-id>"
  resourceGroup: "bank-interoperability-rg"
  location: "eastus"
  
vault:
  enabled: true
  url: "https://vault.bank.com"
  role: "interoperability-role"
  azureAuth: true
  
kafka:
  enabled: true
  bootstrapServers: "kafka-cluster:9092"
  schemaRegistryUrl: "http://schema-registry:8081"
  
temporal:
  enabled: true
  host: "temporal.bank.com"
  port: 7233
  
istio:
  enabled: true
  mtls:
    mode: "STRICT"
  
monitoring:
  prometheus:
    enabled: true
    url: "http://prometheus:9090"
  jaeger:
    enabled: true
    url: "http://jaeger:16686"
  grafana:
    enabled: true
    url: "http://grafana:3000"
  azureMonitor:
    enabled: true
    workspaceId: "<log-analytics-workspace-id>"
    workspaceKey: "<log-analytics-workspace-key>"
```

## Azure Monitor Integration

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

### 3. Azure Monitor Configuration
```yaml
# azure-monitor-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: azure-monitor-config
  namespace: interoperability-monitoring
data:
  workspace-id: "<log-analytics-workspace-id>"
  workspace-key: "<log-analytics-workspace-key>"
  application-insights-key: "<app-insights-key>"
```

## Azure DevOps Pipeline Variables

### 1. Pipeline Variables
```yaml
# Pipeline variables in Azure DevOps
variables:
  - name: buildConfiguration
    value: 'Release'
  - name: dockerRegistry
    value: 'bankregistry.azurecr.io'
  - name: imageRepository
    value: 'bank-interoperability'
  - name: containerRegistry
    value: 'bankregistry.azurecr.io'
  - name: vmImageName
    value: 'ubuntu-latest'
  - name: terraformVersion
    value: '1.5.0'
```

### 2. Secret Variables
```yaml
# Secret variables (configured in Azure DevOps)
secrets:
  - name: acrUsername
    value: <acr-username>
  - name: acrPassword
    value: <acr-password>
  - name: vaultToken
    value: <vault-token>
  - name: sonarToken
    value: <sonar-token>
```

## Azure DevOps Environments

### 1. Development Environment
```yaml
# Development environment configuration
name: development
description: Development environment for bank interoperability
approvals: []
checks:
  - type: requiredTemplate
    displayName: Required Template
    inputs:
      allowedTemplates: ["development-template"]
```

### 2. Staging Environment
```yaml
# Staging environment configuration
name: staging
description: Staging environment for bank interoperability
approvals:
  - type: manual
    displayName: Manual Approval
    inputs:
      instructions: "Please review and approve the deployment to staging"
checks:
  - type: requiredTemplate
    displayName: Required Template
    inputs:
      allowedTemplates: ["staging-template"]
```

### 3. Production Environment
```yaml
# Production environment configuration
name: production
description: Production environment for bank interoperability
approvals:
  - type: manual
    displayName: Production Approval
    inputs:
      instructions: "Please review and approve the deployment to production"
checks:
  - type: requiredTemplate
    displayName: Required Template
    inputs:
      allowedTemplates: ["production-template"]
  - type: gates
    displayName: Security Gates
    inputs:
      gates:
        - type: securityScan
          displayName: Security Scan
          inputs:
            scanType: "SAST"
            severityThreshold: "high"
```

## Azure DevOps Pipeline Templates

### 1. Build Template (templates/build-template.yml)
```yaml
# templates/build-template.yml
parameters:
- name: buildConfiguration
  type: string
  default: 'Release'
- name: dockerRegistry
  type: string
- name: imageRepository
  type: string
- name: containerRegistry
  type: string
- name: tag
  type: string

steps:
- task: Docker@2
  displayName: 'Build and push image'
  inputs:
    command: buildAndPush
    repository: ${{ parameters.imageRepository }}
    dockerfile: $(Build.SourcesDirectory)/Dockerfile
    containerRegistry: ${{ parameters.containerRegistry }}
    tags: |
      ${{ parameters.tag }}
      latest
```

### 2. Test Template (templates/test-template.yml)
```yaml
# templates/test-template.yml
parameters:
- name: testType
  type: string
  default: 'unit'

steps:
- task: Maven@3
  displayName: 'Run ${{ parameters.testType }} Tests'
  inputs:
    mavenPomFile: 'pom.xml'
    goals: ${{ parameters.testType == 'unit' && 'test' || 'verify' }}
    publishJUnitResults: true
    testResultsFiles: ${{ parameters.testType == 'unit' && '**/surefire-reports/TEST-*.xml' || '**/failsafe-reports/TEST-*.xml' }}
```

### 3. Deploy Template (templates/deploy-template.yml)
```yaml
# templates/deploy-template.yml
parameters:
- name: environment
  type: string
- name: resourceGroup
  type: string
- name: aksName
  type: string
- name: imageTag
  type: string

steps:
- task: AzureCLI@2
  displayName: 'Deploy to ${{ parameters.environment }}'
  inputs:
    azureSubscription: 'Bank-Azure-Subscription'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      # Deploy to AKS
      az aks get-credentials --resource-group ${{ parameters.resourceGroup }} --name ${{ parameters.aksName }}
      helm upgrade --install interoperability ./helm-charts/interoperability --namespace interoperability-${{ parameters.environment }} --set image.tag=${{ parameters.imageTag }}
```

## Azure DevOps Pipeline Best Practices

### 1. Pipeline Organization
```yaml
# Pipeline structure best practices
- Use separate pipelines for different purposes
- Use templates for reusable components
- Use variables for configuration
- Use environments for deployment gates
- Use approvals for production deployments
```

### 2. Security Best Practices
```yaml
# Security best practices
- Use Azure Key Vault for secrets
- Use service connections for authentication
- Use RBAC for access control
- Use security scanning in pipelines
- Use approval gates for production
```

### 3. Performance Best Practices
```yaml
# Performance best practices
- Use parallel jobs where possible
- Use caching for dependencies
- Use incremental builds
- Use artifact publishing
- Use deployment slots
```

This comprehensive Azure DevOps pipeline configuration provides a complete CI/CD solution for your bank interoperability layer with enterprise-grade security, monitoring, and deployment capabilities.