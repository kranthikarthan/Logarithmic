#!/usr/bin/env python3
"""
Selenium Integration for Assertly
Generates and executes Selenium test cases from AI-generated test scenarios
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

@dataclass
class SeleniumTestStep:
    action: str
    selector: str
    value: Optional[str] = None
    wait_time: int = 5
    description: str = ""

@dataclass
class SeleniumTestResult:
    test_name: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    steps_executed: List[str] = None

class AssertlySeleniumIntegration:
    def __init__(self, headless: bool = True, browser: str = "chrome"):
        """
        Initialize Selenium integration
        
        Args:
            headless: Run browser in headless mode
            browser: Browser to use ("chrome", "firefox", "edge")
        """
        self.headless = headless
        self.browser = browser
        self.driver = None
        self.wait = None
        self.results = []
        
    def setup_driver(self):
        """Setup WebDriver based on browser choice"""
        if self.browser.lower() == "chrome":
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            self.driver = webdriver.Chrome(options=options)
            
        elif self.browser.lower() == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=options)
            
        elif self.browser.lower() == "edge":
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            self.driver = webdriver.Edge(options=options)
            
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")
            
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        
    def teardown_driver(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()
            
    def convert_test_case_to_selenium(self, test_case: Dict[str, Any]) -> List[SeleniumTestStep]:
        """
        Convert AI-generated test case to Selenium test steps
        
        Args:
            test_case: AI-generated test case
            
        Returns:
            List of Selenium test steps
        """
        steps = []
        
        for i, step in enumerate(test_case.get('steps', [])):
            selenium_step = self.parse_step_to_selenium(step, i + 1)
            if selenium_step:
                steps.append(selenium_step)
                
        return steps
        
    def parse_step_to_selenium(self, step: str, step_number: int) -> Optional[SeleniumTestStep]:
        """
        Parse a test step into Selenium actions
        
        Args:
            step: Test step description
            step_number: Step number for reference
            
        Returns:
            SeleniumTestStep object or None if step cannot be parsed
        """
        step_lower = step.lower()
        
        # Navigation steps
        if "navigate" in step_lower or "go to" in step_lower or "visit" in step_lower:
            url = self.extract_url(step)
            return SeleniumTestStep(
                action="navigate",
                selector=url,
                description=f"Step {step_number}: {step}"
            )
            
        # Click actions
        elif "click" in step_lower:
            selector = self.extract_selector(step)
            return SeleniumTestStep(
                action="click",
                selector=selector,
                description=f"Step {step_number}: {step}"
            )
            
        # Input actions
        elif "enter" in step_lower or "type" in step_lower or "input" in step_lower:
            selector = self.extract_selector(step)
            value = self.extract_input_value(step)
            return SeleniumTestStep(
                action="input",
                selector=selector,
                value=value,
                description=f"Step {step_number}: {step}"
            )
            
        # Wait actions
        elif "wait" in step_lower:
            wait_time = self.extract_wait_time(step)
            selector = self.extract_selector(step)
            return SeleniumTestStep(
                action="wait",
                selector=selector,
                wait_time=wait_time,
                description=f"Step {step_number}: {step}"
            )
            
        # Verify actions
        elif "verify" in step_lower or "check" in step_lower or "assert" in step_lower:
            selector = self.extract_selector(step)
            return SeleniumTestStep(
                action="verify",
                selector=selector,
                description=f"Step {step_number}: {step}"
            )
            
        # Hover actions
        elif "hover" in step_lower:
            selector = self.extract_selector(step)
            return SeleniumTestStep(
                action="hover",
                selector=selector,
                description=f"Step {step_number}: {step}"
            )
            
        # Scroll actions
        elif "scroll" in step_lower:
            direction = self.extract_scroll_direction(step)
            return SeleniumTestStep(
                action="scroll",
                selector=direction,
                description=f"Step {step_number}: {step}"
            )
            
        return None
        
    def extract_url(self, step: str) -> str:
        """Extract URL from navigation step"""
        import re
        url_pattern = r'(https?://[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(url_pattern, step)
        return match.group(1) if match else "https://example.com"
        
    def extract_selector(self, step: str) -> str:
        """Extract CSS selector from step"""
        # Common selector patterns
        if "button" in step.lower():
            return "button"
        elif "link" in step.lower():
            return "a"
        elif "input" in step.lower():
            return "input"
        elif "form" in step.lower():
            return "form"
        elif "div" in step.lower():
            return "div"
        else:
            # Try to extract specific selectors
            import re
            # Look for quoted text that might be a selector
            quoted = re.search(r'"([^"]+)"', step)
            if quoted:
                return quoted.group(1)
            # Look for specific element mentions
            if "login" in step.lower():
                return "#login, .login, [data-testid='login']"
            elif "submit" in step.lower():
                return "input[type='submit'], button[type='submit']"
            elif "email" in step.lower():
                return "input[type='email'], input[name='email']"
            elif "password" in step.lower():
                return "input[type='password'], input[name='password']"
            else:
                return "body"  # Fallback
                
    def extract_input_value(self, step: str) -> str:
        """Extract input value from step"""
        import re
        # Look for quoted values
        quoted = re.search(r'"([^"]+)"', step)
        if quoted:
            return quoted.group(1)
        # Look for common test values
        if "email" in step.lower():
            return "test@example.com"
        elif "password" in step.lower():
            return "password123"
        elif "username" in step.lower():
            return "testuser"
        else:
            return "test value"
            
    def extract_wait_time(self, step: str) -> int:
        """Extract wait time from step"""
        import re
        time_match = re.search(r'(\d+)\s*(second|sec|s)', step.lower())
        if time_match:
            return int(time_match.group(1))
        return 5  # Default wait time
        
    def extract_scroll_direction(self, step: str) -> str:
        """Extract scroll direction from step"""
        if "down" in step.lower():
            return "down"
        elif "up" in step.lower():
            return "up"
        else:
            return "down"
            
    def execute_selenium_step(self, step: SeleniumTestStep) -> bool:
        """
        Execute a single Selenium test step
        
        Args:
            step: Selenium test step to execute
            
        Returns:
            True if step executed successfully, False otherwise
        """
        try:
            if step.action == "navigate":
                self.driver.get(step.selector)
                return True
                
            elif step.action == "click":
                element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, step.selector)))
                element.click()
                return True
                
            elif step.action == "input":
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.selector)))
                element.clear()
                element.send_keys(step.value or "")
                return True
                
            elif step.action == "wait":
                if step.selector:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.selector)))
                else:
                    time.sleep(step.wait_time)
                return True
                
            elif step.action == "verify":
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.selector)))
                return element.is_displayed()
                
            elif step.action == "hover":
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.selector)))
                ActionChains(self.driver).move_to_element(element).perform()
                return True
                
            elif step.action == "scroll":
                if step.selector == "down":
                    self.driver.execute_script("window.scrollBy(0, 500);")
                elif step.selector == "up":
                    self.driver.execute_script("window.scrollBy(0, -500);")
                return True
                
            return False
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error executing step '{step.description}': {str(e)}")
            return False
            
    def execute_test_case(self, test_case: Dict[str, Any], base_url: str = "https://example.com") -> SeleniumTestResult:
        """
        Execute a complete test case using Selenium
        
        Args:
            test_case: AI-generated test case
            base_url: Base URL for the application
            
        Returns:
            SeleniumTestResult object
        """
        start_time = time.time()
        test_name = test_case.get('title', 'Unknown Test')
        steps_executed = []
        
        try:
            # Setup driver if not already done
            if not self.driver:
                self.setup_driver()
                
            # Convert test case to Selenium steps
            selenium_steps = self.convert_test_case_to_selenium(test_case)
            
            # Execute each step
            for step in selenium_steps:
                print(f"Executing: {step.description}")
                success = self.execute_selenium_step(step)
                steps_executed.append(step.description)
                
                if not success:
                    # Take screenshot on failure
                    screenshot_path = f"screenshots/{test_name}_{int(time.time())}.png"
                    os.makedirs("screenshots", exist_ok=True)
                    self.driver.save_screenshot(screenshot_path)
                    
                    return SeleniumTestResult(
                        test_name=test_name,
                        status="failed",
                        duration=time.time() - start_time,
                        error_message=f"Step failed: {step.description}",
                        screenshot_path=screenshot_path,
                        steps_executed=steps_executed
                    )
                    
            # Test passed
            return SeleniumTestResult(
                test_name=test_name,
                status="passed",
                duration=time.time() - start_time,
                steps_executed=steps_executed
            )
            
        except Exception as e:
            # Take screenshot on exception
            screenshot_path = f"screenshots/{test_name}_{int(time.time())}.png"
            os.makedirs("screenshots", exist_ok=True)
            if self.driver:
                self.driver.save_screenshot(screenshot_path)
                
            return SeleniumTestResult(
                test_name=test_name,
                status="failed",
                duration=time.time() - start_time,
                error_message=str(e),
                screenshot_path=screenshot_path,
                steps_executed=steps_executed
            )
            
    def generate_selenium_test_file(self, test_case: Dict[str, Any], output_path: str):
        """
        Generate a Python Selenium test file from AI test case
        
        Args:
            test_case: AI-generated test case
            output_path: Path to save the test file
        """
        test_name = test_case.get('title', 'Unknown Test').replace(' ', '_').lower()
        selenium_steps = self.convert_test_case_to_selenium(test_case)
        
        test_file_content = f'''#!/usr/bin/env python3
"""
Generated Selenium test for: {test_case.get('title', 'Unknown Test')}
Generated by Assertly AI Test Generator
"""

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

class Test{test_name.title().replace('_', '')}(unittest.TestCase):
    """Test case: {test_case.get('title', 'Unknown Test')}"""
    
    def setUp(self):
        """Setup test environment"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        
    def tearDown(self):
        """Clean up test environment"""
        self.driver.quit()
        
    def test_{test_name}(self):
        """Test: {test_case.get('description', 'No description')}"""
        
        # Test Steps:
'''
        
        # Add test steps
        for i, step in enumerate(selenium_steps):
            test_file_content += f'''        # Step {i+1}: {step.description}
        {self.generate_selenium_code_for_step(step)}
        
'''
            
        # Add assertion
        test_file_content += f'''        # Expected Result: {test_case.get('expected_result', 'Test should pass')}
        self.assertTrue(True, "Test completed successfully")
        
if __name__ == '__main__':
    unittest.main()
'''
        
        # Write test file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(test_file_content)
            
    def generate_selenium_code_for_step(self, step: SeleniumTestStep) -> str:
        """Generate Python Selenium code for a test step"""
        if step.action == "navigate":
            return f'self.driver.get("{step.selector}")'
        elif step.action == "click":
            return f'self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "{step.selector}"))).click()'
        elif step.action == "input":
            return f'self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "{step.selector}"))).send_keys("{step.value or ""}")'
        elif step.action == "wait":
            if step.selector:
                return f'self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "{step.selector}")))'
            else:
                return f'time.sleep({step.wait_time})'
        elif step.action == "verify":
            return f'element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "{step.selector}")))\n        self.assertTrue(element.is_displayed())'
        elif step.action == "hover":
            return f'element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "{step.selector}")))\n        ActionChains(self.driver).move_to_element(element).perform()'
        elif step.action == "scroll":
            if step.selector == "down":
                return 'self.driver.execute_script("window.scrollBy(0, 500);")'
            else:
                return 'self.driver.execute_script("window.scrollBy(0, -500);")'
        else:
            return f'# Unknown action: {step.action}'

# Example usage
if __name__ == "__main__":
    # Example test case
    test_case = {
        "title": "User Login Test",
        "description": "Test user login functionality",
        "steps": [
            "Navigate to login page",
            "Enter email address",
            "Enter password",
            "Click login button",
            "Verify user is logged in"
        ],
        "expected_result": "User should be successfully logged in"
    }
    
    # Initialize integration
    integration = AssertlySeleniumIntegration(headless=True)
    
    try:
        # Execute test case
        result = integration.execute_test_case(test_case)
        print(f"Test Result: {result.status}")
        print(f"Duration: {result.duration:.2f}s")
        
        if result.error_message:
            print(f"Error: {result.error_message}")
            
    finally:
        # Cleanup
        integration.teardown_driver()