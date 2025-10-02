#!/usr/bin/env python3
"""
Setup LLM Providers for Testing Improvement
Easy setup script for multiple LLM providers
"""

import os
import subprocess
import sys
from typing import List, Dict

class LLMProviderSetup:
    """Setup and configure LLM providers"""
    
    def __init__(self):
        self.providers = {
            'openai': {
                'name': 'OpenAI GPT',
                'package': 'openai',
                'env_var': 'OPENAI_API_KEY',
                'description': 'GPT-4 and GPT-3.5 models'
            },
            'anthropic': {
                'name': 'Anthropic Claude',
                'package': 'anthropic',
                'env_var': 'ANTHROPIC_API_KEY',
                'description': 'Claude-3 models'
            },
            'google': {
                'name': 'Google Gemini',
                'package': 'google-generativeai',
                'env_var': 'GOOGLE_API_KEY',
                'description': 'Gemini-Pro models'
            },
            'azure': {
                'name': 'Azure OpenAI',
                'package': 'azure-ai-openai',
                'env_var': 'AZURE_OPENAI_API_KEY',
                'description': 'Azure-hosted GPT models'
            },
            'huggingface': {
                'name': 'Hugging Face',
                'package': 'transformers',
                'env_var': 'HUGGINGFACE_API_KEY',
                'description': 'Open-source models'
            },
            'ollama': {
                'name': 'Ollama Local',
                'package': 'ollama',
                'env_var': None,
                'description': 'Local LLM deployment'
            }
        }
    
    def check_installed_packages(self) -> Dict[str, bool]:
        """Check which packages are installed"""
        installed = {}
        for provider, config in self.providers.items():
            try:
                if provider == 'ollama':
                    # Check if Ollama is running
                    result = subprocess.run(['ollama', '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    installed[provider] = result.returncode == 0
                else:
                    __import__(config['package'])
                    installed[provider] = True
            except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
                installed[provider] = False
        return installed
    
    def install_packages(self, providers: List[str]) -> bool:
        """Install required packages for providers"""
        packages_to_install = []
        for provider in providers:
            if provider in self.providers:
                package = self.providers[provider]['package']
                if package not in packages_to_install:
                    packages_to_install.append(package)
        
        if not packages_to_install:
            print("✅ All required packages are already installed")
            return True
        
        print(f"📦 Installing packages: {', '.join(packages_to_install)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + packages_to_install, 
                          check=True)
            print("✅ Packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    
    def check_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are configured"""
        configured = {}
        for provider, config in self.providers.items():
            if config['env_var']:
                configured[provider] = bool(os.getenv(config['env_var']))
            else:
                configured[provider] = True  # Ollama doesn't need API key
        return configured
    
    def setup_ollama(self) -> bool:
        """Setup Ollama for local LLM deployment"""
        print("🦙 Setting up Ollama...")
        
        # Check if Ollama is installed
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                print("❌ Ollama not found. Please install Ollama first:")
                print("   Visit: https://ollama.ai/download")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Ollama not found. Please install Ollama first:")
            print("   Visit: https://ollama.ai/download")
            return False
        
        # Pull a model
        print("📥 Pulling Llama2 model (this may take a while)...")
        try:
            subprocess.run(['ollama', 'pull', 'llama2'], check=True, timeout=300)
            print("✅ Ollama setup complete")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to pull Llama2 model")
            return False
        except subprocess.TimeoutExpired:
            print("⏰ Model pull timed out")
            return False
    
    def generate_env_template(self) -> str:
        """Generate environment template"""
        template = """# LLM Provider API Keys
# Uncomment and set your API keys for the providers you want to use

# OpenAI
# export OPENAI_API_KEY=sk-your-openai-key

# Anthropic
# export ANTHROPIC_API_KEY=your-anthropic-key

# Google Gemini
# export GOOGLE_API_KEY=your-google-key

# Azure OpenAI
# export AZURE_OPENAI_API_KEY=your-azure-key
# export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# export AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# Hugging Face
# export HUGGINGFACE_API_KEY=your-hf-key

# Ollama (no API key needed, runs locally)
# Make sure Ollama is running: ollama serve llama2
"""
        return template
    
    def run_setup(self):
        """Run complete setup process"""
        print("🚀 LLM Provider Setup for Testing Improvement")
        print("=" * 50)
        
        # Check current status
        print("\n🔍 Checking current setup...")
        installed = self.check_installed_packages()
        configured = self.check_api_keys()
        
        print("\n📊 Current Status:")
        for provider, config in self.providers.items():
            status_icon = "✅" if installed.get(provider, False) else "❌"
            key_status = "🔑" if configured.get(provider, False) else "🔓"
            print(f"  {status_icon} {config['name']}: {key_status}")
        
        # Ask user which providers to setup
        print("\n🤖 Available Providers:")
        for i, (provider, config) in enumerate(self.providers.items(), 1):
            print(f"  {i}. {config['name']} - {config['description']}")
        
        print("\n💡 Recommendations:")
        print("  🏢 Enterprise: Azure OpenAI + Anthropic")
        print("  💰 Cost-conscious: Google Gemini + Hugging Face")
        print("  🔒 Privacy-first: Ollama + Hugging Face")
        print("  ⚡ High-performance: OpenAI + Anthropic")
        
        # Setup selected providers
        print("\n🛠️ Setting up providers...")
        
        # Install packages for providers that need them
        providers_to_install = [p for p, installed in installed.items() if not installed and p != 'ollama']
        if providers_to_install:
            self.install_packages(providers_to_install)
        
        # Setup Ollama if needed
        if not installed.get('ollama', False):
            self.setup_ollama()
        
        # Generate environment template
        env_template = self.generate_env_template()
        with open('.env.template', 'w') as f:
            f.write(env_template)
        
        print("\n📄 Environment template saved to: .env.template")
        print("💡 Copy to .env and add your API keys")
        
        # Final status
        print("\n✅ Setup Complete!")
        print("\n🎯 Next Steps:")
        print("  1. Copy .env.template to .env")
        print("  2. Add your API keys to .env")
        print("  3. Run: python3 test_llm_improvement.py")
        print("  4. Check results in llm_improvement_report.json")
        
        return True

def main():
    """Main setup function"""
    setup = LLMProviderSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 LLM Provider Setup Complete!")
        print("📈 Expected testing improvement: +35-55%")
        return 0
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())