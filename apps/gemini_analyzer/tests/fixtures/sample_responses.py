"""Sample Gemini API responses for testing."""

# Valid vulnerability response
VALID_GEMINI_RESPONSE = [
    {
        'type': 'sql_injection',
        'title': 'SQL Injection vulnerability',
        'description': 'User input directly concatenated in SQL query',
        'line_number': 15,
        'severity': 'critical'
    },
    {
        'type': 'xss',
        'title': 'Cross-Site Scripting (XSS)',
        'description': 'Unescaped user input rendered in HTML',
        'line_number': 42,
        'severity': 'high'
    }
]

# Response wrapped in markdown code block
MARKDOWN_WRAPPED_RESPONSE = '''```json
[
    {
        "type": "xss",
        "title": "XSS vulnerability found",
        "description": "User input not sanitized",
        "line_number": 10,
        "severity": "medium"
    }
]
```'''

# Response with just backticks (no json marker)
MARKDOWN_NO_JSON_MARKER = '''```
[
    {
        "type": "csrf",
        "title": "CSRF token missing",
        "description": "Form lacks CSRF protection",
        "line_number": 5,
        "severity": "high"
    }
]
```'''

# Invalid JSON response
INVALID_JSON_RESPONSE = "This is not valid JSON at all"

# Empty response
EMPTY_RESPONSE = ""

# Non-list JSON response
NON_LIST_RESPONSE = '{"error": "something went wrong"}'

# Response with unknown vulnerability type
UNKNOWN_VULN_TYPE_RESPONSE = [
    {
        'type': 'unknown_vulnerability',
        'title': 'Unknown issue',
        'description': 'This type is not mapped',
        'line_number': 1,
        'severity': 'low'
    }
]

# Response with missing fields
MISSING_FIELDS_RESPONSE = [
    {
        'type': 'xss',
        # Missing title, description, etc.
    }
]

# Response with very long title (for truncation testing)
LONG_TITLE_RESPONSE = [
    {
        'type': 'xss',
        'title': 'A' * 300,  # 300 characters, should be truncated to 255
        'description': 'Test truncation',
        'line_number': 1,
        'severity': 'low'
    }
]
