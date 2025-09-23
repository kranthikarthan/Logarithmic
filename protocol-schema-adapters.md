# Protocol and Schema Adapters for Bank Interoperability

## Protocol Adapter Architecture

### 1. Base Protocol Adapter Interface
```java
public interface ProtocolAdapter {
    AdapterResponse adaptAndCall(ExecutionStep step, Object payload);
    boolean supports(ProtocolType protocol);
    String getAdapterName();
}

public class AdapterResponse {
    private String response;
    private boolean success;
    private String errorMessage;
    private long responseTime;
    private Map<String, String> metadata;
    
    // Constructors, getters, setters
}
```

### 2. REST API Adapter
```java
@Component
public class RestAdapter implements ProtocolAdapter {
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Override
    public AdapterResponse adaptAndCall(ExecutionStep step, Object payload) {
        try {
            long startTime = System.currentTimeMillis();
            
            // Convert payload to JSON
            String jsonPayload = objectMapper.writeValueAsString(payload);
            
            // Create HTTP request
            HttpHeaders headers = createHeaders(step);
            HttpEntity<String> entity = new HttpEntity<>(jsonPayload, headers);
            
            // Make REST call
            ResponseEntity<String> response = restTemplate.exchange(
                step.getTargetEndpoint(),
                HttpMethod.valueOf(step.getHttpMethod()),
                entity,
                String.class
            );
            
            long responseTime = System.currentTimeMillis() - startTime;
            
            return AdapterResponse.builder()
                .response(response.getBody())
                .success(response.getStatusCode().is2xxSuccessful())
                .responseTime(responseTime)
                .metadata(extractMetadata(response))
                .build();
                
        } catch (Exception e) {
            return AdapterResponse.builder()
                .success(false)
                .errorMessage(e.getMessage())
                .build();
        }
    }
    
    @Override
    public boolean supports(ProtocolType protocol) {
        return protocol == ProtocolType.REST;
    }
    
    private HttpHeaders createHeaders(ExecutionStep step) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Request-ID", step.getRequestId());
        headers.set("X-Saga-ID", step.getSagaId());
        return headers;
    }
}
```

### 3. SOAP API Adapter
```java
@Component
public class SoapAdapter implements ProtocolAdapter {
    
    @Autowired
    private SoapTemplate soapTemplate;
    
    @Autowired
    private XmlMapper xmlMapper;
    
    @Override
    public AdapterResponse adaptAndCall(ExecutionStep step, Object payload) {
        try {
            long startTime = System.currentTimeMillis();
            
            // Convert payload to SOAP XML
            String soapXml = createSoapEnvelope(payload, step);
            
            // Create SOAP request
            SoapMessage request = soapTemplate.createSoapMessage();
            request.setSoapAction(step.getSoapAction());
            request.setPayload(soapXml);
            
            // Make SOAP call
            SoapMessage response = soapTemplate.sendAndReceive(
                step.getTargetEndpoint(),
                request
            );
            
            long responseTime = System.currentTimeMillis() - startTime;
            
            return AdapterResponse.builder()
                .response(extractSoapBody(response))
                .success(isSoapSuccess(response))
                .responseTime(responseTime)
                .metadata(extractSoapMetadata(response))
                .build();
                
        } catch (Exception e) {
            return AdapterResponse.builder()
                .success(false)
                .errorMessage(e.getMessage())
                .build();
        }
    }
    
    @Override
    public boolean supports(ProtocolType protocol) {
        return protocol == ProtocolType.SOAP;
    }
    
    private String createSoapEnvelope(Object payload, ExecutionStep step) {
        return String.format(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">" +
            "<soap:Header>" +
            "<RequestID>%s</RequestID>" +
            "<SagaID>%s</SagaID>" +
            "</soap:Header>" +
            "<soap:Body>%s</soap:Body>" +
            "</soap:Envelope>",
            step.getRequestId(),
            step.getSagaId(),
            xmlMapper.writeValueAsString(payload)
        );
    }
}
```

### 4. Message Queue Adapter
```java
@Component
public class MqAdapter implements ProtocolAdapter {
    
    @Autowired
    private JmsTemplate jmsTemplate;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Override
    public AdapterResponse adaptAndCall(ExecutionStep step, Object payload) {
        try {
            long startTime = System.currentTimeMillis();
            
            // Convert payload to message
            String messagePayload = objectMapper.writeValueAsString(payload);
            
            // Create JMS message
            jmsTemplate.convertAndSend(
                step.getTargetEndpoint(),
                messagePayload,
                message -> {
                    message.setStringProperty("RequestID", step.getRequestId());
                    message.setStringProperty("SagaID", step.getSagaId());
                    message.setStringProperty("StepID", step.getStepId());
                    return message;
                }
            );
            
            long responseTime = System.currentTimeMillis() - startTime;
            
            return AdapterResponse.builder()
                .response("Message sent successfully")
                .success(true)
                .responseTime(responseTime)
                .metadata(Map.of("queue", step.getTargetEndpoint()))
                .build();
                
        } catch (Exception e) {
            return AdapterResponse.builder()
                .success(false)
                .errorMessage(e.getMessage())
                .build();
        }
    }
    
    @Override
    public boolean supports(ProtocolType protocol) {
        return protocol == ProtocolType.MQ;
    }
}
```

## Schema Adapters

### 1. JSON Schema Adapter
```java
@Component
public class JsonSchemaAdapter implements SchemaAdapter {
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Override
    public String adaptPayload(Object payload, SchemaType targetSchema) {
        try {
            switch (targetSchema) {
                case JSON:
                    return objectMapper.writeValueAsString(payload);
                case YAML:
                    return convertToYaml(payload);
                case XML:
                    return convertToXml(payload);
                default:
                    throw new UnsupportedSchemaException(targetSchema);
            }
        } catch (Exception e) {
            throw new SchemaAdaptationException("Failed to adapt payload", e);
        }
    }
    
    @Override
    public boolean supports(SchemaType schema) {
        return schema == SchemaType.JSON;
    }
    
    private String convertToYaml(Object payload) throws Exception {
        ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());
        return yamlMapper.writeValueAsString(payload);
    }
    
    private String convertToXml(Object payload) throws Exception {
        XmlMapper xmlMapper = new XmlMapper();
        return xmlMapper.writeValueAsString(payload);
    }
}
```

### 2. XML Schema Adapter
```java
@Component
public class XmlSchemaAdapter implements SchemaAdapter {
    
    @Autowired
    private XmlMapper xmlMapper;
    
    @Override
    public String adaptPayload(Object payload, SchemaType targetSchema) {
        try {
            switch (targetSchema) {
                case XML:
                    return xmlMapper.writeValueAsString(payload);
                case JSON:
                    return convertToJson(payload);
                case YAML:
                    return convertToYaml(payload);
                default:
                    throw new UnsupportedSchemaException(targetSchema);
            }
        } catch (Exception e) {
            throw new SchemaAdaptationException("Failed to adapt payload", e);
        }
    }
    
    @Override
    public boolean supports(SchemaType schema) {
        return schema == SchemaType.XML;
    }
    
    private String convertToJson(Object payload) throws Exception {
        ObjectMapper jsonMapper = new ObjectMapper();
        return jsonMapper.writeValueAsString(payload);
    }
    
    private String convertToYaml(Object payload) throws Exception {
        ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());
        return yamlMapper.writeValueAsString(payload);
    }
}
```

### 3. YAML Schema Adapter
```java
@Component
public class YamlSchemaAdapter implements SchemaAdapter {
    
    @Autowired
    private ObjectMapper yamlMapper;
    
    @Override
    public String adaptPayload(Object payload, SchemaType targetSchema) {
        try {
            switch (targetSchema) {
                case YAML:
                    return yamlMapper.writeValueAsString(payload);
                case JSON:
                    return convertToJson(payload);
                case XML:
                    return convertToXml(payload);
                default:
                    throw new UnsupportedSchemaException(targetSchema);
            }
        } catch (Exception e) {
            throw new SchemaAdaptationException("Failed to adapt payload", e);
        }
    }
    
    @Override
    public boolean supports(SchemaType schema) {
        return schema == SchemaType.YAML;
    }
    
    private String convertToJson(Object payload) throws Exception {
        ObjectMapper jsonMapper = new ObjectMapper();
        return jsonMapper.writeValueAsString(payload);
    }
    
    private String convertToXml(Object payload) throws Exception {
        XmlMapper xmlMapper = new XmlMapper();
        return xmlMapper.writeValueAsString(payload);
    }
}
```

## Protocol and Schema Adapter Factory

### 1. Adapter Factory
```java
@Service
public class AdapterFactory {
    
    @Autowired
    private List<ProtocolAdapter> protocolAdapters;
    
    @Autowired
    private List<SchemaAdapter> schemaAdapters;
    
    public ProtocolAdapter getProtocolAdapter(ProtocolType protocol) {
        return protocolAdapters.stream()
            .filter(adapter -> adapter.supports(protocol))
            .findFirst()
            .orElseThrow(() -> new UnsupportedProtocolException(protocol));
    }
    
    public SchemaAdapter getSchemaAdapter(SchemaType schema) {
        return schemaAdapters.stream()
            .filter(adapter -> adapter.supports(schema))
            .findFirst()
            .orElseThrow(() -> new UnsupportedSchemaException(schema));
    }
}
```

### 2. Unified Adapter Service
```java
@Service
public class UnifiedAdapterService {
    
    @Autowired
    private AdapterFactory adapterFactory;
    
    public AdapterResponse adaptAndCall(ExecutionStep step, Object payload) {
        // Get protocol adapter
        ProtocolAdapter protocolAdapter = adapterFactory.getProtocolAdapter(step.getProtocol());
        
        // Get schema adapter
        SchemaAdapter schemaAdapter = adapterFactory.getSchemaAdapter(step.getSchema());
        
        // Adapt payload to target schema
        String adaptedPayload = schemaAdapter.adaptPayload(payload, step.getSchema());
        
        // Create execution step with adapted payload
        ExecutionStep adaptedStep = step.toBuilder()
            .payload(adaptedPayload)
            .build();
        
        // Make the call using protocol adapter
        return protocolAdapter.adaptAndCall(adaptedStep, adaptedPayload);
    }
}
```

## Configuration Classes

### 1. Protocol Configuration
```java
@Configuration
public class ProtocolConfig {
    
    @Bean
    public RestTemplate restTemplate() {
        RestTemplate template = new RestTemplate();
        
        // Add interceptors
        template.getInterceptors().add(new LoggingInterceptor());
        template.getInterceptors().add(new RetryInterceptor());
        
        return template;
    }
    
    @Bean
    public SoapTemplate soapTemplate() {
        return new SoapTemplate();
    }
    
    @Bean
    public JmsTemplate jmsTemplate(ConnectionFactory connectionFactory) {
        JmsTemplate template = new JmsTemplate(connectionFactory);
        template.setDefaultDestinationName("interoperability.queue");
        return template;
    }
}
```

### 2. Schema Configuration
```java
@Configuration
public class SchemaConfig {
    
    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        mapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
        return mapper;
    }
    
    @Bean
    public XmlMapper xmlMapper() {
        XmlMapper mapper = new XmlMapper();
        mapper.configure(ToXmlGenerator.Feature.WRITE_XML_DECLARATION, true);
        return mapper;
    }
    
    @Bean
    public ObjectMapper yamlMapper() {
        return new ObjectMapper(new YAMLFactory());
    }
}
```

## Error Handling and Retry Logic

### 1. Retry Interceptor
```java
@Component
public class RetryInterceptor implements ClientHttpRequestInterceptor {
    
    private static final int MAX_RETRIES = 3;
    private static final long RETRY_DELAY = 1000; // 1 second
    
    @Override
    public ClientHttpResponse intercept(
            HttpRequest request, 
            byte[] body, 
            ClientHttpRequestExecution execution) throws IOException {
        
        int retryCount = 0;
        IOException lastException = null;
        
        while (retryCount <= MAX_RETRIES) {
            try {
                return execution.execute(request, body);
            } catch (IOException e) {
                lastException = e;
                retryCount++;
                
                if (retryCount <= MAX_RETRIES) {
                    try {
                        Thread.sleep(RETRY_DELAY * retryCount);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new IOException("Retry interrupted", ie);
                    }
                }
            }
        }
        
        throw lastException;
    }
}
```

### 2. Circuit Breaker
```java
@Component
public class CircuitBreaker {
    
    private final Map<String, CircuitState> circuitStates = new ConcurrentHashMap<>();
    private final int failureThreshold = 5;
    private final long timeout = 60000; // 1 minute
    
    public boolean isCircuitOpen(String serviceName) {
        CircuitState state = circuitStates.get(serviceName);
        
        if (state == null) {
            return false;
        }
        
        if (state.getState() == CircuitState.State.OPEN) {
            if (System.currentTimeMillis() - state.getLastFailureTime() > timeout) {
                state.setState(CircuitState.State.HALF_OPEN);
                return false;
            }
            return true;
        }
        
        return false;
    }
    
    public void recordSuccess(String serviceName) {
        CircuitState state = circuitStates.get(serviceName);
        if (state != null) {
            state.setState(CircuitState.State.CLOSED);
            state.setFailureCount(0);
        }
    }
    
    public void recordFailure(String serviceName) {
        CircuitState state = circuitStates.computeIfAbsent(serviceName, k -> new CircuitState());
        state.incrementFailureCount();
        state.setLastFailureTime(System.currentTimeMillis());
        
        if (state.getFailureCount() >= failureThreshold) {
            state.setState(CircuitState.State.OPEN);
        }
    }
}
```