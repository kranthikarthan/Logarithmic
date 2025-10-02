import * as vscode from 'vscode';
import axios from 'axios';

interface AssertlyConfig {
    apiUrl: string;
    apiKey?: string;
    jiraUrl?: string;
    jiraUsername?: string;
    jiraApiToken?: string;
    aiProvider: 'openai' | 'anthropic' | 'local';
    aiApiKey?: string;
    enterpriseMode?: boolean;
    enterpriseAiUrl?: string;
    enterpriseAiModel?: string;
    enterpriseApiKey?: string;
    proxyUrl?: string;
    certPath?: string;
    verifySsl?: boolean;
}

interface TestCase {
    title: string;
    description: string;
    steps: string[];
    expected_result: string;
    test_type: string;
    priority: string;
    tags: string[];
    preconditions: string[];
    test_data: Record<string, any>;
    acceptance_criteria: string[];
}

interface UserStory {
    title: string;
    description: string;
    acceptance_criteria: string[];
    business_value: string;
    user_persona: string;
    epic?: string;
    story_points?: number;
}

export function activate(context: vscode.ExtensionContext) {
    console.log('Assertly Test Manager extension is now active!');

    // Register commands
    const generateTestCasesCommand = vscode.commands.registerCommand('assertly.generateTestCases', async () => {
        await generateTestCases();
    });

    const openDashboardCommand = vscode.commands.registerCommand('assertly.openDashboard', async () => {
        await openDashboard();
    });

    const syncWithJiraCommand = vscode.commands.registerCommand('assertly.syncWithJira', async () => {
        await syncWithJira();
    });

    const createBDDScenarioCommand = vscode.commands.registerCommand('assertly.createBDDScenario', async () => {
        await createBDDScenario();
    });

    const analyzeCoverageCommand = vscode.commands.registerCommand('assertly.analyzeCoverage', async () => {
        await analyzeCoverage();
    });

    const configureEnterpriseCommand = vscode.commands.registerCommand('assertly.configureEnterprise', async () => {
        await configureEnterprise();
    });

    const testEnterpriseConnectionCommand = vscode.commands.registerCommand('assertly.testEnterpriseConnection', async () => {
        await testEnterpriseConnection();
    });

    const openEnterpriseSettingsCommand = vscode.commands.registerCommand('assertly.openEnterpriseSettings', async () => {
        await openEnterpriseSettings();
    });

    // Register test explorer provider
    const testExplorerProvider = new AssertlyTestExplorerProvider();
    vscode.window.registerTreeDataProvider('assertlyTestExplorer', testExplorerProvider);

    // Register webview provider for dashboard
    const dashboardProvider = new AssertlyDashboardProvider(context.extensionUri);
    vscode.window.registerWebviewViewProvider('assertlyDashboard', dashboardProvider);

    // Register file watchers
    const fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.feature');
    fileWatcher.onDidChange(async (uri) => {
        await handleFeatureFileChange(uri);
    });

    // Register document change handlers
    vscode.workspace.onDidChangeTextDocument(async (event) => {
        await handleDocumentChange(event);
    });

    // Add commands to context
    context.subscriptions.push(
        generateTestCasesCommand,
        openDashboardCommand,
        syncWithJiraCommand,
        createBDDScenarioCommand,
        analyzeCoverageCommand,
        configureEnterpriseCommand,
        testEnterpriseConnectionCommand,
        openEnterpriseSettingsCommand,
        fileWatcher
    );

    // Initialize configuration
    initializeConfiguration();
}

async function generateTestCases() {
    try {
        const config = getConfiguration();
        if (!config.apiUrl) {
            vscode.window.showErrorMessage('Assertly API URL not configured. Please set assertly.apiUrl in settings.');
            return;
        }

        // Get user story from active editor or prompt
        const userStory = await getUserStory();
        if (!userStory) {
            return;
        }

        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Generating test cases...",
            cancellable: true
        }, async (progress, token) => {
            try {
                // Choose API endpoint based on enterprise mode
                const endpoint = config.enterpriseMode ? '/api/enterprise/ai/generate-test-cases' : '/api/ai/generate-test-cases';
                
                const response = await axios.post(`${config.apiUrl}${endpoint}`, {
                    ...userStory,
                    test_types: ['functional', 'ui', 'api'],
                    num_cases: 5,
                    additional_prompts: []
                }, {
                    headers: {
                        'Authorization': `Bearer ${config.apiKey}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 30000
                });

                if (response.data.success) {
                    const testCases = response.data.test_cases;
                    await displayTestCases(testCases);
                } else {
                    vscode.window.showErrorMessage(`Failed to generate test cases: ${response.data.error}`);
                }
            } catch (error: any) {
                vscode.window.showErrorMessage(`Error generating test cases: ${error.message}`);
            }
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function createBDDScenario() {
    try {
        const config = getConfiguration();
        if (!config.apiUrl) {
            vscode.window.showErrorMessage('Assertly API URL not configured.');
            return;
        }

        const userStory = await getUserStory();
        if (!userStory) {
            return;
        }

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Generating BDD scenarios...",
            cancellable: true
        }, async (progress, token) => {
            try {
                const response = await axios.post(`${config.apiUrl}/api/ai/generate-bdd-scenarios`, {
                    ...userStory,
                    additional_context: 'Generate comprehensive BDD scenarios'
                }, {
                    headers: {
                        'Authorization': `Bearer ${config.apiKey}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.data.success) {
                    const scenarios = response.data.scenarios;
                    await displayBDDScenarios(scenarios);
                } else {
                    vscode.window.showErrorMessage(`Failed to generate BDD scenarios: ${response.data.error}`);
                }
            } catch (error: any) {
                vscode.window.showErrorMessage(`Error generating BDD scenarios: ${error.message}`);
            }
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function analyzeCoverage() {
    try {
        const config = getConfiguration();
        if (!config.apiUrl) {
            vscode.window.showErrorMessage('Assertly API URL not configured.');
            return;
        }

        // Get user story
        const userStory = await getUserStory();
        if (!userStory) {
            return;
        }

        // Get existing test cases from workspace
        const existingTestCases = await getExistingTestCases();

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing test coverage...",
            cancellable: true
        }, async (progress, token) => {
            try {
                const response = await axios.post(`${config.apiUrl}/api/ai/analyze-coverage`, {
                    user_story: userStory,
                    existing_test_cases: existingTestCases
                }, {
                    headers: {
                        'Authorization': `Bearer ${config.apiKey}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.data.success) {
                    const analysis = response.data.analysis;
                    await displayCoverageAnalysis(analysis);
                } else {
                    vscode.window.showErrorMessage(`Failed to analyze coverage: ${response.data.error}`);
                }
            } catch (error: any) {
                vscode.window.showErrorMessage(`Error analyzing coverage: ${error.message}`);
            }
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function openDashboard() {
    const config = getConfiguration();
    if (!config.apiUrl) {
        vscode.window.showErrorMessage('Assertly API URL not configured.');
        return;
    }

    // Open dashboard in external browser
    const dashboardUrl = `${config.apiUrl}/dashboard`;
    vscode.env.openExternal(vscode.Uri.parse(dashboardUrl));
}

async function syncWithJira() {
    try {
        const config = getConfiguration();
        if (!config.jiraUrl || !config.jiraUsername || !config.jiraApiToken) {
            vscode.window.showErrorMessage('Jira configuration incomplete. Please configure Jira settings.');
            return;
        }

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Syncing with Jira...",
            cancellable: true
        }, async (progress, token) => {
            try {
                const response = await axios.post(`${config.apiUrl}/api/jira/sync`, {
                    jira_url: config.jiraUrl,
                    jira_username: config.jiraUsername,
                    jira_api_token: config.jiraApiToken
                }, {
                    headers: {
                        'Authorization': `Bearer ${config.apiKey}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.data.success) {
                    vscode.window.showInformationMessage('Successfully synced with Jira!');
                } else {
                    vscode.window.showErrorMessage(`Failed to sync with Jira: ${response.data.error}`);
                }
            } catch (error: any) {
                vscode.window.showErrorMessage(`Error syncing with Jira: ${error.message}`);
            }
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function getUserStory(): Promise<UserStory | null> {
    const activeEditor = vscode.window.activeTextEditor;
    if (activeEditor) {
        const document = activeEditor.document;
        const text = document.getText();
        
        // Try to extract user story from current document
        const userStoryMatch = text.match(/As a (.+), I want (.+) so that (.+)/i);
        if (userStoryMatch) {
            return {
                title: extractTitle(text),
                description: userStoryMatch[0],
                acceptance_criteria: extractAcceptanceCriteria(text),
                business_value: userStoryMatch[3],
                user_persona: userStoryMatch[1],
                epic: extractEpic(text)
            };
        }
    }

    // Prompt user for user story
    const title = await vscode.window.showInputBox({
        prompt: 'Enter user story title',
        placeHolder: 'e.g., User Login'
    });
    if (!title) return null;

    const description = await vscode.window.showInputBox({
        prompt: 'Enter user story description',
        placeHolder: 'As a user, I want to log into the system so that I can access my account'
    });
    if (!description) return null;

    const businessValue = await vscode.window.showInputBox({
        prompt: 'Enter business value',
        placeHolder: 'Enables secure access to user accounts'
    });
    if (!businessValue) return null;

    const userPersona = await vscode.window.showInputBox({
        prompt: 'Enter user persona',
        placeHolder: 'Registered user'
    });
    if (!userPersona) return null;

    return {
        title,
        description,
        acceptance_criteria: [],
        business_value: businessValue,
        user_persona: userPersona
    };
}

function extractTitle(text: string): string {
    const lines = text.split('\n');
    for (const line of lines) {
        if (line.trim().startsWith('#') || line.trim().startsWith('##')) {
            return line.replace(/^#+\s*/, '').trim();
        }
    }
    return 'User Story';
}

function extractAcceptanceCriteria(text: string): string[] {
    const criteria: string[] = [];
    const lines = text.split('\n');
    
    for (const line of lines) {
        if (line.trim().startsWith('-') || line.trim().startsWith('*')) {
            criteria.push(line.trim().substring(1).trim());
        }
    }
    
    return criteria;
}

function extractEpic(text: string): string | undefined {
    const epicMatch = text.match(/Epic:\s*(.+)/i);
    return epicMatch ? epicMatch[1].trim() : undefined;
}

async function getExistingTestCases(): Promise<any[]> {
    // Scan workspace for test files and extract test cases
    const testFiles = await vscode.workspace.findFiles('**/*.test.js', '**/node_modules/**');
    const testCases: any[] = [];
    
    for (const file of testFiles) {
        const document = await vscode.workspace.openTextDocument(file);
        const text = document.getText();
        
        // Extract test case titles (basic implementation)
        const testMatches = text.match(/it\(['"`](.+?)['"`]/g);
        if (testMatches) {
            for (const match of testMatches) {
                const title = match.replace(/it\(['"`]/, '').replace(/['"`].*/, '');
                testCases.push({ title });
            }
        }
    }
    
    return testCases;
}

async function displayTestCases(testCases: TestCase[]) {
    const panel = vscode.window.createWebviewPanel(
        'assertlyTestCases',
        'Generated Test Cases',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    const html = generateTestCasesHTML(testCases);
    panel.webview.html = html;

    // Handle messages from webview
    panel.webview.onDidReceiveMessage(
        async (message) => {
            switch (message.command) {
                case 'insertTestCase':
                    await insertTestCase(message.testCase);
                    break;
                case 'exportTestCases':
                    await exportTestCases(testCases);
                    break;
            }
        },
        undefined,
        []
    );
}

async function displayBDDScenarios(scenarios: any[]) {
    const panel = vscode.window.createWebviewPanel(
        'assertlyBDDScenarios',
        'Generated BDD Scenarios',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    const html = generateBDDScenariosHTML(scenarios);
    panel.webview.html = html;
}

async function displayCoverageAnalysis(analysis: any) {
    const panel = vscode.window.createWebviewPanel(
        'assertlyCoverageAnalysis',
        'Test Coverage Analysis',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    const html = generateCoverageAnalysisHTML(analysis);
    panel.webview.html = html;
}

async function insertTestCase(testCase: TestCase) {
    const activeEditor = vscode.window.activeTextEditor;
    if (!activeEditor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    const testCode = generateTestCaseCode(testCase);
    const position = activeEditor.selection.active;
    
    await activeEditor.edit(editBuilder => {
        editBuilder.insert(position, testCode);
    });
}

async function exportTestCases(testCases: TestCase[]) {
    const uri = await vscode.window.showSaveDialog({
        defaultUri: vscode.Uri.file('generated-test-cases.json'),
        filters: {
            'JSON': ['json'],
            'All Files': ['*']
        }
    });

    if (uri) {
        const content = JSON.stringify(testCases, null, 2);
        await vscode.workspace.fs.writeFile(uri, Buffer.from(content));
        vscode.window.showInformationMessage('Test cases exported successfully!');
    }
}

function generateTestCaseCode(testCase: TestCase): string {
    return `
// ${testCase.title}
describe('${testCase.title}', () => {
    it('${testCase.description}', async () => {
        ${testCase.steps.map((step, index) => `// Step ${index + 1}: ${step}`).join('\n        ')}
        
        // Expected: ${testCase.expected_result}
    });
});
`;
}

function generateTestCasesHTML(testCases: TestCase[]): string {
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Test Cases</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }
        .test-case { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .test-case h3 { margin: 0 0 10px 0; color: #333; }
        .test-case p { margin: 5px 0; color: #666; }
        .test-case .steps { margin: 10px 0; }
        .test-case .steps ol { margin: 5px 0; padding-left: 20px; }
        .test-case .meta { display: flex; gap: 10px; margin: 10px 0; }
        .test-case .meta span { background: #f0f0f0; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
        .actions { margin: 20px 0; }
        .btn { background: #007acc; color: white; border: none; padding: 8px 16px; border-radius: 3px; cursor: pointer; margin-right: 10px; }
        .btn:hover { background: #005a9e; }
    </style>
</head>
<body>
    <h1>Generated Test Cases</h1>
    <div class="actions">
        <button class="btn" onclick="exportAll()">Export All</button>
        <button class="btn" onclick="insertAll()">Insert All</button>
    </div>
    
    ${testCases.map((testCase, index) => `
        <div class="test-case">
            <h3>${testCase.title}</h3>
            <p><strong>Description:</strong> ${testCase.description}</p>
            <div class="meta">
                <span>Type: ${testCase.test_type}</span>
                <span>Priority: ${testCase.priority}</span>
                ${testCase.tags.map(tag => `<span>${tag}</span>`).join('')}
            </div>
            <div class="steps">
                <strong>Steps:</strong>
                <ol>
                    ${testCase.steps.map(step => `<li>${step}</li>`).join('')}
                </ol>
            </div>
            <p><strong>Expected Result:</strong> ${testCase.expected_result}</p>
            <div class="actions">
                <button class="btn" onclick="insertTestCase(${index})">Insert</button>
                <button class="btn" onclick="copyTestCase(${index})">Copy</button>
            </div>
        </div>
    `).join('')}
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function insertTestCase(index) {
            vscode.postMessage({
                command: 'insertTestCase',
                testCase: ${JSON.stringify(testCases)}
            });
        }
        
        function insertAll() {
            vscode.postMessage({
                command: 'insertAllTestCases',
                testCases: ${JSON.stringify(testCases)}
            });
        }
        
        function exportAll() {
            vscode.postMessage({
                command: 'exportTestCases',
                testCases: ${JSON.stringify(testCases)}
            });
        }
        
        function copyTestCase(index) {
            const testCase = ${JSON.stringify(testCases)}[index];
            navigator.clipboard.writeText(JSON.stringify(testCase, null, 2));
        }
    </script>
</body>
</html>`;
}

function generateBDDScenariosHTML(scenarios: any[]): string {
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated BDD Scenarios</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }
        .scenario { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .scenario h3 { margin: 0 0 10px 0; color: #333; }
        .gherkin { background: #f8f8f8; padding: 10px; border-radius: 3px; font-family: monospace; }
        .given { color: #2e7d32; }
        .when { color: #1976d2; }
        .then { color: #d32f2f; }
    </style>
</head>
<body>
    <h1>Generated BDD Scenarios</h1>
    
    ${scenarios.map(scenario => `
        <div class="scenario">
            <h3>${scenario.title}</h3>
            <p>${scenario.description}</p>
            <div class="gherkin">
                <div class="given"><strong>Given</strong> ${scenario.given.join(', ')}</div>
                <div class="when"><strong>When</strong> ${scenario.when.join(', ')}</div>
                <div class="then"><strong>Then</strong> ${scenario.then.join(', ')}</div>
            </div>
        </div>
    `).join('')}
</body>
</html>`;
}

function generateCoverageAnalysisHTML(analysis: any): string {
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Coverage Analysis</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }
        .coverage-summary { text-align: center; margin: 20px 0; }
        .percentage { font-size: 3em; font-weight: bold; color: #007acc; }
        .details { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }
        .detail-section { border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
        .detail-section h4 { margin: 0 0 10px 0; color: #333; }
        .detail-section ul { margin: 0; padding-left: 20px; }
        .detail-section li { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Test Coverage Analysis</h1>
    
    <div class="coverage-summary">
        <div class="percentage">${analysis.coverage_percentage}%</div>
        <p>Test Coverage</p>
    </div>
    
    <div class="details">
        <div class="detail-section">
            <h4>Covered Areas</h4>
            <ul>
                ${analysis.covered_areas.map((area: any) => `<li>${area}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detail-section">
            <h4>Missing Areas</h4>
            <ul>
                ${analysis.missing_areas.map((area: any) => `<li>${area}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detail-section">
            <h4>Recommendations</h4>
            <ul>
                ${analysis.recommendations.map((rec: any) => `<li>${rec}</li>`).join('')}
            </ul>
        </div>
    </div>
</body>
</html>`;
}

function getConfiguration(): AssertlyConfig {
    const config = vscode.workspace.getConfiguration('assertly');
    return {
        apiUrl: config.get('apiUrl', 'http://localhost:5000'),
        apiKey: config.get('apiKey'),
        jiraUrl: config.get('jiraUrl'),
        jiraUsername: config.get('jiraUsername'),
        jiraApiToken: config.get('jiraApiToken'),
        aiProvider: config.get('aiProvider', 'openai'),
        aiApiKey: config.get('aiApiKey'),
        enterpriseMode: config.get('enterpriseMode', false),
        enterpriseAiUrl: config.get('enterpriseAiUrl'),
        enterpriseAiModel: config.get('enterpriseAiModel', 'local-copilot'),
        enterpriseApiKey: config.get('enterpriseApiKey'),
        proxyUrl: config.get('proxyUrl'),
        certPath: config.get('certPath'),
        verifySsl: config.get('verifySsl', true)
    };
}

function initializeConfiguration() {
    const config = getConfiguration();
    if (!config.apiUrl) {
        vscode.window.showInformationMessage(
            'Assertly Test Manager: Please configure your API URL in settings.',
            'Open Settings'
        ).then(selection => {
            if (selection === 'Open Settings') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'assertly');
            }
        });
    }
}

async function handleFeatureFileChange(uri: vscode.Uri) {
    // Handle .feature file changes for BDD integration
    console.log('Feature file changed:', uri.fsPath);
}

async function handleDocumentChange(event: vscode.TextDocumentChangeEvent) {
    // Handle document changes for real-time analysis
    if (event.document.fileName.endsWith('.feature')) {
        // Analyze BDD file changes
        console.log('BDD file changed:', event.document.fileName);
    }
}

class AssertlyTestExplorerProvider implements vscode.TreeDataProvider<any> {
    private _onDidChangeTreeData: vscode.EventEmitter<any | undefined | null | void> = new vscode.EventEmitter<any | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<any | undefined | null | void> = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: any): vscode.TreeItem {
        return element;
    }

    getChildren(element?: any): Thenable<any[]> {
        if (!element) {
            return Promise.resolve([
                new vscode.TreeItem('Test Cases', vscode.TreeItemCollapsibleState.Collapsed),
                new vscode.TreeItem('BDD Scenarios', vscode.TreeItemCollapsibleState.Collapsed),
                new vscode.TreeItem('Coverage Analysis', vscode.TreeItemCollapsibleState.Collapsed)
            ]);
        }
        return Promise.resolve([]);
    }
}

class AssertlyDashboardProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'assertlyDashboard';
    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assertly Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; }
        .dashboard { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .card { border: 1px solid #ddd; padding: 15px; border-radius: 5px; text-align: center; }
        .card h3 { margin: 0 0 10px 0; color: #333; }
        .card p { margin: 0; color: #666; }
        .btn { background: #007acc; color: white; border: none; padding: 8px 16px; border-radius: 3px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #005a9e; }
    </style>
</head>
<body>
    <h2>Assertly Test Manager</h2>
    <div class="dashboard">
        <div class="card">
            <h3>Generate Tests</h3>
            <p>AI-powered test case generation</p>
            <button class="btn" onclick="generateTests()">Generate</button>
        </div>
        <div class="card">
            <h3>BDD Scenarios</h3>
            <p>Create BDD scenarios</p>
            <button class="btn" onclick="createBDD()">Create</button>
        </div>
        <div class="card">
            <h3>Coverage Analysis</h3>
            <p>Analyze test coverage</p>
            <button class="btn" onclick="analyzeCoverage()">Analyze</button>
        </div>
        <div class="card">
            <h3>Jira Sync</h3>
            <p>Synchronize with Jira</p>
            <button class="btn" onclick="syncJira()">Sync</button>
        </div>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function generateTests() {
            vscode.postMessage({ command: 'generateTestCases' });
        }
        
        function createBDD() {
            vscode.postMessage({ command: 'createBDDScenario' });
        }
        
        function analyzeCoverage() {
            vscode.postMessage({ command: 'analyzeCoverage' });
        }
        
        function syncJira() {
            vscode.postMessage({ command: 'syncWithJira' });
        }
    </script>
</body>
</html>`;
    }
}

async function configureEnterprise() {
    try {
        const config = getConfiguration();
        if (!config.apiUrl) {
            vscode.window.showErrorMessage('Assertly API URL not configured.');
            return;
        }

        // Show enterprise configuration dialog
        const localAiUrl = await vscode.window.showInputBox({
            prompt: 'Enter Local AI Service URL',
            placeHolder: 'http://internal-ai.company.com:8080/api',
            value: config.enterpriseAiUrl || ''
        });
        if (!localAiUrl) return;

        const localAiModel = await vscode.window.showQuickPick([
            { label: 'Local Copilot', value: 'local-copilot' },
            { label: 'Internal LLM', value: 'internal-llm' },
            { label: 'Custom Model', value: 'custom-model' },
            { label: 'Offline Model', value: 'offline-model' }
        ], {
            placeHolder: 'Select AI Model',
            title: 'Enterprise AI Model'
        });
        if (!localAiModel) return;

        const localApiKey = await vscode.window.showInputBox({
            prompt: 'Enter API Key (Optional)',
            placeHolder: 'Internal API key if required',
            value: config.enterpriseApiKey || '',
            password: true
        });

        const proxyUrl = await vscode.window.showInputBox({
            prompt: 'Enter Proxy URL (Optional)',
            placeHolder: 'http://proxy.company.com:8080',
            value: config.proxyUrl || ''
        });

        const certPath = await vscode.window.showInputBox({
            prompt: 'Enter Certificate Path (Optional)',
            placeHolder: '/path/to/company-cert.pem',
            value: config.certPath || ''
        });

        // Configure enterprise AI
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Configuring enterprise AI...",
            cancellable: true
        }, async (progress, token) => {
            try {
                const response = await axios.post(`${config.apiUrl}/api/enterprise/ai/configure`, {
                    local_ai_url: localAiUrl,
                    local_ai_model: localAiModel.value,
                    local_api_key: localApiKey,
                    proxy_url: proxyUrl,
                    cert_path: certPath,
                    verify_ssl: true
                }, {
                    headers: {
                        'Authorization': `Bearer ${config.apiKey}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 30000
                });

                if (response.data.success) {
                    vscode.window.showInformationMessage('Enterprise AI configured successfully!');
                    
                    // Update VS Code settings
                    const workspaceConfig = vscode.workspace.getConfiguration('assertly');
                    await workspaceConfig.update('enterpriseMode', true, vscode.ConfigurationTarget.Workspace);
                    await workspaceConfig.update('enterpriseAiUrl', localAiUrl, vscode.ConfigurationTarget.Workspace);
                    await workspaceConfig.update('enterpriseAiModel', localAiModel.value, vscode.ConfigurationTarget.Workspace);
                    if (localApiKey) {
                        await workspaceConfig.update('enterpriseApiKey', localApiKey, vscode.ConfigurationTarget.Workspace);
                    }
                    if (proxyUrl) {
                        await workspaceConfig.update('proxyUrl', proxyUrl, vscode.ConfigurationTarget.Workspace);
                    }
                    if (certPath) {
                        await workspaceConfig.update('certPath', certPath, vscode.ConfigurationTarget.Workspace);
                    }
                } else {
                    vscode.window.showErrorMessage(`Failed to configure enterprise AI: ${response.data.error}`);
                }
            } catch (error: any) {
                vscode.window.showErrorMessage(`Error configuring enterprise AI: ${error.message}`);
            }
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function testEnterpriseConnection() {
    try {
        const config = getConfiguration();
        if (!config.apiUrl) {
            vscode.window.showErrorMessage('Assertly API URL not configured.');
            return;
        }

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Testing enterprise AI connection...",
            cancellable: true
        }, async (progress, token) => {
            try {
                const response = await axios.get(`${config.apiUrl}/api/enterprise/ai/test-connection`, {
                    headers: {
                        'Authorization': `Bearer ${config.apiKey}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 10000
                });

                if (response.data.success) {
                    vscode.window.showInformationMessage(
                        `Enterprise AI connection successful!\nURL: ${response.data.url}\nModel: ${response.data.model}`
                    );
                } else {
                    vscode.window.showErrorMessage(`Enterprise AI connection failed: ${response.data.message}`);
                }
            } catch (error: any) {
                vscode.window.showErrorMessage(`Error testing enterprise AI connection: ${error.message}`);
            }
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function openEnterpriseSettings() {
    const config = getConfiguration();
    if (!config.apiUrl) {
        vscode.window.showErrorMessage('Assertly API URL not configured.');
        return;
    }

    // Open enterprise settings in external browser
    const settingsUrl = `${config.apiUrl}/enterprise-settings`;
    vscode.env.openExternal(vscode.Uri.parse(settingsUrl));
}

export function deactivate() {}