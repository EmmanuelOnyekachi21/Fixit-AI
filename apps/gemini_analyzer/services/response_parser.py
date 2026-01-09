"""
Response parser for transforming Gemini API responses into Task objects.
"""
from typing import Dict, List

from apps.repository.models import Repository
from apps.task.models import Task


class ResponseParser:
    """Parses Gemini vulnerability responses and creates Task objects."""

    # Map Gemini vulnerability types to Task model choices
    VULNERABILITY_TYPE_MAP = {
        'xss': 'xss',
        'sql_injection': 'sql_injection',
        'csrf': 'csrf',
        'hardcoded_secret': 'hardcoded_secret',
        'command_injection': 'command_injection',
        'path_traversal': 'path_traversal',
        'authentication_bypass': 'authentication_bypass',
        'insecure_deserialization': 'insecure_deserialization',
    }

    def parse_vulnerabilities(
        self,
        gemini_response: List[Dict],
        file_path: str
    ) -> List[Dict]:
        """
        Parse and validate vulnerability data from Gemini response.

        Args:
            gemini_response: List of vulnerability dicts from Gemini
            file_path: Path to the file that was analyzed

        Returns:
            List of validated vulnerability dictionaries
        """
        validated = []

        for vuln in gemini_response:
            try:
                # Validate required fields
                vuln_type = vuln.get('type', '').lower()
                if vuln_type not in self.VULNERABILITY_TYPE_MAP:
                    print(f"Unknown vulnerability type: {vuln_type}")
                    continue

                validated_vuln = {
                    'type': self.VULNERABILITY_TYPE_MAP[vuln_type],
                    'title': vuln.get(
                        'title',
                        'Unknown vulnerability'
                    )[:255],
                    'description': vuln.get(
                        'description',
                        'No description provided'
                    ),
                    'file_path': file_path,
                    'line_number': vuln.get('line_number'),
                    'severity': vuln.get('severity', 'medium'),
                }

                validated.append(validated_vuln)

            except Exception as e:
                print(f"Error validating vulnerability: {e}")
                continue

        return validated

    def create_tasks(
        self,
        vulnerabilities: List[Dict],
        repository: Repository
    ) -> List[Task]:
        """
        Create Task objects from validated vulnerabilities.

        Args:
            vulnerabilities: List of validated vulnerability dicts
            repository: Repository instance to associate tasks with

        Returns:
            List of created (but not saved) Task objects
        """
        tasks = []

        for vuln in vulnerabilities:
            task = Task(
                repository=repository,
                title=vuln['title'],
                description=vuln['description'],
                vulnerability_type=vuln['type'],
                file_path=vuln['file_path'],
                line_number=vuln['line_number'],
                status='pending',
            )
            tasks.append(task)

        return tasks

    def create_and_save_tasks(
        self,
        vulnerabilities: List[Dict],
        repository: Repository
    ) -> List[Task]:
        """
        Create and save Task objects in bulk.

        Args:
            vulnerabilities: List of validated vulnerability dicts
            repository: Repository instance to associate tasks with

        Returns:
            List of saved Task objects
        """
        tasks = self.create_tasks(vulnerabilities, repository)

        if tasks:
            Task.objects.bulk_create(tasks)

        return tasks
