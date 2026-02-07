"""
TaskLog Django app configuration.

This module configures the TaskLog app for tracking task execution logs.
"""
from django.apps import AppConfig


class TasklogConfig(AppConfig):
    """Configuration for the TaskLog application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasklog'

    def ready(self):
        import apps.tasklog.signals
