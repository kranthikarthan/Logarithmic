# Go Operator CI/CD Pipelines

## CI/CD Pipeline Architecture

### Pipeline Structure
```
┌─────────────────────────────────────────────────────────────────┐
│                    Go Operator CI/CD Pipeline                   │
├─────────────────────────────────────────────────────────────────┤
│ Build → Test → Security → Package → Deploy → Monitor            │
│   ↓      ↓       ↓         ↓        ↓        ↓                 │
│ Go Build Unit Tests SAST/DAST Container AKS   Health           │
│   ↓      ↓       ↓         ↓        ↓        ↓                 │
│ Lint   Integration Container  Helm   Verify  Alerts            │
│   ↓      ↓       ↓         ↓        ↓        ↓                 │
│ Format  E2E     License    Push    Rollout  Notify             │
└─────────────────────────────────────────────────────────────────┘
```

## Azure DevOps Pipeline Configuration

### 1. Main Operator Pipeline
```yaml
# .azuredevops/pipelines/operators/azure-pipelines.yml
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
  imageRepository: 'interoperability-operators'
  containerRegistry: 'bankregistry.azurecr.io'
  tag: '$(Build.BuildId)'
  vmImageName: 'ubuntu-latest'
  goVersion: '1.21'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: BuildOperators
    displayName: 'Build Go Operators'
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
    - task: GoTool@0
      displayName: 'Install Go $(goVersion)'
      inputs:
        version: $(goVersion)
    
    - task: Go@0
      displayName: 'Go Build $(operator)'
      inputs:
        command: 'build'
        arguments: '-o bin/$(operator) ./$(operator)'
        workingDirectory: '$(Build.SourcesDirectory)/operators'
    
    - task: Go@0
      displayName: 'Go Test $(operator)'
      inputs:
        command: 'test'
        arguments: '-v ./$(operator)/...'
        workingDirectory: '$(Build.SourcesDirectory)/operators'
    
    - task: Go@0
      displayName: 'Go Lint $(operator)'
      inputs:
        command: 'custom'
        customCommand: 'run github.com/golangci/golangci-lint/cmd/golangci-lint@latest run ./$(operator)/...'
        workingDirectory: '$(Build.SourcesDirectory)/operators'
    
    - task: Go@0
      displayName: 'Go Format Check $(operator)'
      inputs:
        command: 'custom'
        customCommand: 'fmt -d ./$(operator)/...'
        workingDirectory: '$(Build.SourcesDirectory)/operators'

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
    - task: Go@0
      displayName: 'Go Security Scan'
      inputs:
        command: 'custom'
        customCommand: 'run github.com/securecodewarrior/gosec/v2/cmd/gosec@latest ./operators/...'
        workingDirectory: '$(Build.SourcesDirectory)'
    
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
    displayName: 'Package Operators'
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
        dockerfile: '$(Build.SourcesDirectory)/operators/$(operator)/Dockerfile'
        containerRegistry: $(containerRegistry)
        tags: |
          $(tag)
          latest
        arguments: '--build-arg OPERATOR_NAME=$(operator)'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish $(operator) Artifacts'
      inputs:
        PathtoPublish: '$(Build.SourcesDirectory)/operators/$(operator)/bin'
        ArtifactName: '$(operator)-artifacts'
        publishLocation: 'Container'

- stage: Deploy
  displayName: 'Deploy to AKS'
  dependsOn: Package
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployOperators
    displayName: 'Deploy Operators to AKS'
    environment: 'production'
    pool:
      vmImage: $(vmImageName)
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            displayName: 'Deploy Operators to AKS'
            inputs:
              azureSubscription: 'Bank-Azure-Subscription'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                # Get AKS credentials
                az aks get-credentials --resource-group bank-interoperability-rg --name bank-interoperability-aks
                
                # Install Helm if not present
                helm version
                
                # Deploy operators using Helm
                helm upgrade --install operators ./helm-charts/operators \
                  --namespace interoperability-core \
                  --create-namespace \
                  --set global.image.tag=$(tag) \
                  --set global.image.registry=$(dockerRegistry) \
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
    displayName: 'Setup Monitoring'
    pool:
      vmImage: $(vmImageName)
    steps:
    - task: AzureCLI@2
      displayName: 'Configure Operator Monitoring'
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
# .azuredevops/pipelines/operators/feature-pipeline.yml
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
  imageRepository: 'interoperability-operators'
  containerRegistry: 'bankregistry.azurecr.io'
  tag: '$(Build.BuildId)-$(Build.SourceBranchName)'
  vmImageName: 'ubuntu-latest'
  goVersion: '1.21'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: BuildOperators
    displayName: 'Build Go Operators'
    pool:
      vmImage: $(vmImageName)
    strategy:
      matrix:
        operator:
          - interoperability-operator
          - saga-operator
          - routing-operator
    steps:
    - task: GoTool@0
      displayName: 'Install Go $(goVersion)'
      inputs:
        version: $(goVersion)
    
    - task: Go@0
      displayName: 'Go Build $(operator)'
      inputs:
        command: 'build'
        arguments: '-o bin/$(operator) ./$(operator)'
        workingDirectory: '$(Build.SourcesDirectory)/operators'
    
    - task: Go@0
      displayName: 'Go Test $(operator)'
      inputs:
        command: 'test'
        arguments: '-v ./$(operator)/...'
        workingDirectory: '$(Build.SourcesDirectory)/operators'

- stage: Package
  displayName: 'Package and Push'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - job: PackageOperators
    displayName: 'Package Operators'
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
        dockerfile: '$(Build.SourcesDirectory)/operators/$(operator)/Dockerfile'
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
                helm upgrade --install operators ./helm-charts/operators \
                  --namespace interoperability-dev \
                  --create-namespace \
                  --set global.image.tag=$(tag) \
                  --set global.image.registry=$(dockerRegistry) \
                  --values ./helm-charts/operators/values-dev.yaml
```

## Go Operator Testing

### 1. Unit Tests
```go
// operators/interoperability-operator/controllers/interoperabilityrequest_controller_test.go
package controllers

import (
	"context"
	"testing"
	"time"
	
	"github.com/go-logr/logr"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"
	
	interoperabilityv1 "github.com/bank/interoperability-operator/api/v1"
)

type MockClient struct {
	mock.Mock
}

func (m *MockClient) Get(ctx context.Context, key client.ObjectKey, obj client.Object) error {
	args := m.Called(ctx, key, obj)
	return args.Error(0)
}

func (m *MockClient) List(ctx context.Context, list client.ObjectList, opts ...client.ListOption) error {
	args := m.Called(ctx, list, opts)
	return args.Error(0)
}

func (m *MockClient) Create(ctx context.Context, obj client.Object, opts ...client.CreateOption) error {
	args := m.Called(ctx, obj, opts)
	return args.Error(0)
}

func (m *MockClient) Update(ctx context.Context, obj client.Object, opts ...client.UpdateOption) error {
	args := m.Called(ctx, obj, opts)
	return args.Error(0)
}

func (m *MockClient) Delete(ctx context.Context, obj client.Object, opts ...client.DeleteOption) error {
	args := m.Called(ctx, obj, opts)
	return args.Error(0)
}

func TestInteroperabilityRequestReconciler_Reconcile(t *testing.T) {
	tests := []struct {
		name    string
		request reconcile.Request
		setup   func(*MockClient)
		want    ctrl.Result
		wantErr bool
	}{
		{
			name: "successful reconcile",
			request: reconcile.Request{
				NamespacedName: types.NamespacedName{
					Name:      "test-request",
					Namespace: "test-namespace",
				},
			},
			setup: func(mockClient *MockClient) {
				mockClient.On("Get", mock.Anything, mock.Anything, mock.Anything).Return(nil)
				mockClient.On("Update", mock.Anything, mock.Anything, mock.Anything).Return(nil)
			},
			want:    ctrl.Result{},
			wantErr: false,
		},
		{
			name: "request not found",
			request: reconcile.Request{
				NamespacedName: types.NamespacedName{
					Name:      "not-found",
					Namespace: "test-namespace",
				},
			},
			setup: func(mockClient *MockClient) {
				mockClient.On("Get", mock.Anything, mock.Anything, mock.Anything).Return(client.ErrNotFound)
			},
			want:    ctrl.Result{},
			wantErr: false,
		},
	}
	
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mockClient := &MockClient{}
			tt.setup(mockClient)
			
			r := &InteroperabilityRequestReconciler{
				Client: mockClient,
				Scheme: runtime.NewScheme(),
			}
			
			got, err := r.Reconcile(context.Background(), tt.request)
			
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
			
			assert.Equal(t, tt.want, got)
			mockClient.AssertExpectations(t)
		})
	}
}
```

### 2. Integration Tests
```go
// operators/interoperability-operator/controllers/integration_test.go
package controllers

import (
	"context"
	"testing"
	"time"
	
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/envtest"
	
	interoperabilityv1 "github.com/bank/interoperability-operator/api/v1"
)

func TestInteroperabilityRequestReconciler_Integration(t *testing.T) {
	// Setup test environment
	testEnv := &envtest.Environment{
		CRDDirectoryPaths: []string{"../../config/crd/bases"},
	}
	
	cfg, err := testEnv.Start()
	require.NoError(t, err)
	defer testEnv.Stop()
	
	// Create client
	mgr, err := ctrl.NewManager(cfg, ctrl.Options{
		Scheme: runtime.NewScheme(),
	})
	require.NoError(t, err)
	
	client := mgr.GetClient()
	
	// Create reconciler
	reconciler := &InteroperabilityRequestReconciler{
		Client: client,
		Scheme: mgr.GetScheme(),
	}
	
	// Create test request
	request := &interoperabilityv1.InteroperabilityRequest{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "test-request",
			Namespace: "default",
		},
		Spec: interoperabilityv1.InteroperabilityRequestSpec{
			RequestId:   "test-request-id",
			RequestType:   "payment",
			Payload:       "test-payload",
			RoutingStrategy: "auto",
		},
	}
	
	// Create the request
	err = client.Create(context.Background(), request)
	require.NoError(t, err)
	
	// Reconcile
	result, err := reconciler.Reconcile(context.Background(), reconcile.Request{
		NamespacedName: types.NamespacedName{
			Name:      "test-request",
			Namespace: "default",
		},
	})
	
	assert.NoError(t, err)
	assert.Equal(t, ctrl.Result{}, result)
	
	// Verify the request was processed
	var updatedRequest interoperabilityv1.InteroperabilityRequest
	err = client.Get(context.Background(), types.NamespacedName{
		Name:      "test-request",
		Namespace: "default",
	}, &updatedRequest)
	
	require.NoError(t, err)
	assert.NotEmpty(t, updatedRequest.Status.Phase)
}
```

### 3. End-to-End Tests
```go
// operators/interoperability-operator/controllers/e2e_test.go
package controllers

import (
	"context"
	"testing"
	"time"
	
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/envtest"
	
	interoperabilityv1 "github.com/bank/interoperability-operator/api/v1"
)

func TestInteroperabilityRequest_E2E(t *testing.T) {
	// Setup test environment
	testEnv := &envtest.Environment{
		CRDDirectoryPaths: []string{"../../config/crd/bases"},
	}
	
	cfg, err := testEnv.Start()
	require.NoError(t, err)
	defer testEnv.Stop()
	
	// Create manager
	mgr, err := ctrl.NewManager(cfg, ctrl.Options{
		Scheme: runtime.NewScheme(),
	})
	require.NoError(t, err)
	
	// Start manager
	go func() {
		err := mgr.Start(ctrl.SetupSignalHandler())
		require.NoError(t, err)
	}()
	
	// Wait for manager to start
	time.Sleep(1 * time.Second)
	
	client := mgr.GetClient()
	
	// Create test request
	request := &interoperabilityv1.InteroperabilityRequest{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "e2e-test-request",
			Namespace: "default",
		},
		Spec: interoperabilityv1.InteroperabilityRequestSpec{
			RequestId:   "e2e-test-request-id",
			RequestType: "payment",
			Payload:     "e2e-test-payload",
			RoutingStrategy: "auto",
		},
	}
	
	// Create the request
	err = client.Create(context.Background(), request)
	require.NoError(t, err)
	
	// Wait for reconciliation
	time.Sleep(5 * time.Second)
	
	// Verify the request was processed
	var updatedRequest interoperabilityv1.InteroperabilityRequest
	err = client.Get(context.Background(), types.NamespacedName{
		Name:      "e2e-test-request",
		Namespace: "default",
	}, &updatedRequest)
	
	require.NoError(t, err)
	assert.NotEmpty(t, updatedRequest.Status.Phase)
	assert.NotEmpty(t, updatedRequest.Status.Message)
}
```

## Makefile for Go Operators

### 1. Main Makefile
```makefile
# operators/Makefile
# Go parameters
GOCMD=go
GOBUILD=$(GOCMD) build
GOCLEAN=$(GOCMD) clean
GOTEST=$(GOCMD) test
GOGET=$(GOCMD) get
GOMOD=$(GOCMD) mod
GOFMT=$(GOCMD) fmt

# Binary names
BINARY_NAME=interoperability-operator
BINARY_UNIX=$(BINARY_NAME)_unix

# Docker parameters
DOCKER_REGISTRY=bankregistry.azurecr.io
DOCKER_IMAGE=$(DOCKER_REGISTRY)/interoperability-operator
DOCKER_TAG=latest

# Kubernetes parameters
KUBECONFIG=~/.kube/config
NAMESPACE=interoperability-core

# Build the binary
build:
	$(GOBUILD) -o bin/$(BINARY_NAME) -v ./interoperability-operator

# Build for Linux
build-linux:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 $(GOBUILD) -o bin/$(BINARY_UNIX) -v ./interoperability-operator

# Clean build artifacts
clean:
	$(GOCLEAN)
	rm -f bin/$(BINARY_NAME)
	rm -f bin/$(BINARY_UNIX)

# Run tests
test:
	$(GOTEST) -v ./interoperability-operator/...

# Run tests with coverage
test-coverage:
	$(GOTEST) -v -coverprofile=coverage.out ./interoperability-operator/...
	$(GOCMD) tool cover -html=coverage.out -o coverage.html

# Format code
fmt:
	$(GOFMT) ./interoperability-operator/...

# Lint code
lint:
	golangci-lint run ./interoperability-operator/...

# Security scan
security:
	gosec ./interoperability-operator/...

# Generate code
generate:
	$(GOCMD) generate ./interoperability-operator/...

# Update dependencies
deps:
	$(GOMOD) download
	$(GOMOD) tidy

# Build Docker image
docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f interoperability-operator/Dockerfile .

# Push Docker image
docker-push:
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)

# Deploy to Kubernetes
deploy:
	kubectl apply -f config/crd/
	kubectl apply -f config/rbac/
	kubectl apply -f config/manager/

# Undeploy from Kubernetes
undeploy:
	kubectl delete -f config/manager/
	kubectl delete -f config/rbac/
	kubectl delete -f config/crd/

# Install CRDs
install-crds:
	kubectl apply -f config/crd/

# Uninstall CRDs
uninstall-crds:
	kubectl delete -f config/crd/

# Run operator locally
run:
	$(GOBUILD) -o bin/$(BINARY_NAME) -v ./interoperability-operator
	./bin/$(BINARY_NAME)

# Run operator with debug
run-debug:
	$(GOBUILD) -gcflags="all=-N -l" -o bin/$(BINARY_NAME) -v ./interoperability-operator
	dlv --listen=:2345 --headless=true --api-version=2 exec ./bin/$(BINARY_NAME)

# Generate manifests
manifests:
	controller-gen rbac:roleName=manager-role crd webhook paths="./interoperability-operator/..." output:crd:artifacts:config=config/crd/bases

# Generate code
generate:
	controller-gen object:headerFile="hack/boilerplate.go.txt" paths="./interoperability-operator/..."

# All targets
all: clean deps fmt lint test build

# Help
help:
	@echo "Available targets:"
	@echo "  build          - Build the binary"
	@echo "  build-linux    - Build for Linux"
	@echo "  clean          - Clean build artifacts"
	@echo "  test           - Run tests"
	@echo "  test-coverage  - Run tests with coverage"
	@echo "  fmt            - Format code"
	@echo "  lint           - Lint code"
	@echo "  security       - Security scan"
	@echo "  generate       - Generate code"
	@echo "  deps           - Update dependencies"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-push    - Push Docker image"
	@echo "  deploy         - Deploy to Kubernetes"
	@echo "  undeploy       - Undeploy from Kubernetes"
	@echo "  install-crds   - Install CRDs"
	@echo "  uninstall-crds - Uninstall CRDs"
	@echo "  run            - Run operator locally"
	@echo "  run-debug      - Run operator with debug"
	@echo "  manifests      - Generate manifests"
	@echo "  all            - Clean, deps, fmt, lint, test, build"
	@echo "  help           - Show this help"
```

## GitHub Actions Workflow

### 1. CI Workflow
```yaml
# .github/workflows/ci.yml
name: CI

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
    
    - name: Set up Go
      uses: actions/setup-go@v3
      with:
        go-version: '1.21'
    
    - name: Cache Go modules
      uses: actions/cache@v3
      with:
        path: ~/go/pkg/mod
        key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}
        restore-keys: |
          ${{ runner.os }}-go-
    
    - name: Install dependencies
      run: go mod download
    
    - name: Run tests
      run: go test -v ./operators/...
    
    - name: Run lint
      uses: golangci/golangci-lint-action@v3
      with:
        version: latest
    
    - name: Run security scan
      run: |
        go install github.com/securecodewarrior/gosec/v2/cmd/gosec@latest
        gosec ./operators/...
    
    - name: Build
      run: |
        cd operators
        make build
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.out
```

### 2. CD Workflow
```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Go
      uses: actions/setup-go@v3
      with:
        go-version: '1.21'
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Azure Container Registry
      uses: azure/docker-login@v1
      with:
        login-server: bankregistry.azurecr.io
        username: ${{ secrets.ACR_USERNAME }}
        password: ${{ secrets.ACR_PASSWORD }}
    
    - name: Build and push operators
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
        helm upgrade --install operators ./helm-charts/operators \
          --namespace interoperability-core \
          --create-namespace \
          --set global.image.tag=${{ github.sha }} \
          --set global.image.registry=bankregistry.azurecr.io
```

This completes the comprehensive Go operator CI/CD pipelines!