package com.assertly;

import org.jetbrains.annotations.Nullable;

/**
 * Enterprise Configuration Data Class
 */
public class EnterpriseConfig {
    
    private String localAiUrl;
    private String localAiModel = "local-copilot";
    private String localApiKey;
    private String proxyUrl;
    private String certPath;
    private boolean verifySsl = true;
    private boolean offlineMode = false;
    private boolean customModels = false;
    private boolean externalIntegrations = false;
    
    // AI Configuration
    @Nullable
    public String getLocalAiUrl() {
        return localAiUrl;
    }
    
    public void setLocalAiUrl(@Nullable String localAiUrl) {
        this.localAiUrl = localAiUrl;
    }
    
    @Nullable
    public String getLocalAiModel() {
        return localAiModel;
    }
    
    public void setLocalAiModel(@Nullable String localAiModel) {
        this.localAiModel = localAiModel;
    }
    
    @Nullable
    public String getLocalApiKey() {
        return localApiKey;
    }
    
    public void setLocalApiKey(@Nullable String localApiKey) {
        this.localApiKey = localApiKey;
    }
    
    // Network Configuration
    @Nullable
    public String getProxyUrl() {
        return proxyUrl;
    }
    
    public void setProxyUrl(@Nullable String proxyUrl) {
        this.proxyUrl = proxyUrl;
    }
    
    @Nullable
    public String getCertPath() {
        return certPath;
    }
    
    public void setCertPath(@Nullable String certPath) {
        this.certPath = certPath;
    }
    
    public boolean isVerifySsl() {
        return verifySsl;
    }
    
    public void setVerifySsl(boolean verifySsl) {
        this.verifySsl = verifySsl;
    }
    
    // Feature Flags
    public boolean isOfflineMode() {
        return offlineMode;
    }
    
    public void setOfflineMode(boolean offlineMode) {
        this.offlineMode = offlineMode;
    }
    
    public boolean isCustomModels() {
        return customModels;
    }
    
    public void setCustomModels(boolean customModels) {
        this.customModels = customModels;
    }
    
    public boolean isExternalIntegrations() {
        return externalIntegrations;
    }
    
    public void setExternalIntegrations(boolean externalIntegrations) {
        this.externalIntegrations = externalIntegrations;
    }
    
    /**
     * Check if enterprise mode is properly configured
     */
    public boolean isConfigured() {
        return localAiUrl != null && !localAiUrl.trim().isEmpty();
    }
    
    /**
     * Get configuration summary for display
     */
    public String getSummary() {
        StringBuilder summary = new StringBuilder();
        summary.append("Enterprise AI Configuration:\n");
        summary.append("• AI Service: ").append(localAiUrl != null ? localAiUrl : "Not configured").append("\n");
        summary.append("• Model: ").append(localAiModel).append("\n");
        summary.append("• Offline Mode: ").append(offlineMode ? "Enabled" : "Disabled").append("\n");
        summary.append("• Custom Models: ").append(customModels ? "Enabled" : "Disabled").append("\n");
        
        if (proxyUrl != null && !proxyUrl.isEmpty()) {
            summary.append("• Proxy: ").append(proxyUrl).append("\n");
        }
        
        if (certPath != null && !certPath.isEmpty()) {
            summary.append("• Certificate: ").append(certPath).append("\n");
        }
        
        return summary.toString();
    }
    
    @Override
    public String toString() {
        return "EnterpriseConfig{" +
                "localAiUrl='" + localAiUrl + '\'' +
                ", localAiModel='" + localAiModel + '\'' +
                ", offlineMode=" + offlineMode +
                ", customModels=" + customModels +
                '}';
    }
}