"""
Task URL configuration.

This module defines URL patterns for task-related API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('<int:task_id>/', views.get_task_detail, name='task_detail'),
    path('<int:task_id>/details/', views.get_task_details, name='task_details'),
    path('<str:task_id>/status/', views.get_task_status, name='task_status'),
    path('<int:task_id>/verify-and-fix/', views.verify_and_fix, name='verify_and_fix'),
    path('<int:task_id>/generate-fix/', views.generate_fix, name='generate_fix'),
]
