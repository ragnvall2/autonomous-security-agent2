#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import shutil
import platform
import urllib.request
from pathlib import Path
import time

def simple_progress_bar(count, total, status=''):
    """Simple progress bar without external dependencies"""
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def check_for_python():
    """Check if Python is installed with required version"""
    min_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < min_version:
        print(f"Error: Python {min_version[0]}.{min_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        sys.exit(1)
    
    return True

def create_venv():
    """Create a virtual environment"""
    venv_dir = "venv"
    
    # Check if venv already exists
    if os.path.exists(venv_dir):
        print(f"✅ Virtual environment already exists at {venv_dir}")
        return venv_dir
    
    print(f"Creating virtual environment in {venv_dir}...")
    subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    print(f"✅ Virtual environment created at {venv_dir}")
    return venv_dir

def get_venv_python_path(venv_dir):
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        return os.path.join(venv_dir, "bin", "python")

def get_venv_pip_path(venv_dir):
    """Get the path to pip in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_dir, "bin", "pip")

def install_dependencies(venv_pip):
    """Install dependencies using pip"""
    print("Installing dependencies...")
    
    # List of dependencies
    dependencies = [
        "playwright==1.42.0",
        "llama-cpp-python==0.2.38",
        "pyyaml==6.0.1",
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "python-owasp-zap-v2.4==0.0.20",
        "pytest==7.4.3",
        "python-dotenv==1.0.0",
        "tqdm==4.66.1",
        "requests==2.31.0"
    ]
    
    # Create requirements.txt
    with open("requirements.txt", "w") as f:
        f.write("\n".join(dependencies))
    
    # Install dependencies
    subprocess.run([venv_pip, "install", "-r", "requirements.txt"], check=True)
    print("✅ All dependencies installed successfully")

def install_playwright_browsers(venv_python):
    """Install Playwright browsers"""
    print("Installing Playwright browsers...")
    subprocess.run([venv_python, "-m", "playwright", "install", "chromium"], check=True)
    print("✅ Playwright browsers installed successfully")

def download_file(url, destination):
    """Download a file with a simple progress bar"""
    print(f"Downloading from {url}...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    try:
        # Open a connection to the URL
        with urllib.request.urlopen(url) as response:
            # Get the total file size
            file_size = int(response.info().get('Content-Length', -1))
            
            # Initialize variables for the progress bar
            downloaded = 0
            block_size = 1024 * 1024  # 1 MB chunks
            start_time = time.time()
            
            # Open the destination file
            with open(destination, 'wb') as f:
                while True:
                    # Read a block of data
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    
                    # Write the data to the file
                    f.write(buffer)
                    
                    # Update the progress bar
                    downloaded += len(buffer)
                    if file_size > 0:  # Only show progress bar if file size is known
                        elapsed_time = time.time() - start_time
                        speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                        status = f"{downloaded / (1024*1024):.1f} MB / {file_size / (1024*1024):.1f} MB - {speed / (1024*1024):.1f} MB/s"
                        simple_progress_bar(downloaded, file_size, status)
            
            print("\nDownload completed successfully.")
            return True
    except Exception as e:
        print(f"\nError downloading file: {e}")
        return False

def download_model(model_name, models_dir):
    """Download the LLM model"""
    # Create models directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)
    
    # Model URLs
    model_urls = {
        "llama3-8b": "https://huggingface.co/TheBloke/Llama-3-8B-GGUF/resolve/main/llama-3-8b.Q4_K_M.gguf",
        "mistral-7b": "https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf"
    }
    
    if model_name not in model_urls:
        print(f"Available models: {', '.join(model_urls.keys())}")
        return False
    
    model_url = model_urls[model_name]
    file_name = os.path.basename(model_url)
    save_path = os.path.join(models_dir, file_name)
    
    # Check if model already exists
    if os.path.exists(save_path):
        print(f"✅ Model already exists at {save_path}")
        return save_path
    
    # Download the model
    if download_file(model_url, save_path):
        print(f"✅ Model downloaded successfully to {save_path}")
        return save_path
    else:
        print("❌ Failed to download model")
        return False

def create_directory_structure():
    """Create the project directory structure"""
    print("Creating project directory structure...")
    
    directories = [
        "src/navigator",
        "src/reasoning",
        "src/security",
        "src/utils",
        "tests",
        "examples",
        "models",
        "config"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create __init__.py files in Python packages
        if directory.startswith("src"):
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    f.write("# Package initialization\n")
    
    print("✅ Directory structure created successfully")

def create_config_files(model_path):
    """Create configuration files"""
    print("Creating configuration files...")
    
    config_dir = "config"
    os.makedirs(config_dir, exist_ok=True)
    
    # Create settings.yaml
    settings_path = os.path.join(config_dir, "settings.yaml")
    if not os.path.exists(settings_path):
        with open(settings_path, "w") as f:
            f.write(f"""navigator:
  headless: false
  timeout: 30000
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"

llm:
  model_path: "{model_path}"
  context_window: 4096
  temperature: 0.1
  max_tokens: 1024

security:
  zap_path: ""  # Path to ZAP installation
  scan_timeout: 300
  risk_threshold: "medium"
""")
    
    # Create .gitignore file
    gitignore_path = ".gitignore"
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Models
models/*.gguf
models/*.bin

# IDE files
.idea/
.vscode/
*.swp
*.swo

# Log files
*.log
logs/

# Security scan results
scan_results/

# Config files with sensitive info
.env
""")
    
    print("✅ Configuration files created successfully")

def create_activation_script(venv_dir):
    """Create activation scripts for Windows and Unix"""
    print("Creating activation scripts...")
    
    # Create run.bat for Windows
    with open("run.bat", "w") as f:
        f.write(f"""@echo off
call {venv_dir}\\Scripts\\activate.bat
echo Virtual environment activated. You can now run project scripts.
cmd /k
""")
    
    # Create run.sh for Unix
    with open("run.sh", "w") as f:
        f.write(f"""#!/bin/bash
source {venv_dir}/bin/activate
echo "Virtual environment activated. You can now run project scripts."
exec $SHELL
""")
    
    # Make run.sh executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod("run.sh", 0o755)
    
    print("✅ Activation scripts created successfully")

def create_example_script():
    """Create a basic example script"""
    examples_dir = "examples"
    os.makedirs(examples_dir, exist_ok=True)
    
    example_path = os.path.join(examples_dir, "basic_navigation.py")
    if not os.path.exists(example_path):
        with open(example_path, "w") as f:
            f.write("""#!/usr/bin/env python3
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.navigator.web_navigator import WebNavigator
from src.reasoning.llm_engine import LLMEngine

def main():
    # Initialize components
    navigator = WebNavigator()
    llm_engine = LLMEngine()
    
    # Start navigation
    start_url = "https://owasp.org/www-project-top-ten/"
    print(f"Navigating to {start_url}")
    
    # Navigate to start URL
    page_context = navigator.navigate_to(start_url)
    
    # Get instruction from user
    instruction = "Find information about Cross-Site Scripting (XSS) vulnerabilities"
    print(f"Instruction: {instruction}")
    
    # Get navigation action from LLM
    action = llm_engine.get_navigation_action(page_context, instruction)
    print(f"LLM Action: {action}")
    
    # Execute the action and continue navigation
    # (This would be extended in a real implementation)
    
    # Clean up
    navigator.close()

if __name__ == "__main__":
    main()
""")
    print("✅ Example script created successfully")

def create_core_component_files():
    """Create the core component files"""
    # Create WebNavigator class
    nav_path = "src/navigator/web_navigator.py"
    if not os.path.exists(nav_path):
        with open(nav_path, "w") as f:
            f.write("""#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import yaml
import os

class WebNavigator:
    def __init__(self, config_path="config/settings.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.browser = None
        self.page = None
        self.context = []  # For storing navigation history
        
    def start_browser(self):
        # Launch browser and create new page
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.config['navigator']['headless']
        )
        self.page = self.browser.new_page(
            user_agent=self.config['navigator']['user_agent']
        )
        self.page.set_default_timeout(self.config['navigator']['timeout'])
        
    def navigate_to(self, url):
        # Navigate to the specified URL
        if not self.browser:
            self.start_browser()
        self.page.goto(url)
        self.update_context()
        return self.context[-1]
        
    def update_context(self):
        # Extract page content and structure
        title = self.page.title()
        current_url = self.page.url
        
        # Extract interactive elements
        elements_data = self._extract_interactive_elements()
        
        # Update context with new information
        self.context.append({
            "url": current_url,
            "title": title,
            "elements": elements_data
        })
        
    def _extract_interactive_elements(self):
        # Extract interactive elements from the page
        elements_data = []
        
        # Extract clickable elements
        clickable_selectors = 'a, button, [role="button"], input[type="submit"]'
        clickable_elements = self.page.query_selector_all(clickable_selectors)
        
        for i, element in enumerate(clickable_elements):
            try:
                text = element.inner_text().strip()
                tag = element.evaluate('el => el.tagName')
                href = element.get_attribute('href') if tag == 'A' else None
                
                # Only include visible elements with text or href
                if text or href:
                    elements_data.append({
                        "id": i,
                        "text": text,
                        "tag": tag,
                        "href": href
                    })
            except:
                pass
                
        # Extract form inputs
        input_selectors = 'input:not([type="submit"]), textarea, select'
        input_elements = self.page.query_selector_all(input_selectors)
        
        for i, element in enumerate(input_elements):
            try:
                input_type = element.get_attribute('type') or 'text'
                name = element.get_attribute('name') or ''
                placeholder = element.get_attribute('placeholder') or ''
                
                elements_data.append({
                    "id": len(clickable_elements) + i,
                    "tag": element.evaluate('el => el.tagName'),
                    "type": input_type,
                    "name": name,
                    "placeholder": placeholder
                })
            except:
                pass
                
        return elements_data
        
    def close(self):
        # Close browser and playwright
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
""")
    
    # Create LLM Engine class
    llm_path = "src/reasoning/llm_engine.py"
    if not os.path.exists(llm_path):
        with open(llm_path, "w") as f:
            f.write("""#!/usr/bin/env python3
from llama_cpp import Llama
import json
import yaml

class LLMEngine:
    def __init__(self, config_path="config/settings.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize the LLM
        self.llm = Llama(
            model_path=self.config['llm']['model_path'],
            n_ctx=self.config['llm']['context_window'],
            n_threads=4
        )
        
    def get_navigation_action(self, page_context, instruction):
        # Ask LLM what action to take based on current page context
        prompt = self._create_navigation_prompt(page_context, instruction)
        
        response = self.llm(
            prompt,
            max_tokens=self.config['llm']['max_tokens'],
            temperature=self.config['llm']['temperature'],
            stop=["```"]
        )
        
        # Extract JSON from response
        try:
            response_text = response['choices'][0]['text']
            # Find JSON block in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"error": "No valid JSON found in response"}
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response"}
        
    def _create_navigation_prompt(self, page_context, instruction):
        # Create prompt for navigation decision
        return f'''
        You are an autonomous web navigation agent. Based on the current webpage and the instruction,
        decide what action to take next.
        
        Current webpage: {page_context['title']} ({page_context['url']})
        
        Available elements:
        {json.dumps(page_context['elements'], indent=2)}
        
        Instruction: {instruction}
        
        Respond with a JSON object using this format:
        ```json
        {{
            "action": "click" or "type" or "wait" or "extract",
            "element_id": ID of the element to interact with (if applicable),
            "input_text": Text to type (if action is "type"),
            "reason": Brief explanation of your decision
        }}
        ```
        '''
""")
    
    print("✅ Core component files created successfully")

def create_readme():
    """Create README.md file"""
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write("""# Autonomous Security Agent

An AI-powered security agent that autonomously navigates websites, detects vulnerabilities, and provides improvement recommendations.

## Project Overview

This project combines open-source language models with web automation frameworks and security scanning tools to create a cutting-edge solution for web security assessment.

## Setup

Simply run the setup script:

```bash
python setup.py""")