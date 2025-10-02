# Assertly Enterprise User Guide

## 🏢 **Complete User Guide for Assertly Enterprise**

This guide provides comprehensive instructions for using Assertly's enterprise features, AI-powered test generation, and advanced capabilities.

## 🚀 **Getting Started**

### **Accessing Assertly**
1. **Open your browser** and navigate to your Assertly instance
2. **Login** with your enterprise credentials
3. **Explore the dashboard** to understand the interface

### **First-Time Setup**
1. **Configure AI Providers** (see AI Configuration section)
2. **Set up Jira Integration** (optional)
3. **Configure Enterprise Settings** (see Enterprise Configuration section)
4. **Create your first test project**

## 🤖 **AI-Powered Test Generation**

### **Generating Test Cases from User Stories**

#### **Step 1: Navigate to AI Test Generator**
1. Click on **"AI Test Generator"** in the main menu
2. You'll see the AI test generation interface

#### **Step 2: Enter User Story Information**
```json
{
  "title": "User Authentication",
  "description": "As a user, I want to login to the system so that I can access my account",
  "acceptance_criteria": [
    "User can login with valid credentials",
    "User cannot login with invalid credentials",
    "User receives appropriate error messages"
  ],
  "business_value": "Secure access to user accounts",
  "user_persona": "End user"
}
```

#### **Step 3: Configure AI Settings**
- **AI Provider**: Choose from OpenAI, Anthropic, Google AI, Local LLM
- **Model**: Select the AI model (e.g., GPT-4, Claude-3, Gemini Pro)
- **Test Types**: Select functional, integration, performance, security
- **Number of Cases**: Specify how many test cases to generate
- **Additional Prompts**: Add specific requirements or constraints

#### **Step 4: Generate Test Cases**
1. Click **"Generate Test Cases"**
2. Wait for AI processing (usually 10-30 seconds)
3. Review the generated test cases
4. **Edit** any test cases as needed
5. **Save** the test cases to your project

### **Improving Existing Test Cases**

#### **Step 1: Select Test Case to Improve**
1. Navigate to your test case
2. Click **"Improve with AI"**
3. Enter improvement prompts:
   - "Add security testing scenarios"
   - "Include edge cases and boundary testing"
   - "Add performance testing considerations"
   - "Include accessibility testing"

#### **Step 2: Review Improvements**
1. Review the AI-suggested improvements
2. **Accept** changes that make sense
3. **Reject** changes that don't fit your needs
4. **Edit** the improved test case further if needed

## 🔑 **API Key Management**

### **Adding AI Provider API Keys**

#### **Step 1: Navigate to API Keys**
1. Click on **"API Keys"** in the settings menu
2. You'll see the API key management interface

#### **Step 2: Add New API Key**
1. Click **"Add API Key"**
2. Select your AI provider:
   - **OpenAI**: Enter your OpenAI API key
   - **Anthropic**: Enter your Anthropic API key
   - **Google AI**: Enter your Google AI API key
   - **Azure OpenAI**: Enter your Azure endpoint and key
   - **Hugging Face**: Enter your Hugging Face API key
   - **Local LLM**: Enter your local LLM endpoint

#### **Step 3: Configure Settings**
```json
{
  "provider": "openai",
  "apiKey": "sk-your-openai-key",
  "model": "gpt-4",
  "maxTokens": 4000,
  "temperature": 0.7,
  "timeout": 30,
  "retryAttempts": 3,
  "monthlyLimit": 10000,
  "costPerToken": 0.00003
}
```

#### **Step 4: Test Connection**
1. Click **"Test Connection"**
2. Verify the connection is successful
3. **Save** the API key configuration

## 🏢 **Enterprise Configuration**

### **Enterprise AI Setup**

#### **Step 1: Navigate to Enterprise Settings**
1. Click on **"Enterprise Settings"** in the admin menu
2. Select **"AI Configuration"**

#### **Step 2: Configure Local AI**
```json
{
  "local_ai_url": "http://localhost:11434",
  "local_ai_model": "llama2",
  "offline_mode": true,
  "custom_models": true,
  "audit_enabled": true,
  "data_encryption": true
}
```

#### **Step 3: Test Enterprise AI**
1. Click **"Test Connection"**
2. Verify local AI is working
3. **Save** the configuration

## 🔗 **Jira Integration**

### **Setting Up Jira Connection**

#### **Step 1: Get Jira Credentials**
1. **Jira URL**: Your Jira instance URL
2. **Username**: Your Jira username or email
3. **API Token**: Generate from Jira account settings

#### **Step 2: Configure Integration**
1. Navigate to **"Integrations"** → **"Jira"**
2. Enter your Jira credentials:
   ```
   Jira URL: https://your-company.atlassian.net
   Username: your-email@company.com
   API Token: your-jira-api-token
   ```

#### **Step 3: Test Connection**
1. Click **"Test Connection"**
2. Verify you can access Jira projects
3. **Save** the configuration

## 📊 **Monitoring and Analytics**

### **Dashboard Overview**

#### **Key Metrics**
- **Test Coverage**: Percentage of requirements covered
- **Test Execution**: Pass/fail rates
- **AI Usage**: API calls and costs
- **User Activity**: User engagement metrics

#### **Performance Metrics**
- **Response Time**: Average API response time
- **Throughput**: Requests per minute
- **Error Rate**: Percentage of failed requests
- **Uptime**: System availability

## 🧪 **Test Management**

### **Creating Test Projects**

#### **Step 1: Create New Project**
1. Click **"New Project"**
2. Enter project details:
   - **Project Name**: Descriptive project name
   - **Description**: Project description
   - **Team Members**: Add team members
   - **Jira Integration**: Link to Jira project (optional)

#### **Step 2: Configure Project Settings**
```json
{
  "name": "E-commerce Platform Testing",
  "description": "Comprehensive testing for e-commerce platform",
  "team_members": ["john.doe@company.com", "jane.smith@company.com"],
  "jira_project": "ECOMM",
  "test_types": ["functional", "integration", "performance"],
  "ai_provider": "openai"
}
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **AI Generation Fails**
1. **Check API Keys**: Verify API keys are valid
2. **Check Network**: Ensure internet connectivity
3. **Check Limits**: Verify API usage limits
4. **Try Fallback**: Use local LLM as fallback

#### **Jira Integration Issues**
1. **Check Credentials**: Verify Jira credentials
2. **Check Permissions**: Ensure proper Jira permissions
3. **Check Network**: Verify Jira instance accessibility
4. **Check Configuration**: Review integration settings

### **Getting Help**

#### **Documentation**
- **[README.md](../../README.md)** - Main documentation
- **[API Documentation](../api/enterprise-api.md)** - Complete API reference
- **[Deployment Guide](../../DEPLOYMENT_GUIDE_LATEST.md)** - Deployment instructions

---

**Made with ❤️ by the Assertly Team**