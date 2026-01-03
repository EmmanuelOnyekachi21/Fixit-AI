"""
Repository admin module.

This module configures the Django admin interface for managing Repository
models and their associated tasks.
"""
from django.contrib import admin
from .models import Repository
from apps.task.models import Task


class TaskInline(admin.TabularInline):
    """
    Inline admin interface for displaying tasks within a repository.
    
    This inline allows viewing associated tasks directly in the repository
    admin page without navigation.
    """
    model = Task
    extra = 0
    fields = (
        'title',
        'vulnerability_type',
        'status',
        'file_path',
        'created_at',
    )
    readonly_fields = fields
    can_delete = False


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Repository model.
    
    Provides a comprehensive interface for managing repositories including
    filtering, searching, and viewing associated tasks.
    """
    list_display = (
        "owner",
        "repo_name",
        "repo_url",
        "status",
        "created_at",
        "task_count",
        "last_analyzed_at",
    )
    list_filter = ("status",)
    search_fields = ("owner", "repo_name", 'repo_url')
    readonly_fields = ("created_at", "updated_at", "last_analyzed_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "owner",
                    "repo_name",
                    "repo_url",
                    "status",
                    "created_at",
                    "updated_at",
                    "last_analyzed_at",
                )
            },
        ),
    )
    inlines = [TaskInline]

    def task_count(self, obj):
        """
        Calculate and return the number of tasks for a repository.
        
        Args:
            obj (Repository): The repository instance.
            
        Returns:
            int: The count of tasks associated with this repository.
        """
        return obj.tasks.count()
    task_count.short_description = "Tasks"

