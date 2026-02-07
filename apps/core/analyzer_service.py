"""
Core analyzer service module.

This module orchestrates the complete repository analysis workflow,
coordinating between GitHub integration and Gemini analysis services.
"""
import logging
from typing import List

from django.utils import timezone

from apps.gemini_analyzer.services.code_analyzer import CodeAnalyzer
from apps.gemini_analyzer.exceptions import (
    GeminiRateLimitError,
    GeminiNetworkError,
    GeminiAPIError,
    ResponseParsingError
)
from apps.github_integration.services.github_client import GitHubClient
from apps.repository.models import Repository
from apps.task.models import Task

logger = logging.getLogger(__name__)


class AnalyzerService:
    """
    Orchestrates repository security analysis workflow.

    Coordinates fetching code from GitHub and analyzing it with Gemini
    to identify security vulnerabilities.
    """

    def __init__(self):
        """Initialize the analyzer service with required clients."""
        self.code_analyzer = CodeAnalyzer()
        self.github_service = GitHubClient()

    def analyze_repository(self, repository_id: int) -> List[Task]:
        """
        Analyze a repository for security vulnerabilities.

        Fetches files from GitHub, analyzes them with Gemini,
        and creates Task objects for found vulnerabilities.

        Args:
            repository_id: ID of the Repository to analyze.

        Returns:
            List of created Task objects.

        Raises:
            Repository.DoesNotExist: If repository ID is invalid.
            Exception: For other errors during analysis.
        """
        try:
            repository = Repository.objects.get(id=repository_id)
            # Validate repository is in correct state
            if repository.status == 'analyzing':
                print(
                    f"Repository {repository_id} is already "
                    f"being analyzed."
                )
                return []

            # Update status to analyzing
            print(f"Starting analysis of {repository}")
            repository.status = 'analyzing'
            repository.save()

            # fetch files from repository
            try:
                files = self.github_service.get_repo_files(
                    repository.owner,
                    repository.repo_name
                )

                if not files:
                    print(
                        f"No files found in repository {repository_id}"
                    )
                    repository.status = 'error'
                    repository.save()
                    raise
            except Exception as e:
                print(
                    f"Error fetching files from repository "
                    f"{repository_id}: {e}"
                )
                repository.status = 'error'
                repository.save()
                raise

            # Analyze each file
            all_tasks = []
            total_files = len(files)

            print(f"Analyzing {total_files} files...")

            for index, file_info in enumerate(files, start=1):

                # Update progress
                progress = f"Analyzing {index}/{total_files} files"
                repository.analysis_progress = progress
                repository.save()

                filepath = file_info['path']
                content = file_info['content']

                print(f"  [{index}/{total_files}] Analyzing {filepath}...")

                try:
                    # Analyze this file
                    tasks = self.code_analyzer.analyze_file(
                        content,
                        filepath,
                        repository=repository
                    )

                    # Add to our collection
                    all_tasks.extend(tasks)

                    # Log results
                    if tasks:
                        print(
                            f"    ✓ Found {len(tasks)} vulnerabilities"
                        )
                    else:
                        print("    ✓ No vulnerabilities found")

                except GeminiRateLimitError as e:
                    # Rate limit hit - stop processing and save progress
                    logger.error(
                        f"Rate limit exceeded at file {index}/{total_files}. "
                        f"Stopping analysis. Error: {e}"
                    )
                    print(
                        f"\n⚠ Rate limit exceeded. "
                        f"Analyzed {index-1}/{total_files} files. "
                        f"Please try again later."
                    )
                    repository.status = 'error'
                    repository.analysis_progress = (
                        f"Rate limit exceeded at {index-1}/{total_files} files"
                    )
                    repository.save()
                    # Return tasks created so far
                    return all_tasks

                except GeminiNetworkError as e:
                    # Network error - log and continue with next file
                    logger.warning(
                        f"Network error analyzing {filepath}: {e}. "
                        f"Skipping file and continuing."
                    )
                    print(
                        f"    ⚠ Network error, skipping file: {filepath}"
                    )
                    continue

                except GeminiAPIError as e:
                    print(
                        f"  ⚠️  Skipped {filepath} (API error)"
                    )
                    continue

                except ResponseParsingError as e:
                    print(
                        f"  ⚠️  Skipped {filepath} (parsing error)"
                    )
                    continue

                except Exception as e:
                    # Other errors - log and continue
                    logger.exception(
                        f"Error analyzing file {filepath}: {e}"
                    )
                    print(f"    ✗ Error analyzing file: {e}")
                    continue

            # Update repository status
            repository.status = 'completed'
            repository.last_analyzed_at = timezone.now()
            repository.save()

            print(
                f"✓ Analysis complete: {len(all_tasks)} tasks created"
            )

            return all_tasks
        except Repository.DoesNotExist:
            print(f"Repository with id {repository_id} does not exist.")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            try:
                repository.status = 'error'
                repository.save()
            except Exception:
                pass
            raise


    def analyze_with_checkpoints(
        self,
        repository,
        session,
        checkpoint_interval: int = 5
    ) -> dict:
        """
        Analyze repository with periodic checkpoint saving for crash recovery.

        Args:
            repository: Repository instance to analyze
            session: AnalysisSession for tracking
            checkpoint_interval: Save checkpoint every N files.
        
        Returns:
            dict with analysis results.
        """
        from apps.analysis_session.models import CheckPoint
        from django.utils import timezone
        from apps.tasklog.utils import create_session_log, broadcast_progress_update
        from apps.tasklog.models import LogType

        # Log: Starting analysis
        create_session_log(
            session,
            f"🚀 Starting analysis of {repository.owner}/{repository.repo_name}",
            LogType.INFO
        )

        # Check for existing checkpoint to resume frim
        last_checkpoint = session.checkpoints.first()
        if last_checkpoint:
            print(f"Resuming from checkpoint #{last_checkpoint.checkpoint_number}")
            create_session_log(
                session,
                f"↻ Resuming from checkpoint #{last_checkpoint.checkpoint_number}",
                LogType.INFO
            )
            processed_files = last_checkpoint.files_processed
            start_index = last_checkpoint.last_file_index + 1
            checkpoint_counter = last_checkpoint.checkpoint_number
        else:
            processed_files = []
            start_index = 0
            checkpoint_counter = 0
        
        # Fetch files from Github
        create_session_log(
            session,
            "📥 Fetching repository files from GitHub...",
            LogType.INFO
        )
        
        files = self.github_service.get_repo_files(
            repository.owner,
            repository.repo_name
        )

        # Update session with total files
        session.total_files = len(files)
        session.save()

        create_session_log(
            session,
            f"📊 Found {len(files)} files to analyze",
            LogType.SUCCESS
        )

        print(f"Total files to analyze: {len(files)}")
        if start_index > 0:
            print(f"Resuming from file index {start_index + 1}")
            create_session_log(
                session,
                f"⏩ Skipping {start_index} already processed files",
                LogType.INFO
            )
        
        all_task = []

        # Analyze files starting from checkpoint
        for index, file_info in enumerate(files):
            filepath = file_info['path']
            content = file_info['content']

            # Skip if already processed
            if filepath in processed_files:
                print(f"[{index + 1}/{len(files)}] Skipping {filepath} (already processed)")
                continue

            # Log: Scanning file
            create_session_log(
                session,
                f"→ Scanning {filepath}...",
                LogType.INFO
            )

            print(f"[{index + 1}/{len(files)}] Analyzing {filepath}...")

            try:
                # Analyze this file
                tasks = self.code_analyzer.analyze_file(
                    file_content=content,
                    file_path=filepath,
                    repository=repository
                )

                all_task.extend(tasks)
                processed_files.append(filepath)

                if tasks:
                    print(f"    ✓ Found {len(tasks)} vulnerabilities")
                    # Update vulnerability count in real-time
                    session.vulnerabilities_found = len(all_task)
                    # Log: Found vulnerabilities
                    for task in tasks:
                        create_session_log(
                            session,
                            f"⚠️  Found {task.vulnerability_type} in {filepath}",
                            LogType.WARNING
                        )
                else:
                    print("    ✓ No vulnerabilities found")
                    # Log: File clean
                    create_session_log(
                        session,
                        f"✓ No issues found in {filepath}",
                        LogType.SUCCESS
                    )
                
                # Update session progress
                session.files_analyzed = index + 1
                session.last_checkpoint_at = timezone.now()
                session.save()
                
                # Broadcast progress update
                broadcast_progress_update(session)

                # Create checkpoint every N files
                if (index + 1) % checkpoint_interval == 0:
                    checkpoint_counter += 1
                    CheckPoint.objects.create(
                        session=session,
                        checkpoint_number=checkpoint_counter,
                        last_file_index=index,
                        files_processed=processed_files.copy(),
                        state_data={
                            'task_created': len(all_task),
                            'timestamp': timezone.now().isoformat()
                        }
                    )
                    print(f"  💾 Checkpoint #{checkpoint_counter} saved")
                    create_session_log(
                        session,
                        f"💾 Checkpoint #{checkpoint_counter} saved ({index + 1}/{len(files)} files)",
                        LogType.INFO
                    )
            except Exception as e:
                print(f"  ✗ Error analyzing {filepath}: {e}")
                # Log: Error
                create_session_log(
                    session,
                    f"✗ Error analyzing {filepath}: {str(e)}",
                    LogType.ERROR
                )
                session.files_failed += 1
                session.save()
                continue
        # Update repository status
        repository.status = 'completed'
        repository.last_analyzed_at = timezone.now()
        repository.save()

        # Count actual tasks created in the database
        from apps.task.models import Task

        actual_tasks_count = Task.objects.filter(
            repository=repository,
            created_at__gte=session.started_at
        ).count()

        # Log: Analysis complete
        create_session_log(
            session,
            f"🎉 Analysis complete! Found {actual_tasks_count} vulnerabilities across {len(processed_files)} files",
            LogType.SUCCESS
        )
        
        # Broadcast completion
        from apps.tasklog.utils import broadcast_analysis_complete
        broadcast_analysis_complete(session)

        return {
            'vulnerabilities_found': actual_tasks_count,
            'tasks_created': actual_tasks_count,
            'files_analyzed': len(processed_files),
            'files_failed': session.files_failed
        }


