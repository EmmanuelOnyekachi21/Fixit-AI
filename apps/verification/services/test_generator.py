"""
Test generation service for vulnerability verification.

This module generates pytest tests that prove vulnerabilities exist
using AI-powered code generation.
"""
import re

from apps.gemini_analyzer.services.gemini_client import GeminiClient
from apps.task.models import Task


class TestGenerator:
    """
    Generates tests that prove vulnerability exists.

    Uses Gemini AI to generate pytest tests that will fail if a
    vulnerability is present, confirming its existence.
    """

    def __init__(self):
        """Initialize the TestGenerator with a GeminiClient."""
        self.gemini = GeminiClient()

    def generate_test(self, task: Task) -> str:
        """
        Generate a pytest for the vulnerability.

        Args:
            task: Task object with vulnerability details.

        Returns:
            str: Python test code as a string.
        """
        try:
            prompt = self._build_test_prompt(task)
            response_text = self.gemini.generate_content_with_retry(prompt)
            test_code = self._parse_test_code(response_text)

            print(test_code)

            return test_code

        except Exception as e:
            print(f"Error generating test for task {task.id}: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def _build_test_prompt(self, task: Task) -> str:
        """
        Build the prompt asking Gemini to write the test.

        Args:
            task: Task object with vulnerability details.

        Returns:
            str: Prompt string.
        """
        # Extract just the filename for import purposes
        filename = task.file_path.split('/')[-1].replace('.py', '')
        
        prompt = f"""
You are a security testing expert. Generate a pytest test that proves the following vulnerability exists.

**Vulnerability Details:**
- Type: {task.vulnerability_type}
- File: {task.file_path}
- Line: {task.line_number}
- Description: {task.description}

**ORIGINAL CODE TO TEST:**
```python
{task.original_code}

**CRITICAL REQUIREMENTS:**
1. The vulnerable code will be in a file named '{filename}.py' in the SAME directory as your test
2. Import from it like: `from {filename} import function_name`
3. Write a pytest test function that will FAIL if the vulnerability exists
4. The test should demonstrate how to exploit the vulnerability
5. Include necessary imports
6. Use clear assertion messages that explain the vulnerability
7. Return ONLY executable Python code, no explanations or markdown

**Example format:**
```python
import pytest
from {filename} import vulnerable_function

def test_vulnerability_name():
    # Test code that exploits the vulnerability
    # This should FAIL, proving the bug exists
    assert condition_that_should_be_true, "Vulnerability explanation"
```

Generate the test now.
"""
        return prompt

    def _parse_test_code(self, response):
        """
        Extract python test code from Gemini's response.

        Args:
            response: Raw response from Gemini.

        Returns:
            str: Python test code as a string.
        """
        if not response or not response.strip():
            return ""

        cleaned = response.strip()

        # Look for code wrapped in python
        code_match = re.search(
            r'```(?:python)?\s*(.*?)\s*```',
            cleaned,
            re.DOTALL
        )

        if code_match:
            cleaned = code_match.group(1)

        # Remove any remaining backticks
        cleaned = cleaned.replace(
            '```python',
            ''
        ).replace('```', '').strip()
        return cleaned

