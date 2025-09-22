# Payments Domain Sequence Diagram

## Payment Processing Flow

```
Client Application
    ↓ POST /api/v1/process (Payment Request)
API Gateway
    ↓ Route Request
Intelligent Router
    ↓ Analyze Request Profile
    ↓ Calculate Routing Scores  
    ↓ Determine Strategy (Hybrid)
    ↑ Routing Decision
API Gateway
    ↓ Start Saga
Saga Orchestrator
    ↓ Store Saga Context
    ↓ Publish Saga Started Event
    ↓ Execute Steps

Parallel Execution:
├── Protocol Adapter → On-Premise Services (Account Validation)
│   ├── REST API Call
│   ├── Account Valid Response
│   └── Step 1 Complete
└── Protocol Adapter → Cloud Services (Fraud Check)
    ├── REST API Call
    ├── Fraud Check Passed Response
    └── Step 1 Complete

Event Bus → Trigger Next Steps

Sequential Execution:
├── Protocol Adapter → On-Premise Services (Balance Check)
│   ├── SOAP API Call
│   ├── Sufficient Balance Response
│   └── Step 2 Complete
└── Protocol Adapter → Cloud Services (Payment Processing)
    ├── MQ Message
    ├── Payment Processed Response
    └── Step 2 Complete

Saga Orchestrator
    ↓ Update Saga Status
    ↓ Publish Saga Completed Event
    ↑ Saga Complete
API Gateway
    ↑ Payment Response
Client Application
```

## Detailed Sequence Flow

### 1. Request Arrival and Routing
```
1. Client sends payment request to API Gateway
2. Gateway forwards to Intelligent Router
3. Router analyzes request characteristics:
   - Payment amount
   - Customer data sensitivity
   - Regulatory requirements
   - Current system load
4. Router determines hybrid strategy:
   - On-premise: Account validation, balance check
   - Cloud: Fraud detection, payment processing
5. Router returns routing decision to Gateway
```

### 2. Saga Orchestration
```
1. Gateway starts saga with routing decision
2. Saga Orchestrator creates saga context
3. Saga Orchestrator stores context in Event Store
4. Saga Orchestrator publishes Saga Started Event
5. Saga Orchestrator begins step execution
```

### 3. Parallel Step Execution
```
Step 1A: On-Premise Account Validation
├── Saga Orchestrator → Protocol Adapter
├── Protocol Adapter → On-Premise REST API
├── On-Premise Service validates account
├── Response: Account Valid
└── Event: Step 1A Completed

Step 1B: Cloud Fraud Check
├── Saga Orchestrator → Protocol Adapter  
├── Protocol Adapter → Cloud REST API
├── Cloud Service checks for fraud
├── Response: Fraud Check Passed
└── Event: Step 1B Completed
```

### 4. Sequential Step Execution
```
Step 2A: On-Premise Balance Check
├── Event Bus triggers next step
├── Saga Orchestrator → Protocol Adapter
├── Protocol Adapter → On-Premise SOAP API
├── On-Premise Service checks balance
├── Response: Sufficient Balance
└── Event: Step 2A Completed

Step 2B: Cloud Payment Processing
├── Event Bus triggers next step
├── Saga Orchestrator → Protocol Adapter
├── Protocol Adapter → Cloud MQ Message
├── Cloud Service processes payment
├── Response: Payment Processed
└── Event: Step 2B Completed
```

### 5. Saga Completion
```
1. All steps completed successfully
2. Saga Orchestrator updates saga status
3. Saga Orchestrator publishes Saga Completed Event
4. Gateway returns payment response to client
```

## Error Handling and Compensation

### Failure Scenario
```
If any step fails:
1. Saga Orchestrator receives Step Failed Event
2. Saga Orchestrator initiates compensation
3. Compensation actions executed in reverse order:
   - Cloud Payment Processing → Rollback
   - On-Premise Balance Check → Release Hold
   - Cloud Fraud Check → Log Failure
   - On-Premise Account Validation → Log Failure
4. Saga Orchestrator publishes Saga Compensated Event
5. Gateway returns error response to client
```

## Event Flow Diagram

```
Saga Started Event
    ↓
Step 1A Completed Event
    ↓
Step 1B Completed Event
    ↓
Step 2A Completed Event
    ↓
Step 2B Completed Event
    ↓
Saga Completed Event
```

## Load Balancing Considerations

```
Request arrives at Gateway
    ↓
Intelligent Router analyzes:
├── On-Premise Load: 70% capacity
├── Cloud Load: 30% capacity
├── Request Complexity: Medium
├── Data Sensitivity: High
└── Decision: Hybrid (On-Premise + Cloud)
```

## Protocol and Schema Adaptations

```
Payment Request (JSON)
    ↓
Protocol Adapter converts to:
├── On-Premise: SOAP XML
├── Cloud: REST JSON
└── MQ: JMS Message

Responses converted back to:
└── Unified JSON Response
```