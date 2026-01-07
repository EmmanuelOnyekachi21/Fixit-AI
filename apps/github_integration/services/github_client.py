"""
GitHub API client for fetching repository code.

This module provides functionality to interact with the GitHub API
to fetch repository files and their contents for security analysis.
"""
import base64
from typing import Dict, List, Optional

import requests
from requests.exceptions import HTTPError, Timeout


class GitHubClient:
    """
    Client for fetching code from GitHub repositories.

    Handles:
    - Parsing GitHub URLs
    - Fetching repository file trees
    - Filtering relevant files
    - Downloading file contents
    """
    MAX_FILES = 25

    def __init__(self):
        """Initialize the GitHub client with API endpoints."""
        self.base_url = "https://api.github.com"
        self.raw_base = "https://raw.githubusercontent.com"
        self.session = requests.Session()

    def get_repo_files(
        self,
        owner: str,
        repo: str
    ) -> List[Dict[str, str]]:
        """
        Fetch Python files from a GitHub repository.

        Args:
            owner: Repository owner username or organization.
            repo: Repository name.

        Returns:
            List of dictionaries containing 'path' and 'content' keys.
        """
        # Get default branch
        branch = self._get_default_branch(owner, repo)

        # Fetch full repository tree
        tree = self._get_repo_tree(owner, repo, branch)

        # filter files
        python_files = [
            item for item in tree
            if (item['type'] == 'blob' and
                self._should_analyze_file(item['path']))
        ]

        # Limit number of files
        python_files = python_files[:self.MAX_FILES]

        # Fetch content for each file
        files_with_content = []

        for file_item in python_files:
            filepath = file_item['path']
            content = self._fetch_file_content(
                owner,
                repo,
                filepath,
                branch
            )

            if content:
                files_with_content.append({
                    'path': filepath,
                    'content': content
                })

        print(
            f"Fetched {len(files_with_content)} files "
            f"from {owner}/{repo}"
        )
        return files_with_content

    def _get_default_branch(self, owner: str, repo: str) -> str:
        """
        Get the default branch name for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            str: Name of the default branch (e.g., 'main', 'master').

        Raises:
            HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()['default_branch']

    def _get_repo_tree(
        self,
        owner: str,
        repo: str,
        branch: str
    ) -> List[Dict]:
        """
        Fetch the complete file tree for a repository branch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            branch: Branch name.

        Returns:
            List of file/directory items from the repository tree.
        """
        url = (
            f"{self.base_url}/repos/{owner}/{repo}/git/trees/"
            f"{branch}?recursive=1"
        )
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()['tree']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repository tree: {e}")
            return []

    def _should_analyze_file(self, filepath: str) -> bool:
        """
        Determine if a file should be analyzed.

        Rules:
        - Must be a Python file (.py extension)
        - Exclude test files
        - Exclude migrations
        - Exclude virtual environments
        - Exclude cache directories

        Args:
            filepath: Path to file in repository.

        Returns:
            bool: True if file should be analyzed, False otherwise.
        """
        # Must be a python file
        if not filepath.endswith('.py'):
            return False

        # Exclude patterns
        exclude_patterns = [
            'test_',
            '/tests/',
            '/migrations/',
            '__pycache__',
            'venv/',
            '.venv/',
            'env/',
            '/.env',
            'site-packages',
            '/docs/',
            'setup.py',
            'manage.py',
            'admin_',
            'tests.py',
            '/management/',
            '__init__.py',
            'admin.py',
            'asgi.py',
            'settings.py',
            'urls.py',
            'wsgi.py',
            'apps.py'
        ]

        # Check if filepath contains any of the exclude patterns
        filepath_lower = filepath.lower()
        for pattern in exclude_patterns:
            if pattern in filepath_lower:
                return False
        return True

    def _fetch_file_content(
        self,
        owner: str,
        repo: str,
        filepath: str,
        branch: str = 'main'
    ) -> Optional[str]:
        """
        Fetch the content of a specific file using GitHub API.

        Args:
            owner: Repository owner.
            repo: Repository name.
            filepath: Path to file in repository.
            branch: Branch name.

        Returns:
            str: Content of file if successful, None otherwise.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{filepath}"
        params = {'ref': branch}

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # GitHub API returns content as base64-encoded string
            if 'content' in data:
                content_base64 = data['content']
                content_bytes = base64.b64decode(content_base64)
                return content_bytes.decode('utf-8')

            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching file content {filepath}: {e}")
            return None
