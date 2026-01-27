"""
Task models module.

This module defines the Task model for managing security vulnerability
detection and remediation tasks within repositories.
"""
from django.db import models
from apps.repository.models import Repository


class Task(models.Model):
    """
    Model representing a security vulnerability task for a repository.
    
    This model tracks individual security vulnerabilities found in repositories,
    including their type, location, status, and remediation progress.
    
    Attributes:
        repository (Repository): The repository this task belongs to.
        title (str): A brief title describing the vulnerability.
        description (str): Detailed description of the vulnerability.
        vulnerability_type (str): The type of security vulnerability detected.
        file_path (str): Path to the file containing the vulnerability.
        line_number (int): Line number where the vulnerability is located.
        status (str): Current status of the task (pending, running, completed, etc.).
        retry_count (int): Number of times the fix has been retried.
        applied_fix (str): The fix that was applied to resolve the vulnerability.
        created_at (datetime): Timestamp when the task was created.
        started_at (datetime): Timestamp when work on the task began.
        completed_at (datetime): Timestamp when the task was completed.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('validating', 'Validating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('abandoned', 'Abandoned'),
        ('false_positive', 'False Positive'),
        ('pr_created', 'PR Created')
    ]

    VULNERABILITY_TYPES = [
        ('xss', 'Cross-Site Scripting'),
        ('sql_injection', 'SQL Injection'),
        ('csrf', 'CSRF'),
        ('hardcoded_secret', 'Hardcoded Secret'),
        ('command_injection', 'Command Injection'),
        ('path_traversal', 'Path Traversal'),
        ('authentication_bypass', 'Authentication Bypass'),
        ('insecure_deserialization', 'Insecure Deserialization'),
    ]

    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    vulnerability_type = models.CharField(
        max_length=50,
        choices=VULNERABILITY_TYPES
    )
    file_path = models.CharField(
        max_length=300,
        null=True,
        blank=True
    )
    line_number = models.IntegerField(
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    applied_fix = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # New fields
    test_code = models.TextField(
        blank=True,
        help_text='Generated test that proves vulnerability exists'
    )
    test_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('generated', 'Test Generated'),
            ('failed', 'Test Failed'),  # Proves vulnerability exists
            ('passed', 'Test Passed'),  # Vulnerability fixed
            ('error', 'Test Error'),
        ],
        default='pending'
    )

    fix_code = models.TextField(
        blank=True,
        help_text='Generated fix code for the vulnerability'
    )
    fix_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('generated', 'Fix Generated'),
            ('applied', 'Fix Applied'),
            ('verified', 'Fix Verified'),
            ('failed', 'Fix Failed'),
        ],
        default='pending'
    )
    retry_count = models.IntegerField(
        default=0,
        help_text='Number of times the fix has been retried'
    )
    validation_message = models.TextField(
        blank=True,
        help_text="Details from test/fix validation"
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the fix was verified"
    )
    
    # Store original file content for fix generation
    original_code = models.TextField(
        blank=True,
        help_text="Original vulnerable code from the file"
    )

    def __str__(self):
        """
        Return a string representation of the task.
        
        Returns:
            str: A formatted string showing the status and title, e.g., "[PENDING] Fix XSS vulnerability".
        """
        return f"[{self.status.upper()}] {self.title}"



    
