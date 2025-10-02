" Assertly Test Manager Vim Plugin
" Enterprise AI Integration for Vim/Neovim

if exists('g:assertly_loaded')
    finish
endif
let g:assertly_loaded = 1

" Plugin configuration
let g:assertly_api_url = get(g:, 'assertly_api_url', 'http://localhost:5000')
let g:assertly_api_key = get(g:, 'assertly_api_key', '')
let g:assertly_enterprise_mode = get(g:, 'assertly_enterprise_mode', 0)
let g:assertly_enterprise_ai_url = get(g:, 'assertly_enterprise_ai_url', '')
let g:assertly_enterprise_ai_model = get(g:, 'assertly_enterprise_ai_model', 'local-copilot')
let g:assertly_enterprise_api_key = get(g:, 'assertly_enterprise_api_key', '')
let g:assertly_proxy_url = get(g:, 'assertly_proxy_url', '')
let g:assertly_cert_path = get(g:, 'assertly_cert_path', '')
let g:assertly_verify_ssl = get(g:, 'assertly_verify_ssl', 1)

" Command definitions
command! -nargs=* AssertlyGenerateTests call assertly#generate_test_cases(<f-args>)
command! -nargs=* AssertlyGenerateBDD call assertly#generate_bdd_scenarios(<f-args>)
command! -nargs=* AssertlyAnalyzeCoverage call assertly#analyze_test_coverage(<f-args>)
command! AssertlyConfigureEnterprise call assertly#configure_enterprise()
command! AssertlyTestConnection call assertly#test_enterprise_connection()
command! AssertlyOpenSettings call assertly#open_enterprise_settings()

" Key mappings
if !hasmapto('<Plug>AssertlyGenerateTests')
    nmap <silent> <leader>at <Plug>AssertlyGenerateTests
endif
nnoremap <silent> <Plug>AssertlyGenerateTests :AssertlyGenerateTests<CR>

if !hasmapto('<Plug>AssertlyGenerateBDD')
    nmap <silent> <leader>ab <Plug>AssertlyGenerateBDD
endif
nnoremap <silent> <Plug>AssertlyGenerateBDD :AssertlyGenerateBDD<CR>

if !hasmapto('<Plug>AssertlyAnalyzeCoverage')
    nmap <silent> <leader>ac <Plug>AssertlyAnalyzeCoverage
endif
nnoremap <silent> <Plug>AssertlyAnalyzeCoverage :AssertlyAnalyzeCoverage<CR>

if !hasmapto('<Plug>AssertlyConfigureEnterprise')
    nmap <silent> <leader>ae <Plug>AssertlyConfigureEnterprise
endif
nnoremap <silent> <Plug>AssertlyConfigureEnterprise :AssertlyConfigureEnterprise<CR>

" Status line integration
function! AssertlyStatusLine()
    if g:assertly_enterprise_mode
        return '[Assertly Enterprise]'
    else
        return '[Assertly]'
    endif
endfunction

" Auto-completion for user stories
function! AssertlyCompleteUserStory(findstart, base)
    if a:findstart
        " Find start of current word
        let line = getline('.')
        let start = col('.') - 1
        while start > 0 && line[start - 1] =~ '\S'
            let start -= 1
        endwhile
        return start
    else
        " Return completion suggestions
        let suggestions = [
            \ 'As a user, I want to log in so that I can access my account',
            \ 'As a user, I want to search for products so that I can find what I need',
            \ 'As a user, I want to add items to cart so that I can purchase them',
            \ 'As a user, I want to checkout so that I can complete my purchase',
            \ 'As a user, I want to view my orders so that I can track them'
        \ ]
        
        let matches = []
        for suggestion in suggestions
            if suggestion =~ '^' . a:base
                call add(matches, suggestion)
            endif
        endfor
        return matches
    endif
endfunction

" Set up completion for user stories
set completefunc=AssertlyCompleteUserStory

" Highlight user stories
syntax match AssertlyUserStory /\vAs a \w+, I want .+ so that .+/
highlight link AssertlyUserStory Comment

" Auto-detect user stories in comments
augroup AssertlyUserStoryDetection
    autocmd!
    autocmd BufRead,BufNewFile *.md,*.txt,*.feature,*.gherkin
        \ syntax match AssertlyUserStory /\vAs a \w+, I want .+ so that .+/
augroup END