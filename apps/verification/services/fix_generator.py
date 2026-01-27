"""
Fix generation service for verified vulnerabilities.

This module generates code fixes for confirmed vulnerabilities
using AI-powered code generation.
"""
import re

from apps.gemini_analyzer.services import GeminiClient
from apps.task.models import Task


class FixGenerator:
    """
    Generates fixes for verified vulnerabilities.

    Uses Gemini AI to generate secure code that resolves identified
    vulnerabilities while maintaining original functionality.
    """

    def __init__(self):
        """Initialize the FixGenerator with a GeminiClient."""
        self.gemini = GeminiClient()

    def generate_fix(self, task: Task) -> str:
        """
        Generate fix code for vulnerability.

        Args:
            task: Task object with vulnerability details and test.

        Returns:
            str: Fixed version of the code as a string.
        """
        try:
            prompt = self._build_fix_prompt(task)
            response_text = self.gemini.generate_content_with_retry(prompt)
            fix_code = self._parse_fix_code(response_text)
            return fix_code

        except Exception as e:
            print(f"Error generating fix for task {task.id}: {e}")
            return ""

    def _build_fix_prompt(self, task: Task) -> str:
        """
        Build the prompt asking Gemini to generate a fix.

        Args:
            task: Task object with vulnerability details.

        Returns:
            str: Prompt string.
        """
        # Use stored original code
        original_code = task.original_code
        
        if not original_code:
            print(f"Warning: No original code stored for task {task.id}")
            original_code = "# Original code not available"
        
        prompt = f"""
You are a security expert. Fix the following vulnerability in the code.

**CRITICAL REQUIREMENTS:**
1. Return the COMPLETE fixed file with ALL original code
2. Only modify the vulnerable lines - keep everything else unchanged
3. Maintain all imports, functions, and logic
4. Return ONLY executable Python code, no explanations or markdown
5. Do NOT return empty code or just comments

**Vulnerability Details:**
- Type: {task.vulnerability_type}
- File: {task.file_path}
- Line: {task.line_number}
- Description: {task.description}

**ORIGINAL FILE CONTENT:**
```python
{original_code}
```

**Test That Must Pass:**
```python
{task.test_code}
```

**Your task:**
Generate the COMPLETE fixed version of the file above that:
- Fixes the {task.vulnerability_type} vulnerability at line {task.line_number}
- Makes the test pass
- Preserves ALL other code exactly as-is
- Uses secure coding practices (parameterized queries, input validation, etc.)

Return the COMPLETE fixed file now:
"""
        return prompt

    def _parse_fix_code(self, response: str) -> str:
        """
        Extract Python fix code from Gemini's response.

        Args:
            response: Raw response from Gemini.

        Returns:
            str: Python fix code as a string.
        """
        if not response or not response.strip():
            return ""

        cleaned = response.strip()

        # Look for code wrapped in ```python ... ```
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

    def apply_fix(self, file_path: str, fix_code: str) -> bool:
        """
        Apply fix to file.

        For Week 2: Just validate the fix code exists.
        For Week 3: Actually modify files and create PRs.

        Args:
            file_path: Path to the file to fix.
            fix_code: The fix code to apply.

        Returns:
            bool: True if fix is valid (for now, just checks if code
                  exists).
        """
        # Week 2: Just validate
        if fix_code and len(fix_code.strip()) > 0:
            return True
        return False
