"""
Analysis Session views module.

This module provides API endpoints for tracking and managing
long-running analysis sessions.
"""
from celery.result import AsyncResult
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.analysis_session.models import AnalysisSession, CheckPoint
from apps.core.tasks import analyze_repository_async
from apps.task.models import Task


@api_view(['GET'])
def get_session_status(request, session_id):
    """
    Get real-time analysis progress for a session.

    Args:
        request: HTTP request object.
        session_id: UUID of the analysis session.

    Returns:
        Response: Session status with progress, results, and timing info.
    """
    try:
        session = AnalysisSession.objects.get(session_id=session_id)

        response_data = {
            'session_id': session.session_id,
            'repository': {
                'id': session.repository.id,
                'name': session.repository.repo_name,
                'url': session.repository.repo_url,
            },
            'status': session.status,
            'progress': {
                'total_files': session.total_files,
                'files_analyzed': session.files_analyzed,
                'files_failed': session.files_failed,
                'percentage': round(session.progress_percentage(), 2),
            },
            'results': {
                'vulnerabilities_found': session.vulnerabilities_found,
                'tasks_created': session.task_created,
                'prs_created': session.prs_created,
            },
            'timestamps': {
                'started_at': session.started_at,
                'completed_at': session.completed_at,
                'last_checkpoint_at': session.last_checkpoint_at,
            },
            'error_message': session.error_message,
            'retry_count': session.retry_count,
        }

        # Add estimated time if running.
        if session.status == 'running':
            eta = session.estimated_time_remaining()
            if eta:
                response_data['estimated_time_remaining_seconds'] = eta
                minutes = round(eta / 60, 1)
                response_data['estimated_time_remaining_minutes'] = minutes

        return Response(response_data)
    except AnalysisSession.DoesNotExist:
        return Response(
            {'error': 'Session not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def resume_session(request, session_id):
    """
    Resume a failed or paused analysis session.

    Args:
        request: HTTP request object.
        session_id: UUID of the analysis session to resume.

    Returns:
        Response: Confirmation with new task_id.
    """
    try:
        session = AnalysisSession.objects.get(
            session_id=session_id
        )

        # Check if session can be resumed.
        if session.status not in ['failed', 'paused', 'running']:
            return Response(
                {
                    'error': (
                        f"Cannot resume session with status "
                        f"'{session.status}'"
                    ),
                    'current_status': session.status,
                    'message': (
                        'Only failed or paused sessions can be resumed.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If status is 'running', check if it's actually stuck.
        if session.status == 'running':
            from django.utils import timezone

            # If no checkpoint in last 5 minutes, consider it stuck.
            if session.last_checkpoint_at:
                time_since_checkpoint = (
                    timezone.now() - session.last_checkpoint_at
                ).total_seconds()

                if time_since_checkpoint < 300:  # 5 minutes
                    return Response(
                        {
                            'error': 'Session is currently running',
                            'message': (
                                'Session appears to be actively running. '
                                'Wait or force resume.'
                            ),
                            'last_checkpoint_seconds_ago': int(
                                time_since_checkpoint
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        # Resume analysis
        task = analyze_repository_async.delay(
            repository_id=session.repository.id,
            session_id=str(session.session_id),
            create_pr=session.create_prs
        )

        # Update session status
        session.status = 'running'
        session.retry_count += 1
        session.error_message = ''  # Clear previous error
        session.save()

        return Response({
            'session_id': session.session_id,
            'task_id': task.id,
            'message': 'Session resumed successfully.',
            'progress': {
                'files_analyzed': session.files_analyzed,
                'total_files': session.total_files,
                'percentage': round(session.progress_percentage(), 2),
            }
        })
    except AnalysisSession.DoesNotExist:
        return Response(
            {'error': 'Session not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
