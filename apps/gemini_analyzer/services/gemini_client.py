"""
Gemini API client for code security analysis.
"""
import json
import re

from django.conf import settings
from google import genai

from apps.gemini_analyzer.prompts.security_analysis import (
    build_security_prompt
)


class GeminiClient:
    """Client for interacting with Google's Gemini API."""

    def __init__(self):
        """
        Initialize the Gemini client.

        Raises:
            ValueError: If GEMINI_API_KEY is not found in settings.
        """
        # Ensure api_key exists
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if api_key is None:
            raise ValueError(
                "GEMINI_API_KEY not found in settings or .env"
            )

        # create client object
        self.client = genai.Client(api_key=api_key)

        # Select the model
        self.model_name = "gemini-3-flash-preview"

        # Optional debug storage
        self.last_prompt = None
        self.last_response = None
        self.last_vulnerabilities = None

    def analyze_code(self, code_content, filename):
        """
        Analyze code for security vulnerabilities using Gemini API.

        Args:
            code_content (str): The source code to analyze.
            filename (str): Name of the file being analyzed.

        Returns:
            list: List of vulnerability dictionaries, or empty list on error.
        """
        prompt = self._build_prompt(code_content, filename)
        self.last_prompt = prompt

        try:
            # send prompts to Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )

            # Parse response
            vulnerabilities = self._parse_response(response.text)

            self.last_response = response.text
            self.last_vulnerabilities = vulnerabilities

            return vulnerabilities

        except Exception as e:
            # Handle Errors
            print(f"Gemini API error: {e}")
            return []

    def _build_prompt(self, code_content, filename):
        """
        Build security analysis prompt using template.

        Args:
            code_content (str): The source code to analyze.
            filename (str): Name of the file being analyzed.

        Returns:
            str: Formatted prompt string.
        """
        return build_security_prompt(code_content, filename)

    def _parse_response(self, response_text):
        """
        Parse Gemini response and extract JSON vulnerabilities.

        Handles cases where Gemini wraps JSON in markdown code blocks.

        Args:
            response_text (str): Raw response from Gemini API.

        Returns:
            list: List of vulnerability dictionaries.
        """
        if not response_text or not response_text.strip():
            return []

        # Remove markdown code blocks if present
        # Pattern: ```json\n[...]\n``` or ```\n[...]\n```
        cleaned = response_text.strip()

        json_match = re.search(
            r"```(?:json)\s*(\[.*?\])\s*```",
            cleaned,
            re.DOTALL
        )

        if json_match:
            cleaned = json_match.group(1)

        # Remove any remaining backticks
        cleaned = cleaned.replace(
            '```json',
            ''
        ).replace('```', '').strip()

        try:
            vulnerabilities = json.loads(cleaned)

            # Validate it's a list.
            if not isinstance(vulnerabilities, list):
                print(
                    f"Warning: Expected list, got "
                    f"{type(vulnerabilities)}"
                )
                return []

            return vulnerabilities

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Attempted to parse: {cleaned[:200]}...")
            return []



