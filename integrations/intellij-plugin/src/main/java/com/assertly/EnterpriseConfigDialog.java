package com.assertly;

import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.DialogWrapper;
import com.intellij.ui.components.JBLabel;
import com.intellij.ui.components.JBTextField;
import com.intellij.util.ui.FormBuilder;
import org.jetbrains.annotations.Nullable;

import javax.swing.*;
import java.awt.*;

/**
 * Enterprise Configuration Dialog for IntelliJ Plugin
 */
public class EnterpriseConfigDialog extends DialogWrapper {
    
    private final Project project;
    private JBTextField localAiUrlField;
    private JComboBox<String> localAiModelCombo;
    private JBTextField localApiKeyField;
    private JBTextField proxyUrlField;
    private JBTextField certPathField;
    private JCheckBox verifySslCheckbox;
    private JCheckBox offlineModeCheckbox;
    private JCheckBox customModelsCheckbox;
    
    public EnterpriseConfigDialog(@NotNull Project project) {
        super(project);
        this.project = project;
        setTitle("Configure Enterprise AI");
        setResizable(true);
        init();
    }
    
    @Override
    protected @Nullable JComponent createCenterPanel() {
        // Create form components
        localAiUrlField = new JBTextField();
        localAiUrlField.setPreferredSize(new Dimension(400, 30));
        localAiUrlField.setToolTipText("URL of your internal AI service (e.g., http://internal-ai.company.com:8080/api)");
        
        localAiModelCombo = new JComboBox<>(new String[]{
            "local-copilot", "internal-llm", "custom-model", "offline-model"
        });
        localAiModelCombo.setPreferredSize(new Dimension(200, 30));
        
        localApiKeyField = new JBTextField();
        localApiKeyField.setPreferredSize(new Dimension(400, 30));
        localApiKeyField.setToolTipText("Internal API key if required");
        
        proxyUrlField = new JBTextField();
        proxyUrlField.setPreferredSize(new Dimension(400, 30));
        proxyUrlField.setToolTipText("Corporate proxy URL (e.g., http://proxy.company.com:8080)");
        
        certPathField = new JBTextField();
        certPathField.setPreferredSize(new Dimension(400, 30));
        certPathField.setToolTipText("Path to corporate SSL certificate");
        
        verifySslCheckbox = new JCheckBox("Verify SSL Certificates", true);
        offlineModeCheckbox = new JCheckBox("Enable Offline Mode");
        offlineModeCheckbox.setToolTipText("Work without internet connection using cached responses");
        
        customModelsCheckbox = new JCheckBox("Enable Custom Models");
        customModelsCheckbox.setToolTipText("Allow custom AI model configurations");
        
        // Create form layout
        FormBuilder formBuilder = FormBuilder.createFormBuilder()
            .addLabeledComponent(new JBLabel("Local AI Service URL *:"), localAiUrlField)
            .addLabeledComponent(new JBLabel("AI Model:"), localAiModelCombo)
            .addLabeledComponent(new JBLabel("API Key (Optional):"), localApiKeyField)
            .addSeparator()
            .addLabeledComponent(new JBLabel("Proxy URL (Optional):"), proxyUrlField)
            .addLabeledComponent(new JBLabel("Certificate Path (Optional):"), certPathField)
            .addComponent(verifySslCheckbox)
            .addSeparator()
            .addComponent(offlineModeCheckbox)
            .addComponent(customModelsCheckbox);
        
        // Add help text
        JPanel helpPanel = new JPanel(new BorderLayout());
        JTextArea helpText = new JTextArea(
            "Enterprise AI Configuration\n\n" +
            "Configure your local AI service for secure, on-premise test generation.\n" +
            "All AI processing will stay within your corporate network.\n\n" +
            "Required: Local AI Service URL\n" +
            "Optional: API Key, Proxy, SSL Certificate"
        );
        helpText.setEditable(false);
        helpText.setBackground(getContentPanel().getBackground());
        helpText.setFont(helpText.getFont().deriveFont(Font.ITALIC, 12f));
        helpPanel.add(helpText, BorderLayout.CENTER);
        
        // Create main panel
        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.add(formBuilder.getPanel(), BorderLayout.CENTER);
        mainPanel.add(helpPanel, BorderLayout.SOUTH);
        
        return mainPanel;
    }
    
    @Override
    protected void doOKAction() {
        // Validate required fields
        if (localAiUrlField.getText().trim().isEmpty()) {
            JOptionPane.showMessageDialog(
                getContentPanel(),
                "Local AI Service URL is required.",
                "Validation Error",
                JOptionPane.ERROR_MESSAGE
            );
            return;
        }
        
        // Validate URL format
        String url = localAiUrlField.getText().trim();
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            JOptionPane.showMessageDialog(
                getContentPanel(),
                "URL must start with http:// or https://",
                "Validation Error",
                JOptionPane.ERROR_MESSAGE
            );
            return;
        }
        
        super.doOKAction();
    }
    
    /**
     * Get the configured enterprise settings
     */
    public EnterpriseConfig getConfig() {
        EnterpriseConfig config = new EnterpriseConfig();
        config.setLocalAiUrl(localAiUrlField.getText().trim());
        config.setLocalAiModel((String) localAiModelCombo.getSelectedItem());
        config.setLocalApiKey(localApiKeyField.getText().trim());
        config.setProxyUrl(proxyUrlField.getText().trim());
        config.setCertPath(certPathField.getText().trim());
        config.setVerifySsl(verifySslCheckbox.isSelected());
        config.setOfflineMode(offlineModeCheckbox.isSelected());
        config.setCustomModels(customModelsCheckbox.isSelected());
        return config;
    }
    
    /**
     * Set initial configuration values
     */
    public void setConfig(EnterpriseConfig config) {
        if (config != null) {
            localAiUrlField.setText(config.getLocalAiUrl() != null ? config.getLocalAiUrl() : "");
            localAiModelCombo.setSelectedItem(config.getLocalAiModel() != null ? config.getLocalAiModel() : "local-copilot");
            localApiKeyField.setText(config.getLocalApiKey() != null ? config.getLocalApiKey() : "");
            proxyUrlField.setText(config.getProxyUrl() != null ? config.getProxyUrl() : "");
            certPathField.setText(config.getCertPath() != null ? config.getCertPath() : "");
            verifySslCheckbox.setSelected(config.isVerifySsl());
            offlineModeCheckbox.setSelected(config.isOfflineMode());
            customModelsCheckbox.setSelected(config.isCustomModels());
        }
    }
}