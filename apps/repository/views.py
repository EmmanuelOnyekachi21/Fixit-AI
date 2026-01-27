"""
Repository views module.

This module defines API views for managing repositories, including
creation and retrieval of GitHub repository records.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Repository
from .serializers import (
    RepositorySerializer,
    RepositoryWriteSerializer
)
from apps.core.analyzer_service import AnalyzerService
from django.shortcuts import get_object_or_404


@api_view(['POST'])
def create_repository(request):
    """
    Create or retrieve a repository from a GitHub URL.
    
    Accepts a POST request with a GitHub repository URL, validates it,
    and creates a new repository record or returns an existing one.
    
    Args:
        request (Request): The HTTP request containing repo_url in
                          data.
        
    Returns:
        Response: JSON response with repository data and appropriate
                  status code.
                  - 201 Created: New repository was created
                  - 200 OK: Repository already exists
                  - 400 Bad Request: Invalid data provided
    """
    serializer = RepositoryWriteSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        repository = serializer.save()

        # Trigger analysis immediately
        analyzer = AnalyzerService()

        try:
            tasks = analyzer.analyze_repository(repository.id)

            # Refresh repository to get updated status
            repository.refresh_from_db()

            # Prepare response with analysis results
            response_data = RepositorySerializer(repository).data
            response_data['analysis'] = {
                'status': 'success',
                'tasks_created': len(tasks),
                'message': f'Analysis complete. Found {len(tasks)} security issues.'
            }
                    
        except Exception as e:

            # Analysis failed, but repository exists
            repository.refresh_from_db()
            response_data = RepositorySerializer(repository).data
            response_data['analysis'] = {
                'status': 'failed',
                'tasks_created': 0,
                'message': f'Analysis failed: {str(e)}'
            }
            print(f"Analysis failed: {e}")

        created = serializer.context.get('created', False)
        status_code = (
            status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

        return Response(
            response_data,
            status=status_code
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET'])
def list_repository_tasks(request, repository_id):
    """
    List all tasks for a repository.
    """

    try:
        repository = Repository.objects.get(id=repository_id)
    except Repository.DoesNotExist:
        return Response({
            'error': 'Repository not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    tasks = Task.objects.filter(
        repository=repository
    )

    task_data = [
        {
            'id': task.id,
            'title': task.title,
            'vulnerability_type': task.vulnerability_type,
            'file_path': task.file_path,
            'line_number': task.line_number,
            'status': task.status,
            'test_status': task.test_status,
            'fix_status': task.fix_status,
            'has_pr': task.pull_requests.exists()
        } for task in tasks
    ]

    return Response({
        'repository_id': repository_id,
        'total_task': len(task_data),
        'tasks': task_data
    })
