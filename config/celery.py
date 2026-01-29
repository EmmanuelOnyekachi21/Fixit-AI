"""
Celery configuration module.

This module configures Celery for asynchronous task processing.
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('fixit')

# Load config from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all registered Django apps
app.autodiscover_tasks()

# Import tasks from non-app modules
app.autodiscover_tasks(['apps.core'])


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Debug task to test Celery is working.

    Args:
        self: Task instance (bound).
    """
    print(f"Request: {self.request!r}")

