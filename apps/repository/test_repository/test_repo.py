"""
Repository model unit tests.

This module contains comprehensive test cases for the Repository model,
including creation, validation, constraints, and field behavior.
"""
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from apps.repository.models import Repository


class RepositoryModelTest(TestCase):
    """Test cases for the Repository model."""

    def setUp(self):
        """Set up test data before each test method."""
        self.repo_data = {
            'owner': 'testuser',
            'repo_name': 'test-repo',
            'repo_url': 'https://github.com/testuser/test-repo',
        }
        self.repo = Repository.objects.create(**self.repo_data)

    def test_repository_creation(self):
        """Test that a repository can be created with valid data."""
        self.assertEqual(self.repo.owner, 'testuser')
        self.assertEqual(self.repo.repo_name, 'test-repo')
        self.assertEqual(
            self.repo.repo_url,
            'https://github.com/testuser/test-repo'
        )
        self.assertEqual(self.repo.status, 'idle')  # Default status
        self.assertIsNone(self.repo.last_analyzed_at)
        self.assertIsNone(self.repo.analysis_progress)

    def test_repository_str_representation(self):
        """Test the string representation of a repository."""
        self.assertEqual(str(self.repo), 'testuser/test-repo')

    def test_default_status_is_idle(self):
        """Test that the default status is 'idle'."""
        repo = Repository.objects.create(
            owner='anotheruser',
            repo_name='another-repo',
            repo_url='https://github.com/anotheruser/another-repo'
        )
        self.assertEqual(repo.status, 'idle')

    def test_status_choices(self):
        """Test that all status choices can be set."""
        statuses = ['idle', 'analyzing', 'completed', 'error', 'paused']
        for status in statuses:
            self.repo.status = status
            self.repo.save()
            self.repo.refresh_from_db()
            self.assertEqual(self.repo.status, status)

    def test_unique_repo_url(self):
        """Test that repo_url must be unique."""
        with self.assertRaises(IntegrityError):
            Repository.objects.create(
                owner='differentuser',
                repo_name='different-repo',
                # Duplicate URL
                repo_url='https://github.com/testuser/test-repo'
            )

    def test_unique_together_owner_and_repo_name(self):
        """Test that owner and repo_name combination must be unique."""
        with self.assertRaises(IntegrityError):
            Repository.objects.create(
                owner='testuser',
                repo_name='test-repo',
                repo_url='https://github.com/testuser/test-repo-different'
            )

    def test_timestamps_auto_created(self):
        """Test that created_at and updated_at are automatically set."""
        self.assertIsNotNone(self.repo.created_at)
        self.assertIsNotNone(self.repo.updated_at)

    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when the model is saved."""
        original_updated_at = self.repo.updated_at
        self.repo.status = 'analyzing'
        self.repo.save()
        self.repo.refresh_from_db()
        self.assertGreater(self.repo.updated_at, original_updated_at)

    def test_last_analyzed_at_can_be_set(self):
        """Test that last_analyzed_at can be set to a datetime."""
        now = timezone.now()
        self.repo.last_analyzed_at = now
        self.repo.save()
        self.repo.refresh_from_db()
        self.assertEqual(self.repo.last_analyzed_at, now)

    def test_analysis_progress_can_be_set(self):
        """Test that analysis_progress can be set."""
        progress = "Analyzing 5/10 files"
        self.repo.analysis_progress = progress
        self.repo.save()
        self.repo.refresh_from_db()
        self.assertEqual(self.repo.analysis_progress, progress)
