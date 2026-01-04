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

    def analyze_repository(
        self,
        repository: Repository,
        files_to_analyze: List[dict]
    ) -> List[Task]:
        """
        Analyze multiple files in a repository.

        Args:
            repository: Repository instance
            files_to_analyze: List of dicts with 'path' and 'content' keys

        Returns:
            List of all created Task objects
        """
        all_tasks = []

        for file_info in files_to_analyze:
            file_path = file_info.get('path')
            file_content = file_info.get('content')

            if not file_path or not file_content:
                continue

            try:
                tasks = self.analyze_file(
                    file_content,
                    file_path,
                    repository
                )
                all_tasks.extend(tasks)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                continue

        return all_tasks
