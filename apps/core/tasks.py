"""
Background tasks for Fixit.

This module contains Celery tasks that run asynchronously for
long-running operations like repository analysis.
"""
import time
import uuid

from celery import shared_task
from django.utils import timezone


@shared_task
def test_task(duration=5):
    """
    Simple test task to verify celery is working.

    Args:
        duration: How many seconds to run.

    Returns:
        str: Success message.
    """
    print(f"Test task started - will run for {duration} seconds")

    for i in range(duration):
        print(f"   Working... {i+1}/{duration}")
        time.sleep(1)
    
    print("Test task completed")
    return f"Task completed successfully after {duration} seconds!"


@shared_task(bind=True, max_retries=3)
def analyze_repository_async(
    self,
    repository_id: int,
    session_id: str = None,
    create_pr: bool = False
):
    """
    Asynchronous repository analysis with progress tracking.

    This task runs in the background and can be resumed after crashes.

    Args:
        self: Celery task instance (auto-injected by bind=True).
        repository_id: ID of repository to analyze.
        session_id: Optional existing session to resume.
        create_pr: Whether to create PRs for verified fixes.

    Returns:
        dict: Session ID, status, and results.
    """
    from apps.repository.models import Repository
    from apps.analysis_session.models import AnalysisSession
    from apps.core.analyzer_service import AnalyzerService

    try:
        # Get repository
        repo = Repository.objects.get(id=repository_id)
        print(f"Starting Analysis for {repo.owner}/{repo.repo_name}")

        # Create or resume session
        if session_id:
            session = AnalysisSession.objects.get(session_id=session_id)
            print(f"Resuming session {session_id}")
        else:
            session = AnalysisSession.objects.create(
                repository=repo,
                session_id=str(uuid.uuid4()),
                status='running',
                started_at=timezone.now(),
                create_prs=create_pr
            )
            print(f"Created new session {session.session_id}")

        # Run analysis
        analyzer = AnalyzerService()
        results = analyzer.analyze_with_checkpoints(
            repository=repo,
            session=session,
        )

        # Update session with results
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.vulnerabilities_found = results['vulnerabilities_found']
        session.task_created = results['tasks_created']
        session.save()

        # Update repository status
        repo.status = 'completed'
        repo.last_analyzed_at = timezone.now()
        repo.save()

        print(f"✓ Analysis complete: {session.session_id}")

        return {
            'session_id': session.session_id,
            'status': 'completed',
            'results': results
        }
    
    except Repository.DoesNotExist:
        error_msg = f"Repository {repository_id} not found"
        print(f"✗ {error_msg}")

        return {
            'session_id': session_id,
            'status': 'failed',
            'error': error_msg
        }
    
    except Exception as exc:
        error_msg = str(exc)
        print(f"✗ Analysis failed: {error_msg}")

        # Update session if it exists
        if session_id:
            try:
                session = AnalysisSession.objects.get(session_id=session_id)
                session.status = 'failed'
                session.error_message = error_msg
                session.retry_count += 1
                session.save()
            except AnalysisSession.DoesNotExist:
                pass  # Session might have been deleted
        # Retry logic (up to 3 times)
        try:
            raise self.retry(exc=exc, countdown=60)  # retry after 60 seconds
        except self.MaxRetriesExceededError:
            print(f"✗ Max retries exceeded for repository {repository_id}")
            return {
                'session_id': session_id,
                'status': 'failed',
                'error': f"Max retries exceeded: {error_msg}"
            }
