#!/usr/bin/env python3
"""
Fix AI endpoints to provide fallback responses when API keys are not configured
"""

import re

def fix_ai_endpoints():
    """Fix AI endpoints to provide fallback responses"""
    
    # Read the current app.py file
    with open('/workspace/app.py', 'r') as f:
        content = f.read()
    
    # Fix 1: AI generate test cases endpoint
    old_pattern = r'(\s+api_key = os\.getenv\(\'OPENAI_API_KEY\'\) or os\.getenv\(\'ANTHROPIC_API_KEY\'\)\s+if not api_key:\s+return jsonify\(\{\'error\': \'AI API key not configured\'\}\), 500)'
    
    new_replacement = '''        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            # Return mock test cases when API key is not configured
            return jsonify({
                'success': True,
                'test_cases': [
                    {
                        'title': f'Test Case 1: {data.get("title", "User Story")}',
                        'description': f'Verify that {data.get("description", "the feature works correctly")}',
                        'steps': [
                            '1. Navigate to the application',
                            '2. Perform the required action',
                            '3. Verify the expected result'
                        ],
                        'expected_result': 'The feature should work as expected',
                        'test_type': 'functional',
                        'priority': 'high',
                        'tags': ['smoke', 'regression'],
                        'preconditions': ['User is logged in', 'Application is accessible'],
                        'test_data': 'Sample test data',
                        'acceptance_criteria': data.get('acceptance_criteria', 'Feature works as specified')
                    }
                ],
                'count': 1,
                'note': 'Mock test case generated - configure AI API key for real AI generation'
            })'''
    
    # Apply the fix
    content = re.sub(old_pattern, new_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix 2: AI improve test case endpoint
    old_pattern2 = r'(\s+api_key = os\.getenv\(\'OPENAI_API_KEY\'\) or os\.getenv\(\'ANTHROPIC_API_KEY\'\)\s+if not api_key:\s+return jsonify\(\{\'error\': \'AI API key not configured\'\}\), 500\s+provider = data\.get\(\'provider\', \'openai\'\))'
    
    new_replacement2 = '''        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            # Return improved mock test case when API key is not configured
            return jsonify({
                'success': True,
                'improved_test_case': {
                    'title': f'Improved: {test_case.title}',
                    'description': f'Enhanced: {test_case.description}',
                    'steps': test_case.steps + ['4. Verify enhanced functionality'],
                    'expected_result': f'Enhanced: {test_case.expected_result}',
                    'test_type': test_case.test_type.value,
                    'priority': test_case.priority.value,
                    'tags': test_case.tags + ['improved'],
                    'preconditions': test_case.preconditions,
                    'test_data': test_case.test_data,
                    'acceptance_criteria': test_case.acceptance_criteria
                },
                'note': 'Mock improvement generated - configure AI API key for real AI improvement'
            })
        
        provider = data.get('provider', 'openai')'''
    
    # Apply the fix
    content = re.sub(old_pattern2, new_replacement2, content, flags=re.MULTILINE | re.DOTALL)
    
    # Write the fixed content back
    with open('/workspace/app.py', 'w') as f:
        f.write(content)
    
    print("✅ AI endpoints fixed with fallback responses")

if __name__ == "__main__":
    fix_ai_endpoints()