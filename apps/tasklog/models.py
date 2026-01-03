"""
TaskLog models module.

This module defines the TaskLog model for tracking detailed logs and events
associated with security vulnerability remediation tasks.
"""
from django.db import models


class TaskLog(models.Model):
    """
    Model representing a log entry for a task.
    
    This model captures detailed logging information for actions performed
    during the lifecycle of a security vulnerability task, including
    informational messages, warnings, and errors.
    
    Attributes:
        task (Task): The task this log entry belongs to.
        level (str): The severity level of the log entry (info, warning, error).
        action (str): A brief description of the action being logged.
        message (str): Detailed message describing what occurred.
        agent_note (str): Optional notes from the automated agent performing the action.
        timestamp (datetime): When this log entry was created.
    """
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES,
        default='info'
    )
    action = models.CharField(max_length=255)
    message = models.TextField()
    agent_note = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return a string representation of the task log.
        
        Returns:
            str: A formatted string showing task ID, level, and action, 
                 e.g., "123 - INFO - Analyzing vulnerability".
        """
        return (
            f"{self.task.id} - {self.level.upper()} - {self.action}"
        )


    class Meta:
        ordering = ['-timestamp']

