# Java Operator Monitoring and Observability

## Monitoring Architecture

### Java Operator Observability Stack
```
┌─────────────────────────────────────────────────────────────────┐
│                    Java Operator Observability                  │
├─────────────────────────────────────────────────────────────────┤
│ Prometheus ←→ Grafana ←→ Jaeger ←→ OpenTelemetry               │
│     ↓           ↓         ↓           ↓                        │
│ Metrics    Dashboards  Traces    Instrumentation               │
│     ↓           ↓         ↓           ↓                        │
│ Alerts     Logs      Profiling   Health Checks                │
└─────────────────────────────────────────────────────────────────┘
```

## Spring Boot Actuator Metrics

### 1. Actuator Configuration
```java
// operators/shared/src/main/java/com/bank/interoperability/operator/config/MonitoringConfig.java
package com.bank.interoperability.operator.config;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.Gauge;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MonitoringConfig {
    
    @Bean
    public Counter requestsProcessedCounter(MeterRegistry meterRegistry) {
        return Counter.builder("interoperability.requests.processed.total")
            .description("Total number of requests processed by the operator")
            .tag("operator", "interoperability")
            .register(meterRegistry);
    }
    
    @Bean
    public Counter errorsCounter(MeterRegistry meterRegistry) {
        return Counter.builder("interoperability.errors.total")
            .description("Total number of errors encountered")
            .tag("operator", "interoperability")
            .register(meterRegistry);
    }
    
    @Bean
    public Timer requestProcessingTimer(MeterRegistry meterRegistry) {
        return Timer.builder("interoperability.request.processing.duration")
            .description("Duration of request processing")
            .tag("operator", "interoperability")
            .register(meterRegistry);
    }
    
    @Bean
    public Gauge operatorHealthGauge(MeterRegistry meterRegistry) {
        return Gauge.builder("interoperability.operator.health")
            .description("Health status of the operator")
            .tag("operator", "interoperability")
            .register(meterRegistry, this, MonitoringConfig::getHealthStatus);
    }
    
    private double getHealthStatus() {
        // Return 1 for healthy, 0 for unhealthy
        return 1.0;
    }
}
```

### 2. Custom Metrics Service
```java
// operators/shared/src/main/java/com/bank/interoperability/operator/service/MetricsService.java
package com.bank.interoperability.operator.service;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class MetricsService {
    
    private final Counter requestsProcessedCounter;
    private final Counter errorsCounter;
    private final Timer requestProcessingTimer;
    
    @Autowired
    public MetricsService(MeterRegistry meterRegistry) {
        this.requestsProcessedCounter = Counter.builder("interoperability.requests.processed.total")
            .description("Total number of requests processed")
            .register(meterRegistry);
        
        this.errorsCounter = Counter.builder("interoperability.errors.total")
            .description("Total number of errors")
            .register(meterRegistry);
        
        this.requestProcessingTimer = Timer.builder("interoperability.request.processing.duration")
            .description("Request processing duration")
            .register(meterRegistry);
    }
    
    public void incrementRequestsProcessed(String requestType, String status) {
        requestsProcessedCounter.increment(
            io.micrometer.core.instrument.Tags.of(
                "request_type", requestType,
                "status", status
            )
        );
    }
    
    public void incrementErrors(String errorType, String component) {
        errorsCounter.increment(
            io.micrometer.core.instrument.Tags.of(
                "error_type", errorType,
                "component", component
            )
        );
    }
    
    public Timer.Sample startRequestProcessing() {
        return Timer.start(requestProcessingTimer);
    }
    
    public void recordRequestProcessing(Timer.Sample sample, String requestType) {
        sample.stop(Timer.builder("interoperability.request.processing.duration")
            .tag("request_type", requestType)
            .register(requestProcessingTimer.getId().getMeterRegistry()));
    }
}
```

### 3. Metrics Collection in Controllers
```java
// operators/interoperability-operator/src/main/java/com/bank/interoperability/operator/controller/InteroperabilityRequestController.java
package com.bank.interoperability.operator.controller;

import com.bank.interoperability.operator.model.InteroperabilityRequest;
import com.bank.interoperability.operator.service.InteroperabilityRequestService;
import com.bank.interoperability.operator.service.MetricsService;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.Watcher;
import io.fabric8.kubernetes.client.WatcherException;
import io.micrometer.core.instrument.Timer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;

@Component
public class InteroperabilityRequestController {
    
    private static final Logger logger = LoggerFactory.getLogger(InteroperabilityRequestController.class);
    
    @Autowired
    private KubernetesClient kubernetesClient;
    
    @Autowired
    private InteroperabilityRequestService requestService;
    
    @Autowired
    private MetricsService metricsService;
    
    private Watcher<InteroperabilityRequest> watcher;
    
    @PostConstruct
    public void startWatching() {
        logger.info("Starting to watch InteroperabilityRequest resources");
        
        watcher = kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .watch(new Watcher<InteroperabilityRequest>() {
                @Override
                public void eventReceived(Action action, InteroperabilityRequest resource) {
                    logger.info("Received {} event for InteroperabilityRequest: {}", 
                        action, resource.getMetadata().getName());
                    
                    Timer.Sample sample = metricsService.startRequestProcessing();
                    
                    try {
                        switch (action) {
                            case ADDED:
                            case MODIFIED:
                                requestService.reconcileRequest(resource);
                                metricsService.incrementRequestsProcessed(
                                    resource.getSpec().getRequestType(), "success");
                                break;
                            case DELETED:
                                requestService.handleDeletion(resource);
                                break;
                            case ERROR:
                                logger.error("Error event received for InteroperabilityRequest: {}", 
                                    resource.getMetadata().getName());
                                metricsService.incrementErrors("watcher_error", "controller");
                                break;
                        }
                    } catch (Exception e) {
                        logger.error("Error processing InteroperabilityRequest: {}", 
                            resource.getMetadata().getName(), e);
                        metricsService.incrementErrors("processing_error", "controller");
                    } finally {
                        metricsService.recordRequestProcessing(sample, 
                            resource.getSpec().getRequestType());
                    }
                }
                
                @Override
                public void onClose(WatcherException cause) {
                    if (cause != null) {
                        logger.error("Watcher closed with error", cause);
                        metricsService.incrementErrors("watcher_closed", "controller");
                    } else {
                        logger.info("Watcher closed normally");
                    }
                }
            });
    }
    
    @PreDestroy
    public void stopWatching() {
        if (watcher != null) {
            watcher.close();
        }
    }
}
```

## OpenTelemetry Integration

### 1. OpenTelemetry Configuration
```java
// operators/shared/src/main/java/com/bank/interoperability/operator/config/OpenTelemetryConfig.java
package com.bank.interoperability.operator.config;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.TracerProvider;
import io.opentelemetry.exporter.jaeger.JaegerGrpcSpanExporter;
import io.opentelemetry.exporter.prometheus.PrometheusHttpServer;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.metrics.export.PeriodicMetricReader;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import io.opentelemetry.semconv.resource.attributes.ResourceAttributes;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenTelemetryConfig {
    
    @Value("${jaeger.endpoint:http://jaeger:14268}")
    private String jaegerEndpoint;
    
    @Value("${prometheus.port:9090}")
    private int prometheusPort;
    
    @Bean
    public OpenTelemetry openTelemetry() {
        // Create resource
        Resource resource = Resource.getDefault()
            .merge(Resource.create(
                io.opentelemetry.api.common.Attributes.of(
                    ResourceAttributes.SERVICE_NAME, "interoperability-operator",
                    ResourceAttributes.SERVICE_VERSION, "1.0.0",
                    ResourceAttributes.DEPLOYMENT_ENVIRONMENT, "production"
                )
            ));
        
        // Create Jaeger exporter
        JaegerGrpcSpanExporter jaegerExporter = JaegerGrpcSpanExporter.builder()
            .setEndpoint(jaegerEndpoint)
            .build();
        
        // Create tracer provider
        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(jaegerExporter).build())
            .setResource(resource)
            .build();
        
        // Create meter provider
        SdkMeterProvider meterProvider = SdkMeterProvider.builder()
            .setResource(resource)
            .registerMetricReader(PeriodicMetricReader.builder(
                PrometheusHttpServer.builder()
                    .setPort(prometheusPort)
                    .build()
            ).build())
            .build();
        
        // Create OpenTelemetry SDK
        return OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .setMeterProvider(meterProvider)
            .buildAndRegisterGlobal();
    }
    
    @Bean
    public Tracer tracer(OpenTelemetry openTelemetry) {
        return openTelemetry.getTracer("interoperability-operator");
    }
}
```

### 2. Tracing in Controllers
```java
// operators/interoperability-operator/src/main/java/com/bank/interoperability/operator/controller/TracedInteroperabilityRequestController.java
package com.bank.interoperability.operator.controller;

import com.bank.interoperability.operator.model.InteroperabilityRequest;
import com.bank.interoperability.operator.service.InteroperabilityRequestService;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.Watcher;
import io.fabric8.kubernetes.client.WatcherException;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Context;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;

@Component
public class TracedInteroperabilityRequestController {
    
    private static final Logger logger = LoggerFactory.getLogger(TracedInteroperabilityRequestController.class);
    
    @Autowired
    private KubernetesClient kubernetesClient;
    
    @Autowired
    private InteroperabilityRequestService requestService;
    
    @Autowired
    private Tracer tracer;
    
    private Watcher<InteroperabilityRequest> watcher;
    
    @PostConstruct
    public void startWatching() {
        logger.info("Starting to watch InteroperabilityRequest resources with tracing");
        
        watcher = kubernetesClient.customResources(InteroperabilityRequest.class)
            .inNamespace("interoperability-core")
            .watch(new Watcher<InteroperabilityRequest>() {
                @Override
                public void eventReceived(Action action, InteroperabilityRequest resource) {
                    // Create span for each event
                    Span span = tracer.spanBuilder("reconcile-interoperability-request")
                        .setAttribute("action", action.name())
                        .setAttribute("request.name", resource.getMetadata().getName())
                        .setAttribute("request.namespace", resource.getMetadata().getNamespace())
                        .setAttribute("request.type", resource.getSpec().getRequestType())
                        .startSpan();
                    
                    try (Context context = span.makeCurrent()) {
                        logger.info("Received {} event for InteroperabilityRequest: {}", 
                            action, resource.getMetadata().getName());
                        
                        switch (action) {
                            case ADDED:
                            case MODIFIED:
                                requestService.reconcileRequest(resource);
                                span.setAttribute("result", "success");
                                break;
                            case DELETED:
                                requestService.handleDeletion(resource);
                                span.setAttribute("result", "deleted");
                                break;
                            case ERROR:
                                logger.error("Error event received for InteroperabilityRequest: {}", 
                                    resource.getMetadata().getName());
                                span.setAttribute("result", "error");
                                span.recordException(new RuntimeException("Watcher error"));
                                break;
                        }
                    } catch (Exception e) {
                        logger.error("Error processing InteroperabilityRequest: {}", 
                            resource.getMetadata().getName(), e);
                        span.recordException(e);
                        span.setAttribute("result", "error");
                    } finally {
                        span.end();
                    }
                }
                
                @Override
                public void onClose(WatcherException cause) {
                    if (cause != null) {
                        logger.error("Watcher closed with error", cause);
                    } else {
                        logger.info("Watcher closed normally");
                    }
                }
            });
    }
    
    @PreDestroy
    public void stopWatching() {
        if (watcher != null) {
            watcher.close();
        }
    }
}
```

## Grafana Dashboards

### 1. Java Operator Health Dashboard
```json
{
  "dashboard": {
    "title": "Bank Interoperability Java Operators - Health",
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
            "legendFormat": "{{error_type}} - {{component}}"
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

### 2. JVM Metrics Dashboard
```json
{
  "dashboard": {
    "title": "Bank Interoperability Java Operators - JVM Metrics",
    "panels": [
      {
        "title": "JVM Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "jvm_memory_used_bytes{job=\"interoperability-operator\"}",
            "legendFormat": "Memory Used"
          },
          {
            "expr": "jvm_memory_max_bytes{job=\"interoperability-operator\"}",
            "legendFormat": "Memory Max"
          }
        ]
      },
      {
        "title": "JVM GC Time",
        "type": "graph",
        "targets": [
          {
            "expr": "jvm_gc_pause_seconds_total{job=\"interoperability-operator\"}",
            "legendFormat": "GC Time"
          }
        ]
      },
      {
        "title": "JVM Threads",
        "type": "graph",
        "targets": [
          {
            "expr": "jvm_threads_live_threads{job=\"interoperability-operator\"}",
            "legendFormat": "Live Threads"
          },
          {
            "expr": "jvm_threads_daemon_threads{job=\"interoperability-operator\"}",
            "legendFormat": "Daemon Threads"
          }
        ]
      },
      {
        "title": "JVM Classes",
        "type": "graph",
        "targets": [
          {
            "expr": "jvm_classes_loaded_classes{job=\"interoperability-operator\"}",
            "legendFormat": "Loaded Classes"
          },
          {
            "expr": "jvm_classes_unloaded_classes_total{job=\"interoperability-operator\"}",
            "legendFormat": "Unloaded Classes"
          }
        ]
      }
    ]
  }
}
```

## Health Checks and Probes

### 1. Health Check Implementation
```java
// operators/shared/src/main/java/com/bank/interoperability/operator/health/OperatorHealthIndicator.java
package com.bank.interoperability.operator.health;

import io.fabric8.kubernetes.client.KubernetesClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.actuator.health.Health;
import org.springframework.boot.actuator.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class OperatorHealthIndicator implements HealthIndicator {
    
    @Autowired
    private KubernetesClient kubernetesClient;
    
    @Override
    public Health health() {
        try {
            // Check if the operator can connect to the Kubernetes API
            if (!checkKubernetesConnection()) {
                return Health.down()
                    .withDetail("kubernetes", "Connection failed")
                    .build();
            }
            
            // Check if the operator can access required resources
            if (!checkResourceAccess()) {
                return Health.down()
                    .withDetail("resources", "Access failed")
                    .build();
            }
            
            // Check if the operator is processing requests
            if (!checkRequestProcessing()) {
                return Health.down()
                    .withDetail("processing", "Not processing requests")
                    .build();
            }
            
            return Health.up()
                .withDetail("kubernetes", "Connected")
                .withDetail("resources", "Accessible")
                .withDetail("processing", "Active")
                .build();
                
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
    
    private boolean checkKubernetesConnection() {
        try {
            // Check if we can list namespaces
            kubernetesClient.namespaces().list();
            return true;
        } catch (Exception e) {
            return false;
        }
    }
    
    private boolean checkResourceAccess() {
        try {
            // Check if we can access CRDs
            kubernetesClient.apiextensions().v1().customResourceDefinitions().list();
            return true;
        } catch (Exception e) {
            return false;
        }
    }
    
    private boolean checkRequestProcessing() {
        // This could be implemented to check if the operator is actively processing requests
        // For now, we'll assume it's healthy if the other checks pass
        return true;
    }
}
```

### 2. Readiness Check Implementation
```java
// operators/shared/src/main/java/com/bank/interoperability/operator/health/OperatorReadinessIndicator.java
package com.bank.interoperability.operator.health;

import io.fabric8.kubernetes.client.KubernetesClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.actuator.health.Health;
import org.springframework.boot.actuator.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class OperatorReadinessIndicator implements HealthIndicator {
    
    @Autowired
    private KubernetesClient kubernetesClient;
    
    @Override
    public Health health() {
        try {
            // Check if the operator is ready to process requests
            if (!checkOperatorReady()) {
                return Health.down()
                    .withDetail("operator", "Not ready")
                    .build();
            }
            
            // Check if required dependencies are available
            if (!checkDependencies()) {
                return Health.down()
                    .withDetail("dependencies", "Not available")
                    .build();
            }
            
            return Health.up()
                .withDetail("operator", "Ready")
                .withDetail("dependencies", "Available")
                .build();
                
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
    
    private boolean checkOperatorReady() {
        // Check if the operator has been running for at least 30 seconds
        // This ensures the operator has had time to initialize
        try {
            Thread.sleep(30000);
            return true;
        } catch (InterruptedException e) {
            return false;
        }
    }
    
    private boolean checkDependencies() {
        try {
            // Check if required services are available
            // This could include checking for required ConfigMaps, Secrets, etc.
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
```

## Alerting Rules

### 1. Prometheus Alert Rules
```yaml
# helm-charts/operators/templates/monitoring/alertrules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: interoperability-java-operators-alerts
  namespace: interoperability-monitoring
  labels:
    app.kubernetes.io/component: monitoring
    operator-type: java
spec:
  groups:
  - name: interoperability-java-operators
    rules:
    - alert: JavaOperatorDown
      expr: up{job=~"interoperability-.*-operator"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Java Operator {{ $labels.job }} is down"
        description: "The {{ $labels.job }} Java operator has been down for more than 1 minute"
    
    - alert: HighErrorRate
      expr: rate(interoperability_errors_total[5m]) > 0.1
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High error rate in {{ $labels.operator }}"
        description: "The {{ $labels.operator }} Java operator has a high error rate of {{ $value }} errors per second"
    
    - alert: HighProcessingDuration
      expr: histogram_quantile(0.95, rate(interoperability_request_processing_duration_seconds_bucket[5m])) > 10
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High processing duration in {{ $labels.operator }}"
        description: "The {{ $labels.operator }} Java operator has a high 95th percentile processing duration of {{ $value }} seconds"
    
    - alert: HighJVMMemoryUsage
      expr: jvm_memory_used_bytes{job="interoperability-operator"} / jvm_memory_max_bytes{job="interoperability-operator"} > 0.8
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High JVM memory usage in {{ $labels.job }}"
        description: "The {{ $labels.job }} Java operator has high memory usage of {{ $value }}%"
    
    - alert: HighGCTime
      expr: rate(jvm_gc_pause_seconds_total{job="interoperability-operator"}[5m]) > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High GC time in {{ $labels.job }}"
        description: "The {{ $labels.job }} Java operator has high GC time of {{ $value }} seconds per second"
```

## Logging Configuration

### 1. Structured Logging
```java
// operators/shared/src/main/java/com/bank/interoperability/operator/logging/StructuredLogger.java
package com.bank.interoperability.operator.logging;

import io.opentelemetry.api.trace.Span;
import io.opentelemetry.context.Context;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

@Component
public class StructuredLogger {
    
    private static final Logger logger = LoggerFactory.getLogger(StructuredLogger.class);
    
    public void logRequest(Context context, String requestId, String requestType, String status) {
        Span span = Span.fromContext(context);
        
        Map<String, Object> logData = new HashMap<>();
        logData.put("timestamp", Instant.now().toString());
        logData.put("requestId", requestId);
        logData.put("requestType", requestType);
        logData.put("status", status);
        logData.put("traceId", span.getSpanContext().getTraceId());
        logData.put("spanId", span.getSpanContext().getSpanId());
        
        logger.info("Request processed: {}", logData);
    }
    
    public void logError(Context context, String requestId, String errorType, Exception error) {
        Span span = Span.fromContext(context);
        
        Map<String, Object> logData = new HashMap<>();
        logData.put("timestamp", Instant.now().toString());
        logData.put("requestId", requestId);
        logData.put("errorType", errorType);
        logData.put("error", error.getMessage());
        logData.put("traceId", span.getSpanContext().getTraceId());
        logData.put("spanId", span.getSpanContext().getSpanId());
        
        logger.error("Error processing request: {}", logData, error);
    }
}
```

### 2. Logback Configuration
```xml
<!-- operators/interoperability-operator/src/main/resources/logback-spring.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <include resource="org/springframework/boot/logging/logback/defaults.xml"/>
    
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>/var/log/interoperability-operator.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>/var/log/interoperability-operator.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <logger name="com.bank.interoperability.operator" level="DEBUG"/>
    <logger name="io.fabric8.kubernetes.client" level="INFO"/>
    <logger name="org.springframework" level="INFO"/>
    
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
```

This completes the Java operator monitoring and observability setup!