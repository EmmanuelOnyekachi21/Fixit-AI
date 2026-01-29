"""
Repository URL configuration.

This module defines URL patterns for repository-related API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_repository, name='create_repository'),
    path('<int:repository_id>/tasks/', views.list_repository_tasks, name='list_repository_tasks'),
    path('<int:repository_id>/pull-requests/', views.create_prs_for_repository, name='create_prs'),
]
