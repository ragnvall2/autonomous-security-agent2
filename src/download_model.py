#!/usr/bin/env python3
import os
import sys
import argparse
import yaml

def check_model():
    """Check if the model exists and update config"""
    models_dir = "models"
    model_file = "Meta-Llama-3-8B.Q4_K_M.gguf"  # or "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
    model_path = os.path.join(models_dir, model_file)
    
    if os.path.exists(model_path):
        print(f"✅ Model found at {model_path}")
        update_config(model_path)
        return True
    else:
        print("❌ Model not found!")
        print("\nTo download the model, run:")
        print(f"huggingface-cli download QuantFactory/Meta-Llama-3-8B-GGUF --include \"{model_file}\" --local-dir ./models")
        print("\nOr download manually from:")
        print("https://huggingface.co/QuantFactory/Meta-Llama-3-8B-GGUF")
        return False

def update_config(model_path):
    """Update the configuration file with the model path"""
    config_path = "config/settings.yaml"
    os.makedirs("config", exist_ok=True)
    
    default_config = {
        "navigator": {
            "headless": False,
            "timeout": 30000,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        },
        "llm": {
            "model_path": model_path,
            "context_window": 4096,
            "temperature": 0.1,
            "max_tokens": 1024
        },
        "security": {
            "zap_path": "",
            "scan_timeout": 300,
            "risk_threshold": "medium"
        }
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            config['llm']['model_path'] = model_path
        except Exception as e:
            print(f"Error reading config file: {e}")
            config = default_config
    else:
        config = default_config
    
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        print(f"✅ Updated config file with model path: {model_path}")
    except Exception as e:
        print(f"❌ Error updating config file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Check for LLM model for Autonomous Security Agent")
    args = parser.parse_args()
    
    if check_model():
        print("\n" + "=" * 80)
        print("You're all set! You can now use the Autonomous Security Agent.")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("Please download the model following the instructions above.")
        print("=" * 80)

if __name__ == "__main__":
    main()