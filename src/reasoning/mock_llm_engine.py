class MockLLMEngine:
    """Mock LLM Engine for testing without an actual LLM"""
    
    def __init__(self):
        """Initialize the mock LLM engine"""
        # Pre-defined responses for specific code patterns
        self.response_patterns = [
            {
                "pattern": r"document\.write\s*\(.*location",
                "response": """
VULNERABILITY 1:
Type: XSS
Subtype: DOM-based XSS
CWE: 79
Code: document.write(location.hash.substring(1))
Line: 3
Description: The code takes user-controlled data from the URL (location.hash) and writes it directly to the document using document.write without sanitization.
Fix: Use DOMPurify or similar library to sanitize user input: document.write(DOMPurify.sanitize(location.hash.substring(1)))
"""
            },
            {
                "pattern": r"<input[^>]*value\s*=\s*[\"']?\s*<\?php\s+echo\s+\$_GET",
                "response": """
VULNERABILITY 1:
Type: XSS
Subtype: Reflected XSS
CWE: 79
Code: <input type="text" name="username" value="<?php echo $_GET['user']; ?>">
Line: 2
Description: Unsanitized user input from a GET parameter is directly echoed into an HTML attribute, allowing for attribute escape and XSS attacks.
Fix: Use proper escaping: <input type="text" name="username" value="<?php echo htmlspecialchars($_GET['user'], ENT_QUOTES); ?>">
"""
            },
            {
                "pattern": r"<form[^>]*method\s*=\s*[\"']?\s*POST[\"']?[^>]*>(?!.*csrf)",
                "response": """
VULNERABILITY 1:
Type: CSRF
Subtype: Missing Token
CWE: 352
Code: <form action="process.php" method="POST">
Line: 1
Description: The form submits a POST request without a CSRF token, making it vulnerable to Cross-Site Request Forgery attacks.
Fix: Add a CSRF token: <input type="hidden" name="csrf_token" value="<?php echo generate_csrf_token(); ?>">
"""
            },
            {
                "pattern": r"<script>.*innerHTML\s*=",
                "response": """
VULNERABILITY 1:
Type: XSS
Subtype: DOM-based XSS
CWE: 79
Code: document.getElementById('welcome').innerHTML = '<div class="' + theme + '">Welcome back!</div>';
Line: 7
Description: User-controlled data from window.name is inserted into the DOM using innerHTML without sanitization.
Fix: Use textContent instead, or sanitize input: document.getElementById('welcome').innerHTML = '<div class="' + DOMPurify.sanitize(theme) + '">Welcome back!</div>';
"""
            }
        ]
        
        # Default response for code with no identified vulnerabilities
        self.default_response = "NO_VULNERABILITIES_FOUND"
    
    def generate(self, prompt):
        """Generate a response for the given prompt
        
        Args:
            prompt: The prompt to generate a response for
            
        Returns:
            A string response
        """
        # Extract HTML code from the prompt
        import re
        html_match = re.search(r"```html\s+(.*?)\s+```", prompt, re.DOTALL)
        if not html_match:
            return "NO_VULNERABILITIES_FOUND"
        
        html_code = html_match.group(1)
        
        # Check for each response pattern
        for pattern in self.response_patterns:
            if re.search(pattern["pattern"], html_code, re.DOTALL):
                return pattern["response"]
        
        # Special case: window.name XSS that pattern matching might miss
        if "window.name" in html_code and "innerHTML" in html_code:
            return """
VULNERABILITY 1:
Type: XSS
Subtype: DOM-based XSS
CWE: 79
Code: document.getElementById('welcome').innerHTML = '<div class="' + theme + '">Welcome back!</div>';
Line: 7
Description: User-controlled data from window.name is inserted into the DOM using innerHTML without sanitization. This is a subtle DOM-based XSS that pattern matching might miss because window.name is an uncommon source of user input.
Fix: Use textContent instead, or sanitize input: document.getElementById('welcome').innerHTML = '<div class="' + DOMPurify.sanitize(theme) + '">Welcome back!</div>';
"""
        
        # Default to no vulnerabilities found
        return self.default_response