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
from apps.task.models import Task
from apps.verification.services.verification_orchestrator import VerificationOrchestrator


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
    from apps.core.tasks import analyze_repository_async

    serializer = RepositoryWriteSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        repository = serializer.save()

        # Get options
        create_prs = request.data.get('create_prs', False)

        # Create session first
        import uuid
        from django.utils import timezone
        from apps.analysis_session.models import AnalysisSession
        
        session = AnalysisSession.objects.create(
            repository=repository,
            session_id=str(uuid.uuid4()),
            status='running',
            started_at=timezone.now(),
            create_prs=create_prs
        )

        # Start the async analysis with the session_id
        task = analyze_repository_async.delay(
            repository_id=repository.id,
            session_id=str(session.session_id),
            create_pr=create_prs
        )

        return Response({
            'repository': RepositorySerializer(repository).data,
            'task_id': task.id,
            'session_id': str(session.session_id),
            'message': 'Analysis started in background. Use session_id to check status'
        }, status=status.HTTP_202_ACCEPTED)

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
    ).select_related('repository').prefetch_related('pull_requests')

    task_data = []
    for task in tasks:
        pr = task.pull_requests.first()
        task_data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'vulnerability_type': task.vulnerability_type,
            'file_path': task.file_path,
            'line_number': task.line_number,
            'severity': task.severity,
            'status': task.status,
            'test_status': task.test_status,
            'fix_status': task.fix_status,
            'original_code': task.original_code or '',
            'fix_code': task.fix_code or '',
            'fix_explanation': task.fix_explanation or '',
            'test_code': task.test_code or '',
            'pr_url': pr.pr_url if pr else None,
            'created_at': task.created_at.isoformat() if task.created_at else None,
        })

    return Response({
        'repository_id': repository_id,
        'total_task': len(task_data),
        'tasks': task_data
    })


@api_view(['POST'])
def create_prs_for_repository(request, repository_id):
    """
    Create PRs for all verified fixes in a repository.

    URL: /api/v1/repositories/{repository_id}/pull-requests/

    Returns:
        {
            'message': 'Created X pull requests',
            'prs': [
                {'task_id': 1, 'pr_url': 'https://...'},
                ...
            ]
        }
    """
    try:
        repository = Repository.objects.get(id=repository_id)
    except Repository.DoesNotExist:
        return Response(
            {'error': 'Repository not found'},
            status=404
        )
    
    # Get all verified tasks without PRs
    verified_tasks = Task.objects.filter(
        repository=repository,
        fix_status='verified',
        pull_requests__isnull=True
    )

    if not verified_tasks.exists():
        return Response({
            'message': 'No verified fixes to create PRs for',
            'prs': []
        })
    
    orchestrator = VerificationOrchestrator()
    created_prs = []

    for task in verified_tasks:
        try:
            orchestrator._create_github_pr(task)
            pr = task.pull_requests.first()
            created_prs.append({
                'task_id': task.id,
                'pr_url': pr.pr_url if pr else None
            })
        except Exception as e:
            print(f"failed to create PR for task {task.id}: {e}")
            # continue with other tasks
    
    return Response({
        'message': f'Created {len(created_prs)} pull requests',
        'prs': created_prs
    })

