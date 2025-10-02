#!/usr/bin/env python3
"""
Simple Page Checker for Style Consistency and Bugs
Uses only standard library modules
"""

import urllib.request
import urllib.error
import re
import json
from urllib.parse import urljoin

class SimplePageChecker:
    """Simple page checker using only standard library"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.issues = []
        self.pages_checked = []
        
    def check_page(self, path, expected_title=None):
        """Check a single page for issues"""
        url = f"{self.base_url}{path}"
        print(f"🔍 Checking: {path}")
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read().decode('utf-8')
                page_issues = []
                
                # Check HTTP status
                if response.status != 200:
                    page_issues.append(f"HTTP {response.status} error")
                    return page_issues
                
                # Check for basic HTML structure
                if not content.strip():
                    page_issues.append("Empty page content")
                    return page_issues
                
                # Check for title
                title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                if title_match:
                    title_text = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                    if expected_title and expected_title not in title_text:
                        page_issues.append(f"Title mismatch: expected '{expected_title}', got '{title_text}'")
                else:
                    page_issues.append("Missing title tag")
                
                # Check for required meta tags
                if not re.search(r'<meta[^>]*charset', content, re.IGNORECASE):
                    page_issues.append("Missing charset meta tag")
                
                if not re.search(r'<meta[^>]*name=["\']viewport["\']', content, re.IGNORECASE):
                    page_issues.append("Missing viewport meta tag")
                
                # Check for CSS files
                css_links = re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', content, re.IGNORECASE)
                if not css_links:
                    page_issues.append("No CSS files found")
                
                # Check for modern design CSS
                modern_css = any('modern-design' in link for link in css_links)
                if not modern_css:
                    page_issues.append("Not using modern design system")
                
                # Check for JavaScript
                js_scripts = re.findall(r'<script[^>]*src=["\'][^"\']*["\'][^>]*>', content, re.IGNORECASE)
                inline_js = re.findall(r'<script[^>]*>(.*?)</script>', content, re.IGNORECASE | re.DOTALL)
                if not js_scripts and not inline_js:
                    page_issues.append("No JavaScript found - may affect functionality")
                
                # Check for navigation
                if not re.search(r'<nav[^>]*>', content, re.IGNORECASE):
                    page_issues.append("No navigation found")
                
                # Check for proper HTML structure
                if not re.search(r'<html[^>]*>', content, re.IGNORECASE):
                    page_issues.append("Missing HTML tag")
                if not re.search(r'<head[^>]*>', content, re.IGNORECASE):
                    page_issues.append("Missing head tag")
                if not re.search(r'<body[^>]*>', content, re.IGNORECASE):
                    page_issues.append("Missing body tag")
                
                # Check for H1 heading
                h1_count = len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE))
                if h1_count == 0:
                    page_issues.append("No H1 heading found")
                elif h1_count > 1:
                    page_issues.append("Multiple H1 headings found")
                
                # Check for images without alt text
                img_tags = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
                for img in img_tags:
                    if not re.search(r'alt=["\'][^"\']*["\']', img, re.IGNORECASE):
                        page_issues.append("Image missing alt text")
                
                # Check for forms without proper labels
                form_inputs = re.findall(r'<input[^>]*>', content, re.IGNORECASE)
                for input_tag in form_inputs:
                    if 'type' in input_tag and 'hidden' not in input_tag.lower():
                        if not re.search(r'id=["\'][^"\']*["\']', input_tag, re.IGNORECASE):
                            page_issues.append("Form input missing id attribute")
                
                # Check for inline styles (should be minimal)
                inline_styles = re.findall(r'style=["\'][^"\']*["\']', content, re.IGNORECASE)
                if len(inline_styles) > 10:
                    page_issues.append(f"Too many inline styles found: {len(inline_styles)}")
                
                # Check for broken internal links
                internal_links = re.findall(r'href=["\']([^"\']*)["\']', content, re.IGNORECASE)
                for link in internal_links:
                    if link.startswith('#') and not re.search(rf'id=["\']?{re.escape(link[1:])}["\']?', content, re.IGNORECASE):
                        page_issues.append(f"Broken anchor link: {link}")
                
                # Check for Font Awesome icons
                fa_icons = re.findall(r'fa[sr]? fa-[a-zA-Z0-9-]+', content, re.IGNORECASE)
                if not fa_icons:
                    page_issues.append("No Font Awesome icons found - may affect UI")
                
                # Check for responsive design indicators
                viewport_meta = re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*content=["\']([^"\']*)["\'][^>]*>', content, re.IGNORECASE)
                if viewport_meta:
                    content_attr = viewport_meta.group(1)
                    if 'width=device-width' not in content_attr:
                        page_issues.append("Viewport meta tag missing width=device-width")
                
                # Check for modern CSS classes
                if not re.search(r'class=["\'][^"\']*(?:modern|app|container)[^"\']*["\']', content, re.IGNORECASE):
                    page_issues.append("Not using modern CSS classes")
                
                # Check for proper DOCTYPE
                if not re.search(r'<!DOCTYPE html>', content, re.IGNORECASE):
                    page_issues.append("Missing or incorrect DOCTYPE")
                
                # Check for language attribute
                if not re.search(r'<html[^>]*lang=["\'][^"\']*["\']', content, re.IGNORECASE):
                    page_issues.append("Missing language attribute on HTML tag")
                
                if page_issues:
                    self.issues.extend([(path, issue) for issue in page_issues])
                    print(f"❌ Found {len(page_issues)} issues")
                    for issue in page_issues:
                        print(f"   - {issue}")
                else:
                    print("✅ No issues found")
                
                self.pages_checked.append(path)
                return page_issues
                
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP {e.code} error: {e.reason}"
            self.issues.append((path, error_msg))
            print(f"❌ {error_msg}")
            return [error_msg]
        except urllib.error.URLError as e:
            error_msg = f"URL error: {e.reason}"
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
        print("🔍 Starting Simple Page Check")
        print("=" * 50)
        
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
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "=" * 50)
        print("📊 SIMPLE PAGE CHECK REPORT")
        print("=" * 50)
        
        total_pages = len(self.pages_checked)
        total_issues = len(self.issues)
        
        print(f"Pages Checked: {total_pages}")
        print(f"Total Issues Found: {total_issues}")
        
        if total_issues == 0:
            print("\n🎉 ALL PAGES PASSED! No issues found.")
            print("✅ Style consistency: PASSED")
            print("✅ Bug detection: PASSED")
            print("✅ Basic accessibility: PASSED")
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
        elif "alt" in issue.lower() or "accessibility" in issue.lower():
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
    checker = SimplePageChecker()
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