from src.security_analyzer import SecurityAnalyzer
from src.reasoning.llm_engine import LLMEngine
from src.reasoning.mock_llm_engine import MockLLMEngine

import json

def print_findings(findings):
    """Print findings in a readable format"""
    for i, finding in enumerate(findings):
        print(f"\n[Finding {i+1}] {finding.get('type')} - {finding.get('subtype', '')}")
        print(f"CWE: {finding.get('cwe', 'Unknown')}")
        print(f"Line: {finding.get('line', 'Unknown')}")
        print(f"Source: {finding.get('source', 'Unknown')}")
        print(f"Description: {finding.get('description', '')}")
        
        if "code" in finding:
            print(f"Code: {finding.get('code')}")
        
        if "fix" in finding:
            print(f"Fix: {finding.get('fix')}")
        
        if "nvd_info" in finding and "examples" in finding["nvd_info"]:
            examples = finding["nvd_info"]["examples"]
            if examples:
                print(f"NVD Example: {examples[0].get('id', '')}")
                print(f"Severity: {examples[0].get('severity', 'Unknown')} (Score: {examples[0].get('score', 'Unknown')})")

def test_basic_xss():
    """Test detection of basic XSS vulnerabilities"""
    print("\n=== Testing Basic XSS Detection ===\n")
    
    html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>XSS Test</title>
</head>
<body>
    <h1>Welcome</h1>
    <div id="content">
        <script>
            // This is vulnerable to XSS
            document.write(location.hash.substring(1));
        </script>
    </div>
</body>
</html>
    """
    
    # Create analyzer with mock LLM
    analyzer = SecurityAnalyzer(MockLLMEngine())
    
    # Analyze HTML
    result = analyzer.analyze_html(html_code)
    
    # Print results
    print(f"Total findings: {result['summary']['total_findings']}")
    print(f"- Pattern findings: {result['summary']['pattern_findings']}")
    print(f"- LLM findings: {result['summary']['llm_findings']}")
    print(f"- Unique findings: {result['summary']['unique_findings']}")
    print(f"- Total time: {result['summary']['timing']['total_time']:.2f} seconds")
    
    print_findings(result["findings"])

def test_reflected_xss():
    """Test detection of reflected XSS"""
    print("\n=== Testing Reflected XSS Detection ===\n")
    
    html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>Login Form</title>
</head>
<body>
    <h1>Login</h1>
    <form action="process.php" method="POST">
        <input type="text" name="username" value="<?php echo $_GET['user']; ?>">
        <input type="password" name="password">
        <button type="submit">Login</button>
    </form>
</body>
</html>
    """
    
    analyzer = SecurityAnalyzer(MockLLMEngine())
    result = analyzer.analyze_html(html_code)
    
    print(f"Total findings: {result['summary']['total_findings']}")
    print_findings(result["findings"])

def test_csrf():
    """Test detection of CSRF vulnerabilities"""
    print("\n=== Testing CSRF Detection ===\n")
    
    html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>Transfer Funds</title>
</head>
<body>
    <h1>Transfer Funds</h1>
    <form action="/transfer.php" method="POST">
        <input type="text" name="amount" placeholder="Amount">
        <input type="text" name="destination" placeholder="Destination Account">
        <button type="submit">Transfer</button>
    </form>
</body>
</html>
    """
    
    analyzer = SecurityAnalyzer(MockLLMEngine())
    result = analyzer.analyze_html(html_code)
    
    print(f"Total findings: {result['summary']['total_findings']}")
    print_findings(result["findings"])

def test_subtle_xss():
    """Test detection of subtle XSS that pattern matching might miss"""
    print("\n=== Testing Subtle XSS Detection ===\n")
    
    html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>Theme Test</title>
</head>
<body>
    <div id="welcome"></div>
    <script>
        // Load user preferences
        function loadPreferences() {
            let theme = window.name;
            if (theme) {
                // Apply theme from window.name (not properly sanitized)
                document.getElementById('welcome').innerHTML = 
                    '<div class="' + theme + '">Welcome back!</div>';
            }
        }
        window.onload = loadPreferences;
    </script>
</body>
</html>
    """
    
    analyzer = SecurityAnalyzer(MockLLMEngine())
    result = analyzer.analyze_html(html_code)
    
    print(f"Total findings: {result['summary']['total_findings']}")
    print(f"- Pattern findings: {result['summary']['pattern_findings']}")
    print(f"- LLM findings: {result['summary']['llm_findings']}")
    
    print_findings(result["findings"])

def main():
    """Run all tests"""
    test_basic_xss()
    test_reflected_xss()
    test_csrf()
    test_subtle_xss()

if __name__ == "__main__":
    main()