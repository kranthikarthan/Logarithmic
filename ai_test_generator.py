#!/usr/bin/env python3
"""
AI Test Case Generator for Assertly
Generates test cases from user stories and requirements using AI
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available. Install with: pip install openai")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: Anthropic not available. Install with: pip install anthropic")

# Import enterprise/local AI providers
try:
    from local_ai_provider import LocalAIProvider, LocalAIConfig
    from enterprise_config import EnterpriseConfigManager
    ENTERPRISE_AVAILABLE = True
except ImportError:
    ENTERPRISE_AVAILABLE = False
    print("Warning: Enterprise AI not available. Local AI features disabled.")

class TestCaseType(Enum):
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    UI = "ui"
    API = "api"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"

class TestPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TestCase:
    title: str
    description: str
    steps: List[str]
    expected_result: str
    test_type: TestCaseType
    priority: TestPriority
    tags: List[str]
    preconditions: List[str]
    test_data: Dict[str, Any]
    acceptance_criteria: List[str]

@dataclass
class UserStory:
    title: str
    description: str
    acceptance_criteria: List[str]
    business_value: str
    user_persona: str
    epic: Optional[str] = None
    story_points: Optional[int] = None

class AITestGenerator:
    def __init__(self, api_key: str = None, provider: str = "openai", enterprise_mode: bool = False):
        """
        Initialize AI Test Generator with enterprise support
        
        Args:
            api_key: API key for AI service
            provider: AI provider ("openai", "anthropic", or "local")
            enterprise_mode: Enable enterprise/local AI mode
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.provider = provider.lower()
        self.enterprise_mode = enterprise_mode
        
        # Initialize enterprise config manager if in enterprise mode
        if enterprise_mode and ENTERPRISE_AVAILABLE:
            self.enterprise_config = EnterpriseConfigManager()
            self._load_enterprise_settings()
        else:
            self.enterprise_config = None
        
        # Initialize AI client based on provider
        if self.provider == "local" and ENTERPRISE_AVAILABLE:
            self._init_local_ai()
        elif self.provider == "openai" and OPENAI_AVAILABLE:
            self.client = openai.OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            self.client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Provider {provider} not available or API key not provided")
    
    def _load_enterprise_settings(self):
        """Load enterprise settings from configuration"""
        if not self.enterprise_config:
            return
        
        settings = self.enterprise_config.load_enterprise_settings()
        if settings:
            self.enterprise_settings = settings
        else:
            # Default enterprise settings
            self.enterprise_settings = None
    
    def _init_local_ai(self):
        """Initialize local AI provider"""
        if not self.enterprise_settings:
            raise ValueError("Enterprise settings not configured for local AI")
        
        # Create local AI configuration
        local_config = LocalAIConfig(
            base_url=self.enterprise_settings.local_ai_url,
            api_key=self.enterprise_settings.local_api_key,
            model_name=self.enterprise_settings.local_ai_model,
            proxy_url=self.enterprise_settings.proxy_url,
            cert_path=self.enterprise_settings.cert_path,
            verify_ssl=self.enterprise_settings.verify_ssl
        )
        
        # Initialize local AI provider
        self.local_ai = LocalAIProvider(local_config)
        
        # Test connection
        if not self.local_ai.test_connection():
            raise ValueError("Failed to connect to local AI service")

    def generate_test_cases_from_story(
        self, 
        user_story: UserStory, 
        test_types: List[TestCaseType] = None,
        num_cases: int = 5,
        additional_prompts: List[str] = None
    ) -> List[TestCase]:
        """
        Generate test cases from a user story
        
        Args:
            user_story: User story object
            test_types: Types of test cases to generate
            num_cases: Number of test cases to generate
            additional_prompts: Additional prompts for customization
            
        Returns:
            List of generated test cases
        """
        if test_types is None:
            test_types = [TestCaseType.FUNCTIONAL, TestCaseType.UI, TestCaseType.API]
        
        if additional_prompts is None:
            additional_prompts = []
        
        # Build the prompt
        prompt = self._build_test_generation_prompt(
            user_story, test_types, num_cases, additional_prompts
        )
        
        # Generate test cases
        response = self._call_ai_api(prompt)
        
        # Parse response into test cases
        test_cases = self._parse_test_cases_response(response, test_types)
        
        return test_cases

    def improve_test_case(
        self, 
        test_case: TestCase, 
        improvement_prompts: List[str]
    ) -> TestCase:
        """
        Improve an existing test case based on prompts
        
        Args:
            test_case: Original test case
            improvement_prompts: Prompts for improvement
            
        Returns:
            Improved test case
        """
        prompt = self._build_improvement_prompt(test_case, improvement_prompts)
        response = self._call_ai_api(prompt)
        
        # Parse improved test case
        improved_case = self._parse_single_test_case(response)
        return improved_case

    def generate_bdd_scenarios(
        self, 
        user_story: UserStory,
        additional_context: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generate BDD scenarios from user story
        
        Args:
            user_story: User story object
            additional_context: Additional context for scenarios
            
        Returns:
            List of BDD scenarios with Given/When/Then structure
        """
        prompt = self._build_bdd_prompt(user_story, additional_context)
        response = self._call_ai_api(prompt)
        
        scenarios = self._parse_bdd_scenarios(response)
        return scenarios

    def generate_test_data(
        self, 
        test_case: TestCase,
        data_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate test data for a test case
        
        Args:
            test_case: Test case object
            data_types: Types of test data to generate
            
        Returns:
            Dictionary of test data
        """
        if data_types is None:
            data_types = ["valid", "invalid", "boundary", "edge"]
        
        prompt = self._build_test_data_prompt(test_case, data_types)
        response = self._call_ai_api(prompt)
        
        test_data = self._parse_test_data(response)
        return test_data

    def analyze_test_coverage(
        self, 
        user_story: UserStory,
        existing_test_cases: List[TestCase]
    ) -> Dict[str, Any]:
        """
        Analyze test coverage for a user story
        
        Args:
            user_story: User story object
            existing_test_cases: Existing test cases
            
        Returns:
            Coverage analysis with recommendations
        """
        prompt = self._build_coverage_analysis_prompt(user_story, existing_test_cases)
        response = self._call_ai_api(prompt)
        
        analysis = self._parse_coverage_analysis(response)
        return analysis

    def _build_test_generation_prompt(
        self, 
        user_story: UserStory, 
        test_types: List[TestCaseType],
        num_cases: int,
        additional_prompts: List[str]
    ) -> str:
        """Build prompt for test case generation"""
        
        test_types_str = ", ".join([t.value for t in test_types])
        
        prompt = f"""
You are an expert QA engineer with 10+ years of experience in test case design and automation.
Generate {num_cases} comprehensive test cases for the following user story.

USER STORY:
Title: {user_story.title}
Description: {user_story.description}
Acceptance Criteria: {', '.join(user_story.acceptance_criteria)}
Business Value: {user_story.business_value}
User Persona: {user_story.user_persona}

REQUIREMENTS:
- Generate test cases of types: {test_types_str}
- Include both positive and negative test scenarios
- Consider edge cases and boundary conditions
- Include security and accessibility considerations where relevant
- Each test case should be detailed and actionable
- Include preconditions and test data requirements

ADDITIONAL CONTEXT:
{chr(10).join(additional_prompts) if additional_prompts else "None"}

Please provide the test cases in the following JSON format:
{{
    "test_cases": [
        {{
            "title": "Test case title",
            "description": "Detailed description",
            "steps": ["Step 1", "Step 2", "Step 3"],
            "expected_result": "Expected outcome",
            "test_type": "functional|ui|api|integration|performance|security|accessibility",
            "priority": "high|medium|low",
            "tags": ["tag1", "tag2"],
            "preconditions": ["Precondition 1", "Precondition 2"],
            "test_data": {{"key": "value"}},
            "acceptance_criteria": ["Criteria 1", "Criteria 2"]
        }}
    ]
}}
"""
        return prompt

    def _build_improvement_prompt(
        self, 
        test_case: TestCase, 
        improvement_prompts: List[str]
    ) -> str:
        """Build prompt for test case improvement"""
        
        prompt = f"""
You are an expert QA engineer reviewing and improving a test case.

ORIGINAL TEST CASE:
Title: {test_case.title}
Description: {test_case.description}
Steps: {test_case.steps}
Expected Result: {test_case.expected_result}
Type: {test_case.test_type.value}
Priority: {test_case.priority.value}
Tags: {test_case.tags}

IMPROVEMENT REQUESTS:
{chr(10).join(improvement_prompts)}

Please provide an improved version of the test case that addresses the improvement requests.
Maintain the same JSON format as the original test case.
"""
        return prompt

    def _build_bdd_prompt(self, user_story: UserStory, additional_context: str) -> str:
        """Build prompt for BDD scenario generation"""
        
        prompt = f"""
You are a BDD expert. Generate comprehensive BDD scenarios for the following user story.

USER STORY:
Title: {user_story.title}
Description: {user_story.description}
Acceptance Criteria: {', '.join(user_story.acceptance_criteria)}

ADDITIONAL CONTEXT:
{additional_context or "None"}

Generate scenarios in Gherkin format with Given/When/Then structure.
Include happy path, edge cases, and error scenarios.
Provide the scenarios in JSON format:
{{
    "scenarios": [
        {{
            "title": "Scenario title",
            "description": "Scenario description",
            "given": ["Given condition 1", "Given condition 2"],
            "when": ["When action 1", "When action 2"],
            "then": ["Then expected result 1", "Then expected result 2"],
            "tags": ["@tag1", "@tag2"],
            "examples": [
                {{"param1": "value1", "param2": "value2"}},
                {{"param1": "value3", "param2": "value4"}}
            ]
        }}
    ]
}}
"""
        return prompt

    def _build_test_data_prompt(self, test_case: TestCase, data_types: List[str]) -> str:
        """Build prompt for test data generation"""
        
        prompt = f"""
You are a test data expert. Generate comprehensive test data for the following test case.

TEST CASE:
Title: {test_case.title}
Description: {test_case.description}
Steps: {test_case.steps}
Type: {test_case.test_type.value}

Generate test data for the following types: {', '.join(data_types)}

Provide realistic, diverse test data that covers:
- Valid inputs
- Invalid inputs
- Boundary values
- Edge cases
- Security considerations

Return in JSON format:
{{
    "test_data": {{
        "valid": {{"field1": "value1", "field2": "value2"}},
        "invalid": {{"field1": "invalid_value", "field2": "invalid_value"}},
        "boundary": {{"field1": "boundary_value", "field2": "boundary_value"}},
        "edge": {{"field1": "edge_value", "field2": "edge_value"}}
    }}
}}
"""
        return prompt

    def _build_coverage_analysis_prompt(
        self, 
        user_story: UserStory, 
        existing_test_cases: List[TestCase]
    ) -> str:
        """Build prompt for coverage analysis"""
        
        existing_titles = [tc.title for tc in existing_test_cases]
        
        prompt = f"""
You are a test coverage expert. Analyze the test coverage for the following user story.

USER STORY:
Title: {user_story.title}
Description: {user_story.description}
Acceptance Criteria: {', '.join(user_story.acceptance_criteria)}

EXISTING TEST CASES:
{chr(10).join(existing_titles)}

Analyze the coverage and provide recommendations for:
1. Missing test scenarios
2. Coverage gaps
3. Test case improvements
4. Additional test types needed

Return in JSON format:
{{
    "coverage_analysis": {{
        "coverage_percentage": 85,
        "covered_areas": ["area1", "area2"],
        "missing_areas": ["area3", "area4"],
        "recommendations": [
            "Add negative test cases",
            "Include performance testing",
            "Add security test cases"
        ],
        "suggested_test_cases": [
            {{
                "title": "Suggested test case title",
                "type": "functional",
                "priority": "high",
                "reason": "Covers missing scenario"
            }}
        ]
    }}
}}
"""
        return prompt

    def _call_ai_api(self, prompt: str) -> str:
        """Call AI API and return response"""
        
        if self.provider == "local":
            # Use local AI provider
            response = self.local_ai.generate_test_cases(prompt)
            if response.success:
                return response.content
            else:
                raise Exception(f"Local AI error: {response.error}")
        
        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert QA engineer and test automation specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _parse_test_cases_response(self, response: str, test_types: List[TestCaseType]) -> List[TestCase]:
        """Parse AI response into test case objects"""
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            test_cases = []
            for tc_data in data.get('test_cases', []):
                test_case = TestCase(
                    title=tc_data.get('title', ''),
                    description=tc_data.get('description', ''),
                    steps=tc_data.get('steps', []),
                    expected_result=tc_data.get('expected_result', ''),
                    test_type=TestCaseType(tc_data.get('test_type', 'functional')),
                    priority=TestPriority(tc_data.get('priority', 'medium')),
                    tags=tc_data.get('tags', []),
                    preconditions=tc_data.get('preconditions', []),
                    test_data=tc_data.get('test_data', {}),
                    acceptance_criteria=tc_data.get('acceptance_criteria', [])
                )
                test_cases.append(test_case)
            
            return test_cases
            
        except Exception as e:
            print(f"Error parsing test cases: {e}")
            return []

    def _parse_single_test_case(self, response: str) -> TestCase:
        """Parse single test case from response"""
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            return TestCase(
                title=data.get('title', ''),
                description=data.get('description', ''),
                steps=data.get('steps', []),
                expected_result=data.get('expected_result', ''),
                test_type=TestCaseType(data.get('test_type', 'functional')),
                priority=TestPriority(data.get('priority', 'medium')),
                tags=data.get('tags', []),
                preconditions=data.get('preconditions', []),
                test_data=data.get('test_data', {}),
                acceptance_criteria=data.get('acceptance_criteria', [])
            )
            
        except Exception as e:
            print(f"Error parsing test case: {e}")
            return TestCase("", "", [], "", TestCaseType.FUNCTIONAL, TestPriority.MEDIUM, [], [], {}, [])

    def _parse_bdd_scenarios(self, response: str) -> List[Dict[str, Any]]:
        """Parse BDD scenarios from response"""
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            return data.get('scenarios', [])
            
        except Exception as e:
            print(f"Error parsing BDD scenarios: {e}")
            return []

    def _parse_test_data(self, response: str) -> Dict[str, Any]:
        """Parse test data from response"""
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            return data.get('test_data', {})
            
        except Exception as e:
            print(f"Error parsing test data: {e}")
            return {}

    def _parse_coverage_analysis(self, response: str) -> Dict[str, Any]:
        """Parse coverage analysis from response"""
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            return data.get('coverage_analysis', {})
            
        except Exception as e:
            print(f"Error parsing coverage analysis: {e}")
            return {}

# Example usage and testing
if __name__ == "__main__":
    # Example user story
    user_story = UserStory(
        title="User Login",
        description="As a user, I want to log into the system so that I can access my account",
        acceptance_criteria=[
            "User can log in with valid credentials",
            "User cannot log in with invalid credentials",
            "User is redirected to dashboard after successful login",
            "User receives error message for invalid login attempts"
        ],
        business_value="Enables secure access to user accounts",
        user_persona="Registered user",
        epic="Authentication",
        story_points=5
    )
    
    # Initialize AI generator (requires API key)
    try:
        generator = AITestGenerator(provider="openai")
        
        # Generate test cases
        test_cases = generator.generate_test_cases_from_story(
            user_story=user_story,
            test_types=[TestCaseType.FUNCTIONAL, TestCaseType.UI, TestCaseType.SECURITY],
            num_cases=5,
            additional_prompts=[
                "Focus on security testing",
                "Include mobile responsiveness",
                "Consider accessibility requirements"
            ]
        )
        
        print(f"Generated {len(test_cases)} test cases:")
        for i, tc in enumerate(test_cases, 1):
            print(f"\n{i}. {tc.title}")
            print(f"   Type: {tc.test_type.value}")
            print(f"   Priority: {tc.priority.value}")
            print(f"   Steps: {len(tc.steps)} steps")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")