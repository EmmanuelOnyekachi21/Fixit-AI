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
        'colored_test_status',
        'colored_fix_status',
        'file_path',
        'retry_count',
        'created_at',
    )
    list_filter = (
        'status',
        'test_status',
        'fix_status',
        'vulnerability_type',
        'repository',
    )
    search_fields = (
        'title',
        'description',
        'file_path',
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'started_at', 'completed_at', 'verified_at')

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

    def colored_test_status(self, obj):
        """
        Display the test status with color coding.
        
        Args:
            obj (Task): The task instance.
            
        Returns:
            str: HTML formatted string with colored test status text.
        """
        colors = {
            'pending': 'gray',
            'generated': 'blue',
            'failed': 'orange',  # Test failed means vulnerability exists
            'passed': 'green',   # Test passed means vulnerability fixed
            'error': 'red'
        }

        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.test_status, 'black'),
            obj.test_status.upper()
        )
    colored_test_status.short_description = 'Test Status'

    def colored_fix_status(self, obj):
        """
        Display the fix status with color coding.
        
        Args:
            obj (Task): The task instance.
            
        Returns:
            str: HTML formatted string with colored fix status text.
        """
        colors = {
            'pending': 'gray',
            'generated': 'blue',
            'applied': 'orange',
            'verified': 'green',
            'failed': 'red'
        }

        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.fix_status, 'black'),
            obj.fix_status.upper()
        )
    colored_fix_status.short_description = 'Fix Status'

