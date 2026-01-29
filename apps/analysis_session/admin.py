"""
Admin interface for analysis sessions.
"""
from django.contrib import admin

from .models import AnalysisSession, CheckPoint


@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    """Admin interface for AnalysisSession."""
    
    list_display = [
        'session_id_short',
        'repository',
        'status',
        'progress_display',
        'started_at',
        'completed_at'
    ]
    list_filter = ['status', 'started_at']
    search_fields = ['session_id', 'repository__repo_name']
    readonly_fields = [
        'session_id',
        'started_at',
        'completed_at',
        'last_checkpoint_at'
    ]
    
    def session_id_short(self, obj):
        """Show shortened session ID."""
        return obj.session_id[:8]
    session_id_short.short_description = 'Session'
    
    def progress_display(self, obj):
        """Show progress as fraction and percentage."""
        percentage = obj.progress_percentage()
        return (
            f"{obj.files_analyzed}/{obj.total_files} "
            f"({percentage:.1f}%)"
        )
    progress_display.short_description = 'Progress'


@admin.register(CheckPoint)
class CheckpointAdmin(admin.ModelAdmin):
    """Admin interface for Checkpoint."""
    
    list_display = [
        'checkpoint_number',
        'session_short',
        'last_file_index',
        'created_at'
    ]
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    
    def session_short(self, obj):
        """Show shortened session ID."""
        return obj.session.session_id[:8]
    session_short.short_description = 'Session'

