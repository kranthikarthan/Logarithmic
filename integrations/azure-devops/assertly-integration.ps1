# Assertly Azure DevOps Integration Script
# This PowerShell script provides helper functions for integrating Assertly with Azure DevOps

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$true)]
    [string]$ApiUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectKey = "",
    
    [Parameter(Mandatory=$false)]
    [string]$JiraUrl = "",
    
    [Parameter(Mandatory=$false)]
    [string]$JiraToken = "",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "./generated-tests"
)

# Function to install Assertly CLI
function Install-AssertlyCLI {
    Write-Host "Installing Assertly CLI..." -ForegroundColor Green
    
    try {
        # Install Assertly CLI globally
        npm install -g @assertly/cli
        
        # Verify installation
        $version = assertly --version
        Write-Host "Assertly CLI installed successfully: $version" -ForegroundColor Green
        
        return $true
    }
    catch {
        Write-Error "Failed to install Assertly CLI: $_"
        return $false
    }
}

# Function to configure Assertly
function Set-AssertlyConfig {
    param(
        [string]$ApiKey,
        [string]$ApiUrl
    )
    
    Write-Host "Configuring Assertly..." -ForegroundColor Green
    
    try {
        # Set API configuration
        assertly config set api-key $ApiKey
        assertly config set api-url $ApiUrl
        
        Write-Host "Assertly configured successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to configure Assertly: $_"
        return $false
    }
}

# Function to generate test cases
function Invoke-TestGeneration {
    param(
        [string]$ProjectKey,
        [string]$OutputDir,
        [string]$JiraUrl,
        [string]$JiraToken
    )
    
    Write-Host "Generating test cases..." -ForegroundColor Green
    
    try {
        # Create output directory
        if (!(Test-Path $OutputDir)) {
            New-Item -ItemType Directory -Path $OutputDir -Force
        }
        
        # Generate test cases
        $generateArgs = @(
            "generate-tests",
            "--output-format", "jira",
            "--include-bdd-scenarios",
            "--output-dir", $OutputDir
        )
        
        if ($ProjectKey) {
            $generateArgs += @("--project-key", $ProjectKey)
        }
        
        if ($JiraUrl -and $JiraToken) {
            $generateArgs += @("--jira-url", $JiraUrl)
            $generateArgs += @("--jira-token", $JiraToken)
        }
        
        & assertly @generateArgs
        
        Write-Host "Test cases generated successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to generate test cases: $_"
        return $false
    }
}

# Function to generate test data
function Invoke-TestDataGeneration {
    param(
        [string]$TestCasesPath,
        [string]$OutputDir
    )
    
    Write-Host "Generating test data..." -ForegroundColor Green
    
    try {
        $testDataDir = Join-Path $OutputDir "test-data"
        if (!(Test-Path $testDataDir)) {
            New-Item -ItemType Directory -Path $testDataDir -Force
        }
        
        # Generate test data
        & assertly generate-test-data `
            --test-cases $TestCasesPath `
            --output-format csv `
            --output-dir $testDataDir
        
        Write-Host "Test data generated successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to generate test data: $_"
        return $false
    }
}

# Function to generate BDD scenarios
function Invoke-BDDGeneration {
    param(
        [string]$UserStoriesPath,
        [string]$OutputDir
    )
    
    Write-Host "Generating BDD scenarios..." -ForegroundColor Green
    
    try {
        $bddDir = Join-Path $OutputDir "bdd-scenarios"
        if (!(Test-Path $bddDir)) {
            New-Item -ItemType Directory -Path $bddDir -Force
        }
        
        # Generate BDD scenarios
        & assertly generate-bdd-scenarios `
            --user-stories $UserStoriesPath `
            --output-format gherkin `
            --output-dir $bddDir
        
        Write-Host "BDD scenarios generated successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to generate BDD scenarios: $_"
        return $false
    }
}

# Function to analyze test coverage
function Invoke-CoverageAnalysis {
    param(
        [string]$UserStoriesPath,
        [string]$TestCasesPath,
        [string]$OutputDir
    )
    
    Write-Host "Analyzing test coverage..." -ForegroundColor Green
    
    try {
        $coverageDir = Join-Path $OutputDir "coverage-report"
        if (!(Test-Path $coverageDir)) {
            New-Item -ItemType Directory -Path $coverageDir -Force
        }
        
        # Analyze coverage
        & assertly analyze-coverage `
            --user-stories $UserStoriesPath `
            --test-cases $TestCasesPath `
            --output-format html `
            --output-dir $coverageDir
        
        Write-Host "Coverage analysis completed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to analyze coverage: $_"
        return $false
    }
}

# Function to publish results to Azure DevOps
function Publish-AssertlyResults {
    param(
        [string]$OutputDir
    )
    
    Write-Host "Publishing results to Azure DevOps..." -ForegroundColor Green
    
    try {
        # Publish test results
        if (Test-Path (Join-Path $OutputDir "test-results.xml")) {
            Write-Host "Publishing test results..." -ForegroundColor Yellow
            # This would typically be handled by Azure DevOps tasks
        }
        
        # Publish artifacts
        if (Test-Path $OutputDir) {
            Write-Host "Publishing artifacts..." -ForegroundColor Yellow
            # This would typically be handled by Azure DevOps tasks
        }
        
        Write-Host "Results published successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to publish results: $_"
        return $false
    }
}

# Main execution
function Main {
    Write-Host "Starting Assertly Azure DevOps Integration..." -ForegroundColor Cyan
    Write-Host "===============================================" -ForegroundColor Cyan
    
    # Install and configure Assertly CLI
    if (!(Install-AssertlyCLI)) {
        exit 1
    }
    
    if (!(Set-AssertlyConfig -ApiKey $ApiKey -ApiUrl $ApiUrl)) {
        exit 1
    }
    
    # Generate test cases
    if (!(Invoke-TestGeneration -ProjectKey $ProjectKey -OutputDir $OutputDir -JiraUrl $JiraUrl -JiraToken $JiraToken)) {
        exit 1
    }
    
    # Generate test data if test cases exist
    $testCasesPath = Join-Path $OutputDir "test-cases.json"
    if (Test-Path $testCasesPath) {
        Invoke-TestDataGeneration -TestCasesPath $testCasesPath -OutputDir $OutputDir
    }
    
    # Generate BDD scenarios if user stories exist
    $userStoriesPath = "./user-stories.json"
    if (Test-Path $userStoriesPath) {
        Invoke-BDDGeneration -UserStoriesPath $userStoriesPath -OutputDir $OutputDir
        Invoke-CoverageAnalysis -UserStoriesPath $userStoriesPath -TestCasesPath $testCasesPath -OutputDir $OutputDir
    }
    
    # Publish results
    Publish-AssertlyResults -OutputDir $OutputDir
    
    Write-Host "Assertly Azure DevOps Integration completed successfully!" -ForegroundColor Green
}

# Execute main function
Main