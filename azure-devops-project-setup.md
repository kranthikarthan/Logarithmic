# Azure DevOps Project Setup for Bank Interoperability Layer

## Project Structure

### Repository Structure
```
bank-interoperability-layer/
├── .azuredevops/
│   ├── pipelines/
│   │   ├── azure-pipelines.yml
│   │   ├── feature-pipeline.yml
│   │   ├── infrastructure-pipeline.yml
│   │   └── security-pipeline.yml
│   ├── environments/
│   │   ├── development.yml
│   │   ├── staging.yml
│   │   └── production.yml
│   └── templates/
│       ├── build-template.yml
│       ├── test-template.yml
│       └── deploy-template.yml
├── src/
│   ├── api-gateway/
│   ├── intelligent-router/
│   ├── saga-orchestrator/
│   ├── protocol-adapters/
│   ├── schema-adapters/
│   └── security-services/
├── infrastructure/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
├── helm-charts/
│   ├── interoperability/
│   ├── api-gateway/
│   ├── intelligent-router/
│   └── saga-orchestrator/
├── k8s/
│   ├── namespaces/
│   ├── configmaps/
│   ├── secrets/
│   └── network-policies/
├── docs/
│   ├── architecture/
│   ├── api/
│   └── deployment/
└── scripts/
    ├── setup/
    ├── deployment/
    └── monitoring/
```

## Azure DevOps Project Creation

### 1. Azure DevOps Organization Setup
```bash
# Create Azure DevOps organization
az devops configure --defaults organization=https://dev.azure.com/Bank-Interoperability

# Create project
az devops project create \
  --name "Bank-Interoperability-Layer" \
  --description "Bank Interoperability Layer for On-Premise to Cloud Migration" \
  --visibility private \
  --source-control git
```

### 2. Repository Setup
```bash
# Initialize Git repository
git init
git remote add origin https://dev.azure.com/Bank-Interoperability/Bank-Interoperability-Layer/_git/Bank-Interoperability-Layer

# Create initial structure
mkdir -p .azuredevops/{pipelines,environments,templates}
mkdir -p src/{api-gateway,intelligent-router,saga-orchestrator,protocol-adapters,schema-adapters,security-services}
mkdir -p infrastructure/{modules}
mkdir -p helm-charts/{interoperability,api-gateway,intelligent-router,saga-orchestrator}
mkdir -p k8s/{namespaces,configmaps,secrets,network-policies}
mkdir -p docs/{architecture,api,deployment}
mkdir -p scripts/{setup,deployment,monitoring}
```

### 3. Service Connections Configuration
```yaml
# Service connections to create in Azure DevOps
service_connections:
  - name: "Bank-Azure-Subscription"
    type: "AzureRM"
    subscription_id: "<subscription-id>"
    subscription_name: "Bank Azure Subscription"
    resource_group: "bank-interoperability-rg"
    
  - name: "Bank-Container-Registry"
    type: "DockerRegistry"
    registry: "bankregistry.azurecr.io"
    username: "<acr-username>"
    password: "<acr-password>"
    
  - name: "Bank-Key-Vault"
    type: "AzureKeyVault"
    vault_name: "bank-interoperability-kv"
    resource_group: "bank-interoperability-rg"
    
  - name: "SonarCloud-Service"
    type: "SonarCloud"
    organization: "bank-org"
    token: "<sonar-token>"
    
  - name: "Snyk-Service"
    type: "Snyk"
    token: "<snyk-token>"
```

## Initial Pipeline Configuration

### 1. Main Build Pipeline (.azuredevops/pipelines/azure-pipelines.yml)
```yaml
# .azuredevops/pipelines/azure-pipelines.yml
trigger:
  branches:
    include:
    - main
    - develop
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

### 2. Feature Branch Pipeline (.azuredevops/pipelines/feature-pipeline.yml)
```yaml
# .azuredevops/pipelines/feature-pipeline.yml
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

### 3. Infrastructure Pipeline (.azuredevops/pipelines/infrastructure-pipeline.yml)
```yaml
# .azuredevops/pipelines/infrastructure-pipeline.yml
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

## Environment Configuration

### 1. Development Environment (.azuredevops/environments/development.yml)
```yaml
# .azuredevops/environments/development.yml
name: development
description: Development environment for bank interoperability
approvals: []
checks:
  - type: requiredTemplate
    displayName: Required Template
    inputs:
      allowedTemplates: ["development-template"]
```

### 2. Staging Environment (.azuredevops/environments/staging.yml)
```yaml
# .azuredevops/environments/staging.yml
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

### 3. Production Environment (.azuredevops/environments/production.yml)
```yaml
# .azuredevops/environments/production.yml
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

## Pipeline Templates

### 1. Build Template (.azuredevops/templates/build-template.yml)
```yaml
# .azuredevops/templates/build-template.yml
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

### 2. Test Template (.azuredevops/templates/test-template.yml)
```yaml
# .azuredevops/templates/test-template.yml
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

### 3. Deploy Template (.azuredevops/templates/deploy-template.yml)
```yaml
# .azuredevops/templates/deploy-template.yml
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

## Initial Setup Scripts

### 1. Project Setup Script (scripts/setup/setup-project.sh)
```bash
#!/bin/bash
# scripts/setup/setup-project.sh

echo "Setting up Bank Interoperability Layer project..."

# Create directory structure
mkdir -p .azuredevops/{pipelines,environments,templates}
mkdir -p src/{api-gateway,intelligent-router,saga-orchestrator,protocol-adapters,schema-adapters,security-services}
mkdir -p infrastructure/{modules}
mkdir -p helm-charts/{interoperability,api-gateway,intelligent-router,saga-orchestrator}
mkdir -p k8s/{namespaces,configmaps,secrets,network-policies}
mkdir -p docs/{architecture,api,deployment}
mkdir -p scripts/{setup,deployment,monitoring}

# Create initial files
touch README.md
touch .gitignore
touch .dockerignore

# Create initial documentation
cat > README.md << EOF
# Bank Interoperability Layer

This repository contains the source code and infrastructure for the Bank Interoperability Layer, designed to facilitate the migration from on-premise to cloud environments.

## Architecture

The system consists of the following components:
- API Gateway (Kong + Spring Boot)
- Intelligent Router Service
- Saga Orchestrator (Temporal.io)
- Protocol Adapters (REST, SOAP, MQ)
- Schema Adapters (JSON, XML, YAML)
- Security Services

## Getting Started

1. Clone the repository
2. Set up Azure DevOps project
3. Configure service connections
4. Deploy infrastructure
5. Run pipelines

## Documentation

See the docs/ directory for detailed documentation.
EOF

echo "Project structure created successfully!"
```

### 2. Azure DevOps Setup Script (scripts/setup/setup-azure-devops.sh)
```bash
#!/bin/bash
# scripts/setup/setup-azure-devops.sh

echo "Setting up Azure DevOps project..."

# Set Azure DevOps defaults
az devops configure --defaults organization=https://dev.azure.com/Bank-Interoperability

# Create project
az devops project create \
  --name "Bank-Interoperability-Layer" \
  --description "Bank Interoperability Layer for On-Premise to Cloud Migration" \
  --visibility private \
  --source-control git

# Create service connections
echo "Creating service connections..."

# Azure service connection
az devops service-endpoint azurerm create \
  --name "Bank-Azure-Subscription" \
  --azure-rm-service-principal-id "<service-principal-id>" \
  --azure-rm-service-principal-key "<service-principal-key>" \
  --azure-rm-subscription-id "<subscription-id>" \
  --azure-rm-subscription-name "Bank Azure Subscription" \
  --azure-rm-tenant-id "<tenant-id>"

# Container registry service connection
az devops service-endpoint docker create \
  --name "Bank-Container-Registry" \
  --docker-registry "bankregistry.azurecr.io" \
  --docker-username "<acr-username>" \
  --docker-password "<acr-password>"

echo "Azure DevOps setup completed!"
```

## Git Configuration

### 1. .gitignore
```gitignore
# .gitignore
# Compiled class file
*.class

# Log file
*.log

# BlueJ files
*.ctxt

# Mobile Tools for Java (J2ME)
.mtj.tmp/

# Package Files #
*.jar
*.war
*.nar
*.ear
*.zip
*.tar.gz
*.rar

# virtual machine crash logs
hs_err_pid*

# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties
dependency-reduced-pom.xml
buildNumber.properties
.mvn/timing.properties
.mvn/wrapper/maven-wrapper.jar

# IDE
.idea/
*.iws
*.iml
*.ipr
.vscode/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl

# Kubernetes
*.kubeconfig

# Docker
.dockerignore

# Azure
.azure/
```

### 2. .dockerignore
```dockerignore
# .dockerignore
# Git
.git
.gitignore

# Documentation
README.md
docs/

# IDE
.idea/
.vscode/
*.iml

# Maven
target/
pom.xml

# Node.js
node_modules/
npm-debug.log

# Python
__pycache__/
*.pyc

# Terraform
*.tfstate
*.tfstate.*
.terraform/

# Kubernetes
*.kubeconfig

# Azure
.azure/
```

This completes the Azure DevOps project structure and initial setup. The next step would be to set up the Azure infrastructure using Terraform.