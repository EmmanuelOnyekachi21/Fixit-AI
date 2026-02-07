"""
Utility functions for task logging with real-time WebSocket broadcasting.
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import TaskLog, LogType


def create_log(session, task, message, log_type=LogType.INFO, file_path='', line_number=None):
    """
    Create a log entry and broadcast it via WebSocket.
    
    Args:
        session: AnalysisSession instance
        task: Task instance (can be None for session-level logs)
        message: Log message string
        log_type: LogType enum value (INFO, SUCCESS, ERROR, WARNING)
        file_path: Optional file path being processed
        line_number: Optional line number
    
    Returns:
        TaskLog instance
    """
    # Create the log entry
    log = TaskLog.objects.create(
        task=task,
        session=session,
        message=message,
        log_type=log_type,
        file_path=file_path,
        line_number=line_number
    )
    
    # The signal will automatically broadcast via WebSocket
    # (see apps/tasklog/signals.py)
    
    return log


def create_session_log(session, message, log_type=LogType.INFO):
    """
    Create a session-level log (no specific task).
    
    Useful for general progress messages like "Starting analysis..."
    """
    # Create a dummy task or use None
    # For session-level logs, we'll create without a task
    log = TaskLog.objects.create(
        task=None,  # No specific task
        session=session,
        message=message,
        log_type=log_type
    )
    
    return log


def broadcast_progress_update(session):
    """
    Broadcast session progress update via WebSocket.
    
    Args:
        session: AnalysisSession instance with updated progress
    """
    channel_layer = get_channel_layer()
    room_group_name = f'session_{session.session_id}'
    
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'session_update',
            'data': {
                'files_analyzed': session.files_analyzed,
                'total_files': session.total_files,
                'progress_percentage': round(session.progress_percentage(), 2),
                'vulnerabilities_found': session.vulnerabilities_found,
                'current_file': getattr(session, 'current_file', ''),
                'estimated_time_remaining_seconds': session.estimated_time_remaining(),
            }
        }
    )


def broadcast_analysis_complete(session):
    """
    Broadcast analysis completion via WebSocket.
    
    Args:
        session: Completed AnalysisSession instance
    """
    channel_layer = get_channel_layer()
    room_group_name = f'session_{session.session_id}'
    
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'analysis_complete',
            'data': {
                'session_id': str(session.session_id),
                'status': 'completed',
                'vulnerabilities_found': session.vulnerabilities_found,
                'tasks_created': session.task_created,
                'prs_created': session.prs_created,
            }
        }
    )
