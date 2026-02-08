"""
Core API views for credential validation and system utilities.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from google import genai
from google.api_core import exceptions as google_exceptions
from github import Github
from github.GithubException import BadCredentialsException, GithubException


@api_view(['POST'])
def validate_credentials(request):
    """
    Validate Gemini API key and GitHub token.
    
    POST /api/v1/credentials/validate/
    
    Request body:
        {
            "gemini_key": "AIzaSy...",
            "github_token": "ghp_..."
        }
    
    Returns:
        {
            "valid": true/false,
            "error": "error message if invalid"
        }
    """
    gemini_key = request.data.get('gemini_key', '').strip()
    github_token = request.data.get('github_token', '').strip()
    
    if not gemini_key or not github_token:
        return Response({
            'valid': False,
            'error': 'Both gemini_key and github_token are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate Gemini API key
    try:
        client = genai.Client(api_key=gemini_key)
        # Try to list models to verify the key works
        models = client.models.list()
        # If we get here, the key is valid
        gemini_valid = True
        gemini_error = None
    except google_exceptions.Unauthenticated:
        gemini_valid = False
        gemini_error = "Invalid Gemini API key"
    except google_exceptions.PermissionDenied:
        gemini_valid = False
        gemini_error = "Gemini API key does not have required permissions"
    except Exception as e:
        gemini_valid = False
        gemini_error = f"Gemini validation error: {str(e)}"
    
    # Validate GitHub token
    try:
        g = Github(github_token)
        # Try to get user info to verify the token works
        user = g.get_user()
        user.login  # Access a property to trigger API call
        github_valid = True
        github_error = None
    except BadCredentialsException:
        github_valid = False
        github_error = "Invalid GitHub token"
    except GithubException as e:
        github_valid = False
        github_error = f"GitHub validation error: {e.data.get('message', str(e))}"
    except Exception as e:
        github_valid = False
        github_error = f"GitHub validation error: {str(e)}"
    
    # Both must be valid
    if gemini_valid and github_valid:
        return Response({
            'valid': True,
            'message': 'Credentials validated successfully'
        }, status=status.HTTP_200_OK)
    else:
        errors = []
        if not gemini_valid:
            errors.append(f"Gemini: {gemini_error}")
        if not github_valid:
            errors.append(f"GitHub: {github_error}")
        
        return Response({
            'valid': False,
            'error': '; '.join(errors)
        }, status=status.HTTP_400_BAD_REQUEST)
