# Enhanced Saga Pattern Implementation with Temporal.io for Bank Interoperability

## Enhanced Saga Pattern Overview

The enhanced Saga pattern integrates Temporal.io workflow engine, Apache Kafka event streaming, and advanced security technologies to ensure data consistency across distributed services with enterprise-grade reliability and observability.

## Enhanced Core Saga Components

### 1. Temporal.io Workflow Integration
```java
@WorkflowInterface
public interface BankInteroperabilityWorkflow {
    @WorkflowMethod
    String processBankingRequest(BankingRequest request, SecurityContext securityContext);
}

@Component
public class BankInteroperabilityWorkflowImpl implements BankInteroperabilityWorkflow {
    
    @Override
    public String processBankingRequest(BankingRequest request, SecurityContext securityContext) {
        // Step 1: Validate request with security context
        String validationResult = activities.validateRequestWithSecurity(request, securityContext);
        
        // Step 2: Execute on-premise steps
        String onPremResult = activities.executeOnPremiseSteps(request, securityContext);
        
        // Step 3: Execute cloud steps
        String cloudResult = activities.executeCloudSteps(request, securityContext);
        
        // Step 4: Finalize transaction
        String finalResult = activities.finalizeTransaction(request, onPremResult, cloudResult);
        
        return finalResult;
    }
}
```

### 2. Enhanced Saga Context with Temporal.io
```java
@Entity
@Table(name = "saga_context")
public class SagaContext {
    
    @Id
    private String sagaId;
    
    @Enumerated(EnumType.STRING)
    private SagaStatus status;
    
    @OneToMany(cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<SagaStep> steps;
    
    @OneToMany(cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<CompensationAction> compensationActions;
    
    private String originalRequest;
    private String routingDecision;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;
    private String failureReason;
}

@Entity
@Table(name = "saga_step")
public class SagaStep {
    
    @Id
    private String stepId;
    
    private String sagaId;
    
    @Enumerated(EnumType.STRING)
    private StepStatus status;
    
    @Enumerated(EnumType.STRING)
    private StepType type;
    
    private String targetService;
    private String targetEndpoint;
    private String payload;
    private String response;
    private String errorMessage;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;
    
    @OneToMany(cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<StepDependency> dependencies;
}
```

### 2. Saga Orchestrator
```java
@Service
@Transactional
public class SagaOrchestratorService {
    
    @Autowired
    private SagaContextRepository sagaContextRepository;
    
    @Autowired
    private SagaStepRepository sagaStepRepository;
    
    @Autowired
    private EventPublisher eventPublisher;
    
    @Autowired
    private ProtocolAdapterService protocolAdapterService;
    
    public String startSaga(IncomingRequest request, RoutingDecision decision) {
        String sagaId = UUID.randomUUID().toString();
        
        // Create saga context
        SagaContext context = createSagaContext(sagaId, request, decision);
        sagaContextRepository.save(context);
        
        // Create saga steps
        List<SagaStep> steps = createSagaSteps(context, decision);
        sagaStepRepository.saveAll(steps);
        
        // Publish saga started event
        eventPublisher.publishSagaStartedEvent(context);
        
        // Start execution
        executeSagaAsync(context);
        
        return sagaId;
    }
    
    @Async
    public void executeSagaAsync(SagaContext context) {
        try {
            executeSagaSteps(context);
            completeSaga(context);
        } catch (Exception e) {
            compensateSaga(context, e);
        }
    }
    
    private void executeSagaSteps(SagaContext context) {
        List<SagaStep> executableSteps = getExecutableSteps(context);
        
        while (!executableSteps.isEmpty()) {
            // Execute steps in parallel where possible
            List<CompletableFuture<Void>> futures = executableSteps.stream()
                .map(step -> executeStepAsync(context, step))
                .collect(Collectors.toList());
            
            // Wait for all steps to complete
            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
            
            // Get next executable steps
            executableSteps = getExecutableSteps(context);
        }
    }
    
    @Async
    public CompletableFuture<Void> executeStepAsync(SagaContext context, SagaStep step) {
        try {
            step.setStatus(StepStatus.EXECUTING);
            step.setStartedAt(LocalDateTime.now());
            sagaStepRepository.save(step);
            
            // Execute the step
            AdapterResponse response = protocolAdapterService.adaptAndCall(
                createExecutionStep(step), step.getPayload());
            
            step.setStatus(StepStatus.COMPLETED);
            step.setResponse(response.getResponse());
            step.setCompletedAt(LocalDateTime.now());
            sagaStepRepository.save(step);
            
            // Publish step completed event
            eventPublisher.publishSagaStepCompletedEvent(context.getSagaId(), step.getStepId());
            
        } catch (Exception e) {
            step.setStatus(StepStatus.FAILED);
            step.setErrorMessage(e.getMessage());
            step.setCompletedAt(LocalDateTime.now());
            sagaStepRepository.save(step);
            
            // Publish step failed event
            eventPublisher.publishSagaStepFailedEvent(context.getSagaId(), step.getStepId(), e);
            
            throw new SagaExecutionException("Step execution failed", e);
        }
        
        return CompletableFuture.completedFuture(null);
    }
    
    private void compensateSaga(SagaContext context, Exception failure) {
        context.setStatus(SagaStatus.COMPENSATING);
        context.setFailureReason(failure.getMessage());
        sagaContextRepository.save(context);
        
        // Execute compensation actions in reverse order
        List<SagaStep> completedSteps = getCompletedSteps(context);
        Collections.reverse(completedSteps);
        
        for (SagaStep step : completedSteps) {
            try {
                executeCompensationAction(context, step);
            } catch (Exception e) {
                // Log compensation failure
                log.error("Compensation failed for step: {}", step.getStepId(), e);
            }
        }
        
        context.setStatus(SagaStatus.COMPENSATED);
        context.setCompletedAt(LocalDateTime.now());
        sagaContextRepository.save(context);
        
        // Publish saga compensated event
        eventPublisher.publishSagaCompensatedEvent(context);
    }
}
```

### 3. Compensation Actions
```java
@Service
public class CompensationService {
    
    @Autowired
    private ProtocolAdapterService protocolAdapterService;
    
    public void executeCompensationAction(SagaContext context, SagaStep step) {
        CompensationAction compensation = createCompensationAction(step);
        
        try {
            // Execute compensation
            AdapterResponse response = protocolAdapterService.adaptAndCall(
                createCompensationStep(compensation), compensation.getPayload());
            
            compensation.setStatus(CompensationStatus.COMPLETED);
            compensation.setResponse(response.getResponse());
            
        } catch (Exception e) {
            compensation.setStatus(CompensationStatus.FAILED);
            compensation.setErrorMessage(e.getMessage());
            throw new CompensationException("Compensation failed", e);
        }
    }
    
    private CompensationAction createCompensationAction(SagaStep step) {
        return CompensationAction.builder()
            .sagaId(step.getSagaId())
            .originalStepId(step.getStepId())
            .compensationType(determineCompensationType(step))
            .targetService(step.getTargetService())
            .targetEndpoint(getCompensationEndpoint(step))
            .payload(createCompensationPayload(step))
            .status(CompensationStatus.PENDING)
            .build();
    }
}
```

### 4. Saga State Management
```java
@Repository
public interface SagaContextRepository extends JpaRepository<SagaContext, String> {
    
    List<SagaContext> findByStatus(SagaStatus status);
    
    List<SagaContext> findByStatusAndStartedAtBefore(
        SagaStatus status, LocalDateTime before);
    
    @Query("SELECT s FROM SagaContext s WHERE s.status IN :statuses")
    List<SagaContext> findByStatusIn(@Param("statuses") List<SagaStatus> statuses);
}

@Repository
public interface SagaStepRepository extends JpaRepository<SagaStep, String> {
    
    List<SagaStep> findBySagaIdAndStatus(String sagaId, StepStatus status);
    
    List<SagaStep> findBySagaIdOrderByCreatedAt(String sagaId);
    
    @Query("SELECT s FROM SagaStep s WHERE s.sagaId = :sagaId AND s.status = :status")
    List<SagaStep> findExecutableSteps(@Param("sagaId") String sagaId, @Param("status") StepStatus status);
}
```

## Saga Event Handling

### Event Listeners
```java
@Component
public class SagaEventListener {
    
    @Autowired
    private SagaOrchestratorService sagaOrchestratorService;
    
    @EventListener
    public void handleSagaStepCompleted(SagaStepCompletedEvent event) {
        // Check if saga can proceed
        SagaContext context = sagaOrchestratorService.getSagaContext(event.getSagaId());
        
        if (areAllStepsCompleted(context)) {
            sagaOrchestratorService.completeSaga(context);
        } else {
            // Trigger next executable steps
            sagaOrchestratorService.triggerNextSteps(context);
        }
    }
    
    @EventListener
    public void handleSagaStepFailed(SagaStepFailedEvent event) {
        // Initiate compensation
        SagaContext context = sagaOrchestratorService.getSagaContext(event.getSagaId());
        sagaOrchestratorService.compensateSaga(context, event.getException());
    }
}
```

## Saga Monitoring and Recovery

### Saga Monitor Service
```java
@Service
@Scheduled(fixedRate = 30000) // Run every 30 seconds
public class SagaMonitorService {
    
    @Autowired
    private SagaContextRepository sagaContextRepository;
    
    @Autowired
    private SagaOrchestratorService sagaOrchestratorService;
    
    public void monitorStuckSagas() {
        LocalDateTime threshold = LocalDateTime.now().minusMinutes(5);
        
        List<SagaContext> stuckSagas = sagaContextRepository
            .findByStatusAndStartedAtBefore(SagaStatus.EXECUTING, threshold);
        
        for (SagaContext saga : stuckSagas) {
            log.warn("Found stuck saga: {}", saga.getSagaId());
            // Attempt recovery or compensation
            sagaOrchestratorService.recoverSaga(saga);
        }
    }
    
    public void cleanupCompletedSagas() {
        LocalDateTime cleanupThreshold = LocalDateTime.now().minusDays(7);
        
        List<SagaContext> oldSagas = sagaContextRepository
            .findByStatusAndCompletedAtBefore(SagaStatus.COMPLETED, cleanupThreshold);
        
        sagaContextRepository.deleteAll(oldSagas);
    }
}
```