"""
Task Django app configuration.

This module configures the Task app for managing security vulnerability tasks.
"""
from django.apps import AppConfig


class TaskConfig(AppConfig):
    """Configuration for the Task application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.task'
