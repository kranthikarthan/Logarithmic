# Event-Driven Architecture for Bank Interoperability

## Event-Driven Components

### 1. Event Definitions
```java
// Base Event Class
public abstract class InteroperabilityEvent {
    private String eventId;
    private String sagaId;
    private LocalDateTime timestamp;
    private String eventType;
    
    public InteroperabilityEvent(String sagaId, String eventType) {
        this.eventId = UUID.randomUUID().toString();
        this.sagaId = sagaId;
        this.timestamp = LocalDateTime.now();
        this.eventType = eventType;
    }
}

// Saga Events
public class SagaStartedEvent extends InteroperabilityEvent {
    private IncomingRequest request;
    private RoutingDecision routingDecision;
    
    public SagaStartedEvent(String sagaId, IncomingRequest request, RoutingDecision routingDecision) {
        super(sagaId, "SAGA_STARTED");
        this.request = request;
        this.routingDecision = routingDecision;
    }
}

public class SagaStepCompletedEvent extends InteroperabilityEvent {
    private String stepId;
    private String response;
    
    public SagaStepCompletedEvent(String sagaId, String stepId, String response) {
        super(sagaId, "SAGA_STEP_COMPLETED");
        this.stepId = stepId;
        this.response = response;
    }
}

public class SagaStepFailedEvent extends InteroperabilityEvent {
    private String stepId;
    private String errorMessage;
    private Exception exception;
    
    public SagaStepFailedEvent(String sagaId, String stepId, String errorMessage, Exception exception) {
        super(sagaId, "SAGA_STEP_FAILED");
        this.stepId = stepId;
        this.errorMessage = errorMessage;
        this.exception = exception;
    }
}

public class SagaCompletedEvent extends InteroperabilityEvent {
    private String finalResponse;
    
    public SagaCompletedEvent(String sagaId, String finalResponse) {
        super(sagaId, "SAGA_COMPLETED");
        this.finalResponse = finalResponse;
    }
}

public class SagaCompensatedEvent extends InteroperabilityEvent {
    private String compensationReason;
    
    public SagaCompensatedEvent(String sagaId, String compensationReason) {
        super(sagaId, "SAGA_COMPENSATED");
        this.compensationReason = compensationReason;
    }
}

// Routing Events
public class RoutingDecisionEvent extends InteroperabilityEvent {
    private RoutingDecision routingDecision;
    private RequestProfile requestProfile;
    
    public RoutingDecisionEvent(String sagaId, RoutingDecision routingDecision, RequestProfile requestProfile) {
        super(sagaId, "ROUTING_DECISION");
        this.routingDecision = routingDecision;
        this.requestProfile = requestProfile;
    }
}

// Load Balancing Events
public class LoadBalancingEvent extends InteroperabilityEvent {
    private String serviceName;
    private String environment;
    private double loadScore;
    
    public LoadBalancingEvent(String sagaId, String serviceName, String environment, double loadScore) {
        super(sagaId, "LOAD_BALANCING");
        this.serviceName = serviceName;
        this.environment = environment;
        this.loadScore = loadScore;
    }
}
```

### 2. Event Publisher Service
```java
@Service
public class EventPublisherService {
    
    @Autowired
    private ApplicationEventPublisher applicationEventPublisher;
    
    @Autowired
    private JmsTemplate jmsTemplate;
    
    @Autowired
    private EventStore eventStore;
    
    public void publishSagaStartedEvent(SagaContext context) {
        SagaStartedEvent event = new SagaStartedEvent(
            context.getSagaId(), 
            context.getOriginalRequest(), 
            context.getRoutingDecision());
        
        publishEvent(event);
    }
    
    public void publishSagaStepCompletedEvent(String sagaId, String stepId, String response) {
        SagaStepCompletedEvent event = new SagaStepCompletedEvent(sagaId, stepId, response);
        publishEvent(event);
    }
    
    public void publishSagaStepFailedEvent(String sagaId, String stepId, String errorMessage, Exception exception) {
        SagaStepFailedEvent event = new SagaStepFailedEvent(sagaId, stepId, errorMessage, exception);
        publishEvent(event);
    }
    
    public void publishRoutingDecisionEvent(String sagaId, RoutingDecision decision, RequestProfile profile) {
        RoutingDecisionEvent event = new RoutingDecisionEvent(sagaId, decision, profile);
        publishEvent(event);
    }
    
    private void publishEvent(InteroperabilityEvent event) {
        // Store event for audit
        eventStore.storeEvent(event);
        
        // Publish to local event bus
        applicationEventPublisher.publishEvent(event);
        
        // Publish to message queue for external systems
        jmsTemplate.convertAndSend("interoperability.events", event);
    }
}
```

### 3. Event Subscriber Service
```java
@Service
public class EventSubscriberService {
    
    @Autowired
    private SagaOrchestratorService sagaOrchestratorService;
    
    @Autowired
    private DependencyResolverService dependencyResolverService;
    
    @Autowired
    private LoadBalancerService loadBalancerService;
    
    @EventListener
    public void handleSagaStepCompleted(SagaStepCompletedEvent event) {
        log.info("Saga step completed: {}", event.getStepId());
        
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
        log.error("Saga step failed: {}", event.getStepId());
        
        // Initiate compensation
        SagaContext context = sagaOrchestratorService.getSagaContext(event.getSagaId());
        sagaOrchestratorService.compensateSaga(context, event.getException());
    }
    
    @EventListener
    public void handleRoutingDecisionEvent(RoutingDecisionEvent event) {
        log.info("Routing decision made for saga: {}", event.getSagaId());
        
        // Update load balancer with routing decision
        loadBalancerService.updateLoadMetrics(event.getRoutingDecision());
    }
    
    @EventListener
    public void handleLoadBalancingEvent(LoadBalancingEvent event) {
        log.info("Load balancing event: {} - {}: {}", 
            event.getServiceName(), event.getEnvironment(), event.getLoadScore());
        
        // Update load balancer metrics
        loadBalancerService.updateServiceLoad(
            event.getServiceName(), 
            event.getEnvironment(), 
            event.getLoadScore());
    }
}
```

### 4. Message Queue Configuration
```java
@Configuration
@EnableJms
public class JmsConfig {
    
    @Bean
    public ConnectionFactory connectionFactory() {
        ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory();
        factory.setBrokerURL("tcp://localhost:61616");
        return factory;
    }
    
    @Bean
    public JmsTemplate jmsTemplate(ConnectionFactory connectionFactory) {
        JmsTemplate template = new JmsTemplate(connectionFactory);
        template.setDefaultDestinationName("interoperability.events");
        return template;
    }
    
    @Bean
    public Queue interoperabilityEventsQueue() {
        return new ActiveMQQueue("interoperability.events");
    }
    
    @Bean
    public Queue sagaEventsQueue() {
        return new ActiveMQQueue("saga.events");
    }
    
    @Bean
    public Queue routingEventsQueue() {
        return new ActiveMQQueue("routing.events");
    }
}
```

### 5. Event Store Implementation
```java
@Entity
@Table(name = "event_store")
public class EventStore {
    
    @Id
    private String eventId;
    
    private String sagaId;
    private String eventType;
    private String eventData;
    private LocalDateTime timestamp;
    private String eventVersion;
    
    // Getters and setters
}

@Repository
public interface EventStoreRepository extends JpaRepository<EventStore, String> {
    
    List<EventStore> findBySagaIdOrderByTimestamp(String sagaId);
    
    List<EventStore> findByEventTypeAndTimestampBetween(
        String eventType, LocalDateTime start, LocalDateTime end);
    
    @Query("SELECT e FROM EventStore e WHERE e.sagaId = :sagaId AND e.eventType = :eventType")
    List<EventStore> findBySagaIdAndEventType(@Param("sagaId") String sagaId, @Param("eventType") String eventType);
}

@Service
public class EventStoreService {
    
    @Autowired
    private EventStoreRepository eventStoreRepository;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    public void storeEvent(InteroperabilityEvent event) {
        try {
            EventStore eventStore = EventStore.builder()
                .eventId(event.getEventId())
                .sagaId(event.getSagaId())
                .eventType(event.getEventType())
                .eventData(objectMapper.writeValueAsString(event))
                .timestamp(event.getTimestamp())
                .eventVersion("1.0")
                .build();
            
            eventStoreRepository.save(eventStore);
        } catch (Exception e) {
            log.error("Failed to store event: {}", event.getEventId(), e);
        }
    }
    
    public List<InteroperabilityEvent> getEventsBySagaId(String sagaId) {
        List<EventStore> events = eventStoreRepository.findBySagaIdOrderByTimestamp(sagaId);
        
        return events.stream()
            .map(this::deserializeEvent)
            .collect(Collectors.toList());
    }
    
    private InteroperabilityEvent deserializeEvent(EventStore eventStore) {
        try {
            return objectMapper.readValue(eventStore.getEventData(), InteroperabilityEvent.class);
        } catch (Exception e) {
            log.error("Failed to deserialize event: {}", eventStore.getEventId(), e);
            return null;
        }
    }
}
```

### 6. Event-Driven Coordination
```java
@Service
public class EventDrivenCoordinator {
    
    @Autowired
    private SagaOrchestratorService sagaOrchestratorService;
    
    @Autowired
    private DependencyResolverService dependencyResolverService;
    
    @Autowired
    private LoadBalancerService loadBalancerService;
    
    @EventListener
    public void handleSagaStepCompleted(SagaStepCompletedEvent event) {
        // Check if all dependencies are satisfied for next steps
        SagaContext context = sagaOrchestratorService.getSagaContext(event.getSagaId());
        
        List<SagaStep> nextSteps = dependencyResolverService.getNextExecutableSteps(context);
        
        if (!nextSteps.isEmpty()) {
            // Execute next steps
            for (SagaStep step : nextSteps) {
                sagaOrchestratorService.executeStepAsync(context, step);
            }
        }
    }
    
    @EventListener
    public void handleLoadBalancingEvent(LoadBalancingEvent event) {
        // Update load balancer with new metrics
        loadBalancerService.updateServiceLoad(
            event.getServiceName(), 
            event.getEnvironment(), 
            event.getLoadScore());
    }
    
    @EventListener
    public void handleRoutingDecisionEvent(RoutingDecisionEvent event) {
        // Log routing decision for audit
        log.info("Routing decision for saga {}: {}", 
            event.getSagaId(), event.getRoutingDecision());
        
        // Update load balancer with routing decision
        loadBalancerService.updateLoadMetrics(event.getRoutingDecision());
    }
}
```

## Event-Driven Benefits

1. **Loose Coupling**: Services communicate through events
2. **Scalability**: Easy to add new event handlers
3. **Resilience**: Event replay for recovery
4. **Audit Trail**: Complete event history
5. **Real-time Monitoring**: Event-driven metrics
6. **Flexibility**: Easy to modify event handling logic