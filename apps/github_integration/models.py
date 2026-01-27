"""
GitHub Integration models module.

This module defines models for GitHub authentication and pull request tracking.
"""
from django.db import models

from apps.repository.models import Repository
from apps.task.models import Task


class GithubAuth(models.Model):
    """
    Stores the Github bot Authentication credentials.

    For hackathon: stores bot account credentials (single account approach).
    Token is stored in .env file for simplicity.

    Attributes:
        username (str): Github bot username  # fixit-bot-agent
        is_active (bool): whether this auth is currently active.
        created_at (datetime): When credentials were added.
        updated_at (datetime): Last update timestamp
    """

    username = models.CharField(
        max_length=255,
        unique=True,
        help_text="Github bot username"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this auth is currently active."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When credentials were added."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp."
    )

    def __str__(self):
        """
        Return string representation of the object.
        """
        return f"Github Auth: {self.username}"
    
    class Meta:
        verbose_name = 'Github Authentication'
        verbose_name_plural = 'Github Authentications'


class PullRequest(models.Model):
    """
    Tracks pull requests created by the agent.

    Links verified fixes to actual Github pull requests,
    enabling tracking of PR status and outcomes.

    Attributes:
        task (Task): The task this PR fixes
        repository (Repository): The repository where PR was created.
        pr_number (int): Github PR number
        pr_url (str): Full URL to the PR on Github
        branch_name (str): Name of the branch containing this fix.
        title (str): PR title
        description (str): PR description
        status (str): Current status of the PR (open, merged, closed, draft).
        created_at (datetime): When the PR was created.
        merged_at (datetime): When PR was merged (if applicable).
    """
    STATUS_CHOICE = [
        ('open', 'Open'),
        ('merged', 'Merged'),
        ('closed', 'Closed'),
        ('draft', 'Draft')
    ]

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        help_text="The task this PR fixes",
        related_name='pull_requests'
    )
    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        help_text="The repository where PR was created.",
        related_name='pull_requests'
    )
    pr_number = models.IntegerField(
        help_text="Github PR number"
    )
    pr_url = models.URLField(
        help_text="Full URL to the PR on Github"
    )
    branch_name = models.CharField(
        max_length=255,
        help_text="Name of the branch containing this fix."
    )
    title = models.CharField(
        max_length=255,
        help_text="PR title"
    )
    description = models.TextField(
        help_text="PR description in markdown format"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default='open',
        help_text='Current PR status'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When PR was created"
    )
    merged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When PR was merged (if applicable)."
    )

    def __str__(self):
        """
        Return String representation.
        """
        return f"PR #{self.pr_number}: {self.title}"
    

    class Meta:
        verbose_name = "Pull Request"
        verbose_name_plural = 'Pull Requests'
        unique_together = ['repository', 'pr_number']
        ordering = ['-created_at']

