// Integrations JavaScript
class IntegrationsManager {
    constructor() {
        this.currentCategory = 'ide';
        this.init();
    }

    init() {
        this.setupCategoryTabs();
        this.setupWebhookManagement();
        this.setupNotifications();
    }

    setupCategoryTabs() {
        const tabs = document.querySelectorAll('.category-tab');
        const contents = document.querySelectorAll('.category-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const category = tab.dataset.category;
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Show corresponding content
                contents.forEach(content => {
                    content.style.display = 'none';
                });
                
                const targetContent = document.getElementById(`${category}-category`);
                if (targetContent) {
                    targetContent.style.display = 'block';
                }
                
                this.currentCategory = category;
            });
        });
    }

    setupWebhookManagement() {
        const registerBtn = document.getElementById('register-webhook-btn');
        const webhookList = document.getElementById('webhook-list');
        
        if (registerBtn) {
            registerBtn.addEventListener('click', () => {
                const url = document.getElementById('webhook-url').value;
                const events = Array.from(document.querySelectorAll('input[name="webhook-events"]:checked'))
                    .map(cb => cb.value);
                
                if (url && events.length > 0) {
                    this.registerWebhook(url, events);
                } else {
                    this.showNotification('Please fill in all required fields', 'error');
                }
            });
        }
    }

    setupNotifications() {
        // Setup notification system
        this.notificationContainer = document.createElement('div');
        this.notificationContainer.className = 'notification-container';
        this.notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
        `;
        document.body.appendChild(this.notificationContainer);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        
        this.notificationContainer.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    async registerWebhook(url, events) {
        try {
            const response = await fetch('/api/integrations/webhooks/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    events: events
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Webhook registered successfully!', 'success');
                this.loadWebhooks();
            } else {
                this.showNotification(result.error || 'Failed to register webhook', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to register webhook', 'error');
        }
    }

    async loadWebhooks() {
        try {
            const response = await fetch('/api/integrations/webhooks');
            const result = await response.json();
            
            if (result.success) {
                this.displayWebhooks(result.webhooks);
            }
        } catch (error) {
            console.error('Failed to load webhooks:', error);
        }
    }

    displayWebhooks(webhooks) {
        const webhookList = document.getElementById('webhook-list');
        if (!webhookList) return;
        
        webhookList.innerHTML = '';
        
        webhooks.forEach(webhook => {
            const webhookItem = document.createElement('div');
            webhookItem.className = 'webhook-item';
            webhookItem.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-bottom: 8px;
                background: white;
            `;
            
            webhookItem.innerHTML = `
                <div>
                    <div style="font-weight: 500;">${webhook.url}</div>
                    <div style="font-size: 0.875rem; color: #6b7280;">Events: ${webhook.events.join(', ')}</div>
                </div>
                <button onclick="integrationsManager.unregisterWebhook('${webhook.id}')" 
                        style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">
                    Remove
                </button>
            `;
            
            webhookList.appendChild(webhookItem);
        });
    }

    async unregisterWebhook(webhookId) {
        try {
            const response = await fetch(`/api/integrations/webhooks/${webhookId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Webhook removed successfully!', 'success');
                this.loadWebhooks();
            } else {
                this.showNotification(result.error || 'Failed to remove webhook', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to remove webhook', 'error');
        }
    }
}

// Integration functions
function copyGitHubAction() {
    // Copy GitHub Actions template to clipboard
    const template = 'name: Assertly Test Generation\n\n' +
        'on:\n' +
        '  push:\n' +
        '    branches: [ main, develop ]\n' +
        '  pull_request:\n' +
        '    branches: [ main ]\n\n' +
        'jobs:\n' +
        '  generate-tests:\n' +
        '    runs-on: ubuntu-latest\n' +
        '    steps:\n' +
        '    - uses: actions/checkout@v4\n' +
        '    - name: Generate Test Cases\n' +
        '      uses: assertly/generate-tests@v1\n' +
        '      with:\n' +
        '        api-url: ${{ secrets.ASSERTLY_API_URL }}\n' +
        '        api-key: ${{ secrets.ASSERTLY_API_KEY }}\n' +
        '        jira-url: ${{ secrets.JIRA_URL }}\n' +
        '        jira-token: ${{ secrets.JIRA_TOKEN }}';
    
    navigator.clipboard.writeText(template).then(() => {
        showNotification('GitHub Actions template copied to clipboard!', 'success');
    }).catch(err => {
        showNotification('Failed to copy template', 'error');
    });
}

function viewGitHubDocs() {
    window.open('/docs/integrations/github-actions', '_blank');
}

function copyGitLabCI() {
    // Copy GitLab CI template to clipboard
    navigator.clipboard.writeText(`
stages:
  - test-generation

generate-tests:
  stage: test-generation
  image: node:18
  script:
    - npm install -g @assertly/cli
    - assertly generate-tests --api-key $ASSERTLY_API_KEY
  artifacts:
    reports:
      junit: test-results.xml
    paths:
      - test-results/
`).then(() => {
        showNotification('GitLab CI template copied to clipboard!', 'success');
    }).catch(err => {
        showNotification('Failed to copy template', 'error');
    });
}

function viewGitLabDocs() {
    window.open('/docs/integrations/gitlab-ci', '_blank');
}

function installJenkinsPlugin() {
    window.open('https://plugins.jenkins.io/assertly-test-manager', '_blank');
}

function viewJenkinsDocs() {
    window.open('/docs/integrations/jenkins', '_blank');
}

function copyAzureDevOpsTemplate() {
    // Copy Azure DevOps pipeline template to clipboard
    navigator.clipboard.writeText(`
# Azure DevOps Pipeline for Assertly Test Generation
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  ASSERTLY_API_KEY: $(ASSERTLY_API_KEY)
  ASSERTLY_API_URL: $(ASSERTLY_API_URL)
  JIRA_URL: $(JIRA_URL)
  JIRA_TOKEN: $(JIRA_TOKEN)

stages:
- stage: TestGeneration
  displayName: 'Generate Tests with Assertly'
  jobs:
  - job: GenerateTests
    displayName: 'Generate Test Cases'
    steps:
    - task: PowerShell@2
      displayName: 'Install Assertly CLI'
      inputs:
        targetType: 'inline'
        script: |
          # Install Assertly CLI globally
          npm install -g @assertly/cli
          
          # Verify installation
          assertly --version
          
          # Configure Assertly
          assertly config set api-key $(ASSERTLY_API_KEY)
          assertly config set api-url $(ASSERTLY_API_URL)
    
    - task: PowerShell@2
      displayName: 'Generate Test Cases from User Stories'
      inputs:
        targetType: 'inline'
        script: |
          # Create output directories
          mkdir -p ./generated-tests
          mkdir -p ./test-results
          
          # Generate test cases from user stories
          assertly generate-tests \\
            --project-key $(PROJECT_KEY) \\
            --output-format jira \\
            --include-bdd-scenarios \\
            --output-dir ./generated-tests \\
            --jira-url $(JIRA_URL) \\
            --jira-token $(JIRA_TOKEN)
          
          # Generate test data for the test cases
          assertly generate-test-data \\
            --test-cases ./generated-tests/test-cases.json \\
            --output-format csv \\
            --output-dir ./generated-tests/test-data
          
          # Generate BDD scenarios
          assertly generate-bdd-scenarios \\
            --user-stories ./user-stories.json \\
            --output-format gherkin \\
            --output-dir ./generated-tests/bdd-scenarios
    
    - task: PowerShell@2
      displayName: 'Analyze Test Coverage'
      inputs:
        targetType: 'inline'
        script: |
          # Analyze test coverage
          assertly analyze-coverage \\
            --user-stories ./user-stories.json \\
            --test-cases ./generated-tests/test-cases.json \\
            --output-format html \\
            --output-dir ./generated-tests/coverage-report
    
    - task: PublishTestResults@2
      displayName: 'Publish Test Results'
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/test-results.xml'
        mergeTestResults: true
        testRunTitle: 'Assertly Generated Tests'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish Generated Tests'
      inputs:
        pathToPublish: 'generated-tests'
        artifactName: 'assertly-generated-tests'
        publishLocation: 'Container'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish Test Data'
      inputs:
        pathToPublish: 'generated-tests/test-data'
        artifactName: 'assertly-test-data'
        publishLocation: 'Container'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish BDD Scenarios'
      inputs:
        pathToPublish: 'generated-tests/bdd-scenarios'
        artifactName: 'assertly-bdd-scenarios'
        publishLocation: 'Container'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish Coverage Report'
      inputs:
        pathToPublish: 'generated-tests/coverage-report'
        artifactName: 'assertly-coverage-report'
        publishLocation: 'Container'
`).then(() => {
        showNotification('Azure DevOps template copied to clipboard!', 'success');
    }).catch(err => {
        showNotification('Failed to copy template', 'error');
    });
}

function viewAzureDevOpsDocs() {
    window.open('/docs/integrations/azure-devops', '_blank');
}

function installSelenium() {
    window.open('/docs/integrations/selenium', '_blank');
}

function viewSeleniumDocs() {
    window.open('/docs/integrations/selenium', '_blank');
}

function installCypress() {
    window.open('/docs/integrations/cypress', '_blank');
}

function viewCypressDocs() {
    window.open('/docs/integrations/cypress', '_blank');
}

function installVSCode() {
    window.open('https://marketplace.visualstudio.com/items?itemName=assertly.assertly-test-manager', '_blank');
}

function viewVSCodeDocs() {
    window.open('/docs/integrations/vscode', '_blank');
}

function installIntelliJ() {
    window.open('https://plugins.jetbrains.com/plugin/assertly-test-manager', '_blank');
}

function viewIntelliJDocs() {
    window.open('/docs/integrations/intellij', '_blank');
}

function installVim() {
    window.open('/docs/integrations/vim', '_blank');
}

function viewVimDocs() {
    window.open('/docs/integrations/vim', '_blank');
}

function showNotification(message, type = 'info') {
    if (window.integrationsManager) {
        window.integrationsManager.showNotification(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Initialize integrations manager
let integrationsManager;
document.addEventListener('DOMContentLoaded', function() {
    integrationsManager = new IntegrationsManager();
    window.integrationsManager = integrationsManager;
});