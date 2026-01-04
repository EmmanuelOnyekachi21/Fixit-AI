"""
Management command to test Gemini integration.

Usage:
    python manage.py test_gemini
"""
from django.core.management.base import BaseCommand

from apps.gemini_analyzer.services import GeminiClient


class Command(BaseCommand):
    """Django management command to test Gemini API integration."""

    help = 'Test Gemini API integration with sample code'

    def handle(self, *args, **options):
        """
        Execute the test command.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """
        self.stdout.write(
            self.style.SUCCESS('Testing Gemini Integration...')
        )

        # Sample vulnerable code
        sample_code = """
import os

# Hardcoded API key - security issue!
API_KEY = "sk-1234567890abcdef"

def login(request):
    username = request.GET['username']
    password = request.GET['password']
    
    # SQL Injection vulnerability
    query = (
        f"SELECT * FROM users WHERE username='{username}' "
        f"AND password='{password}'"
    )
    
    # XSS vulnerability
    return f"<h1>Welcome {username}</h1>"
"""

        # Initialize client
        client = GeminiClient()

        self.stdout.write('Analyzing sample code...')

        # Analyze
        vulnerabilities = client.analyze_code(
            sample_code,
            "test_views.py"
        )

        # Display results
        self.stdout.write(
            f'\nFound {len(vulnerabilities)} vulnerabilities:\n'
        )

        for i, vuln in enumerate(vulnerabilities, 1):
            self.stdout.write(
                self.style.WARNING(
                    f'\n{i}. {vuln.get("title", "Unknown")}'
                )
            )
            self.stdout.write(f'   Type: {vuln.get("type", "unknown")}')
            self.stdout.write(
                f'   Line: {vuln.get("line_number", "N/A")}'
            )
            self.stdout.write(
                f'   Severity: {vuln.get("severity", "unknown")}'
            )
            description = vuln.get("description", "No description")
            self.stdout.write(
                f'   Description: {description[:100]}...'
            )

        # Show debug info
        if vulnerabilities:
            self.stdout.write(
                self.style.SUCCESS('\n✓ Gemini integration working!')
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    '\n✗ No vulnerabilities detected. '
                    'Check API key or prompt.'
                )
            )

        prompt_len = len(client.last_prompt or "")
        response_len = len(client.last_response or "")
        self.stdout.write(f'\nLast prompt length: {prompt_len} chars')
        self.stdout.write(f'Last response length: {response_len} chars')
