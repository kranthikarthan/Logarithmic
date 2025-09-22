# Spring Boot Microservices Integration with Java Kubernetes Operators

## Integration Architecture

### Operator-Service Communication
```
┌─────────────────────────────────────────────────────────────────┐
│                    Java Operator-Service Integration            │
├─────────────────────────────────────────────────────────────────┤
│ Spring Boot Services ←→ Kubernetes API ←→ Java Operators        │
│     ↓                    ↓                    ↓                  │
│ API Gateway          InteroperabilityRequest  InteroperabilityOp  │
│ Intelligent Router   RoutingDecision         RoutingOperator     │
│ Saga Orchestrator    Saga                    SagaOperator        │
│ Security Services    SecurityPolicy          SecurityOperator     │
└─────────────────────────────────────────────────────────────────┘
```

## Enhanced Spring Boot Services

### 1. API Gateway with Java Operator Integration
```java
// src/api-gateway/src/main/java/com/bank/interoperability/gateway/service/JavaOperatorIntegratedGatewayService.java
package com.bank.interoperability.gateway.service;

import com.bank.interoperability.gateway.dto.IncomingRequest;
import com.bank.interoperability.gateway.dto.ProcessResponse;
import com.bank.interoperability.operator.model.InteroperabilityRequest;
import com.bank.interoperability.operator.model.InteroperabilityRequestSpec;
import com.bank.interoperability.operator.model.SecurityContext;
import com.bank.interoperability.shared.monitoring.OpenTelemetryService;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.dsl.MixedOperation;
import io.fabric8.kubernetes.client.dsl.Resource;
import io.opentelemetry.api.trace.Span;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class JavaOperatorIntegratedGatewayService {
    
    @Autowired
    private KubernetesClient kubernetesClient;
    
    @Autowired
    private OpenTelemetryService telemetryService;
    
    private MixedOperation<InteroperabilityRequest, ?, Resource<InteroperabilityRequest>> customResourceClient;
    
    @PostConstruct
    public void initialize() {
        customResourceClient = kubernetesClient.customResources(InteroperabilityRequest.class);
    }
    
    public ProcessResponse processRequest(IncomingRequest request, String requestId, String userId) {
        Span span = telemetryService.startSpan("gateway-process-request");
        
        try {
            // Create InteroperabilityRequest CRD
            InteroperabilityRequest crdRequest = createInteroperabilityRequest(request, requestId, userId);
            
            // Submit to Java operator
            InteroperabilityRequest createdRequest = customResourceClient
                .inNamespace("interoperability-core")
                .create(crdRequest);
            
            return ProcessResponse.builder()
                .sagaId(createdRequest.getMetadata().getName())
                .status("PROCESSING")
                .requestId(requestId)
                .crdName(createdRequest.getMetadata().getName())
                .operatorType("java")
                .build();
                
        } finally {
            span.end();
        }
    }
    
    public String getSagaStatus(String sagaId) {
        try {
            InteroperabilityRequest request = customResourceClient
                .inNamespace("interoperability-core")
                .withName(sagaId)
                .get();
            
            if (request != null && request.getStatus() != null) {
                return request.getStatus().getPhase();
            }
            return "UNKNOWN";
        } catch (Exception e) {
            return "ERROR";
        }
    }
    
    private InteroperabilityRequest createInteroperabilityRequest(
            IncomingRequest request, 
            String requestId, 
            String userId) {
        
        InteroperabilityRequest crdRequest = new InteroperabilityRequest();
        
        // Set metadata
        crdRequest.getMetadata().setName(requestId);
        crdRequest.getMetadata().setNamespace("interoperability-core");
        crdRequest.getMetadata().getLabels().put("app", "interoperability");
        crdRequest.getMetadata().getLabels().put("requestId", requestId);
        crdRequest.getMetadata().getLabels().put("operatorType", "java");
        
        // Set spec
        InteroperabilityRequestSpec spec = new InteroperabilityRequestSpec();
        spec.setRequestId(requestId);
        spec.setRequestType(request.getRequestType());
        spec.setPayload(request.getPayload());
        spec.setRoutingStrategy("AUTO");
        
        // Set security context
        SecurityContext securityContext = new SecurityContext();
        securityContext.setAccessToken(userId);
        securityContext.getPolicies().put("encryption", "required");
        securityContext.getPolicies().put("audit", "enabled");
        securityContext.getPolicies().put("operatorType", "java");
        spec.setSecurityContext(securityContext);
        
        crdRequest.setSpec(spec);
        
        return crdRequest;
    }
}
```

### 2. Intelligent Router with Java Operator Integration
```java
// src/intelligent-router/src/main/java/com/bank/interoperability/router/service/JavaOperatorIntegratedRouterService.java
package com.bank.interoperability.router.service;

import com.bank.interoperability.router.dto.IncomingRequest;
import com.bank.interoperability.router.dto.RoutingDecision as RouterDecision;
import com.bank.interoperability.operator.model.RoutingDecision;
import com.bank.interoperability.operator.model.RoutingDecisionSpec;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.dsl.MixedOperation;
import io.fabric8.kubernetes.client.dsl.Resource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.concurrent.TimeUnit;

@Service
public class JavaOperatorIntegratedRouterService {
    
    @Autowired
    private KubernetesClient kubernetesClient;
    
    @Autowired
    private MLRequestAnalyzer mlAnalyzer;
    
    private MixedOperation<RoutingDecision, ?, Resource<RoutingDecision>> routingDecisionClient;
    
    @PostConstruct
    public void initialize() {
        routingDecisionClient = kubernetesClient.customResources(RoutingDecision.class);
    }
    
    public RouterDecision routeRequest(IncomingRequest request) {
        // Create RoutingDecision CRD
        RoutingDecision crdDecision = createRoutingDecision(request);
        
        // Submit to Java routing operator
        RoutingDecision createdDecision = routingDecisionClient
            .inNamespace("interoperability-routing")
            .create(crdDecision);
        
        // Wait for operator to process
        RoutingDecision processedDecision = waitForRoutingDecision(createdDecision.getMetadata().getName());
        
        // Convert CRD response to service response
        return convertToRouterDecision(processedDecision);
    }
    
    private RoutingDecision createRoutingDecision(IncomingRequest request) {
        RoutingDecision crdDecision = new RoutingDecision();
        
        // Set metadata
        crdDecision.getMetadata().setName(request.getRequestId());
        crdDecision.getMetadata().setNamespace("interoperability-routing");
        crdDecision.getMetadata().getLabels().put("operatorType", "java");
        
        // Set spec
        RoutingDecisionSpec spec = new RoutingDecisionSpec();
        spec.setRequestId(request.getRequestId());
        spec.setRequestType(request.getRequestType());
        spec.setPayload(request.getPayload());
        spec.setRequestProfile(analyzeRequestProfile(request));
        
        crdDecision.setSpec(spec);
        
        return crdDecision;
    }
    
    private RoutingDecision waitForRoutingDecision(String decisionName) {
        // Poll the Java operator until decision is made
        int maxAttempts = 30;
        int attempt = 0;
        
        while (attempt < maxAttempts) {
            try {
                RoutingDecision decision = routingDecisionClient
                    .inNamespace("interoperability-routing")
                    .withName(decisionName)
                    .get();
                
                if (decision != null && decision.getStatus() != null && 
                    decision.getStatus().getStrategy() != null) {
                    return decision;
                }
                
                Thread.sleep(1000); // Wait 1 second
                attempt++;
            } catch (Exception e) {
                // Handle error
                break;
            }
        }
        
        throw new RuntimeException("Routing decision timeout");
    }
    
    private RouterDecision convertToRouterDecision(RoutingDecision crdDecision) {
        return RouterDecision.builder()
            .strategy(crdDecision.getStatus().getStrategy())
            .confidence(crdDecision.getStatus().getConfidence())
            .reasoning(crdDecision.getStatus().getReasoning())
            .operatorType("java")
            .build();
    }
}
```

### 3. Saga Orchestrator with Java Operator Integration
```java
// src/saga-orchestrator/src/main/java/com/bank/interoperability/saga/service/JavaOperatorIntegratedSagaService.java
package com.bank.interoperability.saga.service;

import com.bank.interoperability.saga.dto.IncomingRequest;
import com.bank.interoperability.saga.dto.RoutingDecision;
import com.bank.interoperability.operator.model.Saga;
import com.bank.interoperability.operator.model.SagaSpec;
import com.bank.interoperability.operator.model.SagaStep;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.dsl.MixedOperation;
import io.fabric8.kubernetes.client.dsl.Resource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;

@Service
public class JavaOperatorIntegratedSagaService {
    
    @Autowired
    private KubernetesClient kubernetesClient;
    
    private MixedOperation<Saga, ?, Resource<Saga>> sagaClient;
    
    @PostConstruct
    public void initialize() {
        sagaClient = kubernetesClient.customResources(Saga.class);
    }
    
    public String startSaga(IncomingRequest request, RoutingDecision decision) {
        // Create Saga CRD
        Saga saga = createSaga(request, decision);
        
        // Submit to Java saga operator
        Saga createdSaga = sagaClient
            .inNamespace("interoperability-saga")
            .create(saga);
        
        return createdSaga.getMetadata().getName();
    }
    
    public String getSagaStatus(String sagaId) {
        try {
            Saga saga = sagaClient
                .inNamespace("interoperability-saga")
                .withName(sagaId)
                .get();
            
            if (saga != null && saga.getStatus() != null) {
                return saga.getStatus().getPhase();
            }
            return "UNKNOWN";
        } catch (Exception e) {
            return "ERROR";
        }
    }
    
    private Saga createSaga(IncomingRequest request, RoutingDecision decision) {
        Saga saga = new Saga();
        
        // Set metadata
        saga.getMetadata().setName(request.getRequestId());
        saga.getMetadata().setNamespace("interoperability-saga");
        saga.getMetadata().getLabels().put("operatorType", "java");
        
        // Set spec
        SagaSpec spec = new SagaSpec();
        spec.setSagaId(request.getRequestId());
        spec.setRequestId(request.getRequestId());
        
        // Create saga steps based on routing decision
        for (String stepType : decision.getExecutionSteps()) {
            SagaStep step = new SagaStep();
            step.setStepId(stepType + "-" + request.getRequestId());
            step.setStepType(stepType);
            step.setTargetService(getTargetService(stepType));
            step.setTargetEndpoint(getTargetEndpoint(stepType));
            step.setPayload(request.getPayload());
            
            spec.getSteps().add(step);
        }
        
        saga.setSpec(spec);
        
        return saga;
    }
}
```

## Kubernetes Client Configuration

### 1. Kubernetes Client Configuration
```java
// src/shared/kubernetes/src/main/java/com/bank/interoperability/kubernetes/config/KubernetesConfig.java
package com.bank.interoperability.kubernetes.config;

import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class KubernetesConfig {
    
    @Bean
    public KubernetesClient kubernetesClient() {
        return new KubernetesClientBuilder().build();
    }
}
```

### 2. Operator Properties Configuration
```java
// src/shared/kubernetes/src/main/java/com/bank/interoperability/kubernetes/config/OperatorProperties.java
package com.bank.interoperability.kubernetes.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "interoperability.operators")
public class OperatorProperties {
    
    private String namespace = "interoperability-core";
    private String operatorType = "java";
    private long timeout = 30000;
    private int retryAttempts = 3;
    
    // Getters and setters
    public String getNamespace() { return namespace; }
    public void setNamespace(String namespace) { this.namespace = namespace; }
    
    public String getOperatorType() { return operatorType; }
    public void setOperatorType(String operatorType) { this.operatorType = operatorType; }
    
    public long getTimeout() { return timeout; }
    public void setTimeout(long timeout) { this.timeout = timeout; }
    
    public int getRetryAttempts() { return retryAttempts; }
    public void setRetryAttempts(int retryAttempts) { this.retryAttempts = retryAttempts; }
}
```

## Application Configuration Updates

### 1. Enhanced Application Configuration
```yaml
# src/api-gateway/src/main/resources/application.yml
spring:
  application:
    name: api-gateway
  
  # Kubernetes integration
  kubernetes:
    enabled: true
    namespace: interoperability-core
    service-account: api-gateway-service-account

# Operator integration configuration
interoperability:
  operators:
    enabled: true
    namespace: interoperability-core
    timeout: 30000
    retry-attempts: 3
    operator-type: java
    
  # CRD configuration
  crd:
    interoperability-request:
      group: interoperability.bank.com
      version: v1
      plural: interoperabilityrequests
      operator-type: java
    
    routing-decision:
      group: routing.bank.com
      version: v1
      plural: routingdecisions
      operator-type: java
    
    saga:
      group: saga.bank.com
      version: v1
      plural: sagas
      operator-type: java
    
    security-policy:
      group: security.bank.com
      version: v1
      plural: securitypolicies
      operator-type: java

# Monitoring configuration
monitoring:
  kubernetes:
    enabled: true
    metrics:
      enabled: true
      port: 8080
    health:
      enabled: true
      port: 8081
    operator-type: java
```

### 2. Production Configuration
```yaml
# src/api-gateway/src/main/resources/application-prod.yml
server:
  port: 8080

spring:
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

  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    properties:
      hibernate:
        format_sql: false

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
interoperability:
  operators:
    enabled: true
    namespace: interoperability-core
    timeout: 30000
    retry-attempts: 5
    operator-type: java
    
  # Java operator specific configuration
  java-operators:
    enabled: true
    reconciliation-interval: 30000
    max-reconcile-attempts: 5
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

# Security configuration
security:
  jwt:
    secret: ${JWT_SECRET:}
    expiration: 3600
  oauth2:
    client-id: ${OAUTH2_CLIENT_ID:}
    client-secret: ${OAUTH2_CLIENT_SECRET:}
    issuer-uri: ${OAUTH2_ISSUER_URI:}

# Monitoring configuration
monitoring:
  opentelemetry:
    enabled: true
    service-name: api-gateway
    jaeger-endpoint: ${JAEGER_ENDPOINT:http://jaeger:14268/api/traces}
  prometheus:
    enabled: true
    endpoint: ${PROMETHEUS_ENDPOINT:http://prometheus:9090}
  operator-type: java
```

## Maven Dependencies for Java Operator Integration

### 1. Kubernetes Client Dependencies
```xml
<!-- src/shared/kubernetes/pom.xml -->
<dependencies>
    <!-- Fabric8 Kubernetes Client -->
    <dependency>
        <groupId>io.fabric8</groupId>
        <artifactId>kubernetes-client</artifactId>
        <version>6.7.0</version>
    </dependency>
    
    <!-- Fabric8 Kubernetes Model -->
    <dependency>
        <groupId>io.fabric8</groupId>
        <artifactId>kubernetes-model</artifactId>
        <version>6.7.0</version>
    </dependency>
    
    <!-- Spring Boot Kubernetes Integration -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-kubernetes-client</artifactId>
        <version>2.1.0</version>
    </dependency>
    
    <!-- Spring Boot Kubernetes Discovery -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-kubernetes-discovery</artifactId>
        <version>2.1.0</version>
    </dependency>
    
    <!-- Spring Boot Kubernetes Config -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-kubernetes-config</artifactId>
        <version>2.1.0</version>
    </dependency>
    
    <!-- Jackson for JSON processing -->
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
    </dependency>
    
    <!-- OpenTelemetry for tracing -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-api</artifactId>
        <version>1.28.0</version>
    </dependency>
    
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-sdk</artifactId>
        <version>1.28.0</version>
    </dependency>
</dependencies>
```

### 2. Operator Integration Dependencies
```xml
<!-- src/api-gateway/pom.xml -->
<dependencies>
    <!-- Spring Boot Starter Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Spring Boot Starter Security -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    
    <!-- Spring Boot Starter Actuator -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    
    <!-- Spring Boot Starter Data JPA -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    
    <!-- Spring Boot Starter Data Redis -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
    </dependency>
    
    <!-- Spring Kafka -->
    <dependency>
        <groupId>org.springframework.kafka</groupId>
        <artifactId>spring-kafka</artifactId>
    </dependency>
    
    <!-- Fabric8 Kubernetes Client -->
    <dependency>
        <groupId>io.fabric8</groupId>
        <artifactId>kubernetes-client</artifactId>
    </dependency>
    
    <!-- Micrometer Prometheus -->
    <dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-registry-prometheus</artifactId>
    </dependency>
    
    <!-- Shared Libraries -->
    <dependency>
        <groupId>com.bank.interoperability</groupId>
        <artifactId>shared-common</artifactId>
        <version>1.0.0</version>
    </dependency>
    
    <dependency>
        <groupId>com.bank.interoperability</groupId>
        <artifactId>shared-security</artifactId>
        <version>1.0.0</version>
    </dependency>
    
    <dependency>
        <groupId>com.bank.interoperability</groupId>
        <artifactId>shared-kubernetes</artifactId>
        <version>1.0.0</version>
    </dependency>
</dependencies>
```

## Docker Configuration for Java Operators

### 1. Multi-stage Dockerfile
```dockerfile
# operators/interoperability-operator/Dockerfile
# Build stage
FROM maven:3.8.4-openjdk-17-slim AS build

WORKDIR /app

# Copy pom files
COPY pom.xml .
COPY src ./src

# Build application
RUN mvn clean package -DskipTests

# Final stage
FROM openjdk:17-jre-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy JAR file
COPY --from=build /app/target/interoperability-operator-*.jar app.jar

# Change ownership
RUN chown appuser:appuser app.jar

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8081/health || exit 1

# Run application
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 2. Production Dockerfile
```dockerfile
# operators/interoperability-operator/Dockerfile.prod
FROM openjdk:17-jre-slim

WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy JAR file
COPY target/interoperability-operator-*.jar app.jar

# Change ownership
RUN chown appuser:appuser app.jar

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8081/health || exit 1

# Run application with production settings
ENTRYPOINT ["java", "-Xmx512m", "-Xms256m", "-jar", "app.jar"]
```

This completes the Spring Boot microservices integration with Java Kubernetes operators!