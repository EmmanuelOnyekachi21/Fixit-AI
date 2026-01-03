"""
TaskLog admin module.

This module configures the Django admin interface for managing TaskLog
models that track detailed logging information for tasks.
"""
from django.contrib import admin
from apps.tasklog.models import TaskLog


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the TaskLog model.
    
    Provides an interface for creating and viewing task logs with filtering
    by level and task, and displays a preview of log messages.
    """
    list_display = (
        'timestamp',
        'task',
        'level',
        'action',
        'short_message',
    )

    list_filter = ('level', 'task')
    ordering = ('-timestamp',)

    readonly_fields = ('timestamp',)

    def short_message(self, obj):
        """
        Return a truncated preview of the log message.
        
        Args:
            obj (TaskLog): The task log instance.
            
        Returns:
            str: The first 100 characters of the message.
        """
        return obj.message[:100]
    short_message.short_description = "Message Preview"
