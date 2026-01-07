"""
GitHub Integration Django app configuration.

This module configures the GitHub Integration app for fetching repository data.
"""
from django.apps import AppConfig


class GithubIntegrationConfig(AppConfig):
    """Configuration for the GitHub Integration application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.github_integration'
