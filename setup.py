#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse

def check_python_version():
    """Check if Python version is compatible"""
    min_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < min_version:
        print(f"Error: Python {min_version[0]}.{min_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        sys.exit(1)
    
    return True

def setup_environment():
    """Set up a virtual environment and install dependencies"""
    venv_dir = "venv"
    
    # Check if venv already exists
    if os.path.exists(venv_dir):
        print(f"✅ Virtual environment already exists at {venv_dir}")
    else:
        print(f"Creating virtual environment in {venv_dir}...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print(f"✅ Virtual environment created")
    
    # Get path to pip in virtual environment
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
        python_path = os.path.join(venv_dir, "Scripts", "python")
    else:  # Unix/Mac
        pip_path = os.path.join(venv_dir, "bin", "pip")
        python_path = os.path.join(venv_dir, "bin", "python")
    
    print("Installing dependencies...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    print("✅ Dependencies installed")
    
    print("Installing Playwright browsers...")
    subprocess.run([python_path, "-m", "playwright", "install", "chromium"], check=True)
    print("✅ Playwright browsers installed")
    
    return venv_dir

def create_gitignore():
    """Create a comprehensive .gitignore file"""
    print("Creating .gitignore file...")
    
    gitignore_content = """# Virtual Environment
venv/
env/
ENV/

# Python bytecode
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Distribution / packaging
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
wheels/
*.egg-info/
.installed.cfg
*.egg

# Model files (large binary files)
models/*.gguf
models/*.bin
models/*.onnx
models/*.pt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# Environment variables and secrets
.env
.venv
.env.local
.env.*.local

# IDE files
.idea/
.vscode/
*.swp
*.swo
.DS_Store
.project
.pydevproject
.settings/

# Logs
*.log
logs/
log/

# Security scan results
scan_results/
reports/

# User-specific files
*.sublime-project
*.sublime-workspace
.history
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore file created")

def create_activation_scripts(venv_dir):
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
    if os.name != 'nt':
        os.chmod("run.sh", 0o755)
    
    print("✅ Activation scripts created")


def main():
    parser = argparse.ArgumentParser(description="Setup script for Autonomous Security Agent")
    parser.add_argument("--no-venv", action="store_true", help="Skip virtual environment creation")
    args = parser.parse_args()
    
    print("=" * 80)
    print("Autonomous Security Agent - Setup")
    print("=" * 80)
    
    # Check Python version
    check_python_version()
    
    # Create .gitignore file
    create_gitignore()
    
    if not args.no_venv:
        venv_dir = setup_environment()
        create_activation_scripts(venv_dir)
        
        # Remind about model download
        model_script = "download_model.py"
        if os.path.exists(model_script):
            print("\nDon't forget to download a model:")
            
            if os.name == 'nt':  # Windows
                print(f"1. Run 'run.bat' to activate the virtual environment")
                print(f"2. Run 'python {model_script} --list' to see available models")
                print(f"3. Run 'python {model_script}' to download the default model")
            else:  # Unix/Mac
                print(f"1. Run './run.sh' to activate the virtual environment")
                print(f"2. Run 'python {model_script} --list' to see available models")
                print(f"3. Run 'python {model_script}' to download the default model")
    else:
        print("Installing dependencies to global Python...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        
        # Remind about model download
        print("\nDon't forget to download a model:")
        print(f"Run 'python download_model.py' to download the default model")
    
    print("\n" + "=" * 80)
    print("Setup complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()