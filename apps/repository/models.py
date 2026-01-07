"""
Repository models module.

This module defines the Repository model for managing GitHub repository
information and analysis status within the application.
"""
from django.db import models


class Repository(models.Model):
    """
    Model representing a GitHub repository and its analysis status.
    
    This model stores information about repositories being tracked and analyzed,
    including their ownership, URL, and current processing status.
    
    Attributes:
        owner (str): The GitHub username or organization that owns the repository.
        repo_name (str): The name of the repository.
        repo_url (str): The full URL to the repository (must be unique).
        status (str): Current status of the repository analysis.
        created_at (datetime): Timestamp when the repository was added to the system.
        updated_at (datetime): Timestamp of the last update to this record.
        last_analyzed_at (datetime): Timestamp of the most recent analysis completion.
    """
    STATUS_CHOICES = [
        ('idle', 'Idle'),
        ('analyzing', 'Analyzing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('paused', 'Paused'),
    ]

    owner = models.CharField(max_length=255)
    repo_name = models.CharField(max_length=255)
    repo_url = models.URLField(unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='idle'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_analyzed_at = models.DateTimeField(null=True, blank=True)

    # Example values: "Analyzing 3/10 files", "Completed", "Error", "Paused"
    analysis_progress = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        """
        Return a string representation of the repository.
        
        Returns:
            str: A formatted string in the format "owner/repo_name".
        """
        return f"{self.owner}/{self.repo_name}"

    class Meta:
        verbose_name_plural = 'Repositories'
        unique_together = ('owner', 'repo_name')
