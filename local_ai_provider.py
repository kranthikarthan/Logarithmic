#!/usr/bin/env python3
"""
Local AI Provider for Enterprise On-Premise AI Integration
Supports local Copilot, internal LLMs, and custom AI services
"""

import requests
import json
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProviderType(Enum):
    """Supported AI provider types"""
    LOCAL_COPILOT = "local-copilot"
    INTERNAL_LLM = "internal-llm"
    CUSTOM_MODEL = "custom-model"
    OFFLINE_MODEL = "offline-model"

@dataclass
class LocalAIConfig:
    """Configuration for local AI provider"""
    base_url: str
    api_key: Optional[str] = None
    model_name: str = "local-copilot"
    timeout: int = 30
    max_retries: int = 3
    proxy_url: Optional[str] = None
    cert_path: Optional[str] = None
    verify_ssl: bool = True
    headers: Optional[Dict[str, str]] = None

@dataclass
class AIRequest:
    """Request structure for AI calls"""
    prompt: str
    model: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    context: Optional[Dict[str, Any]] = None

@dataclass
class AIResponse:
    """Response structure from AI calls"""
    content: str
    model: str
    tokens_used: Optional[int] = None
    response_time: float = 0.0
    success: bool = True
    error: Optional[str] = None

class LocalAIProvider:
    """Local AI Provider for enterprise environments"""
    
    def __init__(self, config: LocalAIConfig):
        self.config = config
        self.session = self._create_session()
        self.cache = {}
        self.audit_log = []
        
    def _create_session(self) -> requests.Session:
        """Create configured requests session"""
        session = requests.Session()
        
        # Configure timeout
        session.timeout = self.config.timeout
        
        # Configure proxy if provided
        if self.config.proxy_url:
            session.proxies = {
                'http': self.config.proxy_url,
                'https': self.config.proxy_url
            }
        
        # Configure SSL verification
        session.verify = self.config.verify_ssl
        if self.config.cert_path:
            session.cert = self.config.cert_path
        
        # Set default headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Assertly-Enterprise/1.0'
        }
        
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'
        
        if self.config.headers:
            headers.update(self.config.headers)
        
        session.headers.update(headers)
        
        return session
    
    def _log_ai_usage(self, request: AIRequest, response: AIResponse, user: str = "system"):
        """Log AI usage for audit and compliance"""
        log_entry = {
            'timestamp': time.time(),
            'user': user,
            'model': request.model,
            'prompt_hash': hashlib.sha256(request.prompt.encode()).hexdigest(),
            'response_length': len(response.content),
            'response_time': response.response_time,
            'success': response.success,
            'tokens_used': response.tokens_used
        }
        
        self.audit_log.append(log_entry)
        logger.info(f"AI usage logged: {log_entry}")
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        """Make HTTP request with retry logic"""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.post(url, json=data, timeout=self.config.timeout)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == self.config.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Max retries exceeded")
    
    def test_connection(self) -> bool:
        """Test connection to local AI service"""
        try:
            # Try to ping the health endpoint
            health_url = f"{self.config.base_url.rstrip('/')}/health"
            response = self.session.get(health_url, timeout=10)
            response.raise_for_status()
            
            logger.info("Local AI service connection successful")
            return True
            
        except Exception as e:
            logger.error(f"Local AI service connection failed: {e}")
            return False
    
    def generate_test_cases(self, user_story: str, context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Generate test cases from user story using local AI"""
        start_time = time.time()
        
        # Build prompt for test case generation
        prompt = self._build_test_generation_prompt(user_story, context)
        
        # Check cache first
        cache_key = hashlib.sha256(prompt.encode()).hexdigest()
        if cache_key in self.cache:
            logger.info("Using cached AI response")
            cached_response = self.cache[cache_key]
            cached_response.response_time = time.time() - start_time
            return cached_response
        
        try:
            # Prepare request
            request_data = {
                'prompt': prompt,
                'model': self.config.model_name,
                'max_tokens': 2000,
                'temperature': 0.7,
                'context': context or {}
            }
            
            # Make request to local AI service
            response = self._make_request('/generate', request_data)
            result = response.json()
            
            # Parse response
            ai_response = AIResponse(
                content=result.get('content', ''),
                model=self.config.model_name,
                tokens_used=result.get('tokens_used'),
                response_time=time.time() - start_time,
                success=True
            )
            
            # Cache the response
            self.cache[cache_key] = ai_response
            
            # Log usage
            request = AIRequest(prompt=prompt, model=self.config.model_name)
            self._log_ai_usage(request, ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Failed to generate test cases: {e}")
            return AIResponse(
                content="",
                model=self.config.model_name,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def improve_test_case(self, test_case: str, suggestions: Optional[str] = None) -> AIResponse:
        """Improve existing test case using local AI"""
        start_time = time.time()
        
        # Build prompt for test case improvement
        prompt = self._build_improvement_prompt(test_case, suggestions)
        
        try:
            request_data = {
                'prompt': prompt,
                'model': self.config.model_name,
                'max_tokens': 1500,
                'temperature': 0.5
            }
            
            response = self._make_request('/improve', request_data)
            result = response.json()
            
            ai_response = AIResponse(
                content=result.get('content', ''),
                model=self.config.model_name,
                tokens_used=result.get('tokens_used'),
                response_time=time.time() - start_time,
                success=True
            )
            
            # Log usage
            request = AIRequest(prompt=prompt, model=self.config.model_name)
            self._log_ai_usage(request, ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Failed to improve test case: {e}")
            return AIResponse(
                content="",
                model=self.config.model_name,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def generate_bdd_scenarios(self, user_story: str, context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Generate BDD scenarios from user story using local AI"""
        start_time = time.time()
        
        prompt = self._build_bdd_generation_prompt(user_story, context)
        
        try:
            request_data = {
                'prompt': prompt,
                'model': self.config.model_name,
                'max_tokens': 1500,
                'temperature': 0.6
            }
            
            response = self._make_request('/bdd-generate', request_data)
            result = response.json()
            
            ai_response = AIResponse(
                content=result.get('content', ''),
                model=self.config.model_name,
                tokens_used=result.get('tokens_used'),
                response_time=time.time() - start_time,
                success=True
            )
            
            # Log usage
            request = AIRequest(prompt=prompt, model=self.config.model_name)
            self._log_ai_usage(request, ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Failed to generate BDD scenarios: {e}")
            return AIResponse(
                content="",
                model=self.config.model_name,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def generate_test_data(self, test_case: str, data_types: List[str] = None) -> AIResponse:
        """Generate test data for test case using local AI"""
        start_time = time.time()
        
        if data_types is None:
            data_types = ['valid', 'invalid', 'boundary']
        
        prompt = self._build_test_data_prompt(test_case, data_types)
        
        try:
            request_data = {
                'prompt': prompt,
                'model': self.config.model_name,
                'max_tokens': 1000,
                'temperature': 0.8
            }
            
            response = self._make_request('/test-data', request_data)
            result = response.json()
            
            ai_response = AIResponse(
                content=result.get('content', ''),
                model=self.config.model_name,
                tokens_used=result.get('tokens_used'),
                response_time=time.time() - start_time,
                success=True
            )
            
            # Log usage
            request = AIRequest(prompt=prompt, model=self.config.model_name)
            self._log_ai_usage(request, ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Failed to generate test data: {e}")
            return AIResponse(
                content="",
                model=self.config.model_name,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def analyze_coverage(self, user_story: str, existing_tests: List[str]) -> AIResponse:
        """Analyze test coverage using local AI"""
        start_time = time.time()
        
        prompt = self._build_coverage_analysis_prompt(user_story, existing_tests)
        
        try:
            request_data = {
                'prompt': prompt,
                'model': self.config.model_name,
                'max_tokens': 1200,
                'temperature': 0.5
            }
            
            response = self._make_request('/analyze-coverage', request_data)
            result = response.json()
            
            ai_response = AIResponse(
                content=result.get('content', ''),
                model=self.config.model_name,
                tokens_used=result.get('tokens_used'),
                response_time=time.time() - start_time,
                success=True
            )
            
            # Log usage
            request = AIRequest(prompt=prompt, model=self.config.model_name)
            self._log_ai_usage(request, ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Failed to analyze coverage: {e}")
            return AIResponse(
                content="",
                model=self.config.model_name,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def _build_test_generation_prompt(self, user_story: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for test case generation"""
        prompt = f"""
Generate comprehensive test cases for the following user story:

User Story: {user_story}

Context: {context or 'No additional context provided'}

Please generate test cases that include:
1. Happy path scenarios
2. Edge cases
3. Error conditions
4. Boundary value testing
5. Negative test cases

Format the output as structured test cases with:
- Test Case Title
- Test Steps
- Expected Results
- Test Data Requirements
- Priority Level

Ensure the test cases are comprehensive and cover all aspects of the user story.
"""
        return prompt.strip()
    
    def _build_improvement_prompt(self, test_case: str, suggestions: Optional[str] = None) -> str:
        """Build prompt for test case improvement"""
        prompt = f"""
Improve the following test case to make it more comprehensive and effective:

Current Test Case:
{test_case}

Improvement Suggestions: {suggestions or 'No specific suggestions provided'}

Please provide an improved version that includes:
1. More detailed test steps
2. Better test data coverage
3. Additional edge cases
4. Clearer expected results
5. Better test organization

Format the improved test case with clear structure and comprehensive coverage.
"""
        return prompt.strip()
    
    def _build_bdd_generation_prompt(self, user_story: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for BDD scenario generation"""
        prompt = f"""
Generate BDD scenarios in Gherkin format for the following user story:

User Story: {user_story}

Context: {context or 'No additional context provided'}

Please generate scenarios that include:
1. Happy path scenarios
2. Alternative flows
3. Error scenarios
4. Edge cases

Format the output as proper Gherkin scenarios with:
- Feature description
- Background (if applicable)
- Scenario outlines
- Given-When-Then steps
- Examples tables

Ensure the scenarios are comprehensive and follow BDD best practices.
"""
        return prompt.strip()
    
    def _build_test_data_prompt(self, test_case: str, data_types: List[str]) -> str:
        """Build prompt for test data generation"""
        prompt = f"""
Generate test data for the following test case:

Test Case: {test_case}

Required Data Types: {', '.join(data_types)}

Please generate test data that includes:
1. Valid data sets
2. Invalid data sets
3. Boundary value data
4. Edge case data
5. Realistic test data

Format the output as structured test data with:
- Data set name
- Data values
- Expected behavior
- Notes/description

Ensure the test data is comprehensive and covers all testing scenarios.
"""
        return prompt.strip()
    
    def _build_coverage_analysis_prompt(self, user_story: str, existing_tests: List[str]) -> str:
        """Build prompt for coverage analysis"""
        prompt = f"""
Analyze test coverage for the following user story and existing tests:

User Story: {user_story}

Existing Tests:
{chr(10).join(f"- {test}" for test in existing_tests)}

Please provide analysis that includes:
1. Coverage gaps identified
2. Missing test scenarios
3. Additional test cases needed
4. Coverage percentage estimate
5. Recommendations for improvement

Format the analysis with clear sections and actionable recommendations.
"""
        return prompt.strip()
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log for compliance"""
        return self.audit_log.copy()
    
    def clear_cache(self):
        """Clear AI response cache"""
        self.cache.clear()
        logger.info("AI response cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache),
            'total_requests': len(self.audit_log),
            'successful_requests': sum(1 for log in self.audit_log if log.get('success', False)),
            'failed_requests': sum(1 for log in self.audit_log if not log.get('success', True))
        }