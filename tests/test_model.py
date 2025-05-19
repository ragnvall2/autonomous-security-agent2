#!/usr/bin/env python3
import os
import sys
import time
import yaml
import json
from datetime import datetime
from pathlib import Path

# Add the project root to the path so we can import modules correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Import your LLM engine class - adjust this path based on your actual implementation
try:
    # Assuming your LLMEngine is in src/reasoning/llm_engine.py
    from src.reasoning.llm_engine import LLMEngine
except ImportError:
    print("Error: Could not import LLMEngine. Make sure your project structure is set up correctly.")
    sys.exit(1)

# Configuration
CONFIG_PATH = os.path.join(project_root, "config/settings.yaml")
OUTPUT_DIR = os.path.join(project_root, "tests/results")
TIMEOUT = 120  # Maximum time for each test in seconds

# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "XSS Vulnerability Detection",
        "prompt": """
        Analyze this HTML code for potential XSS vulnerabilities:
        
        <div class="user-profile">
            <h1>Welcome, <script>document.write(localStorage.getItem('username'))</script>!</h1>
            <div class="content">
                Your profile was last updated on: 
                <span id="last-login"></span>
            </div>
            <script>
                document.getElementById('last-login').innerHTML = new URLSearchParams(window.location.search).get('last_login');
            </script>
        </div>
        
        Identify all XSS vulnerabilities, explain why they are vulnerabilities, and suggest fixes.
        """,
        "expected_topics": ["reflected XSS", "DOM-based XSS", "user input sanitization"]
    },
    {
        "name": "SQL Injection Detection",
        "prompt": """
        Review this PHP code for SQL injection vulnerabilities:
        
        ```php
        <?php
        $username = $_POST['username'];
        $password = $_POST['password'];
        
        $query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
        $result = mysqli_query($conn, $query);
        
        if(mysqli_num_rows($result) > 0) {
            echo "Login successful!";
            // Set session variables and redirect
        } else {
            echo "Invalid credentials!";
        }
        ?>
        ```
        
        Identify any SQL injection vulnerabilities, explain the risks, and provide a secure implementation.
        """,
        "expected_topics": ["SQL injection", "parameterized queries", "prepared statements", "input validation"]
    },
    {
        "name": "CSRF Vulnerability Analysis",
        "prompt": """
        Analyze this web form for CSRF vulnerabilities:
        
        ```html
        <form action="/transfer_funds.php" method="POST">
            <input type="text" name="amount" placeholder="Amount">
            <input type="text" name="destination_account" placeholder="Destination Account">
            <button type="submit">Transfer</button>
        </form>
        ```
        
        Identify if there are any CSRF vulnerabilities, explain the risks, and provide recommendations to fix them.
        """,
        "expected_topics": ["CSRF token", "origin validation", "SameSite cookies"]
    },
    {
        "name": "Security Header Analysis",
        "prompt": """
        Analyze these HTTP response headers for security issues:
        
        ```
        HTTP/1.1 200 OK
        Date: Mon, 23 May 2025 12:34:56 GMT
        Server: Apache/2.4.41 (Ubuntu)
        Content-Type: text/html; charset=UTF-8
        Cache-Control: no-store, no-cache
        X-Powered-By: PHP/7.4.3
        ```
        
        Identify missing security headers and explain which headers should be added and why.
        """,
        "expected_topics": ["Content-Security-Policy", "X-Frame-Options", "X-XSS-Protection", "Strict-Transport-Security"]
    },
    {
        "name": "API Security Analysis",
        "prompt": """
        Review this Node.js API endpoint for security issues:
        
        ```javascript
        app.get('/api/users/:id', (req, res) => {
            const userId = req.params.id;
            const userRecord = db.findUserById(userId);
            
            if (userRecord) {
                res.json({
                    id: userRecord.id,
                    username: userRecord.username,
                    email: userRecord.email,
                    role: userRecord.role,
                    apiKey: userRecord.apiKey,
                    lastLogin: userRecord.lastLogin
                });
            } else {
                res.status(404).json({error: "User not found"});
            }
        });
        ```
        
        Identify any security issues and provide recommendations for a more secure implementation.
        """,
        "expected_topics": ["authorization", "excessive data exposure", "sensitive data", "access control"]
    },
    {
        "name": "Website Vulnerability Analysis",
        "prompt": """
        You are a security agent analyzing a login page at https://example.com/login.
        
        The page contains:
        1. A form with username and password fields
        2. A "Remember me" checkbox
        3. A "Forgot password" link
        4. The form submits to /login.php
        5. The page is served over HTTPS
        
        Based on this information, what potential security vulnerabilities should I look for?
        Provide a comprehensive analysis of possible security issues and how I might test for them.
        """,
        "expected_topics": ["brute force protection", "account lockout", "password policies", "HTTPS validation"]
    },
    {
        "name": "Security Recommendation Generation",
        "prompt": """
        The client has a WordPress website with the following characteristics:
        - Running WordPress 5.8.1
        - Has 15 plugins installed, some not updated for over a year
        - Uses a custom theme
        - Hosted on shared hosting
        - Accepts credit card payments through a plugin
        - Has user registration enabled
        
        Generate a comprehensive security recommendation report with specific, actionable items to improve the website's security.
        """,
        "expected_topics": ["WordPress updates", "plugin vulnerabilities", "payment security", "PCI compliance"]
    }
]

def load_config():
    """Load configuration from the config file"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def init_llm_engine(model_path):
    """Initialize the LLM engine with the specified model"""
    try:
        # You might need to adjust these parameters based on your LLMEngine implementation
        engine = LLMEngine(
            model_path=model_path,
            temperature=0.1,  # Lower temperature for more focused, deterministic responses
            max_tokens=2048
        )
        return engine
    except Exception as e:
        print(f"Error initializing LLM engine: {e}")
        return None

def run_test(engine, scenario, index):
    """Run a single test scenario"""
    print(f"\n[{index+1}/{len(TEST_SCENARIOS)}] Testing: {scenario['name']}")
    print("-" * 80)
    
    start_time = time.time()
    try:
        # Set a timeout for the test
        response = engine.generate(scenario['prompt'])
        elapsed_time = time.time() - start_time
        
        # Check if expected topics are present in the response
        topics_found = []
        for topic in scenario['expected_topics']:
            if topic.lower() in response.lower():
                topics_found.append(topic)
        
        coverage = len(topics_found) / len(scenario['expected_topics']) * 100
        
        result = {
            "name": scenario['name'],
            "success": True,
            "response": response,
            "elapsed_time": elapsed_time,
            "topics_found": topics_found,
            "topics_coverage": f"{coverage:.1f}%",
            "topics_missing": [t for t in scenario['expected_topics'] if t not in topics_found]
        }
        
        print(f"✅ Test completed in {elapsed_time:.2f} seconds")
        print(f"Topics coverage: {coverage:.1f}%")
        if result['topics_missing']:
            print(f"Missing topics: {', '.join(result['topics_missing'])}")
        
    except Exception as e:
        result = {
            "name": scenario['name'],
            "success": False,
            "error": str(e),
            "elapsed_time": time.time() - start_time
        }
        print(f"❌ Test failed: {e}")
    
    return result

def save_results(results):
    """Save test results to a file"""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTPUT_DIR}/model_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {filename}")
    return filename

def print_summary(results):
    """Print a summary of the test results"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    successful_tests = sum(1 for r in results['scenarios'] if r['success'])
    total_tests = len(results['scenarios'])
    
    print(f"Model: {results['model_info']['name']}")
    print(f"Tests completed: {successful_tests}/{total_tests}")
    
    if successful_tests > 0:
        # Calculate average time
        avg_time = sum(r['elapsed_time'] for r in results['scenarios'] if r['success']) / successful_tests
        print(f"Average response time: {avg_time:.2f} seconds")
        
        # Calculate average topic coverage
        coverage_values = [float(r['topics_coverage'].strip('%')) for r in results['scenarios'] 
                          if r['success'] and 'topics_coverage' in r]
        if coverage_values:
            avg_coverage = sum(coverage_values) / len(coverage_values)
            print(f"Average topic coverage: {avg_coverage:.1f}%")
    
    print("\nPer-scenario results:")
    for i, scenario in enumerate(results['scenarios']):
        status = "✅" if scenario['success'] else "❌"
        name = scenario['name']
        coverage = scenario.get('topics_coverage', 'N/A')
        print(f"{status} {name} - Coverage: {coverage}")
    
    print("=" * 80)

def main():
    """Run model testing"""
    print("=" * 80)
    print("Llama 3 8B Instruct Model Testing for Security Analysis")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration. Please make sure your config file exists.")
        return
    
    model_path = config.get('llm', {}).get('model_path')
    if not model_path or not os.path.exists(model_path):
        print(f"Model path not found: {model_path}")
        print("Please make sure you've downloaded the model and updated your config.")
        return
    
    print(f"Using model: {model_path}")
    model_name = os.path.basename(model_path)
    
    # Initialize the LLM engine
    engine = init_llm_engine(model_path)
    if not engine:
        print("Failed to initialize LLM engine.")
        return
    
    # Prepare results container
    results = {
        "model_info": {
            "name": model_name,
            "path": model_path,
            "timestamp": datetime.now().isoformat()
        },
        "scenarios": []
    }
    
    # Run tests
    for i, scenario in enumerate(TEST_SCENARIOS):
        result = run_test(engine, scenario, i)
        results['scenarios'].append(result)
    
    # Save and summarize results
    results_file = save_results(results)
    print_summary(results)
    
    print(f"\nTest completed. You can view detailed results in {results_file}")

if __name__ == "__main__":
    main()