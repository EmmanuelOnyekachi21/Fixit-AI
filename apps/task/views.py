"""
Task views module.

This module provides API endpoints for task management and status tracking.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.task.models import Task
from apps.verification.services.verification_orchestrator import VerificationOrchestrator


@api_view(['GET'])
def get_task_details(request, task_id):
    """
    Retrieve details of a specific task by its ID.

    Args:
        request: The HTTP request object.
        task_id (int): The ID of the task to retrieve.

    Returns:
        Response: The HTTP response containing task details.
    """
    try:
        task = Task.objects.get(pk=task_id)
        return Response({'task': task})
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=404)
    
    pr = task.pull_request.first()

    return Response({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'vulnerability_type': task.vulnerability_type,
        'file_path': task.file_path,
        'line_number': task.line_number,
        'status': task.status,
        'test_code': task.test_code,
        'test_status': task.test_status,
        'fix_code': task.fix_code,
        'fix_status': task.fix_status,
        'pr': {
            'number': pr.pr_number,
            'url': pr.pr_url,
            'status': pr.status
        } if pr else None
    })


@api_view(['GET'])
def get_task_status(request, task_id):
    """
    Get status of a background task.

    Args:
        request: HTTP request object.
        task_id: Celery task ID.

    Returns:
        Response: Task status and result if completed.
    """
    from celery.result import AsyncResult

    task = AsyncResult(task_id)

    response_data = {
        'task_id': task_id,
        'status': task.status,
    }

    if task.status == 'SUCCESS':
        response_data['result'] = task.result
    elif task.status == 'FAILURE':
        response_data['error'] = str(task.info)

    return Response(response_data)


@api_view(['POST'])
def verify_and_fix(request, task_id):
    """
    Verify vulnerability and attempt to fix it.

    Request body:
        {
            "create_pr": true
        }
    
    Returns:
        {
            "success": true,
            "task_id": 1,
            "status": "completed",
            "test_status": "passed",
            "fix_status": "verified",
            "message": "Verification completed"
        }
    """
    create_pr = request.data.get('create_pr', False)

    if isinstance(create_pr, str):
        create_pr = create_pr.lower() == 'true'

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response(
            {'error': 'Task not found'},
            status=404
        )
    
    orchestrator = VerificationOrchestrator()
    success = orchestrator.verify_and_fix_vulnerability(
        task,
        create_pr=create_pr
    )

    return Response(
        {
            'success': success,
            'task_id': task.id,
            'status': task.status,
            'test_status': task.test_status,
            'fix_status': task.fix_status,
            'message': "Verification completed" if success else "Verification failed"
        },
        status=200
    )



@api_view(['POST'])
def generate_fix(request, task_id):
    """
    Manually trigger fix generation for a single task.
    
    POST /api/v1/tasks/{task_id}/generate-fix/
    Body: {"create_pr": true/false}
    
    Returns:
        {
            "task_id": int,
            "status": "processing",
            "celery_task_id": str,
            "message": "Fix generation started"
        }
    """
    from apps.core.tasks import process_single_task_async
    from rest_framework import status as http_status
    
    try:
        task = Task.objects.get(id=task_id)
        create_pr = request.data.get('create_pr', False)
        
        # Convert string to boolean if needed
        if isinstance(create_pr, str):
            create_pr = create_pr.lower() == 'true'
        
        # Start Celery task
        result = process_single_task_async.delay(task_id, create_pr)
        
        return Response({
            'task_id': task_id,
            'status': 'processing',
            'celery_task_id': result.id,
            'message': 'Fix generation started'
        }, status=http_status.HTTP_202_ACCEPTED)
        
    except Task.DoesNotExist:
        return Response({
            'error': 'Task not found'
        }, status=http_status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def process_all_tasks(request, session_id):
    """
    Automatically process all tasks in a session.
    
    POST /api/v1/sessions/{session_id}/process-all/
    Body: {"create_pr": true/false}
    
    Returns:
        {
            "session_id": str,
            "total_tasks": int,
            "status": "processing",
            "celery_task_id": str,
            "message": "Processing X tasks"
        }
    """
    from apps.analysis_session.models import AnalysisSession
    from apps.core.tasks import process_all_tasks_async
    from rest_framework import status as http_status
    
    try:
        session = AnalysisSession.objects.get(session_id=session_id)
        create_pr = request.data.get('create_pr', False)
        
        # Convert string to boolean if needed
        if isinstance(create_pr, str):
            create_pr = create_pr.lower() == 'true'
        
        # Count tasks
        total_tasks = Task.objects.filter(
            repository=session.repository,
            status='pending'
        ).count()
        
        # Start Celery task
        result = process_all_tasks_async.delay(session_id, create_pr)
        
        return Response({
            'session_id': session_id,
            'total_tasks': total_tasks,
            'status': 'processing',
            'celery_task_id': result.id,
            'message': f'Processing {total_tasks} tasks'
        }, status=http_status.HTTP_202_ACCEPTED)
        
    except AnalysisSession.DoesNotExist:
        return Response({
            'error': 'Session not found'
        }, status=http_status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_task_detail(request, task_id):
    """
    Get detailed information about a task including fix and tests.
    
    GET /api/v1/tasks/{task_id}/
    
    Returns full task details with all generated code.
    """
    from rest_framework import status as http_status
    
    try:
        task = Task.objects.select_related('repository').get(id=task_id)
        
        return Response({
            'id': task.id,
            'title': task.title,
            'vulnerability_type': task.vulnerability_type,
            'description': task.description,
            'file_path': task.file_path,
            'line_number': task.line_number,
            'severity': task.severity,
            'original_code': task.original_code or '',
            'fix_code': task.fix_code or '',
            'fix_explanation': task.fix_explanation or '',
            'test_code': task.test_code or '',
            'status': task.status,
            'test_status': task.test_status,
            'fix_status': task.fix_status,
            'pr_url': task.pr_url,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'repository': {
                'id': task.repository.id,
                'name': f"{task.repository.owner}/{task.repository.repo_name}",
                'url': task.repository.repo_url
            }
        })
        
    except Task.DoesNotExist:
        return Response({
            'error': 'Task not found'
        }, status=http_status.HTTP_404_NOT_FOUND)
