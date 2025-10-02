" Assertly Test Manager Vim Plugin - Autoload Functions
" Enterprise AI Integration Functions

" Generate test cases from user story
function! assertly#generate_test_cases(...)
    let user_story = a:0 > 0 ? a:1 : assertly#get_user_story_from_buffer()
    
    if empty(user_story)
        echo "No user story found. Please provide one as an argument or ensure the current buffer contains a user story."
        return
    endif
    
    echo "Generating test cases for: " . user_story
    
    " Choose API endpoint based on enterprise mode
    let endpoint = g:assertly_enterprise_mode ? '/api/enterprise/ai/generate-test-cases' : '/api/ai/generate-test-cases'
    
    let request_data = {
        \ 'title': assertly#extract_title(user_story),
        \ 'description': user_story,
        \ 'acceptance_criteria': assertly#extract_acceptance_criteria(),
        \ 'business_value': assertly#extract_business_value(user_story),
        \ 'user_persona': assertly#extract_user_persona(user_story),
        \ 'test_types': ['functional', 'ui', 'api'],
        \ 'num_cases': 5,
        \ 'additional_prompts': []
    \ }
    
    call assertly#make_api_request(endpoint, request_data, 'assertly#display_test_cases')
endfunction

" Generate BDD scenarios from user story
function! assertly#generate_bdd_scenarios(...)
    let user_story = a:0 > 0 ? a:1 : assertly#get_user_story_from_buffer()
    
    if empty(user_story)
        echo "No user story found. Please provide one as an argument or ensure the current buffer contains a user story."
        return
    endif
    
    echo "Generating BDD scenarios for: " . user_story
    
    let request_data = {
        \ 'title': assertly#extract_title(user_story),
        \ 'description': user_story,
        \ 'acceptance_criteria': assertly#extract_acceptance_criteria(),
        \ 'business_value': assertly#extract_business_value(user_story),
        \ 'user_persona': assertly#extract_user_persona(user_story),
        \ 'additional_context': 'Generate comprehensive BDD scenarios'
    \ }
    
    call assertly#make_api_request('/api/ai/generate-bdd-scenarios', request_data, 'assertly#display_bdd_scenarios')
endfunction

" Analyze test coverage
function! assertly#analyze_test_coverage(...)
    let user_story = a:0 > 0 ? a:1 : assertly#get_user_story_from_buffer()
    
    if empty(user_story)
        echo "No user story found. Please provide one as an argument or ensure the current buffer contains a user story."
        return
    endif
    
    echo "Analyzing test coverage for: " . user_story
    
    let existing_tests = assertly#get_existing_test_cases()
    
    let request_data = {
        \ 'user_story': user_story,
        \ 'existing_test_cases': existing_tests
    \ }
    
    call assertly#make_api_request('/api/ai/analyze-coverage', request_data, 'assertly#display_coverage_analysis')
endfunction

" Configure enterprise AI
function! assertly#configure_enterprise()
    echo "Configuring Enterprise AI..."
    
    " Get enterprise configuration from user
    let local_ai_url = input('Enter Local AI Service URL: ', g:assertly_enterprise_ai_url)
    if empty(local_ai_url)
        echo "Configuration cancelled."
        return
    endif
    
    let local_ai_model = input('Enter AI Model [local-copilot]: ', g:assertly_enterprise_ai_model)
    if empty(local_ai_model)
        let local_ai_model = 'local-copilot'
    endif
    
    let local_api_key = inputsecret('Enter API Key (optional): ')
    let proxy_url = input('Enter Proxy URL (optional): ', g:assertly_proxy_url)
    let cert_path = input('Enter Certificate Path (optional): ', g:assertly_cert_path)
    
    let request_data = {
        \ 'local_ai_url': local_ai_url,
        \ 'local_ai_model': local_ai_model,
        \ 'local_api_key': local_api_key,
        \ 'proxy_url': proxy_url,
        \ 'cert_path': cert_path,
        \ 'verify_ssl': g:assertly_verify_ssl
    \ }
    
    call assertly#make_api_request('/api/enterprise/ai/configure', request_data, 'assertly#handle_enterprise_configuration')
endfunction

" Test enterprise AI connection
function! assertly#test_enterprise_connection()
    echo "Testing enterprise AI connection..."
    
    call assertly#make_api_request('/api/enterprise/ai/test-connection', {}, 'assertly#handle_connection_test')
endfunction

" Open enterprise settings
function! assertly#open_enterprise_settings()
    let settings_url = g:assertly_api_url . '/enterprise-settings'
    
    if has('win32')
        silent execute '!start ' . settings_url
    elseif has('mac')
        silent execute '!open ' . settings_url
    else
        silent execute '!xdg-open ' . settings_url
    endif
endfunction

" Extract user story from current buffer
function! assertly#get_user_story_from_buffer()
    let lines = getline(1, '$')
    let user_story = ''
    
    for line in lines
        if line =~ '\vAs a \w+, I want .+ so that .+'
            let user_story = line
            break
        endif
    endfor
    
    return user_story
endfunction

" Extract title from user story
function! assertly#extract_title(user_story)
    " Try to extract from current buffer first
    let lines = getline(1, 10)
    for line in lines
        if line =~ '\v^#+\s+.+'
            return substitute(line, '\v^#+\s+', '', '')
        endif
    endfor
    
    " Fallback to generic title
    return 'User Story'
endfunction

" Extract acceptance criteria from buffer
function! assertly#extract_acceptance_criteria()
    let criteria = []
    let lines = getline(1, '$')
    
    for line in lines
        if line =~ '\v^\s*[-*]\s+.+'
            let criterion = substitute(line, '\v^\s*[-*]\s+', '', '')
            call add(criteria, criterion)
        endif
    endfor
    
    return criteria
endfunction

" Extract business value from user story
function! assertly#extract_business_value(user_story)
    let match = matchstr(user_story, '\vso that \zs.+')
    return empty(match) ? 'Improves user experience' : match
endfunction

" Extract user persona from user story
function! assertly#extract_user_persona(user_story)
    let match = matchstr(user_story, '\vAs a \zs\w+')
    return empty(match) ? 'user' : match
endfunction

" Get existing test cases from workspace
function! assertly#get_existing_test_cases()
    let test_cases = []
    
    " Find test files in current directory
    let test_files = glob('**/*.test.js', 0, 1)
    let test_files += glob('**/*.spec.js', 0, 1)
    let test_files += glob('**/*.test.ts', 0, 1)
    let test_files += glob('**/*.spec.ts', 0, 1)
    
    for file in test_files
        let lines = readfile(file)
        for line in lines
            if line =~ '\vit\([''"]\zs[^''"]*\ze[''"]'
                let test_title = matchstr(line, '\vit\([''"]\zs[^''"]*\ze[''"]')
                call add(test_cases, {'title': test_title})
            endif
        endfor
    endfor
    
    return test_cases
endfunction

" Make API request
function! assertly#make_api_request(endpoint, data, callback)
    let url = g:assertly_api_url . a:endpoint
    let json_data = json_encode(a:data)
    
    " Build curl command
    let curl_cmd = 'curl -s -X POST'
    let curl_cmd .= ' -H "Content-Type: application/json"'
    
    if !empty(g:assertly_api_key)
        let curl_cmd .= ' -H "Authorization: Bearer ' . g:assertly_api_key . '"'
    endif
    
    if !empty(g:assertly_proxy_url)
        let curl_cmd .= ' --proxy ' . g:assertly_proxy_url
    endif
    
    if !g:assertly_verify_ssl
        let curl_cmd .= ' -k'
    endif
    
    let curl_cmd .= ' -d ' . shellescape(json_data)
    let curl_cmd .= ' ' . shellescape(url)
    
    " Execute request
    let response = system(curl_cmd)
    
    if v:shell_error
        echo "API request failed: " . response
        return
    endif
    
    " Parse response
    try
        let result = json_decode(response)
        call call(a:callback, [result])
    catch
        echo "Failed to parse API response: " . response
    endtry
endfunction

" Display test cases
function! assertly#display_test_cases(result)
    if get(a:result, 'success', 0)
        let test_cases = get(a:result, 'test_cases', [])
        echo "Generated " . len(test_cases) . " test cases"
        
        " Create new buffer for test cases
        new
        setlocal buftype=nofile
        setlocal bufhidden=wipe
        setlocal noswapfile
        setlocal filetype=javascript
        
        let lines = ['// Generated Test Cases', '']
        
        for test_case in test_cases
            call add(lines, '// ' . get(test_case, 'title', 'Test Case'))
            call add(lines, 'describe("' . get(test_case, 'title', 'Test Case') . '", () => {')
            call add(lines, '    it("' . get(test_case, 'description', 'should work') . '", async () => {')
            
            let steps = get(test_case, 'steps', [])
            for step in steps
                call add(lines, '        // ' . step)
            endfor
            
            call add(lines, '        // Expected: ' . get(test_case, 'expected_result', ''))
            call add(lines, '    });')
            call add(lines, '});')
            call add(lines, '')
        endfor
        
        call setline(1, lines)
        echo "Test cases displayed in new buffer"
    else
        echo "Failed to generate test cases: " . get(a:result, 'error', 'Unknown error')
    endif
endfunction

" Display BDD scenarios
function! assertly#display_bdd_scenarios(result)
    if get(a:result, 'success', 0)
        let scenarios = get(a:result, 'scenarios', [])
        echo "Generated " . len(scenarios) . " BDD scenarios"
        
        " Create new buffer for BDD scenarios
        new
        setlocal buftype=nofile
        setlocal bufhidden=wipe
        setlocal noswapfile
        setlocal filetype=gherkin
        
        let lines = ['Feature: Generated BDD Scenarios', '']
        
        for scenario in scenarios
            call add(lines, 'Scenario: ' . get(scenario, 'title', 'Scenario'))
            call add(lines, '    ' . get(scenario, 'description', ''))
            call add(lines, '')
            
            let given = get(scenario, 'given', [])
            for step in given
                call add(lines, '    Given ' . step)
            endfor
            
            let when = get(scenario, 'when', [])
            for step in when
                call add(lines, '    When ' . step)
            endfor
            
            let then = get(scenario, 'then', [])
            for step in then
                call add(lines, '    Then ' . step)
            endfor
            
            call add(lines, '')
        endfor
        
        call setline(1, lines)
        echo "BDD scenarios displayed in new buffer"
    else
        echo "Failed to generate BDD scenarios: " . get(a:result, 'error', 'Unknown error')
    endif
endfunction

" Display coverage analysis
function! assertly#display_coverage_analysis(result)
    if get(a:result, 'success', 0)
        let analysis = get(a:result, 'analysis', {})
        echo "Coverage analysis complete"
        
        " Create new buffer for coverage analysis
        new
        setlocal buftype=nofile
        setlocal bufhidden=wipe
        setlocal noswapfile
        setlocal filetype=markdown
        
        let lines = ['# Test Coverage Analysis', '']
        call add(lines, '## Coverage Summary')
        call add(lines, 'Coverage: ' . get(analysis, 'coverage_percentage', 'N/A') . '%')
        call add(lines, '')
        
        let covered_areas = get(analysis, 'covered_areas', [])
        if !empty(covered_areas)
            call add(lines, '## Covered Areas')
            for area in covered_areas
                call add(lines, '- ' . area)
            endfor
            call add(lines, '')
        endif
        
        let missing_areas = get(analysis, 'missing_areas', [])
        if !empty(missing_areas)
            call add(lines, '## Missing Areas')
            for area in missing_areas
                call add(lines, '- ' . area)
            endfor
            call add(lines, '')
        endif
        
        let recommendations = get(analysis, 'recommendations', [])
        if !empty(recommendations)
            call add(lines, '## Recommendations')
            for rec in recommendations
                call add(lines, '- ' . rec)
            endfor
        endif
        
        call setline(1, lines)
        echo "Coverage analysis displayed in new buffer"
    else
        echo "Failed to analyze coverage: " . get(a:result, 'error', 'Unknown error')
    endif
endfunction

" Handle enterprise configuration response
function! assertly#handle_enterprise_configuration(result)
    if get(a:result, 'success', 0)
        echo "Enterprise AI configured successfully!"
        
        " Update global variables
        let g:assertly_enterprise_mode = 1
        echo "Enterprise mode enabled. Restart Vim to apply changes."
    else
        echo "Failed to configure enterprise AI: " . get(a:result, 'error', 'Unknown error')
    endif
endfunction

" Handle connection test response
function! assertly#handle_connection_test(result)
    if get(a:result, 'success', 0)
        echo "Enterprise AI connection successful!"
        echo "URL: " . get(a:result, 'url', 'N/A')
        echo "Model: " . get(a:result, 'model', 'N/A')
    else
        echo "Enterprise AI connection failed: " . get(a:result, 'message', 'Unknown error')
    endif
endfunction