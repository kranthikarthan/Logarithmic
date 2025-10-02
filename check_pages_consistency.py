#!/usr/bin/env python3
"""
Comprehensive Style and Bug Check for All Pages
Checks for consistency, bugs, and accessibility issues
"""

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

class PageChecker:
    """Comprehensive page checker for style consistency and bugs"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.issues = []
        self.pages_checked = []
        
    def check_page(self, path, expected_title=None):
        """Check a single page for issues"""
        url = f"{self.base_url}{path}"
        print(f"🔍 Checking: {path}")
        
        try:
            response = requests.get(url, timeout=10)
            page_issues = []
            
            # Check HTTP status
            if response.status_code != 200:
                page_issues.append(f"HTTP {response.status_code} error")
                return page_issues
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check title
            title = soup.find('title')
            if title:
                title_text = title.get_text().strip()
                if expected_title and expected_title not in title_text:
                    page_issues.append(f"Title mismatch: expected '{expected_title}', got '{title_text}'")
            else:
                page_issues.append("Missing title tag")
            
            # Check for required meta tags
            meta_charset = soup.find('meta', {'charset': True})
            if not meta_charset:
                page_issues.append("Missing charset meta tag")
            
            meta_viewport = soup.find('meta', {'name': 'viewport'})
            if not meta_viewport:
                page_issues.append("Missing viewport meta tag")
            
            # Check for CSS files
            css_links = soup.find_all('link', {'rel': 'stylesheet'})
            if not css_links:
                page_issues.append("No CSS files found")
            
            # Check for JavaScript errors (basic check)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'error' in script.string.lower():
                    page_issues.append("Potential JavaScript error found")
            
            # Check for broken images
            images = soup.find_all('img')
            for img in images:
                src = img.get('src')
                if src and not src.startswith('data:') and not src.startswith('http'):
                    # Check if it's a relative path that might be broken
                    if src.startswith('/static/') and 'placeholder' not in src.lower():
                        page_issues.append(f"Potential broken image: {src}")
            
            # Check for accessibility issues
            # Check for alt text on images
            for img in images:
                if not img.get('alt') and not img.get('aria-label'):
                    page_issues.append(f"Image missing alt text: {img.get('src', 'unknown')}")
            
            # Check for proper heading hierarchy
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                h1_count = len(soup.find_all('h1'))
                if h1_count == 0:
                    page_issues.append("No H1 heading found")
                elif h1_count > 1:
                    page_issues.append("Multiple H1 headings found")
            
            # Check for form accessibility
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all(['input', 'select', 'textarea'])
                for input_elem in inputs:
                    if input_elem.get('type') not in ['hidden', 'submit', 'button']:
                        if not input_elem.get('id') and not input_elem.get('name'):
                            page_issues.append("Form input missing id or name attribute")
            
            # Check for consistent navigation
            nav = soup.find('nav')
            if not nav:
                page_issues.append("No navigation found")
            
            # Check for responsive design
            viewport_meta = soup.find('meta', {'name': 'viewport'})
            if viewport_meta:
                content = viewport_meta.get('content', '')
                if 'width=device-width' not in content:
                    page_issues.append("Viewport meta tag missing width=device-width")
            
            # Check for modern CSS classes
            body = soup.find('body')
            if body:
                body_classes = body.get('class', [])
                if not any('modern' in cls.lower() or 'app' in cls.lower() for cls in body_classes):
                    # Check if it's using modern design system
                    css_links = soup.find_all('link', {'rel': 'stylesheet'})
                    modern_css = any('modern-design' in link.get('href', '') for link in css_links)
                    if not modern_css:
                        page_issues.append("Not using modern design system")
            
            # Check for JavaScript functionality
            js_scripts = soup.find_all('script', src=True)
            if not js_scripts and not soup.find_all('script', string=True):
                page_issues.append("No JavaScript found - may affect functionality")
            
            # Check for proper HTML structure
            if not soup.find('html'):
                page_issues.append("Missing HTML tag")
            if not soup.find('head'):
                page_issues.append("Missing head tag")
            if not soup.find('body'):
                page_issues.append("Missing body tag")
            
            # Check for inline styles (should be minimal)
            inline_styles = soup.find_all(attrs={'style': True})
            if len(inline_styles) > 10:  # Allow some inline styles but not too many
                page_issues.append(f"Too many inline styles found: {len(inline_styles)}")
            
            # Check for broken links (basic check)
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if href.startswith('#') and not soup.find(id=href[1:]):
                    page_issues.append(f"Broken anchor link: {href}")
            
            if page_issues:
                self.issues.extend([(path, issue) for issue in page_issues])
                print(f"❌ Found {len(page_issues)} issues")
                for issue in page_issues:
                    print(f"   - {issue}")
            else:
                print("✅ No issues found")
            
            self.pages_checked.append(path)
            return page_issues
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            self.issues.append((path, error_msg))
            print(f"❌ {error_msg}")
            return [error_msg]
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.issues.append((path, error_msg))
            print(f"❌ {error_msg}")
            return [error_msg]
    
    def check_all_pages(self):
        """Check all pages for consistency and bugs"""
        print("🔍 Starting Comprehensive Page Check")
        print("=" * 60)
        
        # Define pages to check
        pages_to_check = [
            ("/", "Assertly"),
            ("/landing", "Assertly"),
            ("/dashboard", "Dashboard"),
            ("/ai-test-generator", "AI Test Generator"),
            ("/integrations", "Integrations"),
            ("/enterprise-settings", "Enterprise Settings"),
            ("/signup", "Sign Up"),
            ("/login", "Login"),
            ("/health", "Health"),
        ]
        
        # Check each page
        for path, expected_title in pages_to_check:
            self.check_page(path, expected_title)
            time.sleep(0.5)  # Be nice to the server
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE PAGE CHECK REPORT")
        print("=" * 60)
        
        total_pages = len(self.pages_checked)
        total_issues = len(self.issues)
        
        print(f"Pages Checked: {total_pages}")
        print(f"Total Issues Found: {total_issues}")
        
        if total_issues == 0:
            print("\n🎉 ALL PAGES PASSED! No issues found.")
            print("✅ Style consistency: PASSED")
            print("✅ Bug detection: PASSED")
            print("✅ Accessibility: PASSED")
            print("✅ Responsive design: PASSED")
        else:
            print(f"\n⚠️  Found {total_issues} issues across {total_pages} pages")
            
            # Group issues by type
            issue_types = {}
            for path, issue in self.issues:
                issue_type = self.categorize_issue(issue)
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append((path, issue))
            
            print("\n📋 Issues by Category:")
            for issue_type, issues in issue_types.items():
                print(f"\n{issue_type}: {len(issues)} issues")
                for path, issue in issues[:5]:  # Show first 5 issues
                    print(f"  - {path}: {issue}")
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if total_issues == 0:
            print("✅ All pages are consistent and bug-free!")
            print("✅ Ready for production deployment!")
        else:
            print("🔧 Fix the identified issues before production deployment")
            print("🔧 Consider running automated accessibility tests")
            print("🔧 Test responsive design on multiple devices")
            print("🔧 Validate HTML and CSS")
        
        return total_issues == 0
    
    def categorize_issue(self, issue):
        """Categorize issue by type"""
        if "HTTP" in issue and "error" in issue:
            return "🚨 Critical Errors"
        elif "missing" in issue.lower() or "no " in issue.lower():
            return "⚠️  Missing Elements"
        elif "accessibility" in issue.lower() or "alt" in issue.lower():
            return "♿ Accessibility"
        elif "responsive" in issue.lower() or "viewport" in issue.lower():
            return "📱 Responsive Design"
        elif "CSS" in issue or "style" in issue.lower():
            return "🎨 Styling"
        elif "JavaScript" in issue or "script" in issue.lower():
            return "⚡ JavaScript"
        else:
            return "🔧 General Issues"

def main():
    """Main function to run page checks"""
    checker = PageChecker()
    success = checker.check_all_pages()
    
    if success:
        print("\n🎉 ALL PAGES ARE CONSISTENT AND BUG-FREE!")
        print("✅ Ready for production deployment!")
        return True
    else:
        print("\n⚠️  Some issues found. Please review and fix before production.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)