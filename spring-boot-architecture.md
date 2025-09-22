# Spring Boot Microservices Architecture for Bank Interoperability

## Core Microservices

### 1. Gateway Service (API Gateway)
```java
@RestController
@RequestMapping("/api/v1")
public class InteroperabilityGateway {
    
    @Autowired
    private IntelligentRouter intelligentRouter;
    
    @Autowired
    private SagaOrchestrator sagaOrchestrator;
    
    @PostMapping("/process")
    public ResponseEntity<ProcessResponse> processRequest(
            @RequestBody IncomingRequest request) {
        
        // Route request intelligently
        RoutingDecision decision = intelligentRouter.routeRequest(request);
        
        // Start saga orchestration
        String sagaId = sagaOrchestrator.startSaga(request, decision);
        
        return ResponseEntity.ok(ProcessResponse.builder()
            .sagaId(sagaId)
            .status("PROCESSING")
            .build());
    }
}
```

### 2. Intelligent Router Service
```java
@Service
public class IntelligentRouterService {
    
    @Autowired
    private RequestAnalyzer requestAnalyzer;
    
    @Autowired
    private LoadBalancer loadBalancer;
    
    @Autowired
    private DependencyResolver dependencyResolver;
    
    public RoutingDecision routeRequest(IncomingRequest request) {
        // Analyze request characteristics
        RequestProfile profile = requestAnalyzer.analyze(request);
        
        // Calculate routing scores
        RoutingScores scores = calculateRoutingScores(profile);
        
        // Determine optimal strategy
        RoutingStrategy strategy = determineOptimalStrategy(scores, profile);
        
        // Generate execution plan
        return generateExecutionPlan(strategy, profile);
    }
    
    private RoutingScores calculateRoutingScores(RequestProfile profile) {
        return RoutingScores.builder()
            .onPremScore(calculateOnPremScore(profile))
            .cloudScore(calculateCloudScore(profile))
            .hybridScore(calculateHybridScore(profile))
            .build();
    }
}
```

### 3. Saga Orchestrator Service
```java
@Service
public class SagaOrchestratorService {
    
    @Autowired
    private SagaStateManager sagaStateManager;
    
    @Autowired
    private EventPublisher eventPublisher;
    
    public String startSaga(IncomingRequest request, RoutingDecision decision) {
        String sagaId = UUID.randomUUID().toString();
        
        SagaContext context = SagaContext.builder()
            .sagaId(sagaId)
            .request(request)
            .routingDecision(decision)
            .status(SagaStatus.STARTED)
            .build();
        
        // Persist saga state
        sagaStateManager.createSaga(context);
        
        // Publish saga started event
        eventPublisher.publishSagaStartedEvent(context);
        
        // Start execution
        executeSagaSteps(context);
        
        return sagaId;
    }
    
    @Async
    public void executeSagaSteps(SagaContext context) {
        try {
            for (ExecutionStep step : context.getRoutingDecision().getExecutionSteps()) {
                executeStep(context, step);
            }
            completeSaga(context);
        } catch (Exception e) {
            compensateSaga(context, e);
        }
    }
}
```

### 4. Protocol Adapter Service
```java
@Service
public class ProtocolAdapterService {
    
    @Autowired
    private RestAdapter restAdapter;
    
    @Autowired
    private SoapAdapter soapAdapter;
    
    @Autowired
    private MqAdapter mqAdapter;
    
    public AdapterResponse adaptAndCall(ExecutionStep step, Object payload) {
        ProtocolAdapter adapter = getAdapter(step.getProtocol());
        return adapter.adaptAndCall(step, payload);
    }
    
    private ProtocolAdapter getAdapter(ProtocolType protocol) {
        return switch (protocol) {
            case REST -> restAdapter;
            case SOAP -> soapAdapter;
            case MQ -> mqAdapter;
            default -> throw new UnsupportedProtocolException(protocol);
        };
    }
}
```

### 5. Event-Driven Coordinator Service
```java
@Service
public class EventDrivenCoordinator {
    
    @Autowired
    private EventPublisher eventPublisher;
    
    @Autowired
    private EventSubscriber eventSubscriber;
    
    @EventListener
    public void handleSagaStepCompleted(SagaStepCompletedEvent event) {
        // Check if all dependencies are satisfied
        if (areDependenciesSatisfied(event.getSagaId(), event.getStepId())) {
            // Trigger next dependent steps
            triggerDependentSteps(event.getSagaId(), event.getStepId());
        }
    }
    
    @EventListener
    public void handleSagaStepFailed(SagaStepFailedEvent event) {
        // Initiate compensation
        initiateCompensation(event.getSagaId(), event.getStepId());
    }
}
```

## Configuration Classes

### Application Configuration
```java
@Configuration
@EnableAsync
@EnableScheduling
public class InteroperabilityConfig {
    
    @Bean
    public TaskExecutor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("interop-");
        executor.initialize();
        return executor;
    }
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
    
    @Bean
    public JmsTemplate jmsTemplate(ConnectionFactory connectionFactory) {
        return new JmsTemplate(connectionFactory);
    }
}
```

### Event Configuration
```java
@Configuration
@EnableJpaRepositories
public class EventConfig {
    
    @Bean
    public ApplicationEventPublisher applicationEventPublisher() {
        return new SimpleApplicationEventPublisher();
    }
    
    @Bean
    public EventStore eventStore() {
        return new JpaEventStore();
    }
}
```