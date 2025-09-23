# Spring Boot Microservices Integration with Go Kubernetes Operators

## Integration Architecture

### Operator-Service Communication
```
┌─────────────────────────────────────────────────────────────────┐
│                    Operator-Service Integration                  │
├─────────────────────────────────────────────────────────────────┤
│ Spring Boot Services ←→ Kubernetes API ←→ Go Operators          │
│     ↓                    ↓                    ↓                  │
│ API Gateway          InteroperabilityRequest  InteroperabilityOp  │
│ Intelligent Router   RoutingDecision         RoutingOperator     │
│ Saga Orchestrator    Saga                    SagaOperator        │
│ Security Services    SecurityPolicy          SecurityOperator     │
└─────────────────────────────────────────────────────────────────┘
```

## Spring Boot Kubernetes Client Integration

### 1. Kubernetes Client Configuration
```java
// src/shared/kubernetes/src/main/java/com/bank/interoperability/kubernetes/config/KubernetesConfig.java
package com.bank.interoperability.kubernetes.config;

import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.Configuration;
import io.kubernetes.client.openapi.apis.CustomObjectsApi;
import io.kubernetes.client.util.Config;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class KubernetesConfig {
    
    @Bean
    public ApiClient kubernetesApiClient() throws Exception {
        ApiClient client = Config.defaultClient();
        Configuration.setDefaultApiClient(client);
        return client;
    }
    
    @Bean
    public CustomObjectsApi customObjectsApi(ApiClient apiClient) {
        return new CustomObjectsApi(apiClient);
    }
}
```

### 2. Custom Resource Client
```java
// src/shared/kubernetes/src/main/java/com/bank/interoperability/kubernetes/client/InteroperabilityRequestClient.java
package com.bank.interoperability.kubernetes.client;

import com.bank.interoperability.kubernetes.model.InteroperabilityRequest;
import com.bank.interoperability.kubernetes.model.InteroperabilityRequestList;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.apis.CustomObjectsApi;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class InteroperabilityRequestClient {
    
    private static final String GROUP = "interoperability.bank.com";
    private static final String VERSION = "v1";
    private static final String PLURAL = "interoperabilityrequests";
    
    @Autowired
    private CustomObjectsApi customObjectsApi;
    
    public InteroperabilityRequest createInteroperabilityRequest(
            String namespace, 
            InteroperabilityRequest request) throws ApiException {
        
        Object response = customObjectsApi.createNamespacedCustomObject(
            GROUP, VERSION, namespace, PLURAL, request, null, null, null);
        
        return convertToInteroperabilityRequest(response);
    }
    
    public InteroperabilityRequest getInteroperabilityRequest(
            String namespace, 
            String name) throws ApiException {
        
        Object response = customObjectsApi.getNamespacedCustomObject(
            GROUP, VERSION, namespace, PLURAL, name);
        
        return convertToInteroperabilityRequest(response);
    }
    
    public InteroperabilityRequest updateInteroperabilityRequest(
            String namespace, 
            String name, 
            InteroperabilityRequest request) throws ApiException {
        
        Object response = customObjectsApi.replaceNamespacedCustomObject(
            GROUP, VERSION, namespace, PLURAL, name, request, null, null);
        
        return convertToInteroperabilityRequest(response);
    }
    
    public InteroperabilityRequestList listInteroperabilityRequests(
            String namespace) throws ApiException {
        
        Object response = customObjectsApi.listNamespacedCustomObject(
            GROUP, VERSION, namespace, PLURAL, null, null, null, null, null, null, null, null);
        
        return convertToInteroperabilityRequestList(response);
    }
    
    public void deleteInteroperabilityRequest(
            String namespace, 
            String name) throws ApiException {
        
        customObjectsApi.deleteNamespacedCustomObject(
            GROUP, VERSION, namespace, PLURAL, name, null, null, null, null);
    }
    
    private InteroperabilityRequest convertToInteroperabilityRequest(Object response) {
        // Convert Kubernetes Object to InteroperabilityRequest
        // Implementation depends on your JSON serialization library
        return null; // Placeholder
    }
    
    private InteroperabilityRequestList convertToInteroperabilityRequestList(Object response) {
        // Convert Kubernetes Object to InteroperabilityRequestList
        return null; // Placeholder
    }
}
```

## API Gateway Integration

### 1. Enhanced Gateway Service
```java
// src/api-gateway/src/main/java/com/bank/interoperability/gateway/service/EnhancedGatewayService.java
package com.bank.interoperability.gateway.service;

import com.bank.interoperability.gateway.dto.IncomingRequest;
import com.bank.interoperability.gateway.dto.ProcessResponse;
import com.bank.interoperability.kubernetes.client.InteroperabilityRequestClient;
import com.bank.interoperability.kubernetes.model.InteroperabilityRequest;
import com.bank.interoperability.kubernetes.model.InteroperabilityRequestSpec;
import com.bank.interoperability.kubernetes.model.SecurityContext;
import com.bank.interoperability.shared.monitoring.OpenTelemetryService;
import io.opentelemetry.api.trace.Span;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class EnhancedGatewayService {
    
    @Autowired
    private InteroperabilityRequestClient interoperabilityRequestClient;
    
    @Autowired
    private OpenTelemetryService telemetryService;
    
    public ProcessResponse processRequest(IncomingRequest request, String requestId, String userId) {
        Span span = telemetryService.startSpan("gateway-process-request");
        
        try {
            // Create InteroperabilityRequest CRD
            InteroperabilityRequest crdRequest = createInteroperabilityRequest(request, requestId, userId);
            
            // Submit to Kubernetes operator
            InteroperabilityRequest createdRequest = interoperabilityRequestClient.createInteroperabilityRequest(
                "interoperability-core", crdRequest);
            
            return ProcessResponse.builder()
                .sagaId(createdRequest.getMetadata().getName())
                .status("PROCESSING")
                .requestId(requestId)
                .crdName(createdRequest.getMetadata().getName())
                .build();
                
        } finally {
            span.end();
        }
    }
    
    public String getSagaStatus(String sagaId) {
        try {
            InteroperabilityRequest request = interoperabilityRequestClient.getInteroperabilityRequest(
                "interoperability-core", sagaId);
            
            return request.getStatus().getPhase();
        } catch (Exception e) {
            return "UNKNOWN";
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
        spec.setSecurityContext(securityContext);
        
        crdRequest.setSpec(spec);
        
        return crdRequest;
    }
}
```

## Intelligent Router Integration

### 1. Router Service with Operator Integration
```java
// src/intelligent-router/src/main/java/com/bank/interoperability/router/service/OperatorIntegratedRouterService.java
package com.bank.interoperability.router.service;

import com.bank.interoperability.kubernetes.client.RoutingDecisionClient;
import com.bank.interoperability.kubernetes.model.RoutingDecision;
import com.bank.interoperability.kubernetes.model.RoutingDecisionSpec;
import com.bank.interoperability.router.dto.RequestProfile;
import com.bank.interoperability.router.dto.RoutingDecision as RouterDecision;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class OperatorIntegratedRouterService {
    
    @Autowired
    private RoutingDecisionClient routingDecisionClient;
    
    @Autowired
    private MLRequestAnalyzer mlAnalyzer;
    
    public RouterDecision routeRequest(IncomingRequest request) {
        // Create RoutingDecision CRD
        RoutingDecision crdDecision = createRoutingDecision(request);
        
        // Submit to routing operator
        RoutingDecision createdDecision = routingDecisionClient.createRoutingDecision(
            "interoperability-routing", crdDecision);
        
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
        // Poll the operator until decision is made
        int maxAttempts = 30;
        int attempt = 0;
        
        while (attempt < maxAttempts) {
            try {
                RoutingDecision decision = routingDecisionClient.getRoutingDecision(
                    "interoperability-routing", decisionName);
                
                if (decision.getStatus().getStrategy() != null) {
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
            .build();
    }
}
```

## Saga Orchestrator Integration

### 1. Saga Service with Operator Integration
```java
// src/saga-orchestrator/src/main/java/com/bank/interoperability/saga/service/OperatorIntegratedSagaService.java
package com.bank.interoperability.saga.service;

import com.bank.interoperability.kubernetes.client.SagaClient;
import com.bank.interoperability.kubernetes.model.Saga;
import com.bank.interoperability.kubernetes.model.SagaSpec;
import com.bank.interoperability.kubernetes.model.SagaStep;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class OperatorIntegratedSagaService {
    
    @Autowired
    private SagaClient sagaClient;
    
    public String startSaga(IncomingRequest request, RoutingDecision decision) {
        // Create Saga CRD
        Saga saga = createSaga(request, decision);
        
        // Submit to saga operator
        Saga createdSaga = sagaClient.createSaga("interoperability-saga", saga);
        
        return createdSaga.getMetadata().getName();
    }
    
    public String getSagaStatus(String sagaId) {
        try {
            Saga saga = sagaClient.getSaga("interoperability-saga", sagaId);
            return saga.getStatus().getPhase();
        } catch (Exception e) {
            return "UNKNOWN";
        }
    }
    
    private Saga createSaga(IncomingRequest request, RoutingDecision decision) {
        Saga saga = new Saga();
        
        // Set metadata
        saga.getMetadata().setName(request.getRequestId());
        saga.getMetadata().setNamespace("interoperability-saga");
        
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

## Security Services Integration

### 1. Security Service with Operator Integration
```java
// src/security-services/src/main/java/com/bank/interoperability/security/service/OperatorIntegratedSecurityService.java
package com.bank.interoperability.security.service;

import com.bank.interoperability.kubernetes.client.SecurityPolicyClient;
import com.bank.interoperability.kubernetes.model.SecurityPolicy;
import com.bank.interoperability.kubernetes.model.SecurityPolicySpec;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class OperatorIntegratedSecurityService {
    
    @Autowired
    private SecurityPolicyClient securityPolicyClient;
    
    public SecurityContext validateSecurity(IncomingRequest request, String userId) {
        // Create SecurityPolicy CRD
        SecurityPolicy policy = createSecurityPolicy(request, userId);
        
        // Submit to security operator
        SecurityPolicy createdPolicy = securityPolicyClient.createSecurityPolicy(
            "interoperability-security", policy);
        
        // Wait for security validation
        SecurityPolicy validatedPolicy = waitForSecurityValidation(
            createdPolicy.getMetadata().getName());
        
        // Extract security context
        return extractSecurityContext(validatedPolicy);
    }
    
    private SecurityPolicy createSecurityPolicy(IncomingRequest request, String userId) {
        SecurityPolicy policy = new SecurityPolicy();
        
        // Set metadata
        policy.getMetadata().setName(request.getRequestId() + "-security");
        policy.getMetadata().setNamespace("interoperability-security");
        
        // Set spec
        SecurityPolicySpec spec = new SecurityPolicySpec();
        spec.setRequestId(request.getRequestId());
        spec.setUserId(userId);
        spec.setRequestType(request.getRequestType());
        spec.setSensitivityLevel(determineSensitivityLevel(request));
        spec.setComplianceRequirements(getComplianceRequirements(request));
        
        policy.setSpec(spec);
        
        return policy;
    }
    
    private SecurityPolicy waitForSecurityValidation(String policyName) {
        // Poll the operator until security validation is complete
        int maxAttempts = 30;
        int attempt = 0;
        
        while (attempt < maxAttempts) {
            try {
                SecurityPolicy policy = securityPolicyClient.getSecurityPolicy(
                    "interoperability-security", policyName);
                
                if (policy.getStatus().getEnforcementStatus() != null) {
                    return policy;
                }
                
                Thread.sleep(1000); // Wait 1 second
                attempt++;
            } catch (Exception e) {
                // Handle error
                break;
            }
        }
        
        throw new RuntimeException("Security validation timeout");
    }
}
```

## Kubernetes Model Classes

### 1. InteroperabilityRequest Model
```java
// src/shared/kubernetes/src/main/java/com/bank/interoperability/kubernetes/model/InteroperabilityRequest.java
package com.bank.interoperability.kubernetes.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class InteroperabilityRequest {
    
    @JsonProperty("apiVersion")
    private String apiVersion = "interoperability.bank.com/v1";
    
    @JsonProperty("kind")
    private String kind = "InteroperabilityRequest";
    
    @JsonProperty("metadata")
    private ObjectMetadata metadata = new ObjectMetadata();
    
    @JsonProperty("spec")
    private InteroperabilityRequestSpec spec;
    
    @JsonProperty("status")
    private InteroperabilityRequestStatus status;
    
    // Getters and setters
    public String getApiVersion() { return apiVersion; }
    public void setApiVersion(String apiVersion) { this.apiVersion = apiVersion; }
    
    public String getKind() { return kind; }
    public void setKind(String kind) { this.kind = kind; }
    
    public ObjectMetadata getMetadata() { return metadata; }
    public void setMetadata(ObjectMetadata metadata) { this.metadata = metadata; }
    
    public InteroperabilityRequestSpec getSpec() { return spec; }
    public void setSpec(InteroperabilityRequestSpec spec) { this.spec = spec; }
    
    public InteroperabilityRequestStatus getStatus() { return status; }
    public void setStatus(InteroperabilityRequestStatus status) { this.status = status; }
}

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
}

public class InteroperabilityRequestStatus {
    
    @JsonProperty("phase")
    private String phase;
    
    @JsonProperty("message")
    private String message;
    
    @JsonProperty("lastTransitionTime")
    private String lastTransitionTime;
    
    @JsonProperty("steps")
    private List<StepStatus> steps;
    
    @JsonProperty("conditions")
    private List<Condition> conditions;
    
    // Getters and setters
}

public class ObjectMetadata {
    
    @JsonProperty("name")
    private String name;
    
    @JsonProperty("namespace")
    private String namespace;
    
    @JsonProperty("labels")
    private Map<String, String> labels = new HashMap<>();
    
    @JsonProperty("annotations")
    private Map<String, String> annotations = new HashMap<>();
    
    // Getters and setters
}
```

## Application Configuration Updates

### 1. Kubernetes Integration Configuration
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
    
  # CRD configuration
  crd:
    interoperability-request:
      group: interoperability.bank.com
      version: v1
      plural: interoperabilityrequests
    
    routing-decision:
      group: routing.bank.com
      version: v1
      plural: routingdecisions
    
    saga:
      group: saga.bank.com
      version: v1
      plural: sagas
    
    security-policy:
      group: security.bank.com
      version: v1
      plural: securitypolicies

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
```

## Maven Dependencies for Kubernetes Integration

### 1. Kubernetes Client Dependencies
```xml
<!-- src/shared/kubernetes/pom.xml -->
<dependencies>
    <!-- Kubernetes Java Client -->
    <dependency>
        <groupId>io.kubernetes</groupId>
        <artifactId>client-java</artifactId>
        <version>18.0.1</version>
    </dependency>
    
    <!-- Kubernetes Spring Integration -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-kubernetes-client</artifactId>
        <version>2.1.0</version>
    </dependency>
    
    <!-- Kubernetes Discovery -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-kubernetes-discovery</artifactId>
        <version>2.1.0</version>
    </dependency>
    
    <!-- Kubernetes Config -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-kubernetes-config</artifactId>
        <version>2.1.0</version>
    </dependency>
</dependencies>
```

This completes the Spring Boot microservices integration with Go Kubernetes operators!