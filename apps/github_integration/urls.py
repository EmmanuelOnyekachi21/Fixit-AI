"""
GitHub Integration URL configuration.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('github/', views.setup_github_auth, name='github_auth'),
]
