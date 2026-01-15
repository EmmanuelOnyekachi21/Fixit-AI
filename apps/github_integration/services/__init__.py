"""
GitHub integration services.

This module exports services for GitHub repository access and file analysis.
"""
from .github_client import GitHubClient
from .heuristic_analyzer import HeuristicAnalyzer
from .import_analyzer import ImportAnalyzer

__all__ = [
    'GitHubClient',
    'HeuristicAnalyzer',
    'ImportAnalyzer',
]
