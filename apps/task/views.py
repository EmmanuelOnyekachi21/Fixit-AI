"""
Task views module.

This module will contain views for task management.
Currently empty as views are not yet implemented.
"""
from apps.task.models import Task
from rest_framework.decorators import api_view
from rest_framework.response import Response


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

