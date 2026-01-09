"""
Gemini API client for code security analysis.
"""
import json
import re
import time
from typing import List, Dict

from django.conf import settings
from google import genai
from google.api_core import exceptions as google_exceptions

from apps.gemini_analyzer.exceptions import (
    GeminiAPIError,
    GeminiRateLimitError,
    GeminiNetworkError,
    ResponseParsingError
)
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

        # Retry configuration
        self.max_retries = 3
        self.initial_retry_delay = 1  # seconds
        self.max_retry_delay = 60  # seconds

        # Optional debug storage
        self.last_prompt = None
        self.last_response = None
        self.last_vulnerabilities = None

    def analyze_code(self, code_content: str, filename: str) -> List[Dict]:
        """
        Analyze code for security vulnerabilities using Gemini API.

        Implements retry logic with exponential backoff for rate limits
        and network errors.

        Args:
            code_content: The source code to analyze.
            filename: Name of the file being analyzed.

        Returns:
            List of vulnerability dictionaries.

        Raises:
            GeminiRateLimitError: If rate limit is exceeded after retries.
            GeminiNetworkError: If network connection fails after retries.
            GeminiAPIError: For other API errors.
            ResponseParsingError: If response cannot be parsed.
        """
        prompt = self._build_prompt(code_content, filename)
        self.last_prompt = prompt

        retry_delay = self.initial_retry_delay

        for attempt in range(self.max_retries):
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

            except google_exceptions.ResourceExhausted as e:
                # Rate limit exceeded
                print(f"Rate limit exceeded (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, self.max_retry_delay)
                else:
                    raise GeminiRateLimitError(
                        f"Rate limit exceeded after {self.max_retries} attempts. "
                        "Please wait before making more requests."
                    ) from e

            except (
                google_exceptions.ServiceUnavailable,
                google_exceptions.DeadlineExceeded,
                ConnectionError,
                TimeoutError
            ) as e:
                # Network/connectivity errors
                print(f"Network error (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, self.max_retry_delay)
                else:
                    raise GeminiNetworkError(
                        f"Network error after {self.max_retries} attempts: {str(e)}"
                    ) from e

            except google_exceptions.GoogleAPIError as e:
                # Other Google API errors (don't retry)
                print(f"Gemini API error: {e}")
                raise GeminiAPIError(f"Gemini API error: {str(e)}") from e

            except Exception as e:
                # Unexpected errors
                print(f"Unexpected error during Gemini API call: {e}")
                raise GeminiAPIError(f"Unexpected error: {str(e)}") from e

        # Should not reach here, but just in case
        raise GeminiAPIError("Failed to analyze code after all retries")

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

    def _parse_response(self, response_text: str) -> List[Dict]:
        """
        Parse Gemini response and extract JSON vulnerabilities.

        Handles cases where Gemini wraps JSON in markdown code blocks.

        Args:
            response_text: Raw response from Gemini API.

        Returns:
            List of vulnerability dictionaries.

        Raises:
            ResponseParsingError: If response cannot be parsed as valid JSON.
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
            error_msg = f"Error parsing JSON response: {e}"
            print(error_msg)
            print(f"Attempted to parse: {cleaned[:200]}...")
            raise ResponseParsingError(error_msg) from e



