"""
Task URL configuration.

This module defines URL patterns for task-related API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('<int:task_id>/', views.get_task_details, name='task_details'),
    path('<str:task_id>/status/', views.get_task_status, name='task_status'),
    path('<int:task_id>/verify-and-fix/', views.verify_and_fix, name='verify_and_fix'),
]
