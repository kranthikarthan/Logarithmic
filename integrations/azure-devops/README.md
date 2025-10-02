# Azure DevOps Integration for Assertly

This integration allows you to use Assertly AI-powered test generation within your Azure DevOps pipelines.

## 🚀 Features

- **AI-Powered Test Generation**: Generate test cases from user stories using Assertly AI
- **BDD Scenario Generation**: Create Gherkin scenarios automatically
- **Test Data Generation**: Generate comprehensive test data sets
- **Coverage Analysis**: Analyze test coverage and generate reports
- **Jira Integration**: Direct integration with Jira for test case management
- **Artifact Publishing**: Publish generated tests and reports as build artifacts

## 📋 Prerequisites

1. **Azure DevOps Organization** with appropriate permissions
2. **Assertly API Key** - Get from your Assertly account
3. **Node.js 18+** - Required for Assertly CLI
4. **Jira Integration** (optional) - For direct test case creation

## 🔧 Setup

### 1. Configure Pipeline Variables

Add the following variables to your Azure DevOps pipeline:

```yaml
variables:
  ASSERTLY_API_KEY: $(ASSERTLY_API_KEY)  # Your Assertly API key
  ASSERTLY_API_URL: $(ASSERTLY_API_URL)  # Assertly API endpoint
  JIRA_URL: $(JIRA_URL)                 # Optional: Jira URL
  JIRA_TOKEN: $(JIRA_TOKEN)             # Optional: Jira API token
  PROJECT_KEY: $(PROJECT_KEY)           # Optional: Jira project key
```

### 2. Add Pipeline Template

Copy the `azure-pipeline.yml` template to your repository and customize as needed.

### 3. Configure Secrets

In your Azure DevOps project settings, add the following secrets:

- `ASSERTLY_API_KEY`: Your Assertly API key
- `ASSERTLY_API_URL`: Assertly API endpoint (e.g., `https://api.assertly.com`)
- `JIRA_URL`: Your Jira instance URL (optional)
- `JIRA_TOKEN`: Your Jira API token (optional)

## 📁 File Structure

```
integrations/azure-devops/
├── azure-pipeline.yml          # Main pipeline template
├── assertly-integration.ps1    # PowerShell integration script
└── README.md                   # This documentation
```

## 🔄 Pipeline Stages

### 1. Test Generation Stage

- Installs Assertly CLI
- Generates test cases from user stories
- Creates BDD scenarios
- Generates test data
- Analyzes test coverage

### 2. Artifact Publishing

- Publishes generated test cases
- Publishes test data
- Publishes BDD scenarios
- Publishes coverage reports

### 3. Notifications

- Sends Slack notifications (if configured)
- Updates work items with test generation results

## 🛠️ Usage

### Basic Pipeline

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  ASSERTLY_API_KEY: $(ASSERTLY_API_KEY)

stages:
- stage: TestGeneration
  displayName: 'Generate Tests with Assertly'
  jobs:
  - job: GenerateTests
    displayName: 'Generate Test Cases'
    steps:
    - task: PowerShell@2
      displayName: 'Generate Tests'
      inputs:
        targetType: 'inline'
        script: |
          npm install -g @assertly/cli
          assertly generate-tests --api-key $(ASSERTLY_API_KEY)
```

### Advanced Pipeline with Jira Integration

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  ASSERTLY_API_KEY: $(ASSERTLY_API_KEY)
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
      displayName: 'Generate Tests'
      inputs:
        targetType: 'inline'
        script: |
          npm install -g @assertly/cli
          assertly generate-tests \
            --api-key $(ASSERTLY_API_KEY) \
            --jira-url $(JIRA_URL) \
            --jira-token $(JIRA_TOKEN) \
            --project-key $(PROJECT_KEY)
```

## 📊 Generated Artifacts

The pipeline generates the following artifacts:

1. **Test Cases** (`assertly-generated-tests/`)
   - `test-cases.json` - Generated test cases
   - `test-cases.xml` - JUnit format for Azure DevOps

2. **Test Data** (`assertly-test-data/`)
   - `test-data.csv` - Generated test data sets
   - `test-data.json` - JSON format test data

3. **BDD Scenarios** (`assertly-bdd-scenarios/`)
   - `scenarios.feature` - Gherkin format scenarios
   - `scenarios.json` - JSON format scenarios

4. **Coverage Report** (`assertly-coverage-report/`)
   - `coverage.html` - HTML coverage report
   - `coverage.json` - JSON coverage data

## 🔧 Customization

### Custom Test Generation

You can customize the test generation by modifying the PowerShell script:

```powershell
# Generate specific test types
assertly generate-tests \
  --test-types functional,ui,api \
  --priority high,medium \
  --output-format jira
```

### Custom BDD Scenarios

```powershell
# Generate BDD scenarios with specific format
assertly generate-bdd-scenarios \
  --user-stories ./user-stories.json \
  --output-format gherkin \
  --include-examples
```

### Custom Test Data

```powershell
# Generate test data with specific parameters
assertly generate-test-data \
  --test-cases ./test-cases.json \
  --data-types valid,invalid,boundary \
  --output-format csv
```

## 🚨 Troubleshooting

### Common Issues

1. **Assertly CLI Installation Fails**
   - Ensure Node.js 18+ is installed
   - Check npm permissions
   - Verify network connectivity

2. **API Key Issues**
   - Verify API key is correct
   - Check API key permissions
   - Ensure API URL is accessible

3. **Jira Integration Issues**
   - Verify Jira URL and token
   - Check Jira permissions
   - Ensure project key exists

### Debug Mode

Enable debug mode for detailed logging:

```yaml
variables:
  ASSERTLY_DEBUG: true
```

## 📈 Best Practices

1. **Use Variables**: Store sensitive information in Azure DevOps variables
2. **Parallel Execution**: Run test generation in parallel with other tasks
3. **Artifact Retention**: Configure artifact retention policies
4. **Error Handling**: Implement proper error handling and notifications
5. **Security**: Use Azure DevOps service connections for external APIs

## 🔗 Related Documentation

- [Assertly API Documentation](/docs/api)
- [Azure DevOps Pipeline Documentation](https://docs.microsoft.com/en-us/azure/devops/pipelines/)
- [PowerShell Task Documentation](https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/utility/powershell)

## 📞 Support

For issues with this integration:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review Azure DevOps pipeline logs
3. Contact Assertly support
4. Create an issue in the repository

---

**Note**: This integration requires an active Assertly subscription and appropriate API permissions.