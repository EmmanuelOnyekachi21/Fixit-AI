"""
API URL Configuration.
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # GitHub authentication
    path('auth/github/', views.setup_github_auth, name='github_auth'),
    
    # PR creation
    path(
        'repositories/<int:repository_id>/create-prs/',
        views.create_prs_for_repository,
        name='create_prs'
    ),
    path(
        'tasks/<int:task_id>/verify-and-fix/',
        views.verify_and_fix,
        name='verify_and_fix'
    )
]
