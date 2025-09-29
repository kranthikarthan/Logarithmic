"""
Internationalization (i18n) Manager for Assertly
Provides multi-language support for the application
"""

import json
import os
from typing import Dict, Any, Optional
from flask import request, session, g
import logging

class I18nManager:
    """Internationalization manager for multi-language support"""
    
    def __init__(self, app=None):
        """Initialize i18n manager"""
        self.app = app
        self.supported_languages = {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어'
        }
        self.default_language = 'en'
        self.translations = {}
        self.load_translations()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Add template global for language functions
        app.jinja_env.globals['gettext'] = self.gettext
        app.jinja_env.globals['ngettext'] = self.ngettext
        app.jinja_env.globals['get_current_language'] = self.get_current_language
        app.jinja_env.globals['get_supported_languages'] = self.get_supported_languages
    
    def load_translations(self):
        """Load translation files"""
        try:
            # Create translations directory if it doesn't exist
            os.makedirs('translations', exist_ok=True)
            
            for lang_code in self.supported_languages.keys():
                translation_file = f'translations/{lang_code}.json'
                if os.path.exists(translation_file):
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                else:
                    # Create default translation file
                    self.create_default_translation(lang_code)
                    
        except Exception as e:
            logging.error(f"Failed to load translations: {e}")
    
    def create_default_translation(self, lang_code):
        """Create default translation file for language"""
        if lang_code == 'en':
            # English is the default, no translation needed
            self.translations[lang_code] = {}
            return
        
        # Create basic translation structure
        default_translations = {
            "navigation": {
                "dashboard": "Dashboard",
                "test_cases": "Test Cases",
                "test_executions": "Test Executions",
                "reports": "Reports",
                "settings": "Settings",
                "logout": "Logout"
            },
            "common": {
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "create": "Create",
                "search": "Search",
                "loading": "Loading...",
                "error": "Error",
                "success": "Success",
                "warning": "Warning",
                "info": "Information"
            },
            "auth": {
                "login": "Login",
                "logout": "Logout",
                "signup": "Sign Up",
                "email": "Email",
                "password": "Password",
                "forgot_password": "Forgot Password?",
                "remember_me": "Remember Me"
            },
            "test_management": {
                "test_case": "Test Case",
                "test_cases": "Test Cases",
                "test_execution": "Test Execution",
                "test_executions": "Test Executions",
                "test_set": "Test Set",
                "test_sets": "Test Sets",
                "priority": "Priority",
                "status": "Status",
                "assigned_to": "Assigned To",
                "created_by": "Created By",
                "created_at": "Created At",
                "updated_at": "Updated At"
            },
            "ai_features": {
                "ai_test_generator": "AI Test Generator",
                "generate_test_cases": "Generate Test Cases",
                "improve_test_case": "Improve Test Case",
                "generate_bdd_scenarios": "Generate BDD Scenarios",
                "analyze_coverage": "Analyze Coverage"
            },
            "enterprise": {
                "enterprise_settings": "Enterprise Settings",
                "ai_configuration": "AI Configuration",
                "security_settings": "Security Settings",
                "audit_logs": "Audit Logs",
                "compliance": "Compliance"
            }
        }
        
        # Save translation file
        translation_file = f'translations/{lang_code}.json'
        with open(translation_file, 'w', encoding='utf-8') as f:
            json.dump(default_translations, f, ensure_ascii=False, indent=2)
        
        self.translations[lang_code] = default_translations
    
    def get_current_language(self) -> str:
        """Get current language from session or request"""
        # Check session first
        if hasattr(session, 'get') and session.get('language'):
            return session['language']
        
        # Check request headers
        if request and request.headers.get('Accept-Language'):
            accept_language = request.headers.get('Accept-Language')
            # Parse Accept-Language header
            for lang in accept_language.split(','):
                lang_code = lang.split(';')[0].strip().lower()
                if lang_code in self.supported_languages:
                    return lang_code
                # Check language without country code
                lang_base = lang_code.split('-')[0]
                if lang_base in self.supported_languages:
                    return lang_base
        
        return self.default_language
    
    def set_language(self, language: str) -> bool:
        """Set current language"""
        if language not in self.supported_languages:
            return False
        
        if hasattr(session, '__setitem__'):
            session['language'] = language
        return True
    
    def gettext(self, text: str, **kwargs) -> str:
        """Get translated text"""
        current_lang = self.get_current_language()
        
        # If English or no translation available, return original text
        if current_lang == 'en' or current_lang not in self.translations:
            return text.format(**kwargs) if kwargs else text
        
        # Try to find translation
        translation = self.translations[current_lang]
        
        # Split text by dots to handle nested keys
        keys = text.split('.')
        for key in keys:
            if isinstance(translation, dict) and key in translation:
                translation = translation[key]
            else:
                # Translation not found, return original text
                return text.format(**kwargs) if kwargs else text
        
        # Return translated text with formatting
        return translation.format(**kwargs) if kwargs else translation
    
    def ngettext(self, singular: str, plural: str, count: int, **kwargs) -> str:
        """Get translated text with pluralization"""
        if count == 1:
            return self.gettext(singular, **kwargs)
        else:
            return self.gettext(plural, **kwargs)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return self.supported_languages
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name by code"""
        return self.supported_languages.get(lang_code, lang_code)
    
    def add_translation(self, lang_code: str, key: str, value: str):
        """Add or update translation"""
        if lang_code not in self.translations:
            self.translations[lang_code] = {}
        
        # Split key by dots to handle nested structure
        keys = key.split('.')
        current = self.translations[lang_code]
        
        for i, key_part in enumerate(keys[:-1]):
            if key_part not in current:
                current[key_part] = {}
            current = current[key_part]
        
        current[keys[-1]] = value
        
        # Save to file
        self.save_translations(lang_code)
    
    def save_translations(self, lang_code: str):
        """Save translations to file"""
        try:
            translation_file = f'translations/{lang_code}.json'
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations[lang_code], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to save translations for {lang_code}: {e}")
    
    def get_translation_keys(self, lang_code: str = None) -> list:
        """Get all translation keys for a language"""
        if lang_code is None:
            lang_code = self.get_current_language()
        
        if lang_code not in self.translations:
            return []
        
        def extract_keys(translations, prefix=""):
            keys = []
            for key, value in translations.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    keys.extend(extract_keys(value, full_key))
                else:
                    keys.append(full_key)
            return keys
        
        return extract_keys(self.translations[lang_code])
    
    def get_missing_translations(self, lang_code: str) -> list:
        """Get missing translations for a language"""
        if lang_code == 'en':
            return []
        
        en_keys = set(self.get_translation_keys('en'))
        lang_keys = set(self.get_translation_keys(lang_code))
        
        return list(en_keys - lang_keys)
    
    def export_translations(self, lang_code: str) -> Dict[str, Any]:
        """Export translations for a language"""
        return self.translations.get(lang_code, {})
    
    def import_translations(self, lang_code: str, translations: Dict[str, Any]):
        """Import translations for a language"""
        self.translations[lang_code] = translations
        self.save_translations(lang_code)

# Global i18n manager instance
i18n_manager = I18nManager()

def init_i18n_manager(app):
    """Initialize i18n manager with Flask app"""
    global i18n_manager
    i18n_manager = I18nManager(app)
    return i18n_manager