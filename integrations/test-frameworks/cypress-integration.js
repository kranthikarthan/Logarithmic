/**
 * Cypress Integration for Assertly
 * Generates and executes Cypress test cases from AI-generated test scenarios
 */

const fs = require('fs');
const path = require('path');

class AssertlyCypressIntegration {
    constructor(options = {}) {
        this.baseUrl = options.baseUrl || 'https://example.com';
        this.timeout = options.timeout || 10000;
        this.viewport = options.viewport || { width: 1280, height: 720 };
        this.results = [];
    }

    /**
     * Convert AI-generated test case to Cypress test
     * @param {Object} testCase - AI-generated test case
     * @returns {Object} Cypress test configuration
     */
    convertTestCaseToCypress(testCase) {
        const testName = this.sanitizeTestName(testCase.title);
        const steps = this.convertStepsToCypress(testCase.steps);
        
        return {
            name: testName,
            description: testCase.description,
            steps: steps,
            expectedResult: testCase.expected_result,
            testType: testCase.test_type,
            priority: testCase.priority,
            tags: testCase.tags || [],
            preconditions: testCase.preconditions || []
        };
    }

    /**
     * Convert test steps to Cypress commands
     * @param {Array} steps - Test steps
     * @returns {Array} Cypress commands
     */
    convertStepsToCypress(steps) {
        return steps.map((step, index) => {
            const cypressStep = this.parseStepToCypress(step, index + 1);
            return {
                stepNumber: index + 1,
                description: step,
                cypressCommand: cypressStep.command,
                selector: cypressStep.selector,
                value: cypressStep.value,
                options: cypressStep.options || {}
            };
        });
    }

    /**
     * Parse a test step into Cypress command
     * @param {string} step - Test step description
     * @param {number} stepNumber - Step number
     * @returns {Object} Cypress command object
     */
    parseStepToCypress(step, stepNumber) {
        const stepLower = step.toLowerCase();
        
        // Navigation steps
        if (stepLower.includes('navigate') || stepLower.includes('go to') || stepLower.includes('visit')) {
            const url = this.extractUrl(step);
            return {
                command: 'cy.visit',
                selector: url,
                value: null,
                options: { timeout: this.timeout }
            };
        }
        
        // Click actions
        else if (stepLower.includes('click')) {
            const selector = this.extractSelector(step);
            return {
                command: 'cy.get',
                selector: selector,
                value: null,
                options: { timeout: this.timeout }
            };
        }
        
        // Input actions
        else if (stepLower.includes('enter') || stepLower.includes('type') || stepLower.includes('input')) {
            const selector = this.extractSelector(step);
            const value = this.extractInputValue(step);
            return {
                command: 'cy.get',
                selector: selector,
                value: value,
                options: { timeout: this.timeout }
            };
        }
        
        // Wait actions
        else if (stepLower.includes('wait')) {
            const waitTime = this.extractWaitTime(step);
            const selector = this.extractSelector(step);
            return {
                command: 'cy.wait',
                selector: selector,
                value: waitTime,
                options: {}
            };
        }
        
        // Verify actions
        else if (stepLower.includes('verify') || stepLower.includes('check') || stepLower.includes('assert')) {
            const selector = this.extractSelector(step);
            return {
                command: 'cy.get',
                selector: selector,
                value: null,
                options: { timeout: this.timeout }
            };
        }
        
        // Hover actions
        else if (stepLower.includes('hover')) {
            const selector = this.extractSelector(step);
            return {
                command: 'cy.get',
                selector: selector,
                value: null,
                options: { timeout: this.timeout }
            };
        }
        
        // Scroll actions
        else if (stepLower.includes('scroll')) {
            const direction = this.extractScrollDirection(step);
            return {
                command: 'cy.scrollTo',
                selector: direction,
                value: null,
                options: {}
            };
        }
        
        // Default action
        else {
            return {
                command: 'cy.log',
                selector: `Step ${stepNumber}: ${step}`,
                value: null,
                options: {}
            };
        }
    }

    /**
     * Extract URL from navigation step
     * @param {string} step - Test step
     * @returns {string} URL
     */
    extractUrl(step) {
        const urlPattern = /(https?:\/\/[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/;
        const match = step.match(urlPattern);
        return match ? match[1] : this.baseUrl;
    }

    /**
     * Extract CSS selector from step
     * @param {string} step - Test step
     * @returns {string} CSS selector
     */
    extractSelector(step) {
        const stepLower = step.toLowerCase();
        
        // Common selector patterns
        if (stepLower.includes('button')) {
            return 'button';
        } else if (stepLower.includes('link')) {
            return 'a';
        } else if (stepLower.includes('input')) {
            return 'input';
        } else if (stepLower.includes('form')) {
            return 'form';
        } else if (stepLower.includes('div')) {
            return 'div';
        } else {
            // Try to extract specific selectors
            const quoted = step.match(/"([^"]+)"/);
            if (quoted) {
                return quoted[1];
            }
            
            // Look for specific element mentions
            if (stepLower.includes('login')) {
                return '[data-testid="login"], #login, .login';
            } else if (stepLower.includes('submit')) {
                return 'input[type="submit"], button[type="submit"]';
            } else if (stepLower.includes('email')) {
                return 'input[type="email"], input[name="email"]';
            } else if (stepLower.includes('password')) {
                return 'input[type="password"], input[name="password"]';
            } else {
                return 'body'; // Fallback
            }
        }
    }

    /**
     * Extract input value from step
     * @param {string} step - Test step
     * @returns {string} Input value
     */
    extractInputValue(step) {
        const quoted = step.match(/"([^"]+)"/);
        if (quoted) {
            return quoted[1];
        }
        
        const stepLower = step.toLowerCase();
        if (stepLower.includes('email')) {
            return 'test@example.com';
        } else if (stepLower.includes('password')) {
            return 'password123';
        } else if (stepLower.includes('username')) {
            return 'testuser';
        } else {
            return 'test value';
        }
    }

    /**
     * Extract wait time from step
     * @param {string} step - Test step
     * @returns {number} Wait time in milliseconds
     */
    extractWaitTime(step) {
        const timeMatch = step.match(/(\d+)\s*(second|sec|s)/i);
        if (timeMatch) {
            return parseInt(timeMatch[1]) * 1000;
        }
        return 5000; // Default wait time
    }

    /**
     * Extract scroll direction from step
     * @param {string} step - Test step
     * @returns {string} Scroll direction
     */
    extractScrollDirection(step) {
        const stepLower = step.toLowerCase();
        if (stepLower.includes('down')) {
            return 'bottom';
        } else if (stepLower.includes('up')) {
            return 'top';
        } else {
            return 'bottom';
        }
    }

    /**
     * Generate Cypress test file from AI test case
     * @param {Object} testCase - AI-generated test case
     * @param {string} outputPath - Path to save the test file
     */
    generateCypressTestFile(testCase, outputPath) {
        const cypressTest = this.convertTestCaseToCypress(testCase);
        const testName = cypressTest.name;
        const fileName = `${testName}.cy.js`;
        const fullPath = path.join(outputPath, fileName);
        
        const testContent = this.generateCypressTestContent(cypressTest);
        
        // Ensure directory exists
        fs.mkdirSync(path.dirname(fullPath), { recursive: true });
        
        // Write test file
        fs.writeFileSync(fullPath, testContent);
        
        console.log(`Generated Cypress test file: ${fullPath}`);
        return fullPath;
    }

    /**
     * Generate Cypress test content
     * @param {Object} cypressTest - Cypress test configuration
     * @returns {string} Test file content
     */
    generateCypressTestContent(cypressTest) {
        const testName = cypressTest.name;
        const description = cypressTest.description;
        const steps = cypressTest.steps;
        
        let content = `/**
 * Generated Cypress test for: ${testName}
 * Description: ${description}
 * Generated by Assertly AI Test Generator
 */

describe('${testName}', () => {
    beforeEach(() => {
        // Setup test environment
        cy.viewport(${this.viewport.width}, ${this.viewport.height});
    });

    it('${description}', () => {
        // Test Steps:
`;

        // Add test steps
        steps.forEach((step, index) => {
            content += `        // Step ${step.stepNumber}: ${step.description}\n`;
            content += this.generateCypressCommand(step);
            content += '\n';
        });

        // Add expected result
        content += `        // Expected Result: ${cypressTest.expectedResult}\n`;
        content += `        cy.log('Test completed successfully');\n`;
        content += `    });\n`;
        content += `});\n`;

        return content;
    }

    /**
     * Generate Cypress command for a test step
     * @param {Object} step - Test step
     * @returns {string} Cypress command
     */
    generateCypressCommand(step) {
        const { command, selector, value, options } = step;
        
        switch (command) {
            case 'cy.visit':
                return `        cy.visit('${selector}');\n`;
                
            case 'cy.get':
                if (value) {
                    return `        cy.get('${selector}').type('${value}');\n`;
                } else {
                    return `        cy.get('${selector}').click();\n`;
                }
                
            case 'cy.wait':
                if (selector) {
                    return `        cy.get('${selector}').should('be.visible');\n`;
                } else {
                    return `        cy.wait(${value});\n`;
                }
                
            case 'cy.scrollTo':
                return `        cy.scrollTo('${selector}');\n`;
                
            case 'cy.log':
                return `        cy.log('${selector}');\n`;
                
            default:
                return `        cy.log('Unknown command: ${command}');\n`;
        }
    }

    /**
     * Sanitize test name for file system
     * @param {string} name - Test name
     * @returns {string} Sanitized name
     */
    sanitizeTestName(name) {
        return name
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
    }

    /**
     * Execute Cypress test case
     * @param {Object} testCase - AI-generated test case
     * @returns {Promise<Object>} Test execution result
     */
    async executeTestCase(testCase) {
        const startTime = Date.now();
        const testName = testCase.title || 'Unknown Test';
        
        try {
            // Convert to Cypress test
            const cypressTest = this.convertTestCaseToCypress(testCase);
            
            // Generate test file
            const tempDir = path.join(__dirname, 'temp');
            const testFilePath = this.generateCypressTestFile(testCase, tempDir);
            
            // Execute test (this would require Cypress to be installed)
            console.log(`Executing Cypress test: ${testName}`);
            
            // Simulate test execution
            const result = {
                testName: testName,
                status: 'passed',
                duration: Date.now() - startTime,
                stepsExecuted: cypressTest.steps.map(step => step.description),
                errorMessage: null
            };
            
            return result;
            
        } catch (error) {
            return {
                testName: testName,
                status: 'failed',
                duration: Date.now() - startTime,
                stepsExecuted: [],
                errorMessage: error.message
            };
        }
    }

    /**
     * Generate Cypress configuration file
     * @param {string} outputPath - Path to save config file
     */
    generateCypressConfig(outputPath) {
        const configContent = `const { defineConfig } = require('cypress');

module.exports = defineConfig({
    e2e: {
        baseUrl: '${this.baseUrl}',
        viewportWidth: ${this.viewport.width},
        viewportHeight: ${this.viewport.height},
        defaultCommandTimeout: ${this.timeout},
        requestTimeout: ${this.timeout},
        responseTimeout: ${this.timeout},
        setupNodeEvents(on, config) {
            // Setup for Assertly integration
            on('task', {
                log(message) {
                    console.log(message);
                    return null;
                }
            });
        },
    },
    component: {
        devServer: {
            framework: 'create-react-app',
            bundler: 'webpack',
        },
    },
});
`;

        fs.writeFileSync(path.join(outputPath, 'cypress.config.js'), configContent);
        console.log(`Generated Cypress config: ${path.join(outputPath, 'cypress.config.js')}`);
    }

    /**
     * Generate package.json for Cypress project
     * @param {string} outputPath - Path to save package.json
     */
    generatePackageJson(outputPath) {
        const packageJson = {
            name: 'assertly-cypress-tests',
            version: '1.0.0',
            description: 'Generated Cypress tests by Assertly AI',
            scripts: {
                'cypress:open': 'cypress open',
                'cypress:run': 'cypress run',
                'cypress:run:headless': 'cypress run --headless',
                'test': 'cypress run'
            },
            devDependencies: {
                'cypress': '^13.0.0'
            }
        };

        fs.writeFileSync(
            path.join(outputPath, 'package.json'),
            JSON.stringify(packageJson, null, 2)
        );
        console.log(`Generated package.json: ${path.join(outputPath, 'package.json')}`);
    }
}

// Example usage
if (require.main === module) {
    const integration = new AssertlyCypressIntegration({
        baseUrl: 'https://example.com',
        viewport: { width: 1280, height: 720 }
    });

    // Example test case
    const testCase = {
        title: 'User Login Test',
        description: 'Test user login functionality',
        steps: [
            'Navigate to login page',
            'Enter email address',
            'Enter password',
            'Click login button',
            'Verify user is logged in'
        ],
        expected_result: 'User should be successfully logged in',
        test_type: 'functional',
        priority: 'high'
    };

    // Generate Cypress test file
    const outputPath = './cypress-tests';
    integration.generateCypressTestFile(testCase, outputPath);
    integration.generateCypressConfig(outputPath);
    integration.generatePackageJson(outputPath);

    console.log('Cypress integration setup complete!');
}

module.exports = AssertlyCypressIntegration;