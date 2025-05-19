#!/usr/bin/env python3
import os
import sys
import requests
import argparse
from tqdm import tqdm
import hashlib
import yaml

# Define model options
MODELS = {
    "llama3-8b": {
        "url": "https://github.com/YOUR_USERNAME/YOUR_REPO/releases/download/v1.0/llama-3-8b.Q4_K_M.gguf",
        "file_name": "llama-3-8b.Q4_K_M.gguf",
        "size_mb": 4500,
        "sha256": "ADD_HASH_HERE_AFTER_UPLOAD",  # Add the SHA256 hash after uploading to GitHub Releases
        "description": "Llama 3 8B (Q4_K_M quantized) - Best balance of performance and quality"
    },
    "mistral-7b": {
        "url": "https://github.com/YOUR_USERNAME/YOUR_REPO/releases/download/v1.0/mistral-7b-v0.1.Q4_K_M.gguf",
        "file_name": "mistral-7b-v0.1.Q4_K_M.gguf",
        "size_mb": 4100,
        "sha256": "ADD_HASH_HERE_AFTER_UPLOAD",  # Add the SHA256 hash after uploading to GitHub Releases
        "description": "Mistral 7B (Q4_K_M quantized) - Strong performance for specialized tasks"
    },
    "phi-2": {
        "url": "https://github.com/YOUR_USERNAME/YOUR_REPO/releases/download/v1.0/phi-2.Q4_K_M.gguf",
        "file_name": "phi-2.Q4_K_M.gguf", 
        "size_mb": 1500,
        "sha256": "ADD_HASH_HERE_AFTER_UPLOAD",  # Add the SHA256 hash after uploading to GitHub Releases
        "description": "Phi-2 (Q4_K_M quantized) - Smaller model with good performance for basic tasks"
    }
}

def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash in chunks for large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def download_model(model_info, save_path, verify_hash=True):
    """Download a model file with a progress bar"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    print(f"Downloading {model_info['file_name']} ({model_info['size_mb']} MB)...")
    print(f"Model description: {model_info['description']}")
    print(f"This may take a while depending on your internet connection.")
    
    try:
        # Make a streaming request to the URL
        with requests.get(model_info['url'], stream=True) as response:
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Get the total file size (use the content-length header if available)
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0:
                total_size = model_info['size_mb'] * 1024 * 1024  # Estimate based on size_mb
            
            # Download with progress bar
            block_size = 1024 * 1024  # 1 MB chunks
            
            with open(save_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
        
        print(f"\nDownload complete: {save_path}")
        
        # Verify hash if needed and if hash is provided
        if verify_hash and model_info['sha256'] != "ADD_HASH_HERE_AFTER_UPLOAD":
            print("Verifying file integrity...")
            file_hash = calculate_sha256(save_path)
            if file_hash == model_info['sha256']:
                print("✅ Hash verification successful!")
            else:
                print("⚠️ Warning: File hash does not match expected value.")
                print(f"Expected: {model_info['sha256']}")
                print(f"Got:      {file_hash}")
                print("The file may be corrupted or incomplete.")
                return False
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if e.response.status_code == 404:
            print("\nThe model file was not found. This could be because:")
            print("1. You haven't uploaded the model to GitHub Releases yet")
            print("2. The URL in the script needs to be updated")
            print(f"\nPlease check: {model_info['url']}")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Failed to establish connection.")
        print("Please check your internet connection and try again.")
        return False
    except requests.exceptions.Timeout:
        print("\n❌ Timeout Error: The request timed out.")
        print("The server might be under heavy load. Please try again later.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error downloading file: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        # Remove the partially downloaded file
        if os.path.exists(save_path):
            os.remove(save_path)
        return False

def update_config(model_path):
    """Update the configuration file with the model path"""
    config_path = "config/settings.yaml"
    
    # Check if config directory exists
    os.makedirs("config", exist_ok=True)
    
    # Default config if file doesn't exist
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
    
    # Try to load existing config
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update only the model path
            config['llm']['model_path'] = model_path
        except Exception as e:
            print(f"Error reading config file: {e}")
            print("Creating new config file...")
            config = default_config
    else:
        config = default_config
    
    # Write the updated config
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        print(f"✅ Updated config file with model path: {model_path}")
    except Exception as e:
        print(f"❌ Error updating config file: {e}")

def list_models():
    """List available models with their details"""
    print("\nAvailable models:")
    print("-" * 80)
    for name, info in MODELS.items():
        print(f"{name}:")
        print(f"  Description: {info['description']}")
        print(f"  Size: {info['size_mb']} MB")
        print(f"  Filename: {info['file_name']}")
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description="Download LLM model for Autonomous Security Agent")
    parser.add_argument("--model", type=str, choices=list(MODELS.keys()), default="llama3-8b",
                        help="Which model to download")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--skip-verify", action="store_true", help="Skip hash verification")
    parser.add_argument("--force", action="store_true", help="Force download even if file exists")
    args = parser.parse_args()
    
    if args.list:
        list_models()
        return
    
    # Get model info
    model_info = MODELS[args.model]
    models_dir = "models"
    save_path = os.path.join(models_dir, model_info['file_name'])
    
    # Check if model already exists
    if os.path.exists(save_path) and not args.force:
        print(f"Model already exists at {save_path}")
        update_config(save_path)
        return
    
    # Download the model
    success = download_model(model_info, save_path, not args.skip_verify)
    
    if success:
        # Update config with model path
        update_config(save_path)
        
        print("\n" + "=" * 80)
        print("Model downloaded successfully!")
        print("You can now use the Autonomous Security Agent with this model.")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("Failed to download model.")
        print("Please check the error messages above and try again.")
        print("=" * 80)

if __name__ == "__main__":
    main()