package com.assertly;

import com.intellij.openapi.components.Service;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import com.intellij.openapi.util.io.FileUtil;
import com.intellij.util.xmlb.XmlSerializerUtil;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Properties;
import java.util.concurrent.CompletableFuture;

/**
 * Enterprise AI Service for IntelliJ Plugin
 * Handles local AI integration and enterprise configuration
 */
@Service
public final class EnterpriseAIService {
    
    private final Project project;
    private EnterpriseConfig config;
    private HttpClient httpClient;
    
    public EnterpriseAIService(@NotNull Project project) {
        this.project = project;
        this.config = new EnterpriseConfig();
        this.httpClient = createHttpClient();
    }
    
    /**
     * Configure enterprise AI settings
     */
    public void configureEnterpriseAI() {
        EnterpriseConfigDialog dialog = new EnterpriseConfigDialog(project);
        if (dialog.showAndGet()) {
            EnterpriseConfig newConfig = dialog.getConfig();
            if (testConnection(newConfig)) {
                this.config = newConfig;
                saveConfiguration();
                Messages.showInfoMessage(project, "Enterprise AI configured successfully!", "Configuration Complete");
            } else {
                Messages.showErrorMessage(project, "Failed to connect to enterprise AI service. Please check your configuration.", "Connection Failed");
            }
        }
    }
    
    /**
     * Test connection to enterprise AI service
     */
    public boolean testConnection() {
        return testConnection(this.config);
    }
    
    private boolean testConnection(EnterpriseConfig config) {
        if (config.getLocalAiUrl() == null || config.getLocalAiUrl().isEmpty()) {
            return false;
        }
        
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(config.getLocalAiUrl() + "/health"))
                .timeout(Duration.ofSeconds(10))
                .GET()
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return response.statusCode() == 200;
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * Generate test cases using enterprise AI
     */
    public CompletableFuture<String> generateTestCases(String userStory) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String requestBody = buildTestGenerationRequest(userStory);
                
                HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(config.getLocalAiUrl() + "/generate"))
                    .timeout(Duration.ofSeconds(30))
                    .header("Content-Type", "application/json")
                    .header("Authorization", "Bearer " + config.getLocalApiKey())
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                    .build();
                
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                
                if (response.statusCode() == 200) {
                    return parseTestCasesResponse(response.body());
                } else {
                    throw new RuntimeException("AI service returned status: " + response.statusCode());
                }
            } catch (Exception e) {
                throw new RuntimeException("Failed to generate test cases: " + e.getMessage());
            }
        });
    }
    
    /**
     * Generate BDD scenarios using enterprise AI
     */
    public CompletableFuture<String> generateBDDScenarios(String userStory) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String requestBody = buildBDDGenerationRequest(userStory);
                
                HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(config.getLocalAiUrl() + "/bdd-generate"))
                    .timeout(Duration.ofSeconds(30))
                    .header("Content-Type", "application/json")
                    .header("Authorization", "Bearer " + config.getLocalApiKey())
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                    .build();
                
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                
                if (response.statusCode() == 200) {
                    return parseBDDScenariosResponse(response.body());
                } else {
                    throw new RuntimeException("AI service returned status: " + response.statusCode());
                }
            } catch (Exception e) {
                throw new RuntimeException("Failed to generate BDD scenarios: " + e.getMessage());
            }
        });
    }
    
    /**
     * Analyze test coverage using enterprise AI
     */
    public CompletableFuture<String> analyzeTestCoverage(String userStory, String existingTests) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String requestBody = buildCoverageAnalysisRequest(userStory, existingTests);
                
                HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(config.getLocalAiUrl() + "/analyze-coverage"))
                    .timeout(Duration.ofSeconds(30))
                    .header("Content-Type", "application/json")
                    .header("Authorization", "Bearer " + config.getLocalApiKey())
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                    .build();
                
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                
                if (response.statusCode() == 200) {
                    return parseCoverageAnalysisResponse(response.body());
                } else {
                    throw new RuntimeException("AI service returned status: " + response.statusCode());
                }
            } catch (Exception e) {
                throw new RuntimeException("Failed to analyze test coverage: " + e.getMessage());
            }
        });
    }
    
    /**
     * Check if enterprise mode is enabled
     */
    public boolean isEnterpriseModeEnabled() {
        return config.getLocalAiUrl() != null && !config.getLocalAiUrl().isEmpty();
    }
    
    /**
     * Get enterprise configuration
     */
    public EnterpriseConfig getConfig() {
        return config;
    }
    
    /**
     * Load configuration from properties file
     */
    private void loadConfiguration() {
        try {
            Properties props = new Properties();
            String configPath = project.getBasePath() + "/.assertly/enterprise.properties";
            
            if (FileUtil.exists(configPath)) {
                props.load(FileUtil.loadText(FileUtil.loadFile(configPath)));
                
                config.setLocalAiUrl(props.getProperty("ai.url"));
                config.setLocalAiModel(props.getProperty("ai.model", "local-copilot"));
                config.setLocalApiKey(props.getProperty("ai.key"));
                config.setProxyUrl(props.getProperty("proxy.url"));
                config.setCertPath(props.getProperty("cert.path"));
                config.setVerifySsl(Boolean.parseBoolean(props.getProperty("ssl.verify", "true")));
            }
        } catch (IOException e) {
            // Use default configuration
        }
    }
    
    /**
     * Save configuration to properties file
     */
    private void saveConfiguration() {
        try {
            Properties props = new Properties();
            props.setProperty("ai.url", config.getLocalAiUrl());
            props.setProperty("ai.model", config.getLocalAiModel());
            if (config.getLocalApiKey() != null) {
                props.setProperty("ai.key", config.getLocalApiKey());
            }
            if (config.getProxyUrl() != null) {
                props.setProperty("proxy.url", config.getProxyUrl());
            }
            if (config.getCertPath() != null) {
                props.setProperty("cert.path", config.getCertPath());
            }
            props.setProperty("ssl.verify", String.valueOf(config.isVerifySsl()));
            
            String configPath = project.getBasePath() + "/.assertly/enterprise.properties";
            FileUtil.createParentDirs(configPath);
            FileUtil.writeToFile(FileUtil.createFile(configPath), props.toString());
        } catch (IOException e) {
            Messages.showErrorMessage(project, "Failed to save enterprise configuration: " + e.getMessage(), "Save Error");
        }
    }
    
    /**
     * Create HTTP client with enterprise configuration
     */
    private HttpClient createHttpClient() {
        HttpClient.Builder builder = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .followRedirects(HttpClient.Redirect.NORMAL);
        
        // Configure proxy if specified
        if (config.getProxyUrl() != null && !config.getProxyUrl().isEmpty()) {
            // Configure proxy (implementation depends on proxy type)
            // This is a simplified example
        }
        
        // Configure SSL if certificate path is specified
        if (config.getCertPath() != null && !config.getCertPath().isEmpty()) {
            // Configure SSL context with custom certificate
            // This is a simplified example
        }
        
        return builder.build();
    }
    
    /**
     * Build test generation request
     */
    private String buildTestGenerationRequest(String userStory) {
        return String.format("""
            {
                "prompt": "Generate comprehensive test cases for the following user story:\\n\\nUser Story: %s\\n\\nPlease generate test cases that include:\\n1. Happy path scenarios\\n2. Edge cases\\n3. Error conditions\\n4. Boundary value testing\\n5. Negative test cases\\n\\nFormat the output as structured test cases with:\\n- Test Case Title\\n- Test Steps\\n- Expected Results\\n- Test Data Requirements\\n- Priority Level",
                "model": "%s",
                "max_tokens": 2000,
                "temperature": 0.7
            }
            """, userStory, config.getLocalAiModel());
    }
    
    /**
     * Build BDD generation request
     */
    private String buildBDDGenerationRequest(String userStory) {
        return String.format("""
            {
                "prompt": "Generate BDD scenarios in Gherkin format for the following user story:\\n\\nUser Story: %s\\n\\nPlease generate scenarios that include:\\n1. Happy path scenarios\\n2. Alternative flows\\n3. Error scenarios\\n4. Edge cases\\n\\nFormat the output as proper Gherkin scenarios with:\\n- Feature description\\n- Background (if applicable)\\n- Scenario outlines\\n- Given-When-Then steps\\n- Examples tables",
                "model": "%s",
                "max_tokens": 1500,
                "temperature": 0.6
            }
            """, userStory, config.getLocalAiModel());
    }
    
    /**
     * Build coverage analysis request
     */
    private String buildCoverageAnalysisRequest(String userStory, String existingTests) {
        return String.format("""
            {
                "prompt": "Analyze test coverage for the following user story and existing tests:\\n\\nUser Story: %s\\n\\nExisting Tests:\\n%s\\n\\nPlease provide analysis that includes:\\n1. Coverage gaps identified\\n2. Missing test scenarios\\n3. Additional test cases needed\\n4. Coverage percentage estimate\\n5. Recommendations for improvement",
                "model": "%s",
                "max_tokens": 1200,
                "temperature": 0.5
            }
            """, userStory, existingTests, config.getLocalAiModel());
    }
    
    /**
     * Parse test cases response
     */
    private String parseTestCasesResponse(String response) {
        // Parse JSON response and format for display
        // This is a simplified implementation
        return response;
    }
    
    /**
     * Parse BDD scenarios response
     */
    private String parseBDDScenariosResponse(String response) {
        // Parse JSON response and format for display
        // This is a simplified implementation
        return response;
    }
    
    /**
     * Parse coverage analysis response
     */
    private String parseCoverageAnalysisResponse(String response) {
        // Parse JSON response and format for display
        // This is a simplified implementation
        return response;
    }
}