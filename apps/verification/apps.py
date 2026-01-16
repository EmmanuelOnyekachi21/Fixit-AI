"""
Verification Django app configuration.

This module configures the Verification app for vulnerability verification
and fix generation.
"""
from django.apps import AppConfig


class VerificationConfig(AppConfig):
    """Configuration for the Verification application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.verification'
