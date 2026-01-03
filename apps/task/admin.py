"""
Task admin module.

This module configures the Django admin interface for managing Task
models representing security vulnerabilities.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Task model.
    
    Provides a comprehensive interface for managing security vulnerability
    tasks including filtering by status and type, searching, and colored
    status display.
    """
    list_display = (
        'id',
        'repository',
        'vulnerability_type',
        'colored_status',
        'file_path',
        'retry_count',
        'created_at',
    )
    list_filter = (
        'status',
        'vulnerability_type',
        'repository',
    )
    search_fields = (
        'title',
        'description',
        'file_path',
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'started_at', 'completed_at')

    def colored_status(self, obj):
        """
        Display the task status with color coding for better visibility.
        
        Args:
            obj (Task): The task instance.
            
        Returns:
            str: HTML formatted string with colored status text.
        """
        colors = {
            'pending': 'gray',
            'running': 'blue',
            'validating': 'orange',
            'completed': 'green',
            'failed': 'red',
            'abandoned': 'darkred',
            'false_positive': 'purple'
        }

        return format_html(
            '<b style="color: {};">{}</b>',
            colors.get(obj.status, 'black'),
            obj.status.upper()
        )
    colored_status.short_description = 'Status'

