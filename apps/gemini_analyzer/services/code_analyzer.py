"""
High-level code analysis orchestrator.

This module coordinates the analysis workflow:
1. Fetch code from repository
2. Send to Gemini for analysis
3. Parse responses
4. Create Task objects
"""
import logging
from typing import List, Optional

from apps.repository.models import Repository
from apps.task.models import Task
from apps.gemini_analyzer.exceptions import (
    GeminiRateLimitError,
    GeminiNetworkError,
    GeminiAPIError,
    ResponseParsingError
)

from .gemini_client import GeminiClient
from .response_parser import ResponseParser

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Orchestrates code security analysis using Gemini."""

    def __init__(self):
        """Initialize the code analyzer with Gemini client and parser."""
        self.gemini_client = GeminiClient()
        self.parser = ResponseParser()

    def analyze_file(
        self,
        file_content: str,
        file_path: str,
        repository: Repository
    ) -> List[Task]:
        """
        Analyze a single file and create tasks for found vulnerabilities.

        Handles errors gracefully:
        - Rate limit errors: Logs and re-raises for caller to handle
        - Network errors: Logs and re-raises for caller to handle
        - Parsing errors: Logs and returns empty list
        - Other errors: Logs and returns empty list

        Args:
            file_content: Source code content
            file_path: Path to the file in the repository
            repository: Repository instance

        Returns:
            List of created Task objects (empty list on error)

        Raises:
            GeminiRateLimitError: When API rate limit is exceeded
            GeminiNetworkError: When network connection fails
        """
        try:
            # Step 1: Send to Gemini (with retry logic built-in)
            vulnerabilities = self.gemini_client.analyze_code(
                file_content,
                file_path
            )

            if not vulnerabilities:
                logger.info(f"No vulnerabilities found in {file_path}")
                return []

            # Step 2: Parse and validate
            validated_vulns = self.parser.parse_vulnerabilities(
                vulnerabilities,
                file_path
            )

            if not validated_vulns:
                logger.warning(
                    f"No valid vulnerabilities after parsing for {file_path}"
                )
                return []

            # Step 3: Create tasks
            tasks = self.parser.create_and_save_tasks(
                validated_vulns,
                repository,
                file_content  # Pass original code
            )

            logger.info(
                f"Created {len(tasks)} tasks for {file_path}"
            )
            return tasks

        except GeminiRateLimitError as e:
            # Rate limit - caller should handle (stop processing, wait, etc.)
            logger.error(
                f"Rate limit exceeded while analyzing {file_path}: {e}"
            )
            raise

        except GeminiNetworkError as e:
            # Network error - caller should handle (retry later, etc.)
            logger.error(
                f"Network error while analyzing {file_path}: {e}"
            )
            raise

        except ResponseParsingError as e:
            # Parsing error - log and continue with other files
            logger.error(
                f"Failed to parse response for {file_path}: {e}"
            )
            raise

        except GeminiAPIError as e:
            # Other API errors - log and continue
            logger.error(
                f"Gemini API error while analyzing {file_path}: {e}"
            )
            raise

        except Exception as e:
            # Unexpected errors - log and continue
            logger.exception(
                f"Unexpected error while analyzing {file_path}: {e}"
            )
            raise
