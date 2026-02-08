"""
URL configuration for core app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('credentials/validate/', views.validate_credentials, name='validate_credentials'),
]
