from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.repository.models import Repository
from apps.task.models import Task
from apps.github_integration.services.github_auth_service import GithubAuthService
from apps.verification.services.verification_orchestrator import VerificationOrchestrator


@api_view(['POST'])
def setup_github_auth(request):
    """
    Setup Github authentication.

    Request body:
        {
            "token": "ghp_token_here"
        }
    
    Returns:
        Success: {"message": "...", "username": "..."}
        Error: {"error": "..."}
    """
    token = request.data.get('token')

    if not token:
        return Response(
            {'error': 'Token is required'},
            status=400
        )
    
    auth_service = GithubAuthService()
    validation = auth_service.validate_token(token)

    if not validation['valid']:
        return Response(
            {'error': validation['error']},
            status=400
        )
    
    # Save credentials
    auth_service.save_credentials(validation['username'])
    return Response({
        'message': 'Github authentication set up successfully',
        'username': validation['username']
    })


@api_view(['POST'])
def create_prs_for_repository(request, repository_id):
    """
    Create PRs for all verified fixes in a repository.

    URL: /api/repositories/{repository_id}/create-prs/

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

    
