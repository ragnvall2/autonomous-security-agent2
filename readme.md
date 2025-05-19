# Autonomous Security Agent

An AI-powered security agent that autonomously navigates websites, detects vulnerabilities, and provides improvement recommendations.

## Project Overview

This project combines open-source language models with web automation frameworks and security scanning tools to create a cutting-edge solution for web security assessment. Using the power of large language models, it can understand and interact with websites in a human-like way to discover potential security weaknesses.

## Features

- **Natural Language Web Navigation**: Navigate websites using AI-driven understanding of page structures
- **Security Vulnerability Detection**: Identify common web vulnerabilities (OWASP Top 10)
- **Autonomous Operation**: Minimal human intervention required during scanning
- **Detailed Reporting**: Generate comprehensive security reports with actionable recommendations

## Project Structure

```
autonomous-security-agent/
├── config/                 # Configuration files
├── examples/               # Example scripts and use cases
├── models/                 # Directory for LLM models (will be created)
├── src/                    # Source code
│   ├── navigator/          # Web navigation components
│   ├── reasoning/          # LLM reasoning engine
│   ├── security/           # Security scanning modules
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── download_model.py       # Script for downloading LLM models
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/autonomous-security-agent.git
cd autonomous-security-agent
```

### 2. Set up Python environment

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Playwright browsers

```bash
python -m playwright install chromium
```

### 4. Download the LLM model

```bash
# Download the default model (Llama 3 8B)
python download_model.py

# To see available models:
python download_model.py --list

# To download a specific model:
python download_model.py --model mistral-7b
```

## Usage

### Basic Example

```bash
# Run a basic example
python examples/basic_navigation.py
```

### Advanced Usage

```python
from src.navigator.web_navigator import WebNavigator
from src.reasoning.llm_engine import LLMEngine

# Initialize components
navigator = WebNavigator()
llm_engine = LLMEngine()

# Start navigation
url = "https://example-website.com"
page_context = navigator.navigate_to(url)

# Analyze the page for vulnerabilities
analysis = llm_engine.analyze_security(page_context)

# Print findings
print(analysis)

# Clean up
navigator.close()
```

## Available Models

| Model | Size | Description |
|-------|------|-------------|
| llama3-8b | 4.5 GB | Llama 3 8B (Q4_K_M quantized) - Best balance of performance and quality |
| mistral-7b | 4.1 GB | Mistral 7B (Q4_K_M quantized) - Strong performance for specialized tasks |
| phi-2 | 1.5 GB | Phi-2 (Q4_K_M quantized) - Smaller model with good performance for basic tasks |

## Configuration

You can customize the agent's behavior by editing the `config/settings.yaml` file:

```yaml
navigator:
  headless: false  # Run browser in headless mode
  timeout: 30000   # Page load timeout in milliseconds

llm:
  model_path: "models/llama-3-8b.Q4_K_M.gguf"
  context_window: 4096
  temperature: 0.1
  max_tokens: 1024

security:
  zap_path: ""     # Path to OWASP ZAP installation
  scan_timeout: 300
  risk_threshold: "medium"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Playwright](https://playwright.dev/) for web automation
- [Llama 3](https://huggingface.co/meta-llama/Llama-3-8B) and other models for reasoning capabilities
- [OWASP ZAP](https://www.zaproxy.org/) for security scanning functionality