package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"
)

// SagaStep represents a single step in a saga
type SagaStep struct {
	ID              string                 `json:"id"`
	Name            string                 `json:"name"`
	Service         string                 `json:"service"`
	Protocol        string                 `json:"protocol"`
	Schema          string                 `json:"schema"`
	Endpoint        string                 `json:"endpoint"`
	Payload         map[string]interface{} `json:"payload"`
	Compensation    *CompensationStep      `json:"compensation,omitempty"`
	DependsOn       []string               `json:"depends_on,omitempty"`
	Timeout         time.Duration          `json:"timeout"`
	RetryPolicy     RetryPolicy            `json:"retry_policy"`
	IsOnPrem        bool                   `json:"is_onprem"`
	IsCloud         bool                   `json:"is_cloud"`
}

// CompensationStep represents the compensation action for a saga step
type CompensationStep struct {
	ID       string                 `json:"id"`
	Service  string                 `json:"service"`
	Endpoint string                 `json:"endpoint"`
	Payload  map[string]interface{} `json:"payload"`
	Timeout  time.Duration          `json:"timeout"`
}

// RetryPolicy defines retry behavior for saga steps
type RetryPolicy struct {
	MaxRetries int           `json:"max_retries"`
	Backoff    time.Duration `json:"backoff"`
	MaxBackoff time.Duration `json:"max_backoff"`
}

// SagaState represents the current state of a saga execution
type SagaState struct {
	ID            string                 `json:"id"`
	Status        SagaStatus             `json:"status"`
	Steps         map[string]*StepState  `json:"steps"`
	StartTime     time.Time              `json:"start_time"`
	EndTime       *time.Time             `json:"end_time,omitempty"`
	Error         *SagaError             `json:"error,omitempty"`
	Context       map[string]interface{} `json:"context"`
}

// StepState represents the state of an individual saga step
type StepState struct {
	StepID      string                 `json:"step_id"`
	Status      StepStatus             `json:"status"`
	StartTime   time.Time              `json:"start_time"`
	EndTime     *time.Time             `json:"end_time,omitempty"`
	Result      map[string]interface{} `json:"result,omitempty"`
	Error       *StepError             `json:"error,omitempty"`
	RetryCount  int                    `json:"retry_count"`
	Compensated bool                   `json:"compensated"`
}

// SagaStatus represents the overall status of a saga
type SagaStatus string

const (
	SagaStatusPending    SagaStatus = "pending"
	SagaStatusRunning    SagaStatus = "running"
	SagaStatusCompleted  SagaStatus = "completed"
	SagaStatusFailed     SagaStatus = "failed"
	SagaStatusCompensated SagaStatus = "compensated"
)

// StepStatus represents the status of an individual step
type StepStatus string

const (
	StepStatusPending    StepStatus = "pending"
	StepStatusRunning    StepStatus = "running"
	StepStatusCompleted  StepStatus = "completed"
	StepStatusFailed     StepStatus = "failed"
	StepStatusCompensated StepStatus = "compensated"
)

// SagaError represents an error in saga execution
type SagaError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	StepID  string `json:"step_id,omitempty"`
}

// StepError represents an error in step execution
type StepError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
}

// SagaOrchestrator manages saga execution
type SagaOrchestrator struct {
	stateStore         StateStore
	eventBus           EventBus
	protocolAdapters   ProtocolAdapterRegistry
	compensationEngine CompensationEngine
}

// NewSagaOrchestrator creates a new saga orchestrator
func NewSagaOrchestrator(stateStore StateStore, eventBus EventBus, adapters ProtocolAdapterRegistry) *SagaOrchestrator {
	return &SagaOrchestrator{
		stateStore:         stateStore,
		eventBus:           eventBus,
		protocolAdapters:   adapters,
		compensationEngine: NewCompensationEngine(),
	}
}

// ExecuteSaga executes a saga with the given steps
func (so *SagaOrchestrator) ExecuteSaga(ctx context.Context, sagaID string, steps []SagaStep) error {
	// Create initial saga state
	sagaState := &SagaState{
		ID:        sagaID,
		Status:    SagaStatusPending,
		Steps:     make(map[string]*StepState),
		StartTime: time.Now(),
		Context:   make(map[string]interface{}),
	}

	// Initialize step states
	for _, step := range steps {
		sagaState.Steps[step.ID] = &StepState{
			StepID:    step.ID,
			Status:    StepStatusPending,
			StartTime: time.Now(),
		}
	}

	// Save initial state
	if err := so.stateStore.SaveSagaState(sagaState); err != nil {
		return fmt.Errorf("failed to save initial saga state: %w", err)
	}

	// Publish saga started event
	so.eventBus.PublishEvent("saga.started", map[string]interface{}{
		"saga_id": sagaID,
		"steps":   len(steps),
	})

	// Update status to running
	sagaState.Status = SagaStatusRunning
	so.stateStore.SaveSagaState(sagaState)

	// Execute steps based on dependency graph
	executionPlan := so.buildExecutionPlan(steps)
	
	for _, stepGroup := range executionPlan {
		// Execute steps in parallel within the group
		stepResults := make(chan StepResult, len(stepGroup))
		
		for _, step := range stepGroup {
			go func(s SagaStep) {
				result := so.executeStep(ctx, sagaState, s)
				stepResults <- result
			}(step)
		}

		// Wait for all steps in the group to complete
		for i := 0; i < len(stepGroup); i++ {
			result := <-stepResults
			if result.Error != nil {
				// Handle step failure
				sagaState.Status = SagaStatusFailed
				sagaState.Error = &SagaError{
					Code:    "STEP_FAILED",
					Message: result.Error.Error(),
					StepID:  result.StepID,
				}
				so.stateStore.SaveSagaState(sagaState)
				
				// Trigger compensation
				go so.executeCompensation(ctx, sagaState)
				return result.Error
			}
		}
	}

	// All steps completed successfully
	sagaState.Status = SagaStatusCompleted
	now := time.Now()
	sagaState.EndTime = &now
	so.stateStore.SaveSagaState(sagaState)

	// Publish saga completed event
	so.eventBus.PublishEvent("saga.completed", map[string]interface{}{
		"saga_id": sagaID,
		"duration": time.Since(sagaState.StartTime),
	})

	return nil
}

// StepResult represents the result of executing a saga step
type StepResult struct {
	StepID string
	Error  error
}

// executeStep executes a single saga step
func (so *SagaOrchestrator) executeStep(ctx context.Context, sagaState *SagaState, step SagaStep) StepResult {
	stepState := sagaState.Steps[step.ID]
	stepState.Status = StepStatusRunning
	stepState.StartTime = time.Now()
	so.stateStore.SaveSagaState(sagaState)

	// Publish step started event
	so.eventBus.PublishEvent("saga.step.started", map[string]interface{}{
		"saga_id": sagaState.ID,
		"step_id": step.ID,
		"service": step.Service,
	})

	// Execute with retry logic
	var lastErr error
	for attempt := 0; attempt <= step.RetryPolicy.MaxRetries; attempt++ {
		if attempt > 0 {
			// Calculate backoff delay
			delay := time.Duration(attempt) * step.RetryPolicy.Backoff
			if delay > step.RetryPolicy.MaxBackoff {
				delay = step.RetryPolicy.MaxBackoff
			}
			time.Sleep(delay)
		}

		// Execute the step
		result, err := so.executeStepCall(ctx, step)
		if err == nil {
			// Step completed successfully
			stepState.Status = StepStatusCompleted
			stepState.Result = result
			now := time.Now()
			stepState.EndTime = &now
			stepState.RetryCount = attempt
			so.stateStore.SaveSagaState(sagaState)

			// Publish step completed event
			so.eventBus.PublishEvent("saga.step.completed", map[string]interface{}{
				"saga_id": sagaState.ID,
				"step_id": step.ID,
				"duration": time.Since(stepState.StartTime),
			})

			return StepResult{StepID: step.ID, Error: nil}
		}

		lastErr = err
		stepState.RetryCount = attempt
	}

	// Step failed after all retries
	stepState.Status = StepStatusFailed
	stepState.Error = &StepError{
		Code:    "EXECUTION_FAILED",
		Message: lastErr.Error(),
	}
	now := time.Now()
	stepState.EndTime = &now
	so.stateStore.SaveSagaState(sagaState)

	// Publish step failed event
	so.eventBus.PublishEvent("saga.step.failed", map[string]interface{}{
		"saga_id": sagaState.ID,
		"step_id": step.ID,
		"error":   lastErr.Error(),
		"retries": stepState.RetryCount,
	})

	return StepResult{StepID: step.ID, Error: lastErr}
}

// executeStepCall makes the actual service call for a step
func (so *SagaOrchestrator) executeStepCall(ctx context.Context, step SagaStep) (map[string]interface{}, error) {
	// Get protocol adapter
	adapter, err := so.protocolAdapters.GetAdapter(step.Protocol)
	if err != nil {
		return nil, fmt.Errorf("failed to get protocol adapter: %w", err)
	}

	// Create timeout context
	timeoutCtx, cancel := context.WithTimeout(ctx, step.Timeout)
	defer cancel()

	// Execute the call
	result, err := adapter.Call(timeoutCtx, step.Endpoint, step.Payload)
	if err != nil {
		return nil, fmt.Errorf("step call failed: %w", err)
	}

	return result, nil
}

// buildExecutionPlan creates an execution plan based on step dependencies
func (so *SagaOrchestrator) buildExecutionPlan(steps []SagaStep) [][]SagaStep {
	// Create dependency graph
	dependencyGraph := make(map[string][]string)
	stepMap := make(map[string]SagaStep)
	
	for _, step := range steps {
		stepMap[step.ID] = step
		dependencyGraph[step.ID] = step.DependsOn
	}

	// Topological sort to determine execution order
	var executionPlan [][]SagaStep
	visited := make(map[string]bool)
	tempVisited := make(map[string]bool)

	var visit func(string) error
	visit = func(stepID string) error {
		if tempVisited[stepID] {
			return fmt.Errorf("circular dependency detected: %s", stepID)
		}
		if visited[stepID] {
			return nil
		}

		tempVisited[stepID] = true
		step := stepMap[stepID]

		// Visit dependencies first
		for _, depID := range step.DependsOn {
			if err := visit(depID); err != nil {
				return err
			}
		}

		tempVisited[stepID] = false
		visited[stepID] = true

		// Add to execution plan
		// For simplicity, we'll add each step to its own group
		// In a real implementation, you'd group independent steps together
		executionPlan = append(executionPlan, []SagaStep{step})

		return nil
	}

	// Visit all steps
	for _, step := range steps {
		if !visited[step.ID] {
			if err := visit(step.ID); err != nil {
				log.Printf("Error building execution plan: %v", err)
				// Fallback: execute all steps in order
				executionPlan = [][]SagaStep{steps}
				break
			}
		}
	}

	return executionPlan
}

// executeCompensation executes compensation for failed saga
func (so *SagaOrchestrator) executeCompensation(ctx context.Context, sagaState *SagaState) {
	log.Printf("Starting compensation for saga %s", sagaState.ID)

	// Get completed steps in reverse order
	var completedSteps []*StepState
	for _, stepState := range sagaState.Steps {
		if stepState.Status == StepStatusCompleted && !stepState.Compensated {
			completedSteps = append(completedSteps, stepState)
		}
	}

	// Sort by end time (most recent first)
	for i := 0; i < len(completedSteps)-1; i++ {
		for j := i + 1; j < len(completedSteps); j++ {
			if completedSteps[i].EndTime.Before(*completedSteps[j].EndTime) {
				completedSteps[i], completedSteps[j] = completedSteps[j], completedSteps[i]
			}
		}
	}

	// Execute compensation for each step
	for _, stepState := range completedSteps {
		// Find the original step definition
		var step SagaStep
		for _, s := range sagaState.Steps {
			if s.StepID == stepState.StepID {
				// We need to get the original step definition
				// This would typically be stored in the saga state
				break
			}
		}

		if step.Compensation != nil {
			// Execute compensation
			err := so.compensationEngine.ExecuteCompensation(ctx, *step.Compensation)
			if err != nil {
				log.Printf("Compensation failed for step %s: %v", stepState.StepID, err)
			} else {
				stepState.Compensated = true
				so.stateStore.SaveSagaState(sagaState)
			}
		}
	}

	sagaState.Status = SagaStatusCompensated
	so.stateStore.SaveSagaState(sagaState)

	// Publish compensation completed event
	so.eventBus.PublishEvent("saga.compensated", map[string]interface{}{
		"saga_id": sagaState.ID,
		"steps_compensated": len(completedSteps),
	})
}

// StateStore interface for persisting saga state
type StateStore interface {
	SaveSagaState(state *SagaState) error
	GetSagaState(sagaID string) (*SagaState, error)
}

// EventBus interface for publishing events
type EventBus interface {
	PublishEvent(eventType string, data map[string]interface{}) error
}

// ProtocolAdapterRegistry interface for protocol adapters
type ProtocolAdapterRegistry interface {
	GetAdapter(protocol string) (ProtocolAdapter, error)
}

// ProtocolAdapter interface for making service calls
type ProtocolAdapter interface {
	Call(ctx context.Context, endpoint string, payload map[string]interface{}) (map[string]interface{}, error)
}

// CompensationEngine handles compensation execution
type CompensationEngine struct{}

func NewCompensationEngine() CompensationEngine {
	return CompensationEngine{}
}

func (ce *CompensationEngine) ExecuteCompensation(ctx context.Context, step CompensationStep) error {
	// Implementation would depend on the specific compensation logic
	log.Printf("Executing compensation for step %s", step.ID)
	return nil
}

// Example usage
func main() {
	// This would be implemented with actual dependencies
	// stateStore := NewRedisStateStore()
	// eventBus := NewKafkaEventBus()
	// adapters := NewProtocolAdapterRegistry()

	// orchestrator := NewSagaOrchestrator(stateStore, eventBus, adapters)

	// Example saga steps
	steps := []SagaStep{
		{
			ID:       "step1",
			Name:     "Validate Customer",
			Service:  "customer-service",
			Protocol: "REST",
			Schema:   "JSON",
			Endpoint: "https://customer-service/api/validate",
			Payload: map[string]interface{}{
				"customer_id": "12345",
			},
			Timeout: 30 * time.Second,
			RetryPolicy: RetryPolicy{
				MaxRetries: 3,
				Backoff:    1 * time.Second,
				MaxBackoff: 10 * time.Second,
			},
			IsOnPrem: true,
		},
		{
			ID:       "step2",
			Name:     "Process Payment",
			Service:  "payment-service",
			Protocol: "SOAP",
			Schema:   "XML",
			Endpoint: "https://payment-service/soap/process",
			Payload: map[string]interface{}{
				"amount": 100.00,
				"currency": "USD",
			},
			DependsOn: []string{"step1"},
			Timeout:   60 * time.Second,
			RetryPolicy: RetryPolicy{
				MaxRetries: 5,
				Backoff:    2 * time.Second,
				MaxBackoff: 30 * time.Second,
			},
			IsCloud: true,
			Compensation: &CompensationStep{
				ID:       "compensate_payment",
				Service:  "payment-service",
				Endpoint: "https://payment-service/soap/refund",
				Payload: map[string]interface{}{
					"transaction_id": "{{step2.result.transaction_id}}",
				},
				Timeout: 30 * time.Second,
			},
		},
	}

	// Execute saga
	// ctx := context.Background()
	// err := orchestrator.ExecuteSaga(ctx, "saga-123", steps)
	// if err != nil {
	//     log.Fatalf("Saga execution failed: %v", err)
	// }

	fmt.Println("Saga pattern implementation completed")
}