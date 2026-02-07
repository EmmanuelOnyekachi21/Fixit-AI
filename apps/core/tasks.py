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
    from apps.tasklog.models import TaskLog

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

def get_session_status_data(session_id):
    """
    Helper function for both HTTP and WebSocket.
    """
    session = AnalysisSession.objects.select_related(
        'repository'
    ).get(session_id=session_id)

    # Get recent logs efficiently
    recent_logs = session.logs.select_related('task')[:50]

    return {
        'session_id': str(session.session_id),
        'repository': {
            'id': session.repository.id,
            'name': session.repository.repo_name,
            'url': session.repository.repo_url,
        },
        'status': session.status,
        'progress': {
            'total_files': session.total_files,
            'files_analyzed': session.files_analyzed,
            'files_failed': session.files_failed,
            'percentage': round(session.progress_percentage(), 2),
        },
        'results': {
            'vulnerabilities_found': session.vulnerabilities_found,
            'tasks_created': session.task_created,
            'prs_created': session.prs_created,
        },
        'timestamps': {
            'started_at': session.started_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'last_checkpoint_at': session.last_checkpoint_at.isoformat() if session.last_checkpoint_at else None,
        },
        'logs': [log.to_dict() for log in recent_logs],
        'estimated_time_remaining_seconds': session.estimated_time_remaining() if session.status == 'running' else None,
    }


@shared_task(bind=True)
def process_single_task_async(self, task_id: int, create_pr: bool = False):
    """
    Process a single vulnerability task using the VerificationOrchestrator.
    
    This uses the proper verify-first workflow:
    1. Generate test that proves vulnerability exists
    2. Run test (should fail, confirming vulnerability)
    3. Generate fix
    4. Run test again (should pass, confirming fix works)
    5. Retry if fix fails
    6. Create PR if requested and fix is verified
    
    Args:
        task_id: ID of the Task to process
        create_pr: Whether to create a PR after verification
    
    Returns:
        dict: Processing results
    """
    from apps.task.models import Task
    from apps.verification.services.verification_orchestrator import VerificationOrchestrator
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get task
        task = Task.objects.select_related('repository').get(id=task_id)
        task.status = 'processing'
        task.save()
        
        logger.info(f"Processing task {task_id}: {task.vulnerability_type} in {task.file_path}")
        
        # Use the VerificationOrchestrator for the complete workflow
        orchestrator = VerificationOrchestrator()
        success = orchestrator.verify_and_fix_vulnerability(task, create_pr=create_pr)
        
        if success:
            logger.info(f"✓ Task {task_id} processing complete")
            return {
                'task_id': task_id,
                'status': task.status,
                'test_status': task.test_status,
                'fix_status': task.fix_status,
                'pr_created': bool(task.pr_url),
                'message': 'Verification and fix completed successfully'
            }
        else:
            logger.warning(f"⚠ Task {task_id} verification failed or marked as false positive")
            return {
                'task_id': task_id,
                'status': task.status,
                'test_status': task.test_status,
                'fix_status': task.fix_status,
                'pr_created': False,
                'message': task.validation_message or 'Verification failed'
            }
        
    except Task.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return {
            'task_id': task_id,
            'status': 'failed',
            'error': 'Task not found'
        }
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        try:
            task = Task.objects.get(id=task_id)
            task.status = 'failed'
            task.validation_message = f"Processing error: {str(e)}"
            task.save()
        except:
            pass
        
        raise


@shared_task(bind=True)
def process_all_tasks_async(self, session_id: str, create_pr: bool = False):
    """
    Process all tasks in a session automatically.
    
    Args:
        session_id: UUID of the AnalysisSession
        create_pr: Whether to create PRs for all tasks
    
    Returns:
        dict: Processing results
    """
    from apps.analysis_session.models import AnalysisSession
    from apps.task.models import Task
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        session = AnalysisSession.objects.get(session_id=session_id)
        logger.info(f"Processing all tasks for session {session_id}")
        
        # Get all tasks for this session's repository
        tasks = Task.objects.filter(repository=session.repository, status='pending')
        total_tasks = tasks.count()
        
        logger.info(f"Found {total_tasks} tasks to process")
        
        results = []
        successful = 0
        failed = 0
        
        for task in tasks:
            try:
                # Process each task
                result = process_single_task_async.delay(task.id, create_pr)
                results.append({
                    'task_id': task.id,
                    'celery_task_id': result.id,
                    'status': 'queued'
                })
                successful += 1
                logger.info(f"Queued task {task.id} for processing")
            except Exception as e:
                logger.error(f"Failed to queue task {task.id}: {e}")
                failed += 1
                results.append({
                    'task_id': task.id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Queued {successful}/{total_tasks} tasks successfully")
        
        return {
            'session_id': session_id,
            'total_tasks': total_tasks,
            'successful': successful,
            'failed': failed,
            'results': results
        }
        
    except AnalysisSession.DoesNotExist:
        logger.error(f"Session {session_id} not found")
        return {
            'session_id': session_id,
            'status': 'failed',
            'error': 'Session not found'
        }
    except Exception as e:
        logger.error(f"Error processing session {session_id}: {e}")
        raise
