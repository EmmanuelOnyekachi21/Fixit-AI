"""
Gemini Analyzer Django app configuration.

This module configures the Gemini Analyzer app for code security analysis.
"""
from django.apps import AppConfig


class GeminiAnalyzerConfig(AppConfig):
    """Configuration for the Gemini Analyzer application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gemini_analyzer'
    verbose_name = 'Gemini Code Analyzer'
