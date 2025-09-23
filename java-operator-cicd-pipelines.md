# Java Operator CI/CD Pipelines

## CI/CD Pipeline Architecture

### Pipeline Structure
```
┌─────────────────────────────────────────────────────────────────┐
│                    Java Operator CI/CD Pipeline                 │
├─────────────────────────────────────────────────────────────────┤
│ Build → Test → Security → Package → Deploy → Monitor            │
│   ↓      ↓       ↓         ↓        ↓        ↓                 │
│ Maven  Unit Tests SAST/DAST Container AKS   Health           │
│   ↓      ↓       ↓         ↓        ↓        ↓                 │
│ Lint   Integration Container  Helm   Verify  Alerts            │
│   ↓      ↓       ↓         ↓        ↓        ↓                 │
│ Format  E2E     License    Push    Rollout  Notify             │
└─────────────────────────────────────────────────────────────────┘
```

## Azure DevOps Pipeline Configuration

### 1. Main Java Operator Pipeline
```yaml
# .azuredevops/pipelines/operators/java-azure-pipelines.yml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - operators/*
    - helm-charts/operators/*

variables:
  buildConfiguration: 'Release'
  dockerRegistry: 'bankregistry.azurecr.io'
  imageRepository: 'interoperability-java-operators'
  containerRegistry: 'bankregistry.azurecr.io'
  tag: '$(Build.BuildId)'
  vmImageName: 'ubuntu-latest'
  javaVersion: '17'
  mavenVersion: '3.8.4'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: BuildOperators
    displayName: 'Build Java Operators'
    pool:
      vmImage: $(vmImageName)
    strategy:
      matrix:
        operator:
          - interoperability-operator
          - saga-operator
          - routing-operator
          - security-operator
          - monitoring-operator
    steps:
    - task: JavaToolInstaller@0
      displayName: 'Install Java $(javaVersion)'
      inputs:
        versionSpec: $(javaVersion)
        jdkArchitectureOption: 'x64'
    
    - task: Maven@3
      displayName: 'Maven Build $(operator)'
      inputs:
        mavenPomFile: 'operators/$(operator)/pom.xml'
        goals: 'clean package'
        publishJUnitResults: true
        testResultsFiles: '**/surefire-reports/TEST-*.xml'
        codeCoverageToolOption: 'JaCoCo'
        codeCoverageClassFilter: '**/*Test.class'
    
    - task: Maven@3
      displayName: 'Maven Test $(operator)'
      inputs:
        mavenPomFile: 'operators/$(operator)/pom.xml'
        goals: 'test'
        publishJUnitResults: true
        testResultsFiles: '**/surefire-reports/TEST-*.xml'
    
    - task: Maven@3
      displayName: 'Maven Lint $(operator)'
      inputs:
        mavenPomFile: 'operators/$(operator)/pom.xml'
        goals: 'checkstyle:check'
        publishJUnitResults: true
        testResultsFiles: '**/checkstyle-results.xml'
    
    - task: Maven@3
      displayName: 'Maven Format Check $(operator)'
      inputs:
        mavenPomFile: 'operators/$(operator)/pom.xml'
        goals: 'spotless:check'

- stage: Security
  displayName: 'Security Scan'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - job: SecurityScan
    displayName: 'Security Scan'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: Maven@3
      displayName: 'Maven Security Scan'
      inputs:
        mavenPomFile: 'operators/pom.xml'
        goals: 'org.owasp:dependency-check-maven:check'
        publishJUnitResults: true
        testResultsFiles: '**/dependency-check-report.xml'
    
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

- stage: Package
  displayName: 'Package and Push'
  dependsOn: Security
  condition: succeeded()
  jobs:
  - job: PackageOperators
    displayName: 'Package Java Operators'
    pool:
      vmImage: $(vmImageName)
    strategy:
      matrix:
        operator:
          - interoperability-operator
          - saga-operator
          - routing-operator
          - security-operator
          - monitoring-operator
    steps:
    - task: Docker@2
      displayName: 'Build and push $(operator) image'
      inputs:
        command: buildAndPush
        repository: '$(imageRepository)-$(operator)'
        dockerfile: 'operators/$(operator)/Dockerfile'
        containerRegistry: $(containerRegistry)
        tags: |
          $(tag)
          latest
        arguments: '--build-arg OPERATOR_NAME=$(operator)'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish $(operator) Artifacts'
      inputs:
        PathtoPublish: 'operators/$(operator)/target'
        ArtifactName: '$(operator)-artifacts'
        publishLocation: 'Container'

- stage: Deploy
  displayName: 'Deploy to AKS'
  dependsOn: Package
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployOperators
    displayName: 'Deploy Java Operators to AKS'
    environment: 'production'
    pool:
      vmImage: $(vmImageName)
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            displayName: 'Deploy Java Operators to AKS'
            inputs:
              azureSubscription: 'Bank-Azure-Subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                # Get AKS credentials
                az aks get-credentials --resource-group bank-interoperability-rg --name bank-interoperability-aks
                
                # Install Helm if not present
                helm version
                
                # Deploy Java operators using Helm
                helm upgrade --install java-operators ./helm-charts/operators \
                  --namespace interoperability-core \
                  --create-namespace \
                  --set global.image.tag=$(tag) \
                  --set global.image.registry=$(dockerRegistry) \
                  --set global.operatorType=java \
                  --values ./helm-charts/operators/values.yaml
                
                # Verify deployment
                kubectl get pods -n interoperability-core
                kubectl get crd | grep interoperability

- stage: Monitor
  displayName: 'Monitoring Setup'
  dependsOn: Deploy
  condition: succeeded()
  jobs:
  - job: SetupMonitoring
    displayName: 'Setup Java Operator Monitoring'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: AzureCLI@2
      displayName: 'Configure Java Operator Monitoring'
      inputs:
        azureSubscription: 'Bank-Azure-Subscription'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          # Configure Prometheus monitoring
          kubectl apply -f ./helm-charts/operators/templates/monitoring/servicemonitor.yaml
          
          # Configure Grafana dashboards
          kubectl apply -f ./helm-charts/operators/templates/monitoring/grafana-dashboard.yaml
          
          # Configure alerting rules
          kubectl apply -f ./helm-charts/operators/templates/monitoring/alertrules.yaml
          
          # Verify monitoring setup
          kubectl get servicemonitor -n interoperability-monitoring
          kubectl get prometheusrule -n interoperability-monitoring
```

### 2. Feature Branch Pipeline
```yaml
# .azuredevops/pipelines/operators/java-feature-pipeline.yml
trigger:
  branches:
    include:
    - feature/*
  paths:
    include:
    - operators/*

variables:
  buildConfiguration: 'Debug'
  dockerRegistry: 'bankregistry.azurecr.io'
  imageRepository: 'interoperability-java-operators'
  containerRegistry: 'bankregistry.azurecr.io'
  tag: '$(Build.BuildId)-$(Build.SourceBranchName)'
  vmImageName: 'ubuntu-latest'
  javaVersion: '17'
  mavenVersion: '3.8.4'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: BuildOperators
    displayName: 'Build Java Operators'
    pool:
      vmImage: $(vmImageName)
    strategy:
      matrix:
        operator:
          - interoperability-operator
          - saga-operator
          - routing-operator
    steps:
    - task: JavaToolInstaller@0
      displayName: 'Install Java $(javaVersion)'
      inputs:
        versionSpec: $(javaVersion)
        jdkArchitectureOption: 'x64'
    
    - task: Maven@3
      displayName: 'Maven Build $(operator)'
      inputs:
        mavenPomFile: 'operators/$(operator)/pom.xml'
        goals: 'clean package'
        publishJUnitResults: true
        testResultsFiles: '**/surefire-reports/TEST-*.xml'
    
    - task: Maven@3
      displayName: 'Maven Test $(operator)'
      inputs:
        mavenPomFile: 'operators/$(operator)/pom.xml'
        goals: 'test'
        publishJUnitResults: true
        testResultsFiles: '**/surefire-reports/TEST-*.xml'

- stage: Package
  displayName: 'Package and Push'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - job: PackageOperators
    displayName: 'Package Java Operators'
    pool:
      vmImage: $(vmImageName)
    strategy:
      matrix:
        operator:
          - interoperability-operator
          - saga-operator
          - routing-operator
    steps:
    - task: Docker@2
      displayName: 'Build and push $(operator) image'
      inputs:
        command: buildAndPush
        repository: '$(imageRepository)-$(operator)'
        dockerfile: 'operators/$(operator)/Dockerfile'
        containerRegistry: $(containerRegistry)
        tags: |
          $(tag)
          latest

- stage: Deploy
  displayName: 'Deploy to Dev AKS'
  dependsOn: Package
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
                helm upgrade --install java-operators ./helm-charts/operators \
                  --namespace interoperability-dev \
                  --create-namespace \
                  --set global.image.tag=$(tag) \
                  --set global.image.registry=$(dockerRegistry) \
                  --set global.operatorType=java \
                  --values ./helm-charts/operators/values-dev.yaml
```

## Java Operator Testing

### 1. Unit Tests
```java
// operators/interoperability-operator/src/test/java/com/bank/interoperability/operator/controller/InteroperabilityRequestControllerTest.java
package com.bank.interoperability.operator.controller;

import com.bank.interoperability.operator.model.InteroperabilityRequest;
import com.bank.interoperability.operator.model.InteroperabilityRequestSpec;
import com.bank.interoperability.operator.service.InteroperabilityRequestService;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.Watcher;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@SpringJUnitConfig
class InteroperabilityRequestControllerTest {
    
    @Mock
    private KubernetesClient kubernetesClient;
    
    @Mock
    private InteroperabilityRequestService requestService;
    
    private InteroperabilityRequestController controller;
    
    @BeforeEach
    void setUp() {
        controller = new InteroperabilityRequestController();
        // Inject mocks
    }
    
    @Test
    void testEventReceived_Added() {
        // Given
        InteroperabilityRequest request = createTestRequest();
        
        // When
        controller.eventReceived(Watcher.Action.ADDED, request);
        
        // Then
        verify(requestService).reconcileRequest(request);
    }
    
    @Test
    void testEventReceived_Modified() {
        // Given
        InteroperabilityRequest request = createTestRequest();
        
        // When
        controller.eventReceived(Watcher.Action.MODIFIED, request);
        
        // Then
        verify(requestService).reconcileRequest(request);
    }
    
    @Test
    void testEventReceived_Deleted() {
        // Given
        InteroperabilityRequest request = createTestRequest();
        
        // When
        controller.eventReceived(Watcher.Action.DELETED, request);
        
        // Then
        verify(requestService).handleDeletion(request);
    }
    
    @Test
    void testEventReceived_Error() {
        // Given
        InteroperabilityRequest request = createTestRequest();
        
        // When
        controller.eventReceived(Watcher.Action.ERROR, request);
        
        // Then
        verify(requestService, never()).reconcileRequest(any());
        verify(requestService, never()).handleDeletion(any());
    }
    
    private InteroperabilityRequest createTestRequest() {
        InteroperabilityRequest request = new InteroperabilityRequest();
        request.getMetadata().setName("test-request");
        request.getMetadata().setNamespace("interoperability-core");
        
        InteroperabilityRequestSpec spec = new InteroperabilityRequestSpec();
        spec.setRequestId("test-request-id");
        spec.setRequestType("payment");
        spec.setPayload("test-payload");
        request.setSpec(spec);
        
        return request;
    }
}
```

### 2. Integration Tests
```java
// operators/interoperability-operator/src/test/java/com/bank/interoperability/operator/integration/InteroperabilityRequestIntegrationTest.java
package com.bank.interoperability.operator.integration;

import com.bank.interoperability.operator.model.InteroperabilityRequest;
import com.bank.interoperability.operator.model.InteroperabilityRequestSpec;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientBuilder;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringJUnitExtension;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(SpringJUnitExtension.class)
@SpringBootTest
class InteroperabilityRequestIntegrationTest {
    
    private KubernetesClient kubernetesClient;
    
    @BeforeEach
    void setUp() {
        kubernetesClient = new KubernetesClientBuilder().build();
    }
    
    @Test
    void testCreateInteroperabilityRequest() {
        // Given
        InteroperabilityRequest request = createTestRequest();
        
        // When
        InteroperabilityRequest created = kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .create(request);
        
        // Then
        assertNotNull(created);
        assertEquals("test-request", created.getMetadata().getName());
        assertEquals("interoperability-core", created.getMetadata().getNamespace());
        
        // Cleanup
        kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .withName("test-request")
            .delete();
    }
    
    @Test
    void testGetInteroperabilityRequest() {
        // Given
        InteroperabilityRequest request = createTestRequest();
        kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .create(request);
        
        // When
        InteroperabilityRequest retrieved = kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .withName("test-request")
            .get();
        
        // Then
        assertNotNull(retrieved);
        assertEquals("test-request", retrieved.getMetadata().getName());
        
        // Cleanup
        kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .withName("test-request")
            .delete();
    }
    
    private InteroperabilityRequest createTestRequest() {
        InteroperabilityRequest request = new InteroperabilityRequest();
        request.getMetadata().setName("test-request");
        request.getMetadata().setNamespace("interoperability-core");
        
        InteroperabilityRequestSpec spec = new InteroperabilityRequestSpec();
        spec.setRequestId("test-request-id");
        spec.setRequestType("payment");
        spec.setPayload("test-payload");
        request.setSpec(spec);
        
        return request;
    }
}
```

### 3. End-to-End Tests
```java
// operators/interoperability-operator/src/test/java/com/bank/interoperability/operator/e2e/InteroperabilityRequestE2ETest.java
package com.bank.interoperability.operator.e2e;

import com.bank.interoperability.operator.model.InteroperabilityRequest;
import com.bank.interoperability.operator.model.InteroperabilityRequestSpec;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientBuilder;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringJUnitExtension;

import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(SpringJUnitExtension.class)
@SpringBootTest
class InteroperabilityRequestE2ETest {
    
    private KubernetesClient kubernetesClient;
    
    @BeforeEach
    void setUp() {
        kubernetesClient = new KubernetesClientBuilder().build();
    }
    
    @Test
    void testInteroperabilityRequestLifecycle() throws InterruptedException {
        // Given
        InteroperabilityRequest request = createTestRequest();
        
        // When - Create request
        InteroperabilityRequest created = kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .create(request);
        
        // Then - Verify creation
        assertNotNull(created);
        assertEquals("test-request", created.getMetadata().getName());
        
        // Wait for processing
        TimeUnit.SECONDS.sleep(10);
        
        // When - Get updated request
        InteroperabilityRequest updated = kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .withName("test-request")
            .get();
        
        // Then - Verify processing
        assertNotNull(updated);
        assertNotNull(updated.getStatus());
        assertNotNull(updated.getStatus().getPhase());
        
        // Cleanup
        kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .withName("test-request")
            .delete();
    }
    
    private InteroperabilityRequest createTestRequest() {
        InteroperabilityRequest request = new InteroperabilityRequest();
        request.getMetadata().setName("test-request");
        request.getMetadata().setNamespace("interoperability-core");
        
        InteroperabilityRequestSpec spec = new InteroperabilityRequestSpec();
        spec.setRequestId("test-request-id");
        spec.setRequestType("payment");
        spec.setPayload("test-payload");
        request.setSpec(spec);
        
        return request;
    }
}
```

## Maven Configuration for Testing

### 1. Test Dependencies
```xml
<!-- operators/interoperability-operator/pom.xml -->
<dependencies>
    <!-- Test dependencies -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>io.fabric8</groupId>
        <artifactId>kubernetes-server-mock</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>kubernetes</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
        
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <configuration>
                <includes>
                    <include>**/*Test.java</include>
                    <include>**/*Tests.java</include>
                </includes>
            </configuration>
        </plugin>
        
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-failsafe-plugin</artifactId>
            <configuration>
                <includes>
                    <include>**/*IT.java</include>
                    <include>**/*E2ETest.java</include>
                </includes>
            </configuration>
        </plugin>
        
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <executions>
                <execution>
                    <goals>
                        <goal>prepare-agent</goal>
                    </goals>
                </execution>
                <execution>
                    <id>report</id>
                    <phase>test</phase>
                    <goals>
                        <goal>report</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

## GitHub Actions Workflow

### 1. CI Workflow
```yaml
# .github/workflows/java-operators-ci.yml
name: Java Operators CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Cache Maven dependencies
      uses: actions/cache@v3
      with:
        path: ~/.m2
        key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
        restore-keys: |
          ${{ runner.os }}-m2-
    
    - name: Run tests
      run: |
        cd operators
        mvn test
    
    - name: Run integration tests
      run: |
        cd operators
        mvn verify
    
    - name: Generate test report
      uses: dorny/test-reporter@v1
      if: success() || failure()
      with:
        name: Java Operators Tests
        path: operators/target/surefire-reports/*.xml
        reporter: java-junit
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: operators/target/site/jacoco/jacoco.xml
```

### 2. CD Workflow
```yaml
# .github/workflows/java-operators-cd.yml
name: Java Operators CD

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Azure Container Registry
      uses: azure/docker-login@v1
      with:
        login-server: bankregistry.azurecr.io
        username: ${{ secrets.ACR_USERNAME }}
        password: ${{ secrets.ACR_PASSWORD }}
    
    - name: Build and push Java operators
      run: |
        cd operators
        for operator in interoperability-operator saga-operator routing-operator security-operator monitoring-operator; do
          docker build -t bankregistry.azurecr.io/$operator:${{ github.sha }} -f $operator/Dockerfile .
          docker push bankregistry.azurecr.io/$operator:${{ github.sha }}
        done
    
    - name: Deploy to AKS
      uses: azure/aks-set-context@v2
      with:
        resource-group: bank-interoperability-rg
        cluster-name: bank-interoperability-aks
    
    - name: Deploy with Helm
      run: |
        helm upgrade --install java-operators ./helm-charts/operators \
          --namespace interoperability-core \
          --create-namespace \
          --set global.image.tag=${{ github.sha }} \
          --set global.image.registry=bankregistry.azurecr.io \
          --set global.operatorType=java
```

This completes the comprehensive Java operator CI/CD pipelines!