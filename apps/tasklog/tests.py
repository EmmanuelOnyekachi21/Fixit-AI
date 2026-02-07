from django.test import TestCase
from django.utils import timezone
from apps.repository.models import Repository
from apps.task.models import Task
from apps.tasklog.models import TaskLog


class TaskLogModelTest(TestCase):
    """Test cases for the TaskLog model."""

    def setUp(self):
        """Set up test data before each test method."""
        self.repository = Repository.objects.create(
            owner='testuser',
            repo_name='test-repo',
            repo_url='https://github.com/testuser/test-repo'
        )
        
        self.task = Task.objects.create(
            repository=self.repository,
            title='Fix XSS vulnerability',
            description='Found XSS vulnerability in user input handling',
            vulnerability_type='xss'
        )
        
        self.log_data = {
            'task': self.task,
            'log_type': 'info',
            'action': 'Analyzing vulnerability',
            'message': 'Starting analysis of XSS vulnerability',
        }
        self.log = TaskLog.objects.create(**self.log_data)

    def test_tasklog_creation(self):
        """Test that a task log can be created with valid data."""
        self.assertEqual(self.log.task, self.task)
        self.assertEqual(self.log.log_type, 'info')
        self.assertEqual(self.log.action, 'Analyzing vulnerability')
        self.assertEqual(self.log.message, 'Starting analysis of XSS vulnerability')
        self.assertIsNone(self.log.agent_note)
        self.assertIsNotNone(self.log.timestamp)

    def test_tasklog_str_representation(self):
        """Test the string representation of a task log."""
        expected_start = f"Task {self.task.id} - INFO"
        self.assertIn(expected_start, str(self.log))

    def test_default_level_is_info(self):
        """Test that the default log_type is 'info'."""
        log = TaskLog.objects.create(
            task=self.task,
            action='Test action',
            message='Test message'
        )
        self.assertEqual(log.log_type, 'info')

    def test_all_level_choices(self):
        """Test that all log_type choices can be set."""
        levels = ['info', 'warning', 'error']
        for level in levels:
            self.log.log_type = level
            self.log.save()
            self.log.refresh_from_db()
            self.assertEqual(self.log.log_type, level)

    def test_tasklog_with_agent_note(self):
        """Test that agent_note can be set."""
        agent_note = "Agent attempted fix using pattern matching"
        log = TaskLog.objects.create(
            task=self.task,
            log_type='warning',
            action='Applying fix',
            message='Fix applied but needs validation',
            agent_note=agent_note
        )
        self.assertEqual(log.agent_note, agent_note)

    def test_foreign_key_relationship_with_task(self):
        """Test the foreign key relationship with Task."""
        self.assertEqual(self.log.task.id, self.task.id)
        self.assertIn(self.log, self.task.logs.all())

    def test_cascade_delete_on_task_deletion(self):
        """Test that logs are deleted when task is deleted."""
        log_id = self.log.id
        self.task.delete()
        self.assertFalse(TaskLog.objects.filter(id=log_id).exists())

    def test_timestamp_auto_created(self):
        """Test that timestamp is automatically set."""
        self.assertIsNotNone(self.log.timestamp)
        self.assertLessEqual(
            (timezone.now() - self.log.timestamp).total_seconds(),
            1
        )

    def test_multiple_logs_per_task(self):
        """Test that a task can have multiple logs."""
        log2 = TaskLog.objects.create(
            task=self.task,
            log_type='warning',
            action='Validation failed',
            message='Fix did not pass validation'
        )
        log3 = TaskLog.objects.create(
            task=self.task,
            log_type='error',
            action='Fix failed',
            message='Unable to apply fix'
        )
        self.assertEqual(self.task.logs.count(), 3)
        self.assertIn(self.log, self.task.logs.all())
        self.assertIn(log2, self.task.logs.all())
        self.assertIn(log3, self.task.logs.all())

    def test_logs_ordered_by_timestamp_descending(self):
        """Test that logs are ordered by timestamp in descending order."""
        # Create logs with slight delays to ensure different timestamps
        log1 = TaskLog.objects.create(
            task=self.task,
            action='First action',
            message='First message'
        )
        log2 = TaskLog.objects.create(
            task=self.task,
            action='Second action',
            message='Second message'
        )
        log3 = TaskLog.objects.create(
            task=self.task,
            action='Third action',
            message='Third message'
        )
        
        logs = list(TaskLog.objects.filter(task=self.task))
        # Most recent should be first
        self.assertEqual(logs[0].action, 'Third action')
        self.assertGreaterEqual(logs[0].timestamp, logs[1].timestamp)
        self.assertGreaterEqual(logs[1].timestamp, logs[2].timestamp)

    def test_str_representation_with_different_levels(self):
        """Test string representation with different log levels."""
        warning_log = TaskLog.objects.create(
            task=self.task,
            log_type='warning',
            action='Warning action',
            message='Warning message'
        )
        error_log = TaskLog.objects.create(
            task=self.task,
            log_type='error',
            action='Error action',
            message='Error message'
        )
        
        self.assertIn('WARNING', str(warning_log))
        self.assertIn('ERROR', str(error_log))
        self.assertIn('INFO', str(self.log))

    def test_cascade_delete_from_repository(self):
        """Test that logs are deleted when repository is deleted (cascade through task)."""
        log_id = self.log.id
        self.repository.delete()
        self.assertFalse(TaskLog.objects.filter(id=log_id).exists())
