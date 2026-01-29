"""
URL configuration for analysis session endpoints.
"""
from django.urls import path
from . import views

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
]
