"""
Task views module.

This module provides API endpoints for task management and status tracking.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.task.models import Task


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

