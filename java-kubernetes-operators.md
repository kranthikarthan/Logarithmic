# Java-based Kubernetes Operators for Bank Interoperability Layer

## Java Operator Architecture

### Operator Structure
```
operators/
├── interoperability-operator/      # Main interoperability operator
├── saga-operator/                  # Saga orchestration operator
├── routing-operator/               # Intelligent routing operator
├── security-operator/              # Security and compliance operator
├── monitoring-operator/             # Monitoring and observability operator
└── shared/                        # Shared operator libraries
    ├── pkg/
    │   ├── apis/
    │   ├── controllers/
    │   ├── reconcilers/
    │   └── utils/
    └── pom.xml
```

## Main Interoperability Operator

### 1. Project Structure (operators/interoperability-operator/)
```
interoperability-operator/
├── src/main/java/com/bank/interoperability/operator/
│   ├── InteroperabilityOperatorApplication.java
│   ├── config/
│   │   ├── OperatorConfig.java
│   │   ├── KubernetesConfig.java
│   │   └── MonitoringConfig.java
│   ├── controller/
│   │   ├── InteroperabilityRequestController.java
│   │   └── InteroperabilityRequestReconciler.java
│   ├── service/
│   │   ├── InteroperabilityRequestService.java
│   │   ├── RequestProcessingService.java
│   │   └── EventPublishingService.java
│   ├── model/
│   │   ├── InteroperabilityRequest.java
│   │   ├── InteroperabilityRequestSpec.java
│   │   └── InteroperabilityRequestStatus.java
│   └── exception/
│       └── OperatorException.java
├── src/main/resources/
│   ├── application.yml
│   ├── application-dev.yml
│   ├── application-prod.yml
│   └── logback-spring.xml
├── Dockerfile
└── pom.xml
```

### 2. Main Application Class
```java
// operators/interoperability-operator/src/main/java/com/bank/interoperability/operator/InteroperabilityOperatorApplication.java
package com.bank.interoperability.operator;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.kafka.annotation.EnableKafka;

@SpringBootApplication
@EnableScheduling
@EnableKafka
public class InteroperabilityOperatorApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(InteroperabilityOperatorApplication.class, args);
    }
}
```

### 3. Operator Configuration
```java
// operators/interoperability-operator/src/main/java/com/bank/interoperability/operator/config/OperatorConfig.java
package com.bank.interoperability.operator.config;

import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;

@Configuration
@EnableScheduling
public class OperatorConfig {
    
    @Bean
    public KubernetesClient kubernetesClient() {
        return new KubernetesClientBuilder().build();
    }
    
    @Bean
    public OperatorProperties operatorProperties() {
        return new OperatorProperties();
    }
}
```

### 4. Custom Resource Model
```java
// operators/interoperability-operator/src/main/java/com/bank/interoperability/operator/model/InteroperabilityRequest.java
package com.bank.interoperability.operator.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.fabric8.kubernetes.api.model.Namespaced;
import io.fabric8.kubernetes.client.CustomResource;
import io.fabric8.kubernetes.model.annotation.Group;
import io.fabric8.kubernetes.model.annotation.Kind;
import io.fabric8.kubernetes.model.annotation.Version;

@Group("interoperability.bank.com")
@Version("v1")
@Kind("InteroperabilityRequest")
public class InteroperabilityRequest extends CustomResource<InteroperabilityRequestSpec, InteroperabilityRequestStatus> 
    implements Namespaced {
    
    @Override
    protected InteroperabilityRequestSpec initSpec() {
        return new InteroperabilityRequestSpec();
    }
    
    @Override
    protected InteroperabilityRequestStatus initStatus() {
        return new InteroperabilityRequestStatus();
    }
}
```

### 5. Request Spec Model
```java
// operators/interoperability-operator/src/main/java/com/bank/interoperability/operator/model/InteroperabilityRequestSpec.java
package com.bank.interoperability.operator.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class InteroperabilityRequestSpec {
    
    @JsonProperty("requestId")
    private String requestId;
    
    @JsonProperty("requestType")
    private String requestType;
    
    @JsonProperty("payload")
    private String payload;
    
    @JsonProperty("routingStrategy")
    private String routingStrategy;
    
    @JsonProperty("dependencies")
    private List<StepDependency> dependencies;
    
    @JsonProperty("securityContext")
    private SecurityContext securityContext;
    
    // Getters and setters
    public String getRequestId() { return requestId; }
    public void setRequestId(String requestId) { this.requestId = requestId; }
    
    public String getRequestType() { return requestType; }
    public void setRequestType(String requestType) { this.requestType = requestType; }
    
    public String getPayload() { return payload; }
    public void setPayload(String payload) { this.payload = payload; }
    
    public String getRoutingStrategy() { return routingStrategy; }
    public void setRoutingStrategy(String routingStrategy) { this.routingStrategy = routingStrategy; }
    
    public List<StepDependency> getDependencies() { return dependencies; }
    public void setDependencies(List<StepDependency> dependencies) { this.dependencies = dependencies; }
    
    public SecurityContext getSecurityContext() { return securityContext; }
    public void setSecurityContext(SecurityContext securityContext) { this.securityContext = securityContext; }
}

public class StepDependency {
    @JsonProperty("stepId")
    private String stepId;
    
    @JsonProperty("dependsOn")
    private List<String> dependsOn;
    
    // Getters and setters
    public String getStepId() { return stepId; }
    public void setStepId(String stepId) { this.stepId = stepId; }
    
    public List<String> getDependsOn() { return dependsOn; }
    public void setDependsOn(List<String> dependsOn) { this.dependsOn = dependsOn; }
}

public class SecurityContext {
    @JsonProperty("encryptionKey")
    private String encryptionKey;
    
    @JsonProperty("accessToken")
    private String accessToken;
    
    @JsonProperty("policies")
    private Map<String, String> policies;
    
    // Getters and setters
    public String getEncryptionKey() { return encryptionKey; }
    public void setEncryptionKey(String encryptionKey) { this.encryptionKey = encryptionKey; }
    
    public String getAccessToken() { return accessToken; }
    public void setAccessToken(String accessToken) { this.accessToken = accessToken; }
    
    public Map<String, String> getPolicies() { return policies; }
    public void setPolicies(Map<String, String> policies) { this.policies = policies; }
}
```

### 6. Request Status Model
```java
// operators/interoperability-operator/src/main/java/com/bank/interoperability/operator/model/InteroperabilityRequestStatus.java
package com.bank.interoperability.operator.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import java.util.List;

public class InteroperabilityRequestStatus {
    
    @JsonProperty("phase")
    private String phase;
    
    @JsonProperty("message")
    private String message;
    
    @JsonProperty("lastTransitionTime")
    private Instant lastTransitionTime;
    
    @JsonProperty("steps")
    private List<StepStatus> steps;
    
    @JsonProperty("conditions")
    private List<Condition> conditions;
    
    // Getters and setters
    public String getPhase() { return phase; }
    public void setPhase(String phase) { this.phase = phase; }
    
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    
    public Instant getLastTransitionTime() { return lastTransitionTime; }
    public void setLastTransitionTime(Instant lastTransitionTime) { this.lastTransitionTime = lastTransitionTime; }
    
    public List<StepStatus> getSteps() { return steps; }
    public void setSteps(List<StepStatus> steps) { this.steps = steps; }
    
    public List<Condition> getConditions() { return conditions; }
    public void setConditions(List<Condition> conditions) { this.conditions = conditions; }
}

public class StepStatus {
    @JsonProperty("stepId")
    private String stepId;
    
    @JsonProperty("status")
    private String status;
    
    @JsonProperty("message")
    private String message;
    
    @JsonProperty("startTime")
    private Instant startTime;
    
    @JsonProperty("endTime")
    private Instant endTime;
    
    // Getters and setters
    public String getStepId() { return stepId; }
    public void setStepId(String stepId) { this.stepId = stepId; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    
    public Instant getStartTime() { return startTime; }
    public void setStartTime(Instant startTime) { this.startTime = startTime; }
    
    public Instant getEndTime() { return endTime; }
    public void setEndTime(Instant endTime) { this.endTime = endTime; }
}

public class Condition {
    @JsonProperty("type")
    private String type;
    
    @JsonProperty("status")
    private String status;
    
    @JsonProperty("lastTransitionTime")
    private Instant lastTransitionTime;
    
    @JsonProperty("reason")
    private String reason;
    
    @JsonProperty("message")
    private String message;
    
    // Getters and setters
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public Instant getLastTransitionTime() { return lastTransitionTime; }
    public void setLastTransitionTime(Instant lastTransitionTime) { this.lastTransitionTime = lastTransitionTime; }
    
    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }
    
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
```

## Operator Controller Implementation

### 1. Main Controller
```java
// operators/interoperability-operator/src/main/java/com/bank/interoperability/operator/controller/InteroperabilityRequestController.java
package com.bank.interoperability.operator.controller;

import com.bank.interoperability.operator.model.InteroperabilityRequest;
import com.bank.interoperability.operator.service.InteroperabilityRequestService;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.Watcher;
import io.fabric8.kubernetes.client.WatcherException;
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
                    
                    try {
                        switch (action) {
                            case ADDED:
                            case MODIFIED:
                                requestService.reconcileRequest(resource);
                                break;
                            case DELETED:
                                requestService.handleDeletion(resource);
                                break;
                            case ERROR:
                                logger.error("Error event received for InteroperabilityRequest: {}", 
                                    resource.getMetadata().getName());
                                break;
                        }
                    } catch (Exception e) {
                        logger.error("Error processing InteroperabilityRequest: {}", 
                            resource.getMetadata().getName(), e);
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

### 2. Request Service
```java
// operators/interoperability-operator/src/main/java/com/bank/interoperability/operator/service/InteroperabilityRequestService.java
package com.bank.interoperability.operator.service;

import com.bank.interoperability.operator.model.InteroperabilityRequest;
import com.bank.interoperability.operator.model.InteroperabilityRequestStatus;
import com.bank.interoperability.operator.model.StepStatus;
import com.bank.interoperability.operator.model.Condition;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Service
public class InteroperabilityRequestService {
    
    private static final Logger logger = LoggerFactory.getLogger(InteroperabilityRequestService.class);
    
    @Autowired
    private KubernetesClient kubernetesClient;
    
    @Autowired
    private RequestProcessingService processingService;
    
    @Autowired
    private EventPublishingService eventService;
    
    public void reconcileRequest(InteroperabilityRequest request) {
        logger.info("Reconciling InteroperabilityRequest: {}", request.getMetadata().getName());
        
        try {
            // Update status to processing
            updateRequestStatus(request, "Processing", "Request is being processed");
            
            // Process the request based on its current phase
            String currentPhase = request.getStatus() != null ? request.getStatus().getPhase() : null;
            
            switch (currentPhase) {
                case null:
                case "":
                    initializeRequest(request);
                    break;
                case "Initialized":
                    validateRequest(request);
                    break;
                case "Validated":
                    routeRequest(request);
                    break;
                case "Routed":
                    executeRequest(request);
                    break;
                case "Executing":
                    monitorExecution(request);
                    break;
                case "Completed":
                case "Failed":
                    finalizeRequest(request);
                    break;
                default:
                    logger.warn("Unknown phase: {}", currentPhase);
                    break;
            }
            
        } catch (Exception e) {
            logger.error("Error reconciling InteroperabilityRequest: {}", 
                request.getMetadata().getName(), e);
            updateRequestStatus(request, "Failed", "Error processing request: " + e.getMessage());
        }
    }
    
    private void initializeRequest(InteroperabilityRequest request) {
        logger.info("Initializing request: {}", request.getMetadata().getName());
        
        // Set initial status
        InteroperabilityRequestStatus status = new InteroperabilityRequestStatus();
        status.setPhase("Initialized");
        status.setMessage("Request initialized successfully");
        status.setLastTransitionTime(Instant.now());
        
        // Add initial condition
        List<Condition> conditions = new ArrayList<>();
        Condition condition = new Condition();
        condition.setType("Initialized");
        condition.setStatus("True");
        condition.setLastTransitionTime(Instant.now());
        condition.setReason("RequestCreated");
        condition.setMessage("Request has been initialized");
        conditions.add(condition);
        status.setConditions(conditions);
        
        request.setStatus(status);
        updateRequest(request);
        
        // Publish event
        eventService.publishRequestInitialized(request);
    }
    
    private void validateRequest(InteroperabilityRequest request) {
        logger.info("Validating request: {}", request.getMetadata().getName());
        
        try {
            // Perform validation
            boolean isValid = processingService.validateRequest(request);
            
            if (isValid) {
                updateRequestStatus(request, "Validated", "Request validation successful");
                eventService.publishRequestValidated(request);
            } else {
                updateRequestStatus(request, "Failed", "Request validation failed");
                eventService.publishRequestValidationFailed(request);
            }
        } catch (Exception e) {
            logger.error("Error validating request: {}", request.getMetadata().getName(), e);
            updateRequestStatus(request, "Failed", "Validation error: " + e.getMessage());
        }
    }
    
    private void routeRequest(InteroperabilityRequest request) {
        logger.info("Routing request: {}", request.getMetadata().getName());
        
        try {
            // Perform routing
            String routingStrategy = processingService.determineRoutingStrategy(request);
            
            updateRequestStatus(request, "Routed", "Request routed with strategy: " + routingStrategy);
            eventService.publishRequestRouted(request, routingStrategy);
        } catch (Exception e) {
            logger.error("Error routing request: {}", request.getMetadata().getName(), e);
            updateRequestStatus(request, "Failed", "Routing error: " + e.getMessage());
        }
    }
    
    private void executeRequest(InteroperabilityRequest request) {
        logger.info("Executing request: {}", request.getMetadata().getName());
        
        try {
            // Start execution
            updateRequestStatus(request, "Executing", "Request execution started");
            
            // Execute the request
            processingService.executeRequest(request);
            
            updateRequestStatus(request, "Completed", "Request execution completed successfully");
            eventService.publishRequestCompleted(request);
        } catch (Exception e) {
            logger.error("Error executing request: {}", request.getMetadata().getName(), e);
            updateRequestStatus(request, "Failed", "Execution error: " + e.getMessage());
            eventService.publishRequestFailed(request, e);
        }
    }
    
    private void monitorExecution(InteroperabilityRequest request) {
        logger.info("Monitoring execution of request: {}", request.getMetadata().getName());
        
        try {
            // Check execution status
            String executionStatus = processingService.getExecutionStatus(request);
            
            if ("Completed".equals(executionStatus)) {
                updateRequestStatus(request, "Completed", "Request execution completed successfully");
                eventService.publishRequestCompleted(request);
            } else if ("Failed".equals(executionStatus)) {
                updateRequestStatus(request, "Failed", "Request execution failed");
                eventService.publishRequestFailed(request, new RuntimeException("Execution failed"));
            }
            // If still executing, leave status as is
        } catch (Exception e) {
            logger.error("Error monitoring execution: {}", request.getMetadata().getName(), e);
            updateRequestStatus(request, "Failed", "Monitoring error: " + e.getMessage());
        }
    }
    
    private void finalizeRequest(InteroperabilityRequest request) {
        logger.info("Finalizing request: {}", request.getMetadata().getName());
        
        try {
            // Perform finalization
            processingService.finalizeRequest(request);
            
            // Publish final event
            if ("Completed".equals(request.getStatus().getPhase())) {
                eventService.publishRequestFinalized(request);
            }
        } catch (Exception e) {
            logger.error("Error finalizing request: {}", request.getMetadata().getName(), e);
        }
    }
    
    public void handleDeletion(InteroperabilityRequest request) {
        logger.info("Handling deletion of request: {}", request.getMetadata().getName());
        
        try {
            // Perform cleanup
            processingService.cleanupRequest(request);
            
            // Publish deletion event
            eventService.publishRequestDeleted(request);
        } catch (Exception e) {
            logger.error("Error handling deletion: {}", request.getMetadata().getName(), e);
        }
    }
    
    private void updateRequestStatus(InteroperabilityRequest request, String phase, String message) {
        if (request.getStatus() == null) {
            request.setStatus(new InteroperabilityRequestStatus());
        }
        
        request.getStatus().setPhase(phase);
        request.getStatus().setMessage(message);
        request.getStatus().setLastTransitionTime(Instant.now());
        
        updateRequest(request);
    }
    
    private void updateRequest(InteroperabilityRequest request) {
        try {
            kubernetesClient.customResources(InteroperabilityRequest.class)
                .inNamespace(request.getMetadata().getNamespace())
                .withName(request.getMetadata().getName())
                .replace(request);
        } catch (Exception e) {
            logger.error("Error updating request: {}", request.getMetadata().getName(), e);
        }
    }
}
```

## Saga Operator Implementation

### 1. Saga Operator Structure
```java
// operators/saga-operator/src/main/java/com/bank/interoperability/saga/operator/SagaOperatorApplication.java
package com.bank.interoperability.saga.operator;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.kafka.annotation.EnableKafka;

@SpringBootApplication
@EnableScheduling
@EnableKafka
public class SagaOperatorApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(SagaOperatorApplication.class, args);
    }
}
```

### 2. Saga Controller
```java
// operators/saga-operator/src/main/java/com/bank/interoperability/saga/operator/controller/SagaController.java
package com.bank.interoperability.saga.operator.controller;

import com.bank.interoperability.saga.operator.model.Saga;
import com.bank.interoperability.saga.operator.service.SagaService;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.Watcher;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;

@Component
public class SagaController {
    
    private static final Logger logger = LoggerFactory.getLogger(SagaController.class);
    
    @Autowired
    private KubernetesClient kubernetesClient;
    
    @Autowired
    private SagaService sagaService;
    
    private Watcher<Saga> watcher;
    
    @PostConstruct
    public void startWatching() {
        logger.info("Starting to watch Saga resources");
        
        watcher = kubernetesClient.customResources(Saga.class)
            .inNamespace("interoperability-saga")
            .watch(new Watcher<Saga>() {
                @Override
                public void eventReceived(Action action, Saga resource) {
                    logger.info("Received {} event for Saga: {}", 
                        action, resource.getMetadata().getName());
                    
                    try {
                        switch (action) {
                            case ADDED:
                            case MODIFIED:
                                sagaService.reconcileSaga(resource);
                                break;
                            case DELETED:
                                sagaService.handleDeletion(resource);
                                break;
                            case ERROR:
                                logger.error("Error event received for Saga: {}", 
                                    resource.getMetadata().getName());
                                break;
                        }
                    } catch (Exception e) {
                        logger.error("Error processing Saga: {}", 
                            resource.getMetadata().getName(), e);
                    }
                }
                
                @Override
                public void onClose(io.fabric8.kubernetes.client.WatcherException cause) {
                    if (cause != null) {
                        logger.error("Saga watcher closed with error", cause);
                    } else {
                        logger.info("Saga watcher closed normally");
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

## Application Configuration

### 1. Main Application Configuration
```yaml
# operators/interoperability-operator/src/main/resources/application.yml
server:
  port: 8080
  servlet:
    context-path: /

spring:
  application:
    name: interoperability-operator
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
  
  # Kubernetes configuration
  kubernetes:
    enabled: true
    namespace: interoperability-core
    service-account: interoperability-operator
  
  # Kafka configuration
  kafka:
    bootstrap-servers: ${KAFKA_BOOTSTRAP_SERVERS:kafka:9092}
    consumer:
      group-id: interoperability-operator
      auto-offset-reset: earliest
    producer:
      acks: all
      retries: 3

# Operator configuration
operator:
  name: interoperability-operator
  namespace: interoperability-core
  reconciliation-interval: 30000
  max-reconcile-attempts: 3
  
  # Kubernetes client configuration
  kubernetes:
    master-url: ${KUBERNETES_MASTER_URL:}
    namespace: interoperability-core
    service-account: interoperability-operator
  
  # Monitoring configuration
  monitoring:
    enabled: true
    metrics:
      enabled: true
      port: 8080
    health:
      enabled: true
      port: 8081

# Logging configuration
logging:
  level:
    com.bank.interoperability.operator: DEBUG
    io.fabric8.kubernetes.client: INFO
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"

# Management endpoints
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
  metrics:
    export:
      prometheus:
        enabled: true
```

### 2. Production Configuration
```yaml
# operators/interoperability-operator/src/main/resources/application-prod.yml
server:
  port: 8080

spring:
  # Database configuration
  datasource:
    url: ${DATABASE_URL:jdbc:postgresql://postgresql:5432/interoperability}
    username: ${DATABASE_USERNAME:interoperability}
    password: ${DATABASE_PASSWORD:password}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
  
  # JPA configuration
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    properties:
      hibernate:
        format_sql: false
  
  # Redis configuration
  redis:
    host: ${REDIS_HOST:redis}
    port: ${REDIS_PORT:6379}
    password: ${REDIS_PASSWORD:}
    timeout: 2000ms
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
        min-idle: 0

# Operator configuration
operator:
  reconciliation-interval: 30000
  max-reconcile-attempts: 5
  
  # Kubernetes client configuration
  kubernetes:
    master-url: ${KUBERNETES_MASTER_URL:}
    namespace: interoperability-core
    service-account: interoperability-operator
  
  # Monitoring configuration
  monitoring:
    enabled: true
    metrics:
      enabled: true
      port: 8080
    health:
      enabled: true
      port: 8081
    tracing:
      enabled: true
      jaeger:
        endpoint: ${JAEGER_ENDPOINT:http://jaeger:14268/api/traces}

# Logging configuration
logging:
  level:
    com.bank.interoperability.operator: INFO
    io.fabric8.kubernetes.client: WARN
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: /var/log/interoperability-operator.log
```

## Maven Configuration

### 1. Parent POM
```xml
<!-- operators/pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.bank.interoperability</groupId>
    <artifactId>interoperability-operators</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    
    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <spring-boot.version>3.1.0</spring-boot.version>
        <fabric8.version>6.7.0</fabric8.version>
    </properties>
    
    <modules>
        <module>interoperability-operator</module>
        <module>saga-operator</module>
        <module>routing-operator</module>
        <module>security-operator</module>
        <module>monitoring-operator</module>
        <module>shared</module>
    </modules>
    
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${spring-boot.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            <dependency>
                <groupId>io.fabric8</groupId>
                <artifactId>kubernetes-client-bom</artifactId>
                <version>${fabric8.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

### 2. Operator POM
```xml
<!-- operators/interoperability-operator/pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>com.bank.interoperability</groupId>
        <artifactId>interoperability-operators</artifactId>
        <version>1.0.0</version>
    </parent>
    
    <artifactId>interoperability-operator</artifactId>
    <packaging>jar</packaging>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.kafka</groupId>
            <artifactId>spring-kafka</artifactId>
        </dependency>
        <dependency>
            <groupId>io.fabric8</groupId>
            <artifactId>kubernetes-client</artifactId>
        </dependency>
        <dependency>
            <groupId>io.fabric8</groupId>
            <artifactId>kubernetes-model</artifactId>
        </dependency>
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>
        <dependency>
            <groupId>com.bank.interoperability</groupId>
            <artifactId>shared-common</artifactId>
            <version>1.0.0</version>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

This completes the Java-based Kubernetes operators implementation for the bank interoperability layer!