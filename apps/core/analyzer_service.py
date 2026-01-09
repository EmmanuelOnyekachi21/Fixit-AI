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
    GeminiNetworkError
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




