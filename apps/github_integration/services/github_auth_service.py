"""
GitHub authentication service module.

This module handles GitHub authentication, token validation,
and client initialization for bot operations.
"""
from django.conf import settings
from github import Github
from github.GithubException import BadCredentialsException, GithubException

from apps.github_integration.models import GithubAuth


class GithubAuthService:
    """
    Handles Github Authentication and token management.
    """
    def validate_token(self, token: str) -> dict:
        """
        Validate Github token and return user info.

        Args:
            token (str): Github personal access token
        
        Returns:
            dict: Validation result with user info or error.
                {
                    'valid': bool,
                    'username': str (if valid),
                    'error': str (if invalid)
                }
        """
        try:
            # Create github client with token
            g = Github(token)

            # Try to get authenticated user (validates token)
            user = g.get_user()
            username = user.login

            # Check token scopes (optional but good to verify)
            # Note: This requires the token to have appropriate permissions.

            return {
                'valid': True,
                'username': username,
                'name': user.name or username,
                'email': user.email
            }
        except BadCredentialsException:
            return {
                'valid': False,
                'error': 'Invalid token or token has been revoked'
            }
        except GithubException as e:
            return {
                'valid': False,
                'error': f'Github API error: {str(e)}'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def save_credentials(self, username: str) -> GithubAuth:
        """
        Save or update Github credentials.

        Note: Token is stored in .env file for hackathon simplicity.

        This method just tracks which bot account is being used.

        Args:
            username (str): Github bot username.
        
        Returns:
            GithubAuth: Created or updated auth record.
        """
        auth, created = GithubAuth.objects.update_or_create(
            username=username
        )

        auth.is_active = True
        auth.save()

        if created:
            print(f"✓ Created GitHub auth for: {username}")
        else:
            print(f"✓ Updated GitHub auth for: {username}")
        
        return auth
    
    def get_authenticated_client(self, username: str = None) -> Github:
        """
        Get authenticated Github client.
        
        Args:
            username (str, optional): Specific bot username.
                If None, uses token from settings.
        
        Returns:
            Github: Authenticated  Github client.
        
        Raises:
            ValueError: If no authentication found or token missing.
        """

        # For hackathon: Use token from .env
        token = getattr(settings, 'GITHUB_BOT_TOKEN', None)

        if not token:
            raise ValueError(
                "GITHUB_BOT_TOKEN not found in settings. "
                "Please add it to your .env file."
            )
        
        # Verify auth record exists (optional check)
        if username:
            try:
                auth = GithubAuth.objects.get(username=username, is_active=True)
            except GithubAuth.DoesNotExist:
                raise ValueError(
                    f"No active GitHub authentication found for: {username}"
                )
        
        return Github(token)
    
    def test_connection(self) -> dict:
        """
        Test Github connection with current credentials.

        Returns:
            dict: Connection test results.
        """
        try:
            token = getattr(settings, 'GITHUB_BOT_TOKEN', None)

            if not token:
                return {
                    'success': False,
                    'error': 'GITHUB_BOT_TOKEN not found in settings'
                }
            
            validation = self.validate_token(token)

            if validation['valid']:
                return {
                    'success': True,
                    'message': f'Connected as {validation['username']}',
                    'username': validation['username']
                }
            else:
                return {
                    'success': False,
                    'error': validation['error']
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
