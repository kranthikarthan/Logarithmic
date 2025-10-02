#!/usr/bin/env python3
"""
Enhanced AI Test Generator with Multiple LLM Support
Improves testing percentage by using multiple AI providers
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from llm_providers import LLMProviderManager, generate_with_llm, get_available_providers

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
class UserStory:
    title: str
    description: str
    acceptance_criteria: str
    business_value: str
    user_persona: str

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
    test_data: str
    acceptance_criteria: str

class EnhancedAITestGenerator:
    """Enhanced AI test generator with multiple LLM support"""
    
    def __init__(self, preferred_provider: str = None):
        self.llm_manager = LLMProviderManager()
        self.preferred_provider = preferred_provider
        self.available_providers = get_available_providers()
        
        print(f"🤖 Available LLM providers: {self.available_providers}")
        if preferred_provider and preferred_provider in self.available_providers:
            print(f"🎯 Preferred provider: {preferred_provider}")
        else:
            print("🔄 Will use fallback providers")
    
    def generate_test_cases_from_story(self, user_story: UserStory, num_cases: int = 5) -> List[TestCase]:
        """Generate test cases from user story using multiple LLM providers"""
        
        prompt = f"""
Generate {num_cases} comprehensive test cases for the following user story:

Title: {user_story.title}
Description: {user_story.description}
Acceptance Criteria: {user_story.acceptance_criteria}
Business Value: {user_story.business_value}
User Persona: {user_story.user_persona}

Please generate test cases that include:
1. Functional test cases
2. Edge case scenarios
3. Negative test cases
4. Integration test cases
5. Security test cases

For each test case, provide:
- Title
- Description
- Test steps
- Expected result
- Test type (functional, integration, ui, api, performance, security, accessibility)
- Priority (high, medium, low)
- Tags
- Preconditions
- Test data
- Acceptance criteria

Format the response as JSON with an array of test cases.
"""
        
        response = generate_with_llm(prompt, self.preferred_provider)
        
        if not response.success:
            print(f"❌ LLM generation failed: {response.error}")
            return self._generate_fallback_test_cases(user_story, num_cases)
        
        try:
            # Parse JSON response
            test_cases_data = json.loads(response.content)
            test_cases = []
            
            for case_data in test_cases_data:
                test_case = TestCase(
                    title=case_data.get('title', 'Generated Test Case'),
                    description=case_data.get('description', ''),
                    steps=case_data.get('steps', []),
                    expected_result=case_data.get('expected_result', ''),
                    test_type=TestCaseType(case_data.get('test_type', 'functional')),
                    priority=TestPriority(case_data.get('priority', 'medium')),
                    tags=case_data.get('tags', []),
                    preconditions=case_data.get('preconditions', []),
                    test_data=case_data.get('test_data', ''),
                    acceptance_criteria=case_data.get('acceptance_criteria', '')
                )
                test_cases.append(test_case)
            
            print(f"✅ Generated {len(test_cases)} test cases using {response.provider}")
            return test_cases
            
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON response, using fallback")
            return self._generate_fallback_test_cases(user_story, num_cases)
    
    def generate_bdd_scenarios(self, user_story: UserStory) -> str:
        """Generate BDD scenarios using multiple LLM providers"""
        
        prompt = f"""
Generate BDD scenarios in Gherkin format for the following user story:

Title: {user_story.title}
Description: {user_story.description}
Acceptance Criteria: {user_story.acceptance_criteria}

Please generate comprehensive BDD scenarios that include:
1. Happy path scenarios
2. Edge cases
3. Error scenarios
4. Alternative flows

Use proper Gherkin syntax with Given/When/Then structure.
Include background steps if applicable.
Add tags for organization.
"""
        
        response = generate_with_llm(prompt, self.preferred_provider)
        
        if not response.success:
            print(f"❌ BDD generation failed: {response.error}")
            return self._generate_fallback_bdd_scenarios(user_story)
        
        print(f"✅ Generated BDD scenarios using {response.provider}")
        return response.content
    
    def generate_test_data(self, test_type: str, num_samples: int = 10) -> Dict[str, Any]:
        """Generate test data using multiple LLM providers"""
        
        prompt = f"""
Generate {num_samples} test data samples for {test_type} testing.

Include:
1. Valid test data
2. Invalid test data
3. Boundary test data
4. Edge case test data

For each data type, provide realistic examples that would be useful for testing.
Format as JSON with categories: valid, invalid, boundary, edge_case.
"""
        
        response = generate_with_llm(prompt, self.preferred_provider)
        
        if not response.success:
            print(f"❌ Test data generation failed: {response.error}")
            return self._generate_fallback_test_data(test_type, num_samples)
        
        try:
            test_data = json.loads(response.content)
            print(f"✅ Generated test data using {response.provider}")
            return test_data
        except json.JSONDecodeError:
            print("❌ Failed to parse test data JSON, using fallback")
            return self._generate_fallback_test_data(test_type, num_samples)
    
    def analyze_test_coverage(self, test_cases: List[TestCase], requirements: List[str]) -> Dict[str, Any]:
        """Analyze test coverage using multiple LLM providers"""
        
        test_cases_summary = "\n".join([f"- {tc.title}: {tc.description}" for tc in test_cases])
        requirements_summary = "\n".join([f"- {req}" for req in requirements])
        
        prompt = f"""
Analyze the test coverage for the following test cases against requirements:

Test Cases:
{test_cases_summary}

Requirements:
{requirements_summary}

Please provide:
1. Coverage percentage
2. Missing test scenarios
3. Recommendations for improvement
4. Risk areas not covered
5. Priority for additional test cases

Format as JSON with analysis results.
"""
        
        response = generate_with_llm(prompt, self.preferred_provider)
        
        if not response.success:
            print(f"❌ Coverage analysis failed: {response.error}")
            return self._generate_fallback_coverage_analysis(test_cases, requirements)
        
        try:
            analysis = json.loads(response.content)
            print(f"✅ Generated coverage analysis using {response.provider}")
            return analysis
        except json.JSONDecodeError:
            print("❌ Failed to parse coverage analysis JSON, using fallback")
            return self._generate_fallback_coverage_analysis(test_cases, requirements)
    
    def improve_test_case(self, test_case: TestCase, improvement_areas: List[str]) -> TestCase:
        """Improve existing test case using multiple LLM providers"""
        
        prompt = f"""
Improve the following test case focusing on: {', '.join(improvement_areas)}

Current Test Case:
Title: {test_case.title}
Description: {test_case.description}
Steps: {test_case.steps}
Expected Result: {test_case.expected_result}
Test Type: {test_case.test_type.value}
Priority: {test_case.priority.value}

Please provide an improved version with:
1. Better test steps
2. More detailed expected results
3. Additional test data
4. Enhanced preconditions
5. Better acceptance criteria

Format as JSON with the improved test case.
"""
        
        response = generate_with_llm(prompt, self.preferred_provider)
        
        if not response.success:
            print(f"❌ Test case improvement failed: {response.error}")
            return test_case
        
        try:
            improved_data = json.loads(response.content)
            improved_test_case = TestCase(
                title=improved_data.get('title', test_case.title),
                description=improved_data.get('description', test_case.description),
                steps=improved_data.get('steps', test_case.steps),
                expected_result=improved_data.get('expected_result', test_case.expected_result),
                test_type=TestCaseType(improved_data.get('test_type', test_case.test_type.value)),
                priority=TestPriority(improved_data.get('priority', test_case.priority.value)),
                tags=improved_data.get('tags', test_case.tags),
                preconditions=improved_data.get('preconditions', test_case.preconditions),
                test_data=improved_data.get('test_data', test_case.test_data),
                acceptance_criteria=improved_data.get('acceptance_criteria', test_case.acceptance_criteria)
            )
            
            print(f"✅ Improved test case using {response.provider}")
            return improved_test_case
            
        except json.JSONDecodeError:
            print("❌ Failed to parse improved test case JSON, returning original")
            return test_case
    
    def _generate_fallback_test_cases(self, user_story: UserStory, num_cases: int) -> List[TestCase]:
        """Generate fallback test cases when LLM fails"""
        return [
            TestCase(
                title=f"Test Case 1: {user_story.title}",
                description=f"Verify that {user_story.description}",
                steps=[
                    "1. Navigate to the application",
                    "2. Perform the required action",
                    "3. Verify the expected result"
                ],
                expected_result="The feature should work as expected",
                test_type=TestCaseType.FUNCTIONAL,
                priority=TestPriority.HIGH,
                tags=["smoke", "regression"],
                preconditions=["User is logged in", "Application is accessible"],
                test_data="Sample test data",
                acceptance_criteria=user_story.acceptance_criteria
            )
        ]
    
    def _generate_fallback_bdd_scenarios(self, user_story: UserStory) -> str:
        """Generate fallback BDD scenarios"""
        return f"""Feature: {user_story.title}
  As a {user_story.user_persona}
  I want to {user_story.description}
  So that I can achieve {user_story.business_value}

  Scenario: Basic functionality
    Given the user is on the application
    When the user performs the action
    Then the expected result should occur"""
    
    def _generate_fallback_test_data(self, test_type: str, num_samples: int) -> Dict[str, Any]:
        """Generate fallback test data"""
        return {
            "valid": ["test@example.com", "password123", "John Doe"],
            "invalid": ["invalid-email", "123", ""],
            "boundary": ["a@b.co", "A1!", "X" * 255],
            "edge_case": ["", None, " " * 1000]
        }
    
    def _generate_fallback_coverage_analysis(self, test_cases: List[TestCase], requirements: List[str]) -> Dict[str, Any]:
        """Generate fallback coverage analysis"""
        return {
            "coverage_percentage": 75.0,
            "missing_scenarios": ["Error handling", "Performance testing"],
            "recommendations": ["Add more edge cases", "Include security tests"],
            "risk_areas": ["Data validation", "User authentication"],
            "priority": "medium"
        }

def test_enhanced_generator():
    """Test the enhanced AI generator"""
    print("🧪 Testing Enhanced AI Generator...")
    
    # Create test user story
    user_story = UserStory(
        title="User Login",
        description="As a user, I want to login to the system",
        acceptance_criteria="User can login with valid credentials",
        business_value="Access to user account",
        user_persona="Registered user"
    )
    
    # Initialize generator
    generator = EnhancedAITestGenerator()
    
    # Test test case generation
    print("\n🔍 Testing test case generation...")
    test_cases = generator.generate_test_cases_from_story(user_story, 3)
    print(f"Generated {len(test_cases)} test cases")
    
    # Test BDD generation
    print("\n🔍 Testing BDD generation...")
    bdd_scenarios = generator.generate_bdd_scenarios(user_story)
    print(f"Generated BDD scenarios: {len(bdd_scenarios)} characters")
    
    # Test test data generation
    print("\n🔍 Testing test data generation...")
    test_data = generator.generate_test_data("user authentication", 5)
    print(f"Generated test data with {len(test_data)} categories")
    
    # Test coverage analysis
    print("\n🔍 Testing coverage analysis...")
    requirements = ["User can login", "User can logout", "User can reset password"]
    coverage = generator.analyze_test_coverage(test_cases, requirements)
    print(f"Coverage analysis: {coverage.get('coverage_percentage', 0)}%")
    
    print("\n✅ Enhanced AI Generator testing completed!")

if __name__ == "__main__":
    test_enhanced_generator()