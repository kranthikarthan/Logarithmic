# Xray Test Management Tool

A standalone application that replicates Xray test management functionality using personal Jira credentials without requiring admin installation.

## Features

- **Personal Authentication**: Use your own Jira credentials - no admin installation required
- **Test Case Management**: View, filter, and export test cases
- **Test Execution Tracking**: Monitor test execution status and results
- **Test Plan Management**: Organize and manage test plans
- **Data Export**: Export test data to Excel, CSV, or JSON formats
- **Custom JQL Queries**: Use Jira Query Language for advanced filtering
- **Modern Web Interface**: Clean, responsive UI built with Bootstrap

## Quick Start

### Prerequisites

- Python 3.7 or higher
- Jira account with API token access
- Internet connection to your Jira instance

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd xray-test-management-tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:5000`

### First Time Setup

1. **Get your Jira API Token**:
   - Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Click "Create API token"
   - Give it a name and copy the token

2. **Login to the application**:
   - Enter your Jira URL (e.g., `https://your-domain.atlassian.net`)
   - Enter your Jira username/email
   - Enter your API token
   - Click "Connect to Jira"

## Usage

### Dashboard
The main dashboard provides an overview of your test management data:
- Test case counts
- Test execution status
- Test plan summaries
- Quick filters and search

### Test Cases
- View all test cases with filtering options
- Filter by project, status, assignee, etc.
- Use custom JQL queries for advanced filtering
- Export test cases to Excel/CSV

### Test Executions
- Monitor test execution progress
- Track execution results and status
- Filter by date, status, or custom criteria

### Test Plans
- Organize test cases into test plans
- Track test plan progress
- Export test plan data

### Data Export
- Export test cases to Excel format
- Download filtered results
- Custom date ranges and filters

## API Endpoints

The application provides REST API endpoints for programmatic access:

- `GET /api/projects` - List accessible projects
- `GET /api/test-cases` - Get test cases (supports project and JQL filters)
- `GET /api/test-executions` - Get test executions
- `GET /api/test-plans` - Get test plans
- `GET /api/issue/{key}` - Get detailed issue information
- `GET /export/test-cases` - Export test cases to Excel

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key
DEFAULT_JIRA_URL=https://your-domain.atlassian.net
DEBUG=True
HOST=0.0.0.0
PORT=5000
```

### Jira Permissions

Your Jira account needs the following permissions:
- Read access to projects containing test data
- Access to issue types: Test, Test Execution, Test Plan
- Ability to view custom fields (if using Xray custom fields)

## Customization

### Adding Custom Fields
To display additional custom fields, modify the `get_test_cases` method in `app.py`:

```python
'fields': 'summary,description,status,assignee,reporter,created,updated,labels,components,fixVersions,priority,issuetype,customfield_10014,customfield_10015'
```

### Custom JQL Queries
Use JQL (Jira Query Language) for advanced filtering:

```jql
project = "TEST" AND issuetype = "Test" AND status = "Open"
created >= -30d AND assignee = currentUser()
labels in ("regression", "smoke") AND priority in ("High", "Highest")
```

## Troubleshooting

### Connection Issues
- Verify your Jira URL is correct
- Check that your API token is valid and not expired
- Ensure your account has access to the projects you're trying to view

### Data Not Loading
- Check your Jira permissions
- Verify that test-related issue types exist in your projects
- Try using custom JQL queries to narrow down results

### Export Issues
- Ensure you have write permissions in the download directory
- Check that the data you're trying to export is not empty

## Security Notes

- API tokens are stored in session memory only (not persisted)
- No sensitive data is logged or stored permanently
- Use HTTPS in production environments
- Regularly rotate your API tokens

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Jira API documentation
3. Create an issue in the repository

## Changelog

### Version 1.0.0
- Initial release
- Basic test case, execution, and plan management
- Excel export functionality
- Modern web interface
- Personal authentication system