"""
Analysis session models for tracking long-running repository analysis.
"""
from django.db import models
from django.utils import timezone

from apps.repository.models import Repository


class AnalysisSession(models.Model):
    """
    Tracks long-running analysis session with progress and state.

    Enables:
    - Real-time progress tracking
    - Crash recovery via checkpoints
    - Multi-hour analysis runs
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]

    # relationships
    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        related_name='analysis_sessions'
    )

    # Session metadata
    session_id = models.CharField(
        max_length=36,
        unique=True,
        help_text="Unique session identifier for tracking"
    )

    # Progress tracking
    total_files = models.IntegerField(default=0)
    files_analyzed = models.IntegerField(default=0)
    files_failed = models.IntegerField(default=0)

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Results
    vulnerabilities_found = models.IntegerField(default=0)
    task_created = models.IntegerField(default=0)
    prs_created = models.IntegerField(default=0)

    # Timestamps
    started_at = models.DateTimeField(
        null=True,
        blank=True
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    last_checkpoint_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    # Configuration
    create_prs = models.BooleanField(
        default=True,
        help_text="Automatically create PRs for verified fixes."
    )
    max_files = models.IntegerField(
        default=25,
        help_text="Maximum number of files to analyze per session."
    )

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['status'])
        ]
    
    def progress_percentage(self):
        """
        Calculate progress percentage based on files analyzed.

        Returns:
            float: Progress percentage (0-100).
        """
        if self.total_files == 0:
            return 0
        return min(self.files_analyzed / self.total_files * 100, 100)

    def estimated_time_remaining(self):
        """
        Estimate seconds remaining based on current rate.

        Returns:
            int: Estimated seconds remaining, or None if can't calculate.
        """
        if not self.started_at or self.files_analyzed == 0:
            return None

        elapsed = (timezone.now() - self.started_at).total_seconds()
        rate_per_second = self.files_analyzed / elapsed
        remaining_files = self.total_files - self.files_analyzed

        if rate_per_second > 0:
            return int(remaining_files / rate_per_second)
        return None

    def __str__(self):
        """Return string representation of the session."""
        return f"Session {self.session_id[:8]} - {self.status}"



class CheckPoint(models.Model):
    """
    Stores checkpoint data for analysis sessions.

    Checkpoints are created every N files to enable recovery.
    """
    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name='checkpoints'
    )

    # Checkpoint data
    checkpoint_number = models.IntegerField()
    files_processed = models.JSONField(
        help_text="List of files already processed"
    )
    last_file_index = models.IntegerField()

    # State snapshot
    state_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional state data for recovery"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-checkpoint_number']
        unique_together = ['session', 'checkpoint_number']

    def __str__(self):
        """Return string representation of the checkpoint."""
        session_short = self.session.session_id[:8]
        return f"Checkpoint #{self.checkpoint_number} for {session_short}"
    

