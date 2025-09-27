#!/usr/bin/env python3
"""
Fix all remaining endpoints with proper error handling
"""

import re

def fix_remaining_endpoints():
    with open('/workspace/app.py', 'r') as f:
        content = f.read()
    
    # Fix all remaining "if not jira_client:" patterns
    content = re.sub(
        r'(\s+)if not jira_client:',
        r'\1jira_client = get_jira_client()\n\1if not jira_client:',
        content
    )
    
    # Add try-catch blocks to endpoints that don't have them
    endpoints_to_fix = [
        'api_test_steps',
        'update_test_step', 
        'api_execution_progress',
        'api_coverage_report',
        'api_dashboard_metrics',
        'execute_all_tests',
        'reset_all_tests',
        'export_test_cases'
    ]
    
    for endpoint in endpoints_to_fix:
        # Find the function and add try-catch if missing
        pattern = rf'(def {endpoint}[^:]+:\s*[^}]+)(return jsonify[^}]+)'
        replacement = r'\1try:\n        \2\n    except Exception as e:\n        return jsonify({\'error\': str(e)}), 500'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('/workspace/app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed remaining endpoints")

if __name__ == "__main__":
    fix_remaining_endpoints()