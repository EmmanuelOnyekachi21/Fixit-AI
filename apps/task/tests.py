from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from apps.repository.models import Repository
from apps.task.models import Task


class TaskModelTest(TestCase):
    """Test cases for the Task model."""

    def setUp(self):
        """Set up test data before each test method."""
        self.repository = Repository.objects.create(
            owner='testuser',
            repo_name='test-repo',
            repo_url='https://github.com/testuser/test-repo'
        )
        
        self.task_data = {
            'repository': self.repository,
            'title': 'Fix XSS vulnerability',
            'description': 'Found XSS vulnerability in user input handling',
            'vulnerability_type': 'xss',
            'file_path': 'src/views.py',
            'line_number': 42,
        }
        self.task = Task.objects.create(**self.task_data)

    def test_task_creation(self):
        """Test that a task can be created with valid data."""
        self.assertEqual(self.task.repository, self.repository)
        self.assertEqual(self.task.title, 'Fix XSS vulnerability')
        self.assertEqual(self.task.description, 'Found XSS vulnerability in user input handling')
        self.assertEqual(self.task.vulnerability_type, 'xss')
        self.assertEqual(self.task.file_path, 'src/views.py')
        self.assertEqual(self.task.line_number, 42)
        self.assertEqual(self.task.status, 'pending')  # Default status
        self.assertEqual(self.task.retry_count, 0)  # Default retry count
        self.assertIsNone(self.task.applied_fix)
        self.assertIsNone(self.task.started_at)
        self.assertIsNone(self.task.completed_at)

    def test_task_str_representation(self):
        """Test the string representation of a task."""
        self.assertEqual(str(self.task), '[PENDING] Fix XSS vulnerability')
        
        self.task.status = 'completed'
        self.assertEqual(str(self.task), '[COMPLETED] Fix XSS vulnerability')

    def test_default_status_is_pending(self):
        """Test that the default status is 'pending'."""
        task = Task.objects.create(
            repository=self.repository,
            title='Another task',
            description='Test description',
            vulnerability_type='sql_injection'
        )
        self.assertEqual(task.status, 'pending')

    def test_default_retry_count_is_zero(self):
        """Test that the default retry_count is 0."""
        task = Task.objects.create(
            repository=self.repository,
            title='Another task',
            description='Test description',
            vulnerability_type='csrf'
        )
        self.assertEqual(task.retry_count, 0)

    def test_all_status_choices(self):
        """Test that all status choices can be set."""
        statuses = ['pending', 'running', 'validating', 'completed', 'failed', 'abandoned', 'false_positive']
        for status in statuses:
            self.task.status = status
            self.task.save()
            self.task.refresh_from_db()
            self.assertEqual(self.task.status, status)

    def test_all_vulnerability_types(self):
        """Test that all vulnerability types can be set."""
        vuln_types = [
            'xss', 'sql_injection', 'csrf', 'hardcoded_secret',
            'command_injection', 'path_traversal', 'authentication_bypass',
            'insecure_deserialization'
        ]
        for vuln_type in vuln_types:
            self.task.vulnerability_type = vuln_type
            self.task.save()
            self.task.refresh_from_db()
            self.assertEqual(self.task.vulnerability_type, vuln_type)

    def test_task_without_file_path_and_line_number(self):
        """Test that file_path and line_number are optional."""
        task = Task.objects.create(
            repository=self.repository,
            title='General security issue',
            description='Repository-wide security concern',
            vulnerability_type='authentication_bypass'
        )
        self.assertIsNone(task.file_path)
        self.assertIsNone(task.line_number)

    def test_foreign_key_relationship_with_repository(self):
        """Test the foreign key relationship with Repository."""
        self.assertEqual(self.task.repository.id, self.repository.id)
        self.assertIn(self.task, self.repository.tasks.all())

    def test_cascade_delete_on_repository_deletion(self):
        """Test that tasks are deleted when repository is deleted."""
        task_id = self.task.id
        self.repository.delete()
        self.assertFalse(Task.objects.filter(id=task_id).exists())

    def test_timestamps_auto_created(self):
        """Test that created_at is automatically set."""
        self.assertIsNotNone(self.task.created_at)

    def test_started_at_can_be_set(self):
        """Test that started_at can be set to a datetime."""
        now = timezone.now()
        self.task.started_at = now
        self.task.save()
        self.task.refresh_from_db()
        self.assertEqual(self.task.started_at, now)

    def test_completed_at_can_be_set(self):
        """Test that completed_at can be set to a datetime."""
        now = timezone.now()
        self.task.completed_at = now
        self.task.save()
        self.task.refresh_from_db()
        self.assertEqual(self.task.completed_at, now)

    def test_applied_fix_can_be_set(self):
        """Test that applied_fix can be set."""
        fix = "Sanitized user input using escape() function"
        self.task.applied_fix = fix
        self.task.save()
        self.task.refresh_from_db()
        self.assertEqual(self.task.applied_fix, fix)

    def test_retry_count_increment(self):
        """Test that retry_count can be incremented."""
        self.assertEqual(self.task.retry_count, 0)
        self.task.retry_count += 1
        self.task.save()
        self.task.refresh_from_db()
        self.assertEqual(self.task.retry_count, 1)

    def test_multiple_tasks_per_repository(self):
        """Test that a repository can have multiple tasks."""
        task2 = Task.objects.create(
            repository=self.repository,
            title='Fix SQL Injection',
            description='SQL injection in query',
            vulnerability_type='sql_injection'
        )
        self.assertEqual(self.repository.tasks.count(), 2)
        self.assertIn(self.task, self.repository.tasks.all())
        self.assertIn(task2, self.repository.tasks.all())
