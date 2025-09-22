# Spring Boot Microservices Structure for Bank Interoperability Layer

## Microservices Architecture Overview

### Service Structure
```
src/
├── api-gateway/                    # API Gateway Service
├── intelligent-router/            # Intelligent Router Service
├── saga-orchestrator/             # Saga Orchestrator Service
├── protocol-adapters/              # Protocol Adapters Service
├── schema-adapters/               # Schema Adapters Service
├── security-services/             # Security Services
├── event-coordinator/             # Event Coordinator Service
└── shared/                        # Shared Libraries
    ├── common/
    ├── security/
    ├── monitoring/
    └── utils/
```

## API Gateway Service

### 1. Project Structure (src/api-gateway/)
```
api-gateway/
├── src/main/java/com/bank/interoperability/gateway/
│   ├── GatewayApplication.java
│   ├── config/
│   │   ├── SecurityConfig.java
│   │   ├── WebConfig.java
│   │   └── MonitoringConfig.java
│   ├── controller/
│   │   └── InteroperabilityController.java
│   ├── service/
│   │   ├── GatewayService.java
│   │   └── RoutingService.java
│   ├── dto/
│   │   ├── IncomingRequest.java
│   │   └── ProcessResponse.java
│   └── exception/
│       └── GatewayException.java
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
// src/api-gateway/src/main/java/com/bank/interoperability/gateway/GatewayApplication.java
package com.bank.interoperability.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
@EnableFeignClients
public class GatewayApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
    }
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
```

### 3. Gateway Controller
```java
// src/api-gateway/src/main/java/com/bank/interoperability/gateway/controller/InteroperabilityController.java
package com.bank.interoperability.gateway.controller;

import com.bank.interoperability.gateway.dto.IncomingRequest;
import com.bank.interoperability.gateway.dto.ProcessResponse;
import com.bank.interoperability.gateway.service.GatewayService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;

@RestController
@RequestMapping("/api/v1")
@Tag(name = "Interoperability Gateway", description = "Bank Interoperability API Gateway")
public class InteroperabilityController {
    
    @Autowired
    private GatewayService gatewayService;
    
    @PostMapping("/process")
    @Operation(summary = "Process banking request", description = "Process incoming banking request through interoperability layer")
    @PreAuthorize("@securityService.hasPermission(#request.requestType, 'PROCESS')")
    public ResponseEntity<ProcessResponse> processRequest(
            @RequestBody @Valid IncomingRequest request,
            @RequestHeader("X-Request-ID") String requestId,
            @RequestHeader("X-User-ID") String userId) {
        
        ProcessResponse response = gatewayService.processRequest(request, requestId, userId);
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/health")
    @Operation(summary = "Health check", description = "Check gateway health status")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Gateway is healthy");
    }
    
    @GetMapping("/status/{sagaId}")
    @Operation(summary = "Get saga status", description = "Get status of a specific saga")
    public ResponseEntity<String> getSagaStatus(@PathVariable String sagaId) {
        String status = gatewayService.getSagaStatus(sagaId);
        return ResponseEntity.ok(status);
    }
}
```

### 4. Gateway Service
```java
// src/api-gateway/src/main/java/com/bank/interoperability/gateway/service/GatewayService.java
package com.bank.interoperability.gateway.service;

import com.bank.interoperability.gateway.dto.IncomingRequest;
import com.bank.interoperability.gateway.dto.ProcessResponse;
import com.bank.interoperability.gateway.service.RoutingService;
import com.bank.interoperability.shared.monitoring.OpenTelemetryService;
import io.opentelemetry.api.trace.Span;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class GatewayService {
    
    @Autowired
    private RoutingService routingService;
    
    @Autowired
    private OpenTelemetryService telemetryService;
    
    public ProcessResponse processRequest(IncomingRequest request, String requestId, String userId) {
        Span span = telemetryService.startSpan("gateway-process-request");
        
        try {
            // Validate request
            validateRequest(request);
            
            // Route request
            String sagaId = routingService.routeRequest(request, requestId, userId);
            
            return ProcessResponse.builder()
                .sagaId(sagaId)
                .status("PROCESSING")
                .requestId(requestId)
                .build();
                
        } finally {
            span.end();
        }
    }
    
    public String getSagaStatus(String sagaId) {
        return routingService.getSagaStatus(sagaId);
    }
    
    private void validateRequest(IncomingRequest request) {
        if (request == null || request.getRequestType() == null) {
            throw new IllegalArgumentException("Invalid request");
        }
    }
}
```

## Intelligent Router Service

### 1. Project Structure (src/intelligent-router/)
```
intelligent-router/
├── src/main/java/com/bank/interoperability/router/
│   ├── RouterApplication.java
│   ├── config/
│   │   ├── RouterConfig.java
│   │   └── MLConfig.java
│   ├── service/
│   │   ├── IntelligentRouterService.java
│   │   ├── MLRequestAnalyzer.java
│   │   └── LoadBalancerService.java
│   ├── dto/
│   │   ├── RequestProfile.java
│   │   ├── RoutingDecision.java
│   │   └── LoadDistribution.java
│   └── controller/
│       └── RouterController.java
├── src/main/resources/
│   ├── application.yml
│   └── ml-models/
│       ├── request-classifier.model
│       └── risk-assessor.model
├── Dockerfile
└── pom.xml
```

### 2. Intelligent Router Service
```java
// src/intelligent-router/src/main/java/com/bank/interoperability/router/service/IntelligentRouterService.java
package com.bank.interoperability.router.service;

import com.bank.interoperability.router.dto.RequestProfile;
import com.bank.interoperability.router.dto.RoutingDecision;
import com.bank.interoperability.router.service.MLRequestAnalyzer;
import com.bank.interoperability.router.service.LoadBalancerService;
import com.bank.interoperability.shared.monitoring.OpenTelemetryService;
import io.opentelemetry.api.trace.Span;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class IntelligentRouterService {
    
    @Autowired
    private MLRequestAnalyzer mlAnalyzer;
    
    @Autowired
    private LoadBalancerService loadBalancerService;
    
    @Autowired
    private OpenTelemetryService telemetryService;
    
    public RoutingDecision routeRequest(IncomingRequest request) {
        Span span = telemetryService.startSpan("intelligent-routing");
        
        try {
            // Analyze request with ML
            RequestProfile profile = mlAnalyzer.analyzeRequest(request);
            
            // Calculate load distribution
            LoadDistribution distribution = loadBalancerService.calculateDistribution(profile);
            
            // Make routing decision
            RoutingDecision decision = makeRoutingDecision(profile, distribution);
            
            return decision;
            
        } finally {
            span.end();
        }
    }
    
    private RoutingDecision makeRoutingDecision(RequestProfile profile, LoadDistribution distribution) {
        // Implement intelligent routing logic
        double onPremScore = calculateOnPremScore(profile);
        double cloudScore = calculateCloudScore(profile);
        
        if (onPremScore > cloudScore + 0.2) {
            return RoutingDecision.builder()
                .strategy("ON_PREM_ONLY")
                .reasoning("On-premise routing preferred")
                .build();
        } else if (cloudScore > onPremScore + 0.2) {
            return RoutingDecision.builder()
                .strategy("CLOUD_ONLY")
                .reasoning("Cloud routing preferred")
                .build();
        } else {
            return RoutingDecision.builder()
                .strategy("HYBRID")
                .reasoning("Hybrid routing for optimal performance")
                .build();
        }
    }
}
```

## Saga Orchestrator Service

### 1. Project Structure (src/saga-orchestrator/)
```
saga-orchestrator/
├── src/main/java/com/bank/interoperability/saga/
│   ├── SagaApplication.java
│   ├── config/
│   │   ├── TemporalConfig.java
│   │   └── SagaConfig.java
│   ├── workflow/
│   │   ├── BankInteroperabilityWorkflow.java
│   │   └── BankInteroperabilityWorkflowImpl.java
│   ├── activity/
│   │   ├── BankingActivities.java
│   │   └── BankingActivitiesImpl.java
│   ├── service/
│   │   ├── SagaOrchestratorService.java
│   │   └── CompensationService.java
│   └── dto/
│       ├── SagaContext.java
│       └── SagaStep.java
├── src/main/resources/
│   ├── application.yml
│   └── temporal/
│       └── workflow-definitions/
├── Dockerfile
└── pom.xml
```

### 2. Temporal Workflow
```java
// src/saga-orchestrator/src/main/java/com/bank/interoperability/saga/workflow/BankInteroperabilityWorkflow.java
package com.bank.interoperability.saga.workflow;

import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.QueryMethod;

@WorkflowInterface
public interface BankInteroperabilityWorkflow {
    
    @WorkflowMethod
    String processBankingRequest(BankingRequest request, SecurityContext securityContext);
    
    @SignalMethod
    void updateSecurityContext(SecurityContext newContext);
    
    @QueryMethod
    WorkflowStatus getWorkflowStatus();
}
```

### 3. Workflow Implementation
```java
// src/saga-orchestrator/src/main/java/com/bank/interoperability/saga/workflow/BankInteroperabilityWorkflowImpl.java
package com.bank.interoperability.saga.workflow;

import com.bank.interoperability.saga.activity.BankingActivities;
import io.temporal.workflow.Workflow;
import org.springframework.stereotype.Component;

@Component
public class BankInteroperabilityWorkflowImpl implements BankInteroperabilityWorkflow {
    
    private final BankingActivities activities = Workflow.newActivityStub(BankingActivities.class);
    
    @Override
    public String processBankingRequest(BankingRequest request, SecurityContext securityContext) {
        try {
            // Step 1: Validate request with security context
            String validationResult = activities.validateRequestWithSecurity(request, securityContext);
            
            // Step 2: Execute on-premise steps
            String onPremResult = activities.executeOnPremiseSteps(request, securityContext);
            
            // Step 3: Execute cloud steps
            String cloudResult = activities.executeCloudSteps(request, securityContext);
            
            // Step 4: Finalize transaction
            String finalResult = activities.finalizeTransaction(request, onPremResult, cloudResult);
            
            return finalResult;
            
        } catch (Exception e) {
            // Automatic compensation
            activities.compensateTransaction(request, e);
            throw e;
        }
    }
    
    @Override
    public void updateSecurityContext(SecurityContext newContext) {
        // Update security context
        Workflow.getInfo().getWorkflowId();
    }
    
    @Override
    public WorkflowStatus getWorkflowStatus() {
        return WorkflowStatus.builder()
            .status("RUNNING")
            .build();
    }
}
```

## Protocol Adapters Service

### 1. Project Structure (src/protocol-adapters/)
```
protocol-adapters/
├── src/main/java/com/bank/interoperability/adapters/
│   ├── AdaptersApplication.java
│   ├── config/
│   │   ├── AdapterConfig.java
│   │   └── ProtocolConfig.java
│   ├── adapter/
│   │   ├── RestAdapter.java
│   │   ├── SoapAdapter.java
│   │   ├── MqAdapter.java
│   │   └── AdapterFactory.java
│   ├── service/
│   │   ├── ProtocolAdapterService.java
│   │   └── CircuitBreakerService.java
│   └── dto/
│       ├── AdapterRequest.java
│       └── AdapterResponse.java
├── src/main/resources/
│   ├── application.yml
│   └── protocols/
│       ├── rest-config.yml
│       ├── soap-config.yml
│       └── mq-config.yml
├── Dockerfile
└── pom.xml
```

### 2. REST Adapter
```java
// src/protocol-adapters/src/main/java/com/bank/interoperability/adapters/adapter/RestAdapter.java
package com.bank.interoperability.adapters.adapter;

import com.bank.interoperability.adapters.dto.AdapterRequest;
import com.bank.interoperability.adapters.dto.AdapterResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class RestAdapter implements ProtocolAdapter {
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Override
    public AdapterResponse adaptAndCall(AdapterRequest request) {
        try {
            // Create HTTP headers
            HttpHeaders headers = createHeaders(request);
            
            // Create HTTP entity
            HttpEntity<String> entity = new HttpEntity<>(request.getPayload(), headers);
            
            // Make REST call
            ResponseEntity<String> response = restTemplate.exchange(
                request.getEndpoint(),
                HttpMethod.valueOf(request.getMethod()),
                entity,
                String.class
            );
            
            return AdapterResponse.builder()
                .response(response.getBody())
                .success(response.getStatusCode().is2xxSuccessful())
                .statusCode(response.getStatusCode().value())
                .build();
                
        } catch (Exception e) {
            return AdapterResponse.builder()
                .success(false)
                .errorMessage(e.getMessage())
                .build();
        }
    }
    
    private HttpHeaders createHeaders(AdapterRequest request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Request-ID", request.getRequestId());
        headers.set("X-Saga-ID", request.getSagaId());
        return headers;
    }
}
```

## Schema Adapters Service

### 1. Project Structure (src/schema-adapters/)
```
schema-adapters/
├── src/main/java/com/bank/interoperability/schema/
│   ├── SchemaApplication.java
│   ├── config/
│   │   └── SchemaConfig.java
│   ├── adapter/
│   │   ├── JsonSchemaAdapter.java
│   │   ├── XmlSchemaAdapter.java
│   │   ├── YamlSchemaAdapter.java
│   │   └── SchemaAdapterFactory.java
│   ├── service/
│   │   └── SchemaAdapterService.java
│   └── dto/
│       ├── SchemaRequest.java
│       └── SchemaResponse.java
├── src/main/resources/
│   ├── application.yml
│   └── schemas/
│       ├── json-schema.json
│       ├── xml-schema.xsd
│       └── yaml-schema.yml
├── Dockerfile
└── pom.xml
```

## Security Services

### 1. Project Structure (src/security-services/)
```
security-services/
├── src/main/java/com/bank/interoperability/security/
│   ├── SecurityApplication.java
│   ├── config/
│   │   ├── SecurityConfig.java
│   │   ├── OAuth2Config.java
│   │   └── JwtConfig.java
│   ├── service/
│   │   ├── AuthenticationService.java
│   │   ├── AuthorizationService.java
│   │   ├── EncryptionService.java
│   │   └── AuditService.java
│   ├── controller/
│   │   └── SecurityController.java
│   └── dto/
│       ├── SecurityContext.java
│       └── AuthRequest.java
├── src/main/resources/
│   ├── application.yml
│   └── security/
│       ├── oauth2-config.yml
│       └── jwt-config.yml
├── Dockerfile
└── pom.xml
```

## Shared Libraries

### 1. Common Library (src/shared/common/)
```
shared/common/
├── src/main/java/com/bank/interoperability/common/
│   ├── dto/
│   │   ├── BaseRequest.java
│   │   ├── BaseResponse.java
│   │   └── ErrorResponse.java
│   ├── exception/
│   │   ├── InteroperabilityException.java
│   │   └── GlobalExceptionHandler.java
│   ├── util/
│   │   ├── DateUtils.java
│   │   ├── StringUtils.java
│   │   └── ValidationUtils.java
│   └── annotation/
│       ├── LogExecutionTime.java
│       └── ValidateRequest.java
├── pom.xml
└── README.md
```

### 2. Security Library (src/shared/security/)
```
shared/security/
├── src/main/java/com/bank/interoperability/security/
│   ├── config/
│   │   ├── SecurityProperties.java
│   │   └── JwtProperties.java
│   ├── service/
│   │   ├── JwtService.java
│   │   ├── EncryptionService.java
│   │   └── AuditService.java
│   ├── filter/
│   │   ├── JwtAuthenticationFilter.java
│   │   └── SecurityFilter.java
│   └── dto/
│       ├── JwtToken.java
│       └── SecurityContext.java
├── pom.xml
└── README.md
```

## Application Configuration

### 1. Main Application Configuration
```yaml
# src/api-gateway/src/main/resources/application.yml
server:
  port: 8080
  servlet:
    context-path: /

spring:
  application:
    name: api-gateway
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
  cloud:
    openfeign:
      client:
        config:
          default:
            connectTimeout: 5000
            readTimeout: 10000
            loggerLevel: basic

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

logging:
  level:
    com.bank.interoperability: DEBUG
    org.springframework.security: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"

# Application specific configuration
interoperability:
  gateway:
    timeout: 30000
    retry-attempts: 3
    circuit-breaker:
      enabled: true
      failure-threshold: 5
      timeout: 10000
```

### 2. Production Configuration
```yaml
# src/api-gateway/src/main/resources/application-prod.yml
server:
  port: 8080

spring:
  datasource:
    url: ${DATABASE_URL:jdbc:postgresql://postgres:5432/interoperability}
    username: ${DATABASE_USERNAME:postgres}
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
```

## Docker Configuration

### 1. API Gateway Dockerfile
```dockerfile
# src/api-gateway/Dockerfile
FROM openjdk:17-jdk-slim

WORKDIR /app

# Copy Maven files
COPY pom.xml .
COPY src ./src

# Build application
RUN apt-get update && apt-get install -y maven
RUN mvn clean package -DskipTests

# Copy JAR file
COPY target/api-gateway-*.jar app.jar

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run application
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 2. Multi-stage Dockerfile
```dockerfile
# Multi-stage Dockerfile for production
FROM maven:3.8.4-openjdk-17-slim AS build

WORKDIR /app
COPY pom.xml .
COPY src ./src

RUN mvn clean package -DskipTests

FROM openjdk:17-jre-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy JAR file
COPY --from=build /app/target/api-gateway-*.jar app.jar

# Change ownership
RUN chown appuser:appuser app.jar

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run application
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## Maven Configuration

### 1. Parent POM
```xml
<!-- pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.bank.interoperability</groupId>
    <artifactId>bank-interoperability</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    
    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <spring-boot.version>3.1.0</spring-boot.version>
        <spring-cloud.version>2022.0.3</spring-cloud.version>
    </properties>
    
    <modules>
        <module>api-gateway</module>
        <module>intelligent-router</module>
        <module>saga-orchestrator</module>
        <module>protocol-adapters</module>
        <module>schema-adapters</module>
        <module>security-services</module>
        <module>event-coordinator</module>
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
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

### 2. Service POM
```xml
<!-- src/api-gateway/pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>com.bank.interoperability</groupId>
        <artifactId>bank-interoperability</artifactId>
        <version>1.0.0</version>
    </parent>
    
    <artifactId>api-gateway</artifactId>
    <packaging>jar</packaging>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-openfeign</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
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
        <dependency>
            <groupId>com.bank.interoperability</groupId>
            <artifactId>shared-security</artifactId>
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

This completes the Spring Boot microservices structure. The next step would be to configure Helm charts for Kubernetes deployment.