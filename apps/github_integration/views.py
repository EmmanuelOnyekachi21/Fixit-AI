"""
GitHub Integration views module.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.github_auth_service import GithubAuthService


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
