"""
Analysis Session Django app configuration.

This module configures the Analysis Session app for tracking
long-running repository analysis with progress and recovery.
"""
from django.apps import AppConfig


class AnalysisSessionConfig(AppConfig):
    """Configuration for the Analysis Session application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analysis_session'
