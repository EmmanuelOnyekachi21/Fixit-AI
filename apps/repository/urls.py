"""
Repository URL configuration.

This module defines URL patterns for repository-related API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('repository/', views.create_repository, name="create-repo")
]
