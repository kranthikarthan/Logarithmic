# Azure DevOps Pipeline Configuration for Bank Interoperability Layer

## Complete Pipeline Architecture

### Pipeline Structure Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure DevOps Pipeline Architecture            │
├─────────────────────────────────────────────────────────────────┤
│ Build Pipeline → Test Pipeline → Security Pipeline → Deploy    │
│     ↓              ↓              ↓              ↓              │
│  Artifacts → Unit Tests → SAST/DAST → AKS Deployment           │
│     ↓              ↓              ↓              ↓              │
│  Container → Integration → Security → Monitoring                │
│  Registry      Tests       Gates      Setup                     │
└─────────────────────────────────────────────────────────────────┘
```

## Enhanced Pipeline Configurations

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
    - infrastructure/*

variables:
  buildConfiguration: 'Release'
  dockerRegistry: 'bankregistry.azurecr.io'
  imageRepository: 'bank-interoperability'
  containerRegistry: 'bankregistry.azurecr.io'
  dockerfilePath: '$(Build.SourcesDirectory)/Dockerfile'
  tag: '$(Build.BuildId)'
  vmImageName: 'ubuntu-latest'
  terraformVersion: '1.5.0'

stages:
- stage: Build
  displayName: 'Build and Package'
  jobs:
  - job: BuildServices
    displayName: 'Build Microservices'
    pool:
      vmImage: $(vmImageName)
    strategy:
      matrix:
        service:
          - api-gateway
          - intelligent-router
          - saga-orchestrator
          - protocol-adapters
          - schema-adapters
          - security-services
    steps:
    - task: Docker@2
      displayName: 'Build and push $(service) image'
      inputs:
        command: buildAndPush
        repository: '$(imageRepository)-$(service)'
        dockerfile: '$(Build.SourcesDirectory)/src/$(service)/Dockerfile'
        containerRegistry: $(containerRegistry)
        tags: |
          $(tag)
          latest
        arguments: '--build-arg SERVICE_NAME=$(service)'

    - task: PublishBuildArtifacts@1
      displayName: 'Publish $(service) Artifacts'
      inputs:
        PathtoPublish: '$(Build.SourcesDirectory)/src/$(service)/target'
        ArtifactName: '$(service)-artifacts'
        publishLocation: 'Container'

- stage: Test
  displayName: 'Test Suite'
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
        codeCoverageToolOption: 'JaCoCo'
        codeCoverageClassFilter: '**/*Test.class'

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

  - job: ContractTests
    displayName: 'Contract Tests'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: Maven@3
      displayName: 'Run Contract Tests'
      inputs:
        mavenPomFile: 'pom.xml'
        goals: 'test'
        publishJUnitResults: true
        testResultsFiles: '**/contract-test-reports/TEST-*.xml'

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
        monitorWhen: 'always'

    - task: SnykSecurityScan@1
      displayName: 'Snyk Container Scan'
      inputs:
        serviceConnectionEndpoint: 'SnykServiceConnection'
        testType: 'container'
        severityThreshold: 'high'
        monitorWhen: 'always'

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
                # Get AKS credentials
                az aks get-credentials --resource-group bank-interoperability-rg --name bank-interoperability-aks
                
                # Install Helm if not present
                helm version
                
                # Deploy using Helm
                helm upgrade --install interoperability ./helm-charts/interoperability \
                  --namespace interoperability-core \
                  --create-namespace \
                  --set image.tag=$(tag) \
                  --set image.registry=$(dockerRegistry) \
                  --values ./helm-charts/interoperability/values.yaml

          - task: AzureCLI@2
            displayName: 'Verify Deployment'
            inputs:
              azureSubscription: 'Bank-Azure-Subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                # Verify deployment
                kubectl get pods -n interoperability-core
                kubectl get services -n interoperability-core
                kubectl get ingress -n interoperability-core

- stage: Monitor
  displayName: 'Monitoring Setup'
  dependsOn: Deploy
  condition: succeeded()
  jobs:
  - job: SetupMonitoring
    displayName: 'Setup Monitoring'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: AzureCLI@2
      displayName: 'Configure Azure Monitor'
      inputs:
        azureSubscription: 'Bank-Azure-Subscription'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          # Configure Azure Monitor for containers
          az monitor log-analytics workspace create \
            --resource-group bank-interoperability-rg \
            --workspace-name bank-interoperability-logs \
            --location eastus
          
          # Enable monitoring on AKS
          az aks enable-addons \
            --resource-group bank-interoperability-rg \
            --name bank-interoperability-aks \
            --addons monitoring \
            --workspace-resource-id /subscriptions/$(subscriptionId)/resourcegroups/bank-interoperability-rg/providers/microsoft.operationalinsights/workspaces/bank-interoperability-logs
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
    - infrastructure/*

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
  - job: BuildServices
    displayName: 'Build Microservices'
    pool:
      vmImage: $(vmImageName)
    strategy:
      matrix:
        service:
          - api-gateway
          - intelligent-router
          - saga-orchestrator
    steps:
    - task: Docker@2
      displayName: 'Build and push $(service) image'
      inputs:
        command: buildAndPush
        repository: '$(imageRepository)-$(service)'
        dockerfile: '$(Build.SourcesDirectory)/src/$(service)/Dockerfile'
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
                helm upgrade --install interoperability ./helm-charts/interoperability \
                  --namespace interoperability-dev \
                  --create-namespace \
                  --set image.tag=$(tag) \
                  --set image.registry=$(dockerRegistry) \
                  --values ./helm-charts/interoperability/values-dev.yaml
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
        backendServiceArm: 'Bank-Azure-Subscription'
        backendAzureRmResourceGroupName: 'bank-terraform-state-rg'
        backendAzureRmStorageAccountName: 'bankterraformstate'
        backendAzureRmContainerName: 'tfstate'
        backendAzureRmKey: 'interoperability.tfstate'

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
              backendServiceArm: 'Bank-Azure-Subscription'
              backendAzureRmResourceGroupName: 'bank-terraform-state-rg'
              backendAzureRmStorageAccountName: 'bankterraformstate'
              backendAzureRmContainerName: 'tfstate'
              backendAzureRmKey: 'interoperability.tfstate'

          - task: TerraformTaskV3@3
            displayName: 'Terraform Output'
            inputs:
              provider: 'azurerm'
              command: 'output'
              workingDirectory: '$(Build.SourcesDirectory)/infrastructure'
              environmentServiceNameAzureRM: 'Bank-Azure-Subscription'
              backendServiceArm: 'Bank-Azure-Subscription'
              backendAzureRmResourceGroupName: 'bank-terraform-state-rg'
              backendAzureRmStorageAccountName: 'bankterraformstate'
              backendAzureRmContainerName: 'tfstate'
              backendAzureRmKey: 'interoperability.tfstate'
              outputTo: 'console'
```

### 4. Security Pipeline (.azuredevops/pipelines/security-pipeline.yml)
```yaml
# .azuredevops/pipelines/security-pipeline.yml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - src/*

variables:
  vmImageName: 'ubuntu-latest'

stages:
- stage: SecurityScan
  displayName: 'Security Scan'
  jobs:
  - job: SAST
    displayName: 'Static Application Security Testing'
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

  - job: DAST
    displayName: 'Dynamic Application Security Testing'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: SnykSecurityScan@1
      displayName: 'Snyk Security Scan'
      inputs:
        serviceConnectionEndpoint: 'SnykServiceConnection'
        testType: 'app'
        severityThreshold: 'high'
        monitorWhen: 'always'

  - job: ContainerScan
    displayName: 'Container Security Scan'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: SnykSecurityScan@1
      displayName: 'Snyk Container Scan'
      inputs:
        serviceConnectionEndpoint: 'SnykServiceConnection'
        testType: 'container'
        severityThreshold: 'high'
        monitorWhen: 'always'

  - job: DependencyScan
    displayName: 'Dependency Security Scan'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: SnykSecurityScan@1
      displayName: 'Snyk Dependency Scan'
      inputs:
        serviceConnectionEndpoint: 'SnykServiceConnection'
        testType: 'npm'
        severityThreshold: 'high'
        monitorWhen: 'always'
```

## Enhanced Pipeline Templates

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
- name: serviceName
  type: string

steps:
- task: Docker@2
  displayName: 'Build and push ${{ parameters.serviceName }} image'
  inputs:
    command: buildAndPush
    repository: '${{ parameters.imageRepository }}-${{ parameters.serviceName }}'
    dockerfile: '$(Build.SourcesDirectory)/src/${{ parameters.serviceName }}/Dockerfile'
    containerRegistry: ${{ parameters.containerRegistry }}
    tags: |
      ${{ parameters.tag }}
      latest
    arguments: '--build-arg SERVICE_NAME=${{ parameters.serviceName }}'

- task: PublishBuildArtifacts@1
  displayName: 'Publish ${{ parameters.serviceName }} Artifacts'
  inputs:
    PathtoPublish: '$(Build.SourcesDirectory)/src/${{ parameters.serviceName }}/target'
    ArtifactName: '${{ parameters.serviceName }}-artifacts'
    publishLocation: 'Container'
```

### 2. Test Template (.azuredevops/templates/test-template.yml)
```yaml
# .azuredevops/templates/test-template.yml
parameters:
- name: testType
  type: string
  default: 'unit'
- name: serviceName
  type: string

steps:
- task: Maven@3
  displayName: 'Run ${{ parameters.testType }} Tests for ${{ parameters.serviceName }}'
  inputs:
    mavenPomFile: '$(Build.SourcesDirectory)/src/${{ parameters.serviceName }}/pom.xml'
    goals: ${{ parameters.testType == 'unit' && 'test' || 'verify' }}
    publishJUnitResults: true
    testResultsFiles: ${{ parameters.testType == 'unit' && '**/surefire-reports/TEST-*.xml' || '**/failsafe-reports/TEST-*.xml' }}
    codeCoverageToolOption: 'JaCoCo'
    codeCoverageClassFilter: '**/*Test.class'

- task: PublishTestResults@2
  displayName: 'Publish Test Results'
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '**/TEST-*.xml'
    mergeTestResults: true
    failTaskOnFailedTests: true
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
- name: namespace
  type: string
  default: 'interoperability'

steps:
- task: AzureCLI@2
  displayName: 'Deploy to ${{ parameters.environment }}'
  inputs:
    azureSubscription: 'Bank-Azure-Subscription'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      # Get AKS credentials
      az aks get-credentials --resource-group ${{ parameters.resourceGroup }} --name ${{ parameters.aksName }}
      
      # Install Helm if not present
      helm version
      
      # Deploy using Helm
      helm upgrade --install interoperability ./helm-charts/interoperability \
        --namespace ${{ parameters.namespace }} \
        --create-namespace \
        --set image.tag=${{ parameters.imageTag }} \
        --set image.registry=bankregistry.azurecr.io \
        --values ./helm-charts/interoperability/values-${{ parameters.environment }}.yaml

- task: AzureCLI@2
  displayName: 'Verify Deployment'
  inputs:
    azureSubscription: 'Bank-Azure-Subscription'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      # Verify deployment
      kubectl get pods -n ${{ parameters.namespace }}
      kubectl get services -n ${{ parameters.namespace }}
      kubectl get ingress -n ${{ parameters.namespace }}
```

## Environment-Specific Configurations

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
  - type: gates
    displayName: Health Check
    inputs:
      gates:
        - type: healthCheck
          displayName: Service Health Check
          inputs:
            healthCheckUrl: "https://dev-api.bank.com/health"
            timeout: 300
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
      timeout: 1440
checks:
  - type: requiredTemplate
    displayName: Required Template
    inputs:
      allowedTemplates: ["staging-template"]
  - type: gates
    displayName: Security Gates
    inputs:
      gates:
        - type: securityScan
          displayName: Security Scan
          inputs:
            scanType: "SAST"
            severityThreshold: "high"
        - type: healthCheck
          displayName: Service Health Check
          inputs:
            healthCheckUrl: "https://staging-api.bank.com/health"
            timeout: 300
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
      timeout: 1440
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
        - type: securityScan
          displayName: Container Security Scan
          inputs:
            scanType: "container"
            severityThreshold: "high"
        - type: healthCheck
          displayName: Service Health Check
          inputs:
            healthCheckUrl: "https://api.bank.com/health"
            timeout: 300
```

## Pipeline Variables and Secrets

### 1. Pipeline Variables
```yaml
# Pipeline variables configuration
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
  - name: kubernetesVersion
    value: '1.27'
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
  - name: snykToken
    value: <snyk-token>
  - name: postgresqlPassword
    value: <postgresql-password>
```

## Pipeline Monitoring and Alerting

### 1. Pipeline Notifications
```yaml
# Pipeline notification configuration
notifications:
  - type: email
    recipients: ["devops-team@bank.com"]
    events: ["pipeline.failed", "pipeline.succeeded"]
  
  - type: teams
    webhook: "https://bank.webhook.office.com/webhookb2/..."
    events: ["pipeline.failed", "pipeline.succeeded"]
  
  - type: slack
    webhook: "https://hooks.slack.com/services/..."
    events: ["pipeline.failed", "pipeline.succeeded"]
```

### 2. Pipeline Metrics
```yaml
# Pipeline metrics configuration
metrics:
  - name: buildSuccessRate
    description: "Build success rate percentage"
    calculation: "successful_builds / total_builds * 100"
  
  - name: deploymentFrequency
    description: "Number of deployments per day"
    calculation: "deployments / days"
  
  - name: leadTime
    description: "Time from commit to deployment"
    calculation: "deployment_time - commit_time"
  
  - name: meanTimeToRecovery
    description: "Average time to recover from failures"
    calculation: "sum(recovery_times) / count(failures)"
```

This completes the Azure DevOps pipeline configuration. The next step would be to set up the Azure Container Registry and AKS.