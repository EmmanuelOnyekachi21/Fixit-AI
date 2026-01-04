"""
Security analysis prompt templates for Gemini API.
"""

SECURITY_ANALYSIS_PROMPT = """You are a security expert analyzing code for vulnerabilities.

Analyze the following code file and and return ONLY a JSON array of vulnerabilities found.

**File:** {filename}

**Code:**
```
{code}
```

**Instructions:**
- Identify security vulnerabilities. Check specifically for:
  - sql_injection
  - xss
  - authentication_bypass
  - insecure_crypto
  - hardcoded_secrets
  - path_traversal
  - command_injection
- For each vulnerability found, provide:
  - title: short, clear summary of the vulnerability
  - type: vulnerability type (use snake_case from the list above)
  - file: filename where the vulnerability exists
  - line: exact line number where vulnerability exists
  - severity: critical, high, medium, or low
  - description: detailed explanation of the issue
  - suggestion: actionable mitigation advice


**IMPORTANT:** Return ONLY a valid JSON array. No markdown, no code blocks, no explanations outside the JSON.

**Example format:**
[
  {{
    "title": "SQL Injection via Unparameterized Query",
    "type": "sql_injection",
    "file": "{filename}",
    "line": 42,
    "severity": "high",
    "description": "User input directly concatenated into SQL query without parameterization.",
    "suggestion": "Use parameterized queries or ORM methods to prevent SQL injection."
  }},
  {{
    "title": "Reflected XSS in HTML Template",
    "type": "xss",
    "file": "{filename}",
    "line": 88,
    "severity": "medium",
    "description": "Unescaped user input rendered in HTML template.",
    "suggestion": "Escape all user input before rendering, or use a safe templating engine."
  }}
]

If no vulnerabilities found, return: []
"""


def build_security_prompt(code_content: str, filename: str) -> str:
    """
    Build a security analysis prompt for Gemini.

    Args:
        code_content: The source code to analyze.
        filename: Name of the file being analyzed.

    Returns:
        str: Formatted prompt string ready for Gemini API.
    """
    return SECURITY_ANALYSIS_PROMPT.format(
        filename=filename,
        code=code_content
    )
