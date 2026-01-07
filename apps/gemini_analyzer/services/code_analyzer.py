"""
High-level code analysis orchestrator.

This module coordinates the analysis workflow:
1. Fetch code from repository
2. Send to Gemini for analysis
3. Parse responses
4. Create Task objects
"""
from typing import List

from apps.repository.models import Repository
from apps.task.models import Task

from .gemini_client import GeminiClient
from .response_parser import ResponseParser


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

        Args:
            file_content: Source code content
            file_path: Path to the file in the repository
            repository: Repository instance

        Returns:
            List of created Task objects
        """
        # Step 1: Send to Gemini
        vulnerabilities = self.gemini_client.analyze_code(
            file_content,
            file_path
        )

        if not vulnerabilities:
            return []

        # Step 2: Parse and validate
        validated_vulns = self.parser.parse_vulnerabilities(
            vulnerabilities,
            file_path
        )

        # Step 3: Create tasks
        tasks = self.parser.create_and_save_tasks(
            validated_vulns,
            repository
        )

        return tasks
