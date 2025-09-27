#!/usr/bin/env python3
"""
Script to fix all API endpoints with proper error handling and client management
"""

import re

def fix_endpoints():
    """Fix all API endpoints in app.py"""
    
    # Read the current file
    with open('/workspace/app.py', 'r') as f:
        content = f.read()
    
    # Pattern to find endpoints that need fixing
    patterns = [
        # Pattern 1: if not jira_client: -> jira_client = get_jira_client()
        (r'if not jira_client:', r'jira_client = get_jira_client()\n    if not jira_client:'),
        
        # Pattern 2: Add try-catch blocks around jira_client calls
        (r'(\s+)(jira_client\.\w+\([^)]*\))\s*$', r'\1try:\n\1    \2\n\1    return jsonify(result)\n\1except Exception as e:\n\1    return jsonify({\'error\': str(e)}), 500'),
    ]
    
    # Apply fixes
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Write back
    with open('/workspace/app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed API endpoints")

if __name__ == "__main__":
    fix_endpoints()