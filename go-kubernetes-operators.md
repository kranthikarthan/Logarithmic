# Go-based Kubernetes Operators for Bank Interoperability Layer

## Operator Architecture Overview

### Operator Structure
```
operators/
├── interoperability-operator/      # Main interoperability operator
├── saga-operator/                  # Saga orchestration operator
├── routing-operator/               # Intelligent routing operator
├── security-operator/              # Security and compliance operator
├── monitoring-operator/            # Monitoring and observability operator
└── shared/                        # Shared operator libraries
    ├── pkg/
    │   ├── apis/
    │   ├── controllers/
    │   ├── reconcilers/
    │   └── utils/
    └── go.mod
```

## Main Interoperability Operator

### 1. Project Structure (operators/interoperability-operator/)
```
interoperability-operator/
├── main.go
├── go.mod
├── go.sum
├── Dockerfile
├── Makefile
├── api/
│   └── v1/
│       ├── groupversion_info.go
│       ├── interoperabilityrequest_types.go
│       └── zz_generated.deepcopy.go
├── controllers/
│   ├── interoperabilityrequest_controller.go
│   └── reconciliation.go
├── pkg/
│   ├── client/
│   ├── reconciler/
│   └── utils/
└── config/
    ├── crd/
    ├── rbac/
    └── manager/
```

### 2. Main Operator Entry Point
```go
// operators/interoperability-operator/main.go
package main

import (
	"flag"
	"os"

	"k8s.io/apimachinery/pkg/runtime"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	_ "k8s.io/client-go/plugin/pkg/client/auth/gcp"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"

	interoperabilityv1 "github.com/bank/interoperability-operator/api/v1"
	"github.com/bank/interoperability-operator/controllers"
	"github.com/bank/interoperability-operator/pkg/client"
	"github.com/bank/interoperability-operator/pkg/reconciler"
)

var (
	scheme   = runtime.NewScheme()
	setupLog = ctrl.Log.WithName("setup")
)

func init() {
	utilruntime.Must(clientgoscheme.AddToScheme(scheme))
	utilruntime.Must(interoperabilityv1.AddToScheme(scheme))
}

func main() {
	var metricsAddr string
	var enableLeaderElection bool
	var probeAddr string
	flag.StringVar(&metricsAddr, "metrics-bind-address", ":8080", "The address the metric endpoint binds to.")
	flag.StringVar(&probeAddr, "health-probe-bind-address", ":8081", "The address the probe endpoint binds to.")
	flag.BoolVar(&enableLeaderElection, "leader-elect", false,
		"Enable leader election for controller manager. "+
			"Enabling this will ensure there is only one active controller manager.")
	flag.Parse()

	ctrl.SetLogger(zap.New(zap.UseFlagOptions(&zap.Options{
		Development: true,
	})))

	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
		Scheme:                 scheme,
		MetricsBindAddress:     metricsAddr,
		Port:                   9443,
		HealthProbeBindAddress: probeAddr,
		LeaderElection:         enableLeaderElection,
		LeaderElectionID:       "interoperability-operator.bank.com",
	})
	if err != nil {
		setupLog.Error(err, "unable to start manager")
		os.Exit(1)
	}

	if err = (&controllers.InteroperabilityRequestReconciler{
		Client:   mgr.GetClient(),
		Scheme:   mgr.GetScheme(),
		Recorder: mgr.GetEventRecorderFor("interoperability-operator"),
	}).SetupWithManager(mgr); err != nil {
		setupLog.Error(err, "unable to create controller", "controller", "InteroperabilityRequest")
		os.Exit(1)
	}

	if err := mgr.AddHealthzCheck("healthz", mgr.GetWebhookServer().StartedChecker()); err != nil {
		setupLog.Error(err, "unable to set up health check")
		os.Exit(1)
	}

	if err := mgr.AddReadyzCheck("readyz", mgr.GetWebhookServer().StartedChecker()); err != nil {
		setupLog.Error(err, "unable to set up ready check")
		os.Exit(1)
	}

	setupLog.Info("starting manager")
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		setupLog.Error(err, "problem running manager")
		os.Exit(1)
	}
}
```

### 3. Custom Resource Definition
```go
// operators/interoperability-operator/api/v1/interoperabilityrequest_types.go
package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// InteroperabilityRequestSpec defines the desired state of InteroperabilityRequest
type InteroperabilityRequestSpec struct {
	// RequestId is the unique identifier for the request
	RequestId string `json:"requestId"`
	
	// RequestType defines the type of banking request
	RequestType string `json:"requestType"`
	
	// Payload contains the request data
	Payload string `json:"payload"`
	
	// RoutingStrategy defines how the request should be routed
	RoutingStrategy string `json:"routingStrategy"`
	
	// Dependencies lists the steps that must complete before this request
	Dependencies []StepDependency `json:"dependencies,omitempty"`
	
	// SecurityContext contains security-related information
	SecurityContext SecurityContext `json:"securityContext"`
}

// InteroperabilityRequestStatus defines the observed state of InteroperabilityRequest
type InteroperabilityRequestStatus struct {
	// Phase represents the current phase of the request
	Phase string `json:"phase,omitempty"`
	
	// Message provides additional information about the status
	Message string `json:"message,omitempty"`
	
	// LastTransitionTime is the last time the status changed
	LastTransitionTime *metav1.Time `json:"lastTransitionTime,omitempty"`
	
	// Steps contains the status of individual processing steps
	Steps []StepStatus `json:"steps,omitempty"`
	
	// Conditions represents the latest available observations
	Conditions []metav1.Condition `json:"conditions,omitempty"`
}

// StepDependency defines a dependency between processing steps
type StepDependency struct {
	StepId    string   `json:"stepId"`
	DependsOn []string `json:"dependsOn"`
}

// StepStatus defines the status of a processing step
type StepStatus struct {
	StepId    string `json:"stepId"`
	Status    string `json:"status"`
	Message   string `json:"message,omitempty"`
	StartTime *metav1.Time `json:"startTime,omitempty"`
	EndTime   *metav1.Time `json:"endTime,omitempty"`
}

// SecurityContext contains security-related information
type SecurityContext struct {
	EncryptionKey string            `json:"encryptionKey,omitempty"`
	AccessToken   string            `json:"accessToken,omitempty"`
	Policies      map[string]string `json:"policies,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:scope=Namespaced
// +kubebuilder:printcolumn:name="Phase",type="string",JSONPath=".status.phase"
// +kubebuilder:printcolumn:name="Message",type="string",JSONPath=".status.message"
// +kubebuilder:printcolumn:name="Age",type="date",JSONPath=".metadata.creationTimestamp"

// InteroperabilityRequest is the Schema for the interoperabilityrequests API
type InteroperabilityRequest struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   InteroperabilityRequestSpec   `json:"spec,omitempty"`
	Status InteroperabilityRequestStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

// InteroperabilityRequestList contains a list of InteroperabilityRequest
type InteroperabilityRequestList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []InteroperabilityRequest `json:"items"`
}

func init() {
	SchemeBuilder.Register(&InteroperabilityRequest{}, &InteroperabilityRequestList{})
}
```

### 4. Controller Implementation
```go
// operators/interoperability-operator/controllers/interoperabilityrequest_controller.go
package controllers

import (
	"context"
	"fmt"
	"time"

	"github.com/go-logr/logr"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/event"
	"sigs.k8s.io/controller-runtime/pkg/predicate"

	interoperabilityv1 "github.com/bank/interoperability-operator/api/v1"
	"github.com/bank/interoperability-operator/pkg/reconciler"
)

// InteroperabilityRequestReconciler reconciles a InteroperabilityRequest object
type InteroperabilityRequestReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

// +kubebuilder:rbac:groups=interoperability.bank.com,resources=interoperabilityrequests,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=interoperability.bank.com,resources=interoperabilityrequests/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=interoperability.bank.com,resources=interoperabilityrequests/finalizers,verbs=update
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=core,resources=services,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=core,resources=configmaps,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=core,resources=secrets,verbs=get;list;watch;create;update;patch;delete

// Reconcile is part of the main kubernetes reconciliation loop
func (r *InteroperabilityRequestReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := logr.FromContext(ctx)
	
	// Fetch the InteroperabilityRequest instance
	var request interoperabilityv1.InteroperabilityRequest
	if err := r.Get(ctx, req.NamespacedName, &request); err != nil {
		if client.IgnoreNotFound(err) != nil {
			log.Error(err, "unable to fetch InteroperabilityRequest")
			return ctrl.Result{}, err
		}
		return ctrl.Result{}, nil
	}

	// Check if the object is being deleted
	if !request.ObjectMeta.DeletionTimestamp.IsZero() {
		return r.handleDeletion(ctx, &request)
	}

	// Add finalizer if not present
	if !containsString(request.ObjectMeta.Finalizers, interoperabilityv1.InteroperabilityRequestFinalizer) {
		request.ObjectMeta.Finalizers = append(request.ObjectMeta.Finalizers, interoperabilityv1.InteroperabilityRequestFinalizer)
		if err := r.Update(ctx, &request); err != nil {
			return ctrl.Result{}, err
		}
	}

	// Reconcile the request
	result, err := r.reconcileRequest(ctx, &request)
	if err != nil {
		log.Error(err, "failed to reconcile InteroperabilityRequest")
		r.Recorder.Event(&request, "Warning", "ReconcileError", err.Error())
		return ctrl.Result{}, err
	}

	// Update status
	if err := r.Status().Update(ctx, &request); err != nil {
		log.Error(err, "failed to update InteroperabilityRequest status")
		return ctrl.Result{}, err
	}

	return result, nil
}

func (r *InteroperabilityRequestReconciler) reconcileRequest(ctx context.Context, request *interoperabilityv1.InteroperabilityRequest) (ctrl.Result, error) {
	log := logr.FromContext(ctx)
	
	// Initialize reconciler
	reconciler := reconciler.NewInteroperabilityRequestReconciler(r.Client, r.Scheme, r.Recorder)
	
	// Process the request based on its phase
	switch request.Status.Phase {
	case "":
		return reconciler.InitializeRequest(ctx, request)
	case "Initialized":
		return reconciler.ValidateRequest(ctx, request)
	case "Validated":
		return reconciler.RouteRequest(ctx, request)
	case "Routed":
		return reconciler.ExecuteRequest(ctx, request)
	case "Executing":
		return reconciler.MonitorExecution(ctx, request)
	case "Completed", "Failed":
		return reconciler.FinalizeRequest(ctx, request)
	default:
		log.Info("unknown phase", "phase", request.Status.Phase)
		return ctrl.Result{}, nil
	}
}

// SetupWithManager sets up the controller with the Manager
func (r *InteroperabilityRequestReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&interoperabilityv1.InteroperabilityRequest{}).
		WithEventFilter(predicate.Funcs{
			CreateFunc: func(e event.CreateEvent) bool {
				return true
			},
			UpdateFunc: func(e event.UpdateEvent) bool {
				oldObj := e.ObjectOld.(*interoperabilityv1.InteroperabilityRequest)
				newObj := e.ObjectNew.(*interoperabilityv1.InteroperabilityRequest)
				return oldObj.Status.Phase != newObj.Status.Phase
			},
			DeleteFunc: func(e event.DeleteEvent) bool {
				return true
			},
		}).
		Complete(r)
}
```

## Saga Operator

### 1. Saga Operator Structure
```go
// operators/saga-operator/controllers/saga_controller.go
package controllers

import (
	"context"
	"time"

	"github.com/go-logr/logr"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"

	interoperabilityv1 "github.com/bank/interoperability-operator/api/v1"
	sagav1 "github.com/bank/saga-operator/api/v1"
)

// SagaReconciler reconciles a Saga object
type SagaReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

// +kubebuilder:rbac:groups=saga.bank.com,resources=sagas,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=saga.bank.com,resources=sagas/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=interoperability.bank.com,resources=interoperabilityrequests,verbs=get;list;watch;update;patch

func (r *SagaReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := logr.FromContext(ctx)
	
	// Fetch the Saga instance
	var saga sagav1.Saga
	if err := r.Get(ctx, req.NamespacedName, &saga); err != nil {
		if client.IgnoreNotFound(err) != nil {
			log.Error(err, "unable to fetch Saga")
			return ctrl.Result{}, err
		}
		return ctrl.Result{}, nil
	}

	// Reconcile saga execution
	return r.reconcileSaga(ctx, &saga)
}

func (r *SagaReconciler) reconcileSaga(ctx context.Context, saga *sagav1.Saga) (ctrl.Result, error) {
	log := logr.FromContext(ctx)
	
	// Check if saga is completed
	if saga.Status.Phase == "Completed" || saga.Status.Phase == "Failed" {
		return ctrl.Result{}, nil
	}

	// Execute saga steps
	for _, step := range saga.Spec.Steps {
		if !r.isStepCompleted(saga, step.StepId) {
			if r.canExecuteStep(saga, step) {
				if err := r.executeStep(ctx, saga, step); err != nil {
					log.Error(err, "failed to execute step", "stepId", step.StepId)
					return ctrl.Result{}, err
				}
			}
		}
	}

	// Check if all steps are completed
	if r.allStepsCompleted(saga) {
		saga.Status.Phase = "Completed"
		saga.Status.Message = "All steps completed successfully"
	} else {
		// Requeue to continue processing
		return ctrl.Result{RequeueAfter: time.Second * 10}, nil
	}

	return ctrl.Result{}, nil
}
```

## Routing Operator

### 1. Routing Operator Implementation
```go
// operators/routing-operator/controllers/routing_controller.go
package controllers

import (
	"context"
	"encoding/json"

	"github.com/go-logr/logr"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"

	interoperabilityv1 "github.com/bank/interoperability-operator/api/v1"
	routingv1 "github.com/bank/routing-operator/api/v1"
)

// RoutingDecisionReconciler reconciles a RoutingDecision object
type RoutingDecisionReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

func (r *RoutingDecisionReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := logr.FromContext(ctx)
	
	// Fetch the RoutingDecision instance
	var decision routingv1.RoutingDecision
	if err := r.Get(ctx, req.NamespacedName, &decision); err != nil {
		if client.IgnoreNotFound(err) != nil {
			log.Error(err, "unable to fetch RoutingDecision")
			return ctrl.Result{}, err
		}
		return ctrl.Result{}, nil
	}

	// Process routing decision
	return r.processRoutingDecision(ctx, &decision)
}

func (r *RoutingDecisionReconciler) processRoutingDecision(ctx context.Context, decision *routingv1.RoutingDecision) (ctrl.Result, error) {
	log := logr.FromContext(ctx)
	
	// Analyze request characteristics
	profile, err := r.analyzeRequest(decision.Spec.Request)
	if err != nil {
		log.Error(err, "failed to analyze request")
		return ctrl.Result{}, err
	}

	// Calculate routing scores
	onPremScore := r.calculateOnPremScore(profile)
	cloudScore := r.calculateCloudScore(profile)

	// Determine routing strategy
	strategy := r.determineStrategy(onPremScore, cloudScore)
	
	// Update decision
	decision.Status.Strategy = strategy
	decision.Status.Confidence = r.calculateConfidence(onPremScore, cloudScore)
	decision.Status.Reasoning = r.generateReasoning(profile, strategy)

	return ctrl.Result{}, nil
}
```

## Security Operator

### 1. Security Operator Implementation
```go
// operators/security-operator/controllers/security_controller.go
package controllers

import (
	"context"
	"time"

	"github.com/go-logr/logr"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"

	securityv1 "github.com/bank/security-operator/api/v1"
)

// SecurityPolicyReconciler reconciles a SecurityPolicy object
type SecurityPolicyReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

func (r *SecurityPolicyReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := logr.FromContext(ctx)
	
	// Fetch the SecurityPolicy instance
	var policy securityv1.SecurityPolicy
	if err := r.Get(ctx, req.NamespacedName, &policy); err != nil {
		if client.IgnoreNotFound(err) != nil {
			log.Error(err, "unable to fetch SecurityPolicy")
			return ctrl.Result{}, err
		}
		return ctrl.Result{}, nil
	}

	// Enforce security policy
	return r.enforceSecurityPolicy(ctx, &policy)
}

func (r *SecurityPolicyReconciler) enforceSecurityPolicy(ctx context.Context, policy *securityv1.SecurityPolicy) (ctrl.Result, error) {
	log := logr.FromContext(ctx)
	
	// Validate security requirements
	if err := r.validateSecurityRequirements(ctx, policy); err != nil {
		log.Error(err, "security validation failed")
		policy.Status.EnforcementStatus = "Failed"
		policy.Status.Message = err.Error()
		return ctrl.Result{}, err
	}

	// Apply security controls
	if err := r.applySecurityControls(ctx, policy); err != nil {
		log.Error(err, "failed to apply security controls")
		return ctrl.Result{}, err
	}

	policy.Status.EnforcementStatus = "Enforced"
	policy.Status.Message = "Security policy enforced successfully"

	return ctrl.Result{}, nil
}
```

## Go Module Configuration

### 1. Main go.mod
```go
// operators/go.mod
module github.com/bank/interoperability-operators

go 1.21

require (
	k8s.io/api v0.28.0
	k8s.io/apimachinery v0.28.0
	k8s.io/client-go v0.28.0
	sigs.k8s.io/controller-runtime v0.16.0
	github.com/go-logr/logr v1.2.4
	github.com/onsi/ginkgo/v2 v2.13.0
	github.com/onsi/gomega v1.28.0
	github.com/prometheus/client_golang v1.17.0
	github.com/spf13/cobra v1.7.0
	github.com/spf13/viper v1.16.0
)

require (
	github.com/beorn7/perks v1.0.1 // indirect
	github.com/cespare/xxhash/v2 v2.2.0 // indirect
	github.com/davecgh/go-spew v1.1.1 // indirect
	github.com/emicklei/go-restful/v3 v3.11.0 // indirect
	github.com/evanphx/json-patch/v5 v5.6.0 // indirect
	github.com/fsnotify/fsnotify v1.6.0 // indirect
	github.com/go-openapi/jsonpointer v0.19.6 // indirect
	github.com/go-openapi/jsonreference v0.20.2 // indirect
	github.com/go-openapi/swag v0.22.3 // indirect
	github.com/gogo/protobuf v1.3.2 // indirect
	github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da // indirect
	github.com/golang/protobuf v1.5.3 // indirect
	github.com/google/gnostic-models v0.6.8 // indirect
	github.com/google/go-cmp v0.5.9 // indirect
	github.com/google/gofuzz v1.2.0 // indirect
	github.com/google/uuid v1.3.0 // indirect
	github.com/hashicorp/hcl v1.0.0 // indirect
	github.com/imdario/mergo v0.3.6 // indirect
	github.com/josharian/intern v1.0.0 // indirect
	github.com/json-iterator/go v1.1.12 // indirect
	github.com/magiconair/properties v1.8.7 // indirect
	github.com/mailru/easyjson v0.7.7 // indirect
	github.com/matttproud/golang_protobuf_extensions v1.0.4 // indirect
	github.com/mitchellh/mapstructure v1.5.0 // indirect
	github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect
	github.com/modern-go/reflect2 v1.0.2 // indirect
	github.com/munnerz/goautoneg v0.0.0-20191010083416-a7dc8b61c822 // indirect
	github.com/pelletier/go-toml/v2 v2.0.8 // indirect
	github.com/pkg/errors v0.9.1 // indirect
	github.com/prometheus/client_model v0.4.1-0.20230718164431-9a2bf3000d16 // indirect
	github.com/prometheus/common v0.44.0 // indirect
	github.com/prometheus/procfs v0.11.1 // indirect
	github.com/spf13/afero v1.9.5 // indirect
	github.com/spf13/cast v1.5.1 // indirect
	github.com/spf13/jwalterweatherman v1.1.0 // indirect
	github.com/spf13/pflag v1.0.5 // indirect
	github.com/subosito/gotenv v1.4.2 // indirect
	golang.org/x/net v0.13.0 // indirect
	golang.org/x/oauth2 v0.8.0 // indirect
	golang.org/x/sys v0.10.0 // indirect
	golang.org/x/term v0.10.0 // indirect
	golang.org/x/text v0.11.0 // indirect
	golang.org/x/time v0.3.0 // indirect
	gomodules.xyz/jsonpatch/v2 v2.4.0 // indirect
	google.golang.org/appengine v1.6.7 // indirect
	google.golang.org/protobuf v1.31.0 // indirect
	gopkg.in/inf.v0 v0.9.1 // indirect
	gopkg.in/ini.v1 v1.67.0 // indirect
	gopkg.in/yaml.v2 v2.4.0 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
	k8s.io/apiextensions-apiserver v0.28.0 // indirect
	k8s.io/component-base v0.28.0 // indirect
	k8s.io/klog/v2 v2.100.1 // indirect
	k8s.io/kube-openapi v0.0.0-20230717233707-2695361300d9 // indirect
	k8s.io/utils v0.0.0-20230726121419-3b25d923346b // indirect
	sigs.k8s.io/json v0.0.0-20221116044647-bc3834ca7abd // indirect
	sigs.k8s.io/structured-merge-diff/v4 v4.3.0 // indirect
	sigs.k8s.io/yaml v1.3.0 // indirect
)
```

## Docker Configuration for Go Operators

### 1. Multi-stage Dockerfile
```dockerfile
# operators/interoperability-operator/Dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /workspace

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the operator
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o manager main.go

# Final stage
FROM alpine:3.18

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy the binary
COPY --from=builder /workspace/manager .

# Create non-root user
RUN addgroup -g 1001 operator && \
    adduser -D -u 1001 -G operator operator

USER operator

ENTRYPOINT ["./manager"]
```

## Helm Charts for Go Operators

### 1. Operator Deployment Chart
```yaml
# helm-charts/operators/values.yaml
global:
  imageRegistry: "bankregistry.azurecr.io"
  imageTag: "latest"
  imagePullSecrets:
    - name: "acr-secret"

# Interoperability Operator
interoperabilityOperator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/interoperability-operator"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "200m"
      memory: "256Mi"
  
  # Operator configuration
  config:
    metricsBindAddress: ":8080"
    healthProbeBindAddress: ":8081"
    leaderElection: true
    leaderElectionID: "interoperability-operator.bank.com"

# Saga Operator
sagaOperator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/saga-operator"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "200m"
      memory: "256Mi"

# Routing Operator
routingOperator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/routing-operator"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "200m"
      memory: "256Mi"

# Security Operator
securityOperator:
  enabled: true
  replicaCount: 2
  image:
    repository: "bankregistry.azurecr.io/security-operator"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "200m"
      memory: "256Mi"
```

This completes the Go-based Kubernetes operators implementation for the bank interoperability layer!