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
    ]

    VULNERABILITY_TYPES = [
        ('xss', 'Cross-Site Scripting'),
        ('sql_injection', 'SQL Injection'),
        ('csrf', 'CSRF'),
        ('hardcoded_secret', 'Hardcoded Secret'),
        ('command_injection', 'Command Injection'),
        ('path_traversal', 'Path Traversal'),
        ('insecure_deserialization', 'Insecure Deserialization'),
    ]

    repository = models.ForeignKey(
        'Repository',
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
    retry_count = models.IntegerField(default=0)
    applied_fix = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """
        Return a string representation of the task.
        
        Returns:
            str: A formatted string showing the status and title, e.g., "[PENDING] Fix XSS vulnerability".
        """
        return f"[{self.status.upper()}] {self.title}"



    
