import re
import requests
import json
from bs4 import BeautifulSoup

from src.reasoning.llm_engine import LLMEngine

class SecurityAnalyzer:
    """Security analyzer using pattern matching and LLM reasoning"""
    
    def __init__(self, llm_engine=None, api_key=None):
        """Initialize the security analyzer
        
        Args:
            llm_engine: The LLM engine instance for analysis
            api_key: Optional NVD API key for higher rate limits
        """
        self.llm_engine = llm_engine
        self.nvd_api_key = api_key
        self.nvd_base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
        # Initialize pattern databases
        self.initialize_patterns()
    
    def initialize_patterns(self):
        """Initialize vulnerability pattern databases"""
        # XSS patterns
        self.xss_patterns = [
            {
                "regex": r"<script>.*document\.write\s*\(.*location.*\)",
                "cwe": "79",
                "type": "XSS",
                "subtype": "DOM-based XSS",
                "description": "DOM-based XSS using document.write with location"
            },
            {
                "regex": r"<script>.*document\.write\s*\(.*localStorage.*\)",
                "cwe": "79",
                "type": "XSS",
                "subtype": "DOM-based XSS",
                "description": "DOM-based XSS using document.write with localStorage"
            },
            {
                "regex": r"<script>.*innerHTML\s*=.*location.*",
                "cwe": "79",
                "type": "XSS",
                "subtype": "DOM-based XSS",
                "description": "DOM-based XSS setting innerHTML from location"
            },
            {
                "regex": r"<input[^>]*value\s*=\s*[\"']?\s*<\?php\s+echo\s+\$_(GET|POST|REQUEST)",
                "cwe": "79",
                "type": "XSS",
                "subtype": "Reflected XSS",
                "description": "Reflected XSS via PHP echo of user input"
            }
        ]
        
        # CSRF patterns
        self.csrf_patterns = [
            {
                "regex": r"<form[^>]*method\s*=\s*[\"']?\s*POST[\"']?[^>]*>(?!.*csrf)",
                "cwe": "352",
                "type": "CSRF",
                "subtype": "Missing Token",
                "description": "POST form without CSRF token"
            }
        ]
        
        # Information disclosure patterns
        self.info_disclosure_patterns = [
            {
                "regex": r"<!--.*password.*-->",
                "cwe": "200",
                "type": "Information Disclosure",
                "subtype": "Sensitive Comment",
                "description": "Comment containing password information"
            },
            {
                "regex": r"<!--.*TODO.*-->",
                "cwe": "200",
                "type": "Information Disclosure",
                "subtype": "Developer Comment",
                "description": "Developer TODO comment in production code"
            },
            {
                "regex": r"<input[^>]*type\s*=\s*[\"']?password[\"']?[^>]*autocomplete\s*=\s*[\"']?on[\"']?",
                "cwe": "200", 
                "type": "Information Disclosure",
                "subtype": "Password Storage",
                "description": "Password field with autocomplete enabled"
            }
        ]
        
        # Combine all patterns
        self.all_patterns = self.xss_patterns + self.csrf_patterns + self.info_disclosure_patterns
    
    def pattern_match(self, html_code):
        """Identify vulnerabilities using pattern matching
        
        Args:
            html_code: The HTML code to analyze
            
        Returns:
            A list of potential vulnerabilities
        """
        findings = []
        
        # Check all patterns
        for pattern in self.all_patterns:
            matches = re.finditer(pattern["regex"], html_code, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                # Get line number
                line_number = html_code[:match.start()].count('\n') + 1
                
                # Get context (a few lines before and after)
                lines = html_code.split('\n')
                start_line = max(0, line_number - 3)
                end_line = min(len(lines), line_number + 3)
                context_lines = lines[start_line:end_line]
                
                finding = {
                    "type": pattern["type"],
                    "subtype": pattern["subtype"],
                    "cwe": pattern["cwe"],
                    "description": pattern["description"],
                    "line": line_number,
                    "code": match.group(0),
                    "context": '\n'.join(context_lines),
                    "source": "pattern_match"
                }
                findings.append(finding)
        
        return findings
    
    def llm_analyze(self, html_code):
        """Analyze HTML with LLM to find vulnerabilities
        
        Args:
            html_code: The HTML code to analyze
            
        Returns:
            A list of vulnerabilities found by the LLM
        """
        if not self.llm_engine:
            print("Warning: No LLM engine provided. Skipping LLM analysis.")
            return []
        
        prompt = f"""
        Analyze this HTML code for security vulnerabilities:
        
        ```html
        {html_code}
        ```
        
        Consider ALL possible web security vulnerabilities, including but not limited to:
        
        1. Cross-Site Scripting (XSS) - CWE-79
           - Reflected XSS
           - Stored XSS
           - DOM-based XSS
        
        2. Cross-Site Request Forgery (CSRF) - CWE-352
           - Missing anti-CSRF tokens
           - Insecure form submissions
        
        3. Injection Vulnerabilities
           - HTML Injection - CWE-91
           - JavaScript Injection
           - PHP Code Injection - CWE-94
        
        4. Information Disclosure - CWE-200
           - Sensitive data in comments
           - Exposed internal paths
           - Developer notes in HTML
        
        5. Client-Side Validation Issues
           - Security controls implemented only in JavaScript
        
        Look for subtle issues that pattern matching might miss, such as:
        - Context-specific vulnerabilities
        - Logic flaws in form handling
        - Insecure usage of third-party libraries
        - Improper encoding or escaping
        
        For each vulnerability found, provide:
        - The vulnerability type (main category)
        - A more specific subtype if applicable
        - The CWE identifier (if known)
        - The specific part of code that is vulnerable (use the smallest snippet that shows the vulnerability)
        - The line number(s) if you can determine them
        - A brief description of the issue
        - A suggested fix
        
        Format your response in a structured way I can parse:
        
        VULNERABILITY 1:
        Type: [type]
        Subtype: [subtype]
        CWE: [cwe-id]
        Code: [vulnerable code snippet]
        Line: [approximate line number]
        Description: [brief description]
        Fix: [suggested fix]
        
        VULNERABILITY 2:
        ...etc.
        
        If no vulnerabilities are found, reply with "NO_VULNERABILITIES_FOUND".
        """
        
        # Generate analysis using LLM
        analysis = self.llm_engine.generate(prompt)
        
        # Parse LLM response
        findings = []
        
        if "NO_VULNERABILITIES_FOUND" in analysis:
            return findings
        
        vulnerability_sections = analysis.split("VULNERABILITY ")
        
        for section in vulnerability_sections[1:]:
            lines = section.strip().split("\n")
            if not lines:
                continue
                
            vulnerability = {"source": "llm_analysis"}
            
            for line in lines:
                if line.startswith("Type:"):
                    vulnerability["type"] = line.replace("Type:", "").strip()
                elif line.startswith("Subtype:"):
                    vulnerability["subtype"] = line.replace("Subtype:", "").strip()
                elif line.startswith("CWE:"):
                    vulnerability["cwe"] = line.replace("CWE:", "").strip()
                elif line.startswith("Code:"):
                    vulnerability["code"] = line.replace("Code:", "").strip()
                elif line.startswith("Line:"):
                    try:
                        vulnerability["line"] = int(line.replace("Line:", "").strip())
                    except ValueError:
                        vulnerability["line"] = line.replace("Line:", "").strip()
                elif line.startswith("Description:"):
                    vulnerability["description"] = line.replace("Description:", "").strip()
                elif line.startswith("Fix:"):
                    vulnerability["fix"] = line.replace("Fix:", "").strip()
            
            if "type" in vulnerability and "description" in vulnerability:
                findings.append(vulnerability)
        
        return findings
    
    def get_nvd_info(self, cwe_id):
        """Get vulnerability information from NVD for a CWE
        
        Args:
            cwe_id: The CWE ID to look up (e.g., "79")
        
        Returns:
            Dictionary with NVD information
        """
        try:
            # Build request parameters
            params = {
                "cweName": f"CWE-{cwe_id}",
                "resultsPerPage": 5  # Limit to 5 results for simplicity
            }
            
            if self.nvd_api_key:
                params["apiKey"] = self.nvd_api_key
            
            # Make the request
            response = requests.get(self.nvd_base_url, params=params)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract relevant information
            vulnerabilities = []
            if "vulnerabilities" in data:
                for vuln in data["vulnerabilities"]:
                    cve = vuln.get("cve", {})
                    
                    # Get description
                    description = ""
                    for desc in cve.get("descriptions", []):
                        if desc.get("lang") == "en":
                            description = desc.get("value", "")
                            break
                    
                    # Get severity
                    metrics = cve.get("metrics", {})
                    severity = "Unknown"
                    score = 0.0
                    
                    if "cvssMetricV31" in metrics:
                        cvss = metrics["cvssMetricV31"][0]
                        severity = cvss.get("cvssData", {}).get("baseSeverity", "Unknown")
                        score = cvss.get("cvssData", {}).get("baseScore", 0.0)
                    elif "cvssMetricV30" in metrics:
                        cvss = metrics["cvssMetricV30"][0]
                        severity = cvss.get("cvssData", {}).get("baseSeverity", "Unknown")
                        score = cvss.get("cvssData", {}).get("baseScore", 0.0)
                    elif "cvssMetricV2" in metrics:
                        cvss = metrics["cvssMetricV2"][0]
                        severity = cvss.get("baseSeverity", "Unknown")
                        score = cvss.get("cvssData", {}).get("baseScore", 0.0)
                    
                    vulnerabilities.append({
                        "id": cve.get("id", ""),
                        "description": description,
                        "severity": severity,
                        "score": score
                    })
            
            return {
                "cwe_id": cwe_id,
                "examples": vulnerabilities
            }
            
        except Exception as e:
            print(f"Error fetching NVD information: {e}")
            return {"cwe_id": cwe_id, "error": str(e), "examples": []}
    
    def analyze_html(self, html_code):
        """Analyze HTML code for security vulnerabilities
        
        Args:
            html_code: The HTML code to analyze
            
        Returns:
            A dictionary with analysis results
        """
        # Track execution time
        import time
        start_time = time.time()
        
        # Find vulnerabilities using pattern matching
        pattern_findings = self.pattern_match(html_code)
        pattern_time = time.time() - start_time
        
        # Find vulnerabilities using LLM
        llm_start_time = time.time()
        llm_findings = []
        
        if self.llm_engine:
            # For smaller HTML, analyze the whole thing
            if len(html_code) < 5000:
                llm_findings = self.llm_analyze(html_code)
            else:
                # For larger HTML, analyze key sections
                print("HTML too large for full LLM analysis, analyzing key sections...")
                
                # Basic chunking approach
                chunks = []
                
                # Try to parse with BeautifulSoup
                try:
                    soup = BeautifulSoup(html_code, 'html.parser')
                    
                    # Extract forms (high-value targets)
                    forms = soup.find_all('form')
                    for form in forms:
                        chunks.append(str(form))
                    
                    # Extract scripts (high-value targets)
                    scripts = soup.find_all('script')
                    for script in scripts:
                        chunks.append(str(script))
                    
                except Exception as e:
                    print(f"Error parsing HTML: {e}")
                    # Fallback to simple chunking if parsing fails
                    chunk_size = 4000
                    for i in range(0, len(html_code), chunk_size):
                        chunks.append(html_code[i:i+chunk_size])
                
                # Analyze each chunk
                for i, chunk in enumerate(chunks):
                    print(f"Analyzing chunk {i+1}/{len(chunks)}...")
                    chunk_findings = self.llm_analyze(chunk)
                    for finding in chunk_findings:
                        finding["chunk"] = i+1
                    llm_findings.extend(chunk_findings)
        
        llm_time = time.time() - llm_start_time
        
        # Merge findings and remove duplicates
        merged_findings = []
        
        # Add pattern findings
        for finding in pattern_findings:
            merged_findings.append(finding)
        
        # Add LLM findings, avoiding duplicates
        for llm_finding in llm_findings:
            # Check if this is a duplicate
            is_duplicate = False
            for existing in merged_findings:
                # Compare type and code
                if (existing.get("type") == llm_finding.get("type") and 
                    existing.get("code") == llm_finding.get("code")):
                    is_duplicate = True
                    
                    # Add LLM description to pattern finding if not present
                    if existing.get("source") == "pattern_match" and "fix" in llm_finding:
                        existing["fix"] = llm_finding["fix"]
                    
                    break
            
            if not is_duplicate:
                merged_findings.append(llm_finding)
        
        # Enrich with NVD data
        nvd_start_time = time.time()
        for finding in merged_findings:
            # Only look up if we have a CWE ID
            if "cwe" in finding and finding["cwe"].isdigit():
                cwe_id = finding["cwe"]
                
                # Check if we've already looked up this CWE
                nvd_info = next((f.get("nvd_info") for f in merged_findings 
                                 if "nvd_info" in f and f.get("cwe") == cwe_id), None)
                
                if not nvd_info:
                    nvd_info = self.get_nvd_info(cwe_id)
                
                finding["nvd_info"] = nvd_info
        
        nvd_time = time.time() - nvd_start_time
        
        # Sort findings by severity (if available from NVD)
        def get_severity_score(finding):
            nvd_info = finding.get("nvd_info", {})
            if nvd_info and "examples" in nvd_info and len(nvd_info["examples"]) > 0:
                return nvd_info["examples"][0].get("score", 0)
            return 0
        
        merged_findings.sort(key=get_severity_score, reverse=True)
        
        # Prepare final result
        total_time = time.time() - start_time
        
        result = {
            "findings": merged_findings,
            "summary": {
                "total_findings": len(merged_findings),
                "pattern_findings": len(pattern_findings),
                "llm_findings": len(llm_findings),
                "unique_findings": len(merged_findings),
                "timing": {
                    "pattern_match_time": pattern_time,
                    "llm_analysis_time": llm_time,
                    "nvd_lookup_time": nvd_time,
                    "total_time": total_time
                }
            }
        }
        
        return result