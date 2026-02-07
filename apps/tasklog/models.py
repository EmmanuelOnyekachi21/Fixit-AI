"""
TaskLog models module.

This module defines the TaskLog model for tracking detailed logs and events
associated with security vulnerability remediation tasks.
"""
from django.db import models
from apps.task.models import Task
from apps.analysis_session.models import AnalysisSession


class LogType(models.TextChoices):
    INFO = 'info', 'Info'
    SUCCESS = 'success', 'Success'
    ERROR = 'error', 'Error'
    WARNING = 'warning', 'Warning'


class TaskLog(models.Model):
    """
    Model representing a log entry for a task.
    
    This model captures detailed logging information for actions performed
    during the lifecycle of a security vulnerability task, including
    informational messages, warnings, and errors.
    
    Attributes:
        task (Task): The task this log entry belongs to (nullable for session-level logs).
        session (AnalysisSession): The analysis session this log belongs to.
        log_type (str): The severity level of the log entry (info, warning, error, success).
        action (str): A brief description of the action being logged.
        message (str): Detailed message describing what occurred.
        agent_note (str): Optional notes from the automated agent performing the action.
        timestamp (datetime): When this log entry was created.
        file_path (str): Optional file path being processed.
        line_number (int): Optional line number in the file.
    """
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,  # Allow session-level logs
        blank=True
    )
    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="logs",
        null=True,
        db_index=True
    )
    log_type = models.CharField(
        max_length=10,
        choices=LogType.choices,
        default=LogType.INFO
    )
    action = models.CharField(max_length=255)
    message = models.TextField()
    agent_note = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Optional: Store additional context
    file_path = models.CharField(max_length=500, blank=True)
    line_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        """
        Return a string representation of the task log.
        
        Returns:
            str: A formatted string showing task ID or session ID, log type, and message, 
                 e.g., "Task 123 - INFO - Analyzing vulnerability" or "Session abc - INFO - Starting analysis".
        """
        if self.task:
            prefix = f"Task {self.task.id}"
        elif self.session:
            prefix = f"Session {self.session.session_id}"
        else:
            prefix = "Log"
        
        return f"{prefix} - {self.log_type.upper()} - {self.message[:50]}"


    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session', '-timestamp']),
            models.Index(fields=['task', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def to_dict(self):
        """
        Serialize for WebSocket/API
        """
        return {
            'id': self.id,
            'message': self.message,
            'type': self.log_type,  # Use log_type instead of level
            'timestamp': self.timestamp.isoformat(),
            'task_id': self.task.id if self.task else None,
            'file_path': self.file_path,
            'line_number': self.line_number,
        }

