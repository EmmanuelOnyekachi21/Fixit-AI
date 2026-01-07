"""
Repository Django app configuration.

This module configures the Repository app for managing GitHub repositories.
"""
from django.apps import AppConfig


class RepositoryConfig(AppConfig):
    """Configuration for the Repository application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.repository'
