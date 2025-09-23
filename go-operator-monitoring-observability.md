# Go Operator Monitoring and Observability

## Monitoring Architecture

### Operator Observability Stack
```
┌─────────────────────────────────────────────────────────────────┐
│                    Go Operator Observability                    │
├─────────────────────────────────────────────────────────────────┤
│ Prometheus ←→ Grafana ←→ Jaeger ←→ OpenTelemetry               │
│     ↓           ↓         ↓           ↓                        │
│ Metrics    Dashboards  Traces    Instrumentation               │
│     ↓           ↓         ↓           ↓                        │
│ Alerts     Logs      Profiling   Health Checks                │
└─────────────────────────────────────────────────────────────────┘
```

## Prometheus Metrics for Go Operators

### 1. Operator Metrics Implementation
```go
// operators/shared/pkg/metrics/operator_metrics.go
package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	// Request processing metrics
	RequestsProcessedTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "interoperability_requests_processed_total",
			Help: "Total number of requests processed by the operator",
		},
		[]string{"request_type", "status", "operator"},
	)
	
	RequestProcessingDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "interoperability_request_processing_duration_seconds",
			Help:    "Duration of request processing",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"request_type", "operator"},
	)
	
	// Operator health metrics
	OperatorHealth = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "interoperability_operator_health",
			Help: "Health status of the operator (1=healthy, 0=unhealthy)",
		},
		[]string{"operator", "component"},
	)
	
	// Error metrics
	ErrorsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "interoperability_errors_total",
			Help: "Total number of errors encountered",
		},
		[]string{"error_type", "operator", "component"},
	)
	
	// Resource metrics
	ResourceUsage = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "interoperability_resource_usage",
			Help: "Resource usage of the operator",
		},
		[]string{"resource_type", "operator"},
	)
	
	// Custom business metrics
	SagaExecutionDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "interoperability_saga_execution_duration_seconds",
			Help:    "Duration of saga execution",
			Buckets: []float64{0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0},
		},
		[]string{"saga_type", "status"},
	)
	
	RoutingDecisionAccuracy = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "interoperability_routing_decision_accuracy",
			Help: "Accuracy of routing decisions",
		},
		[]string{"algorithm", "request_type"},
	)
	
	SecurityPolicyViolations = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "interoperability_security_policy_violations_total",
			Help: "Total number of security policy violations",
		},
		[]string{"policy_type", "severity"},
	)
)
```

### 2. Metrics Collection in Controllers
```go
// operators/interoperability-operator/controllers/interoperabilityrequest_controller.go
package controllers

import (
	"context"
	"time"
	
	"github.com/bank/interoperability-operators/shared/pkg/metrics"
	"github.com/go-logr/logr"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

func (r *InteroperabilityRequestReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	start := time.Now()
	
	// Increment request counter
	metrics.RequestsProcessedTotal.WithLabelValues("interoperability", "processing", "interoperability-operator").Inc()
	
	// Fetch the InteroperabilityRequest instance
	var request interoperabilityv1.InteroperabilityRequest
	if err := r.Get(ctx, req.NamespacedName, &request); err != nil {
		if client.IgnoreNotFound(err) != nil {
			// Increment error counter
			metrics.ErrorsTotal.WithLabelValues("fetch_error", "interoperability-operator", "controller").Inc()
			return ctrl.Result{}, err
		}
		return ctrl.Result{}, nil
	}
	
	// Process the request
	result, err := r.reconcileRequest(ctx, &request)
	
	// Record processing duration
	metrics.RequestProcessingDuration.WithLabelValues("interoperability", "interoperability-operator").Observe(time.Since(start).Seconds())
	
	if err != nil {
		// Increment error counter
		metrics.ErrorsTotal.WithLabelValues("reconcile_error", "interoperability-operator", "controller").Inc()
		// Update request status
		metrics.RequestsProcessedTotal.WithLabelValues("interoperability", "failed", "interoperability-operator").Inc()
		return ctrl.Result{}, err
	}
	
	// Update request status
	metrics.RequestsProcessedTotal.WithLabelValues("interoperability", "success", "interoperability-operator").Inc()
	
	return result, nil
}
```

## OpenTelemetry Integration

### 1. OpenTelemetry Configuration
```go
// operators/shared/pkg/telemetry/telemetry.go
package telemetry

import (
	"context"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/exporters/prometheus"
	"go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	"go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
)

type TelemetryConfig struct {
	ServiceName    string
	ServiceVersion string
	JaegerEndpoint string
	PrometheusPort int
}

func SetupTelemetry(config TelemetryConfig) error {
	// Create resource
	res, err := resource.New(context.Background(),
		resource.WithAttributes(
			semconv.ServiceName(config.ServiceName),
			semconv.ServiceVersion(config.ServiceVersion),
			semconv.DeploymentEnvironment("production"),
		),
	)
	if err != nil {
		return err
	}
	
	// Setup tracing
	if err := setupTracing(res, config.JaegerEndpoint); err != nil {
		return err
	}
	
	// Setup metrics
	if err := setupMetrics(res, config.PrometheusPort); err != nil {
		return err
	}
	
	return nil
}

func setupTracing(res *resource.Resource, jaegerEndpoint string) error {
	// Create Jaeger exporter
	exp, err := jaeger.New(jaeger.WithCollectorEndpoint(jaeger.WithEndpoint(jaegerEndpoint)))
	if err != nil {
		return err
	}
	
	// Create tracer provider
	tp := trace.NewTracerProvider(
		trace.WithBatcher(exp),
		trace.WithResource(res),
	)
	
	// Set global tracer provider
	otel.SetTracerProvider(tp)
	
	return nil
}

func setupMetrics(res *resource.Resource, prometheusPort int) error {
	// Create Prometheus exporter
	exp, err := prometheus.New()
	if err != nil {
		return err
	}
	
	// Create meter provider
	mp := metric.NewMeterProvider(
		metric.WithResource(res),
		metric.WithReader(exp),
	)
	
	// Set global meter provider
	otel.SetMeterProvider(mp)
	
	return nil
}
```

### 2. Tracing in Controllers
```go
// operators/interoperability-operator/controllers/traced_controller.go
package controllers

import (
	"context"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

func (r *InteroperabilityRequestReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	// Create tracer
	tracer := otel.Tracer("interoperability-operator")
	
	// Start span
	ctx, span := tracer.Start(ctx, "reconcile-interoperability-request")
	defer span.End()
	
	// Add attributes
	span.SetAttributes(
		attribute.String("request.name", req.Name),
		attribute.String("request.namespace", req.Namespace),
	)
	
	// Fetch the InteroperabilityRequest instance
	var request interoperabilityv1.InteroperabilityRequest
	if err := r.Get(ctx, req.NamespacedName, &request); err != nil {
		span.RecordError(err)
		span.SetAttributes(attribute.String("error.type", "fetch_error"))
		return ctrl.Result{}, err
	}
	
	// Add request attributes
	span.SetAttributes(
		attribute.String("request.id", request.Spec.RequestId),
		attribute.String("request.type", request.Spec.RequestType),
		attribute.String("request.phase", request.Status.Phase),
	)
	
	// Process the request
	result, err := r.reconcileRequest(ctx, &request)
	
	if err != nil {
		span.RecordError(err)
		span.SetAttributes(attribute.String("error.type", "reconcile_error"))
	} else {
		span.SetAttributes(attribute.String("result.requeue", "false"))
	}
	
	return result, err
}
```

## Grafana Dashboards

### 1. Operator Health Dashboard
```json
{
  "dashboard": {
    "title": "Bank Interoperability Operators - Health",
    "panels": [
      {
        "title": "Operator Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"interoperability-operator\"}",
            "legendFormat": "Interoperability Operator"
          },
          {
            "expr": "up{job=\"saga-operator\"}",
            "legendFormat": "Saga Operator"
          },
          {
            "expr": "up{job=\"routing-operator\"}",
            "legendFormat": "Routing Operator"
          },
          {
            "expr": "up{job=\"security-operator\"}",
            "legendFormat": "Security Operator"
          }
        ]
      },
      {
        "title": "Request Processing Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(interoperability_requests_processed_total[5m])",
            "legendFormat": "{{request_type}} - {{status}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(interoperability_errors_total[5m])",
            "legendFormat": "{{error_type}} - {{operator}}"
          }
        ]
      },
      {
        "title": "Processing Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(interoperability_request_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "95th Percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(interoperability_request_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "50th Percentile"
          }
        ]
      }
    ]
  }
}
```

### 2. Business Metrics Dashboard
```json
{
  "dashboard": {
    "title": "Bank Interoperability Operators - Business Metrics",
    "panels": [
      {
        "title": "Saga Execution Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(interoperability_saga_execution_duration_seconds_bucket[5m]))",
            "legendFormat": "{{saga_type}} - 95th Percentile"
          }
        ]
      },
      {
        "title": "Routing Decision Accuracy",
        "type": "graph",
        "targets": [
          {
            "expr": "interoperability_routing_decision_accuracy",
            "legendFormat": "{{algorithm}} - {{request_type}}"
          }
        ]
      },
      {
        "title": "Security Policy Violations",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(interoperability_security_policy_violations_total[5m])",
            "legendFormat": "{{policy_type}} - {{severity}}"
          }
        ]
      },
      {
        "title": "Resource Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "interoperability_resource_usage",
            "legendFormat": "{{resource_type}} - {{operator}}"
          }
        ]
      }
    ]
  }
}
```

## Jaeger Tracing Configuration

### 1. Jaeger Configuration
```yaml
# helm-charts/operators/templates/monitoring/jaeger-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: jaeger-config
  namespace: interoperability-monitoring
data:
  jaeger.yaml: |
    # Jaeger configuration
    jaeger:
      enabled: true
      collector:
        endpoint: "http://jaeger-collector:14268/api/traces"
        timeout: "30s"
      query:
        endpoint: "http://jaeger-query:16686"
      agent:
        endpoint: "jaeger-agent:6831"
        protocol: "udp"
      
      # Sampling configuration
      sampling:
        type: "probabilistic"
        param: 1.0
      
      # Service configuration
      service:
        name: "interoperability-operators"
        version: "1.0.0"
        environment: "production"
```

### 2. Distributed Tracing
```go
// operators/shared/pkg/tracing/distributed_tracing.go
package tracing

import (
	"context"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

// TraceRequest traces a request across multiple operators
func TraceRequest(ctx context.Context, requestId string, requestType string) (context.Context, trace.Span) {
	tracer := otel.Tracer("interoperability-operators")
	
	ctx, span := tracer.Start(ctx, "process-interoperability-request")
	
	span.SetAttributes(
		attribute.String("request.id", requestId),
		attribute.String("request.type", requestType),
		attribute.String("service.name", "interoperability-operators"),
	)
	
	return ctx, span
}

// TraceOperatorOperation traces an operation within an operator
func TraceOperatorOperation(ctx context.Context, operator string, operation string) (context.Context, trace.Span) {
	tracer := otel.Tracer(operator)
	
	ctx, span := tracer.Start(ctx, operation)
	
	span.SetAttributes(
		attribute.String("operator.name", operator),
		attribute.String("operation.name", operation),
	)
	
	return ctx, span
}
```

## Health Checks and Probes

### 1. Health Check Implementation
```go
// operators/shared/pkg/health/health_check.go
package health

import (
	"context"
	"net/http"
	"time"
	
	"github.com/go-logr/logr"
	"k8s.io/apimachinery/pkg/runtime"
	"sigs.k8s.io/controller-runtime/pkg/manager"
)

type HealthChecker struct {
	client client.Client
	logger logr.Logger
}

func NewHealthChecker(client client.Client, logger logr.Logger) *HealthChecker {
	return &HealthChecker{
		client: client,
		logger: logger,
	}
}

func (h *HealthChecker) CheckHealth(ctx context.Context) error {
	// Check if the operator can connect to the Kubernetes API
	if err := h.checkKubernetesConnection(ctx); err != nil {
		h.logger.Error(err, "Kubernetes connection check failed")
		return err
	}
	
	// Check if the operator can access required resources
	if err := h.checkResourceAccess(ctx); err != nil {
		h.logger.Error(err, "Resource access check failed")
		return err
	}
	
	// Check if the operator is processing requests
	if err := h.checkRequestProcessing(ctx); err != nil {
		h.logger.Error(err, "Request processing check failed")
		return err
	}
	
	return nil
}

func (h *HealthChecker) checkKubernetesConnection(ctx context.Context) error {
	// Check if we can list namespaces
	_, err := h.client.List(ctx, &corev1.NamespaceList{})
	return err
}

func (h *HealthChecker) checkResourceAccess(ctx context.Context) error {
	// Check if we can access CRDs
	var crdList apiextensionsv1.CustomResourceDefinitionList
	return h.client.List(ctx, &crdList)
}

func (h *HealthChecker) checkRequestProcessing(ctx context.Context) error {
	// Check if we can list our custom resources
	var requestList interoperabilityv1.InteroperabilityRequestList
	return h.client.List(ctx, &requestList)
}
```

### 2. Readiness Check Implementation
```go
// operators/shared/pkg/health/readiness_check.go
package health

import (
	"context"
	"time"
)

type ReadinessChecker struct {
	client client.Client
	logger logr.Logger
}

func NewReadinessChecker(client client.Client, logger logr.Logger) *ReadinessChecker {
	return &ReadinessChecker{
		client: client,
		logger: logger,
	}
}

func (r *ReadinessChecker) CheckReadiness(ctx context.Context) error {
	// Check if the operator is ready to process requests
	if err := r.checkOperatorReady(ctx); err != nil {
		r.logger.Error(err, "Operator readiness check failed")
		return err
	}
	
	// Check if required dependencies are available
	if err := r.checkDependencies(ctx); err != nil {
		r.logger.Error(err, "Dependencies check failed")
		return err
	}
	
	return nil
}

func (r *ReadinessChecker) checkOperatorReady(ctx context.Context) error {
	// Check if the operator has been running for at least 30 seconds
	// This ensures the operator has had time to initialize
	time.Sleep(30 * time.Second)
	return nil
}

func (r *ReadinessChecker) checkDependencies(ctx context.Context) error {
	// Check if required services are available
	// This could include checking for required ConfigMaps, Secrets, etc.
	return nil
}
```

## Alerting Rules

### 1. Prometheus Alert Rules
```yaml
# helm-charts/operators/templates/monitoring/alertrules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: interoperability-operators-alerts
  namespace: interoperability-monitoring
  labels:
    app.kubernetes.io/component: monitoring
spec:
  groups:
  - name: interoperability-operators
    rules:
    - alert: OperatorDown
      expr: up{job=~"interoperability-.*-operator"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Operator {{ $labels.job }} is down"
        description: "The {{ $labels.job }} operator has been down for more than 1 minute"
    
    - alert: HighErrorRate
      expr: rate(interoperability_errors_total[5m]) > 0.1
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High error rate in {{ $labels.operator }}"
        description: "The {{ $labels.operator }} operator has a high error rate of {{ $value }} errors per second"
    
    - alert: HighProcessingDuration
      expr: histogram_quantile(0.95, rate(interoperability_request_processing_duration_seconds_bucket[5m])) > 10
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High processing duration in {{ $labels.operator }}"
        description: "The {{ $labels.operator }} operator has a high 95th percentile processing duration of {{ $value }} seconds"
    
    - alert: SecurityPolicyViolations
      expr: rate(interoperability_security_policy_violations_total[5m]) > 0
      for: 0m
      labels:
        severity: critical
      annotations:
        summary: "Security policy violations detected"
        description: "{{ $value }} security policy violations per second detected in {{ $labels.policy_type }}"
    
    - alert: LowRoutingAccuracy
      expr: interoperability_routing_decision_accuracy < 0.8
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "Low routing decision accuracy"
        description: "Routing decision accuracy is {{ $value }} for {{ $labels.algorithm }}"
```

## Logging Configuration

### 1. Structured Logging
```go
// operators/shared/pkg/logging/structured_logger.go
package logging

import (
	"context"
	"encoding/json"
	"time"
	
	"github.com/go-logr/logr"
	"go.opentelemetry.io/otel/trace"
)

type StructuredLogger struct {
	logger logr.Logger
}

func NewStructuredLogger(logger logr.Logger) *StructuredLogger {
	return &StructuredLogger{
		logger: logger,
	}
}

func (s *StructuredLogger) LogRequest(ctx context.Context, requestId string, requestType string, status string) {
	span := trace.SpanFromContext(ctx)
	
	logData := map[string]interface{}{
		"timestamp":    time.Now().UTC().Format(time.RFC3339),
		"request_id":  requestId,
		"request_type": requestType,
		"status":      status,
		"trace_id":    span.SpanContext().TraceID().String(),
		"span_id":     span.SpanContext().SpanID().String(),
	}
	
	jsonData, _ := json.Marshal(logData)
	s.logger.Info(string(jsonData))
}

func (s *StructuredLogger) LogError(ctx context.Context, err error, component string, operation string) {
	span := trace.SpanFromContext(ctx)
	
	logData := map[string]interface{}{
		"timestamp":  time.Now().UTC().Format(time.RFC3339),
		"error":     err.Error(),
		"component": component,
		"operation": operation,
		"trace_id":  span.SpanContext().TraceID().String(),
		"span_id":   span.SpanContext().SpanID().String(),
	}
	
	jsonData, _ := json.Marshal(logData)
	s.logger.Error(err, string(jsonData))
}
```

This completes the Go operator monitoring and observability setup!