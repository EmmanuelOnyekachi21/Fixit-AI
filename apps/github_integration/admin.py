"""
GitHub Integration admin module.

This module configures the Django admin interface for GitHub authentication
and pull request management.
"""
from django.contrib import admin

from .models import GithubAuth, PullRequest


@admin.register(GithubAuth)
class GithubAuthAdmin(admin.ModelAdmin):
    """
    Admin interface for GithubAuth model.
    """
    list_display = ('username', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('username',)
    readonly_fields = [
        'created_at',
        'updated_at'
    ]

    fieldsets = (
        ('Authentication Details', {
            'fields': ('username', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PullRequest)
class PullRequestAdmin(admin.ModelAdmin):
    """Admin Interface for PullRequest model."""

    list_display = [
        'pr_number',
        'title',
        'repository',
        'status',
        'created_at',
    ]
    list_filter = ['status', 'created_at', 'repository']
    search_fields = ['title', 'description', 'branch_name']
    readonly_fields = ['created_at', 'merged_at']
    
    fieldsets = (
        ('Pull Request Info', {
            'fields': ('task', 'repository', 'pr_number', 'pr_url', 'branch_name')
        }),
        ('Content', {
            'fields': ('title', 'description')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'merged_at')
        }),
    )

    def get_readonly_fields(self, requests, obj=None):
        """
        Make certain fields readonly after creation.
        """
        if obj:
            return self.readonly_fields + ['task', 'repository', 'pr_number']
        return self.readonly_fields

