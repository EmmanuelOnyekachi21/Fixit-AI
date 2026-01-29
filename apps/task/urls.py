"""
Task URL configuration.

This module defines URL patterns for task-related API endpoints.
"""
from django.urls import path

from . import views

urlpatterns = [
    path('<str:task_id>/status/', views.get_task_status, name="task_status"),
]
