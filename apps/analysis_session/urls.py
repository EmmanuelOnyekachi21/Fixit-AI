"""
URL configuration for analysis session endpoints.
"""
from django.urls import path
from . import views
from apps.task.views import process_all_tasks

urlpatterns = [
    path(
        '<str:session_id>/status/',
        views.get_session_status,
        name="session_status"
    ),
    path(
        '<str:session_id>/resume/',
        views.resume_session,
        name="resume_session"
    ),
    path(
        '<str:session_id>/process-all/',
        process_all_tasks,
        name="process_all_tasks"
    ),
    path(
        '',
        views.list_sessions,
        name="list_sessions"
    )
]
