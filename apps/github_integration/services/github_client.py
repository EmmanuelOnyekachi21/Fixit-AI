"""
GitHub API client for fetching repository code.

This module provides functionality to interact with the GitHub API
to fetch repository files and their contents for security analysis.
"""
import base64
from typing import Dict, List, Optional

import requests
from requests.exceptions import HTTPError, Timeout

from .file_prioritizer import FilePrioritizer
from .heuristic_analyzer import HeuristicAnalyzer


class GitHubClient:
    """
    Client for fetching code from GitHub repositories.

    Handles:
    - Parsing GitHub URLs
    - Fetching repository file trees
    - Filtering relevant files
    - Downloading file contents
    - Smart prioritization to stay within API limits
    """
    MAX_FILES = 25
    # Fetch 50 candidates (stays within 60 req/hour limit)
    CANDIDATE_MULTIPLIER = 2

    def __init__(self):
        """Initialize the GitHub client with API endpoints."""
        self.base_url = "https://api.github.com"
        self.raw_base = "https://raw.githubusercontent.com"
        self.session = requests.Session()
        self.heuristic_analyzer = HeuristicAnalyzer()
        self.prioritizer = FilePrioritizer()

    def get_repo_files(
        self,
        owner: str,
        repo: str
    ) -> List[Dict[str, str]]:
        """
        Fetch and prioritize Python files from a GitHub repository.
        
        Uses a two-stage approach for large repos:
        1. Heuristic filtering on file paths (no content needed)
        2. Full prioritization on candidate files (with content)

        Args:
            owner: Repository owner username or organization.
            repo: Repository name.

        Returns:
            List of dictionaries containing 'path' and 'content' keys,
            prioritized by security criticality.
        """
        repo_name = f"{owner}/{repo}"
        
        # Step 1: Get default branch
        branch = self._get_default_branch(owner, repo)

        # Step 2: Fetch full repository tree (metadata only)
        tree = self._get_repo_tree(owner, repo, branch)

        # Step 3: Filter to Python files only
        python_files = [
            item for item in tree
            if (item['type'] == 'blob' and
                self._should_analyze_file(item['path']))
        ]
        
        print(f"Found {len(python_files)} Python files in {repo_name}")

        # Step 4: Early exit if small repo
        if len(python_files) <= self.MAX_FILES:
            print(f"Small repo - fetching all {len(python_files)} files")
            files_with_content = self._fetch_all_files(
                python_files,
                owner,
                repo,
                branch
            )
            print(f"✓ Fetched {len(files_with_content)} files\n")
            return files_with_content

        # Step 5: Large repo - use two-stage prioritization
        print("Large repo - using smart prioritization...")

        # Stage 1: Heuristic pre-filtering (no content needed)
        candidate_count = min(
            len(python_files),
            self.MAX_FILES * self.CANDIDATE_MULTIPLIER
        )
        candidates = self._heuristic_prefilter(
            python_files,
            candidate_count
        )
        print(
            f"  Stage 1: Selected {len(candidates)} candidates "
            f"via heuristic"
        )

        # Stage 2: Fetch content for candidates only
        print(
            f"  Stage 2: Fetching content for "
            f"{len(candidates)} candidates..."
        )
        candidates_with_content = self._fetch_all_files(
            candidates,
            owner,
            repo,
            branch
        )
        print(
            f"  Successfully fetched "
            f"{len(candidates_with_content)} files"
        )

        # Stage 3: Full prioritization with AI + import analysis
        if len(candidates_with_content) > self.MAX_FILES:
            print(
                f"  Stage 3: Final prioritization to "
                f"top {self.MAX_FILES}..."
            )
            final_files = self.prioritizer.prioritize_files(
                candidates_with_content,
                repo_name,
                max_files=self.MAX_FILES
            )
            print(f"✓ Selected {len(final_files)} priority files\n")
            return final_files
        else:
            print(
                f"✓ Returning all {len(candidates_with_content)} "
                f"candidates\n"
            )
            return candidates_with_content

    def _heuristic_prefilter(
        self,
        files: List[Dict],
        target_count: int
    ) -> List[Dict]:
        """
        Pre-filter files using heuristic scoring (path-based only).
        
        This avoids fetching content for all files in large repos.
        
        Args:
            files: List of file metadata dicts
            target_count: Number of candidates to select
            
        Returns:
            Top-scored files by heuristic analysis
        """
        # Score each file by path
        scored = []
        for file_item in files:
            filepath = file_item['path']
            score = self.heuristic_analyzer.score_filepath(filepath)
            scored.append((file_item, score))
        
        # Sort by score (highest first)
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N
        return [file_item for file_item, score in scored[:target_count]]

    def _fetch_all_files(
        self,
        file_items: List[Dict],
        owner: str,
        repo: str,
        branch: str
    ) -> List[Dict[str, str]]:
        """
        Fetch content for a list of files.
        
        Args:
            file_items: List of file metadata dicts
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            List of dicts with 'path' and 'content' keys
        """
        files_with_content = []
        
        for file_item in file_items:
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
            'test_',           # Files starting with test_
            'tests/',          # Files in tests directory (at start or middle)
            '/tests/',         # Files in tests directory (in middle)
            '_tests/',         # Files in *_tests directory
            '/test/',          # Files in test directory
            '/migrations/',
            'migrations/',
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
