"""Tests for ResponseParser service."""
from unittest.mock import Mock, patch

from django.test import TestCase

from apps.gemini_analyzer.services.response_parser import ResponseParser
from apps.repository.models import Repository
from apps.task.models import Task


class TestResponseParserParseVulnerabilities(TestCase):
    """Test ResponseParser.parse_vulnerabilities method."""

    def setUp(self):
        """Set up test parser."""
        self.parser = ResponseParser()

    def test_parse_valid_vulnerabilities(self):
        """Test parsing valid vulnerability data."""
        gemini_response = [
            {
                'type': 'xss',
                'title': 'Cross-site scripting',
                'description': 'User input not sanitized',
                'line_number': 42,
                'severity': 'high'
            },
            {
                'type': 'sql_injection',
                'title': 'SQL Injection',
                'description': 'Direct query concatenation',
                'line_number': 15,
                'severity': 'critical'
            }
        ]
        
        result = self.parser.parse_vulnerabilities(gemini_response, 'app.py')
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'xss')
        self.assertEqual(result[0]['file_path'], 'app.py')
        self.assertEqual(result[0]['line_number'], 42)
        self.assertEqual(result[1]['type'], 'sql_injection')

    def test_parse_unknown_vulnerability_type(self):
        """Test that unknown vulnerability types are skipped."""
        gemini_response = [
            {
                'type': 'unknown_vuln',
                'title': 'Unknown',
                'description': 'Test',
                'line_number': 1,
                'severity': 'low'
            },
            {
                'type': 'xss',
                'title': 'Valid XSS',
                'description': 'Test',
                'line_number': 2,
                'severity': 'medium'
            }
        ]
        
        result = self.parser.parse_vulnerabilities(gemini_response, 'test.py')
        
        # Only the valid one should be included
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'xss')

    def test_parse_case_insensitive_type(self):
        """Test that vulnerability types are case-insensitive."""
        gemini_response = [
            {'type': 'XSS', 'title': 'Test', 'description': 'Test'},
            {'type': 'SQL_INJECTION', 'title': 'Test', 'description': 'Test'},
            {'type': 'Csrf', 'title': 'Test', 'description': 'Test'}
        ]
        
        result = self.parser.parse_vulnerabilities(gemini_response, 'test.py')
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['type'], 'xss')
        self.assertEqual(result[1]['type'], 'sql_injection')
        self.assertEqual(result[2]['type'], 'csrf')

    def test_parse_missing_optional_fields(self):
        """Test parsing with missing optional fields uses defaults."""
        gemini_response = [
            {
                'type': 'xss',
                # Missing title, description, line_number, severity
            }
        ]
        
        result = self.parser.parse_vulnerabilities(gemini_response, 'test.py')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Unknown vulnerability')
        self.assertEqual(result[0]['description'], 'No description provided')
        self.assertIsNone(result[0]['line_number'])
        self.assertEqual(result[0]['severity'], 'medium')

    def test_parse_title_truncation(self):
        """Test that titles longer than 255 chars are truncated."""
        long_title = 'A' * 300
        gemini_response = [
            {
                'type': 'xss',
                'title': long_title,
                'description': 'Test'
            }
        ]
        
        result = self.parser.parse_vulnerabilities(gemini_response, 'test.py')
        
        self.assertEqual(len(result[0]['title']), 255)

    def test_parse_empty_list(self):
        """Test parsing empty vulnerability list."""
        result = self.parser.parse_vulnerabilities([], 'test.py')
        
        self.assertEqual(result, [])

    def test_parse_with_exception_in_item(self):
        """Test that exceptions in individual items are handled gracefully."""
        gemini_response = [
            {
                'type': 'xss',
                'title': 'Valid',
                'description': 'Valid'
            },
            None,  # This will cause an exception
            {
                'type': 'csrf',
                'title': 'Also valid',
                'description': 'Valid'
            }
        ]
        
        result = self.parser.parse_vulnerabilities(gemini_response, 'test.py')
        
        # Should skip the problematic item but process others
        self.assertEqual(len(result), 2)

    def test_parse_all_vulnerability_types(self):
        """Test that all mapped vulnerability types work."""
        types = [
            'xss', 'sql_injection', 'csrf', 'hardcoded_secret',
            'command_injection', 'path_traversal', 'insecure_deserialization'
        ]
        
        gemini_response = [
            {'type': vtype, 'title': f'Test {vtype}', 'description': 'Test'}
            for vtype in types
        ]
        
        result = self.parser.parse_vulnerabilities(gemini_response, 'test.py')
        
        self.assertEqual(len(result), len(types))
        for i, vtype in enumerate(types):
            self.assertEqual(result[i]['type'], vtype)


class TestResponseParserCreateTasks(TestCase):
    """Test ResponseParser.create_tasks method."""

    def setUp(self):
        """Set up test data."""
        self.parser = ResponseParser()
        self.repository = Repository.objects.create(
            owner='test-owner',
            repo_name='test-repo',
            repo_url='https://github.com/test-owner/test-repo'
        )

    def test_create_tasks_from_vulnerabilities(self):
        """Test creating Task objects from vulnerabilities."""
        vulnerabilities = [
            {
                'type': 'xss',
                'title': 'XSS vulnerability',
                'description': 'User input not escaped',
                'file_path': 'app.py',
                'line_number': 42,
                'severity': 'high'
            },
            {
                'type': 'sql_injection',
                'title': 'SQL Injection',
                'description': 'Direct concatenation',
                'file_path': 'db.py',
                'line_number': 15,
                'severity': 'critical'
            }
        ]
        
        tasks = self.parser.create_tasks(vulnerabilities, self.repository)
        
        self.assertEqual(len(tasks), 2)
        
        # Check first task
        self.assertIsInstance(tasks[0], Task)
        self.assertEqual(tasks[0].repository, self.repository)
        self.assertEqual(tasks[0].title, 'XSS vulnerability')
        self.assertEqual(tasks[0].vulnerability_type, 'xss')
        self.assertEqual(tasks[0].file_path, 'app.py')
        self.assertEqual(tasks[0].line_number, 42)
        self.assertEqual(tasks[0].status, 'pending')
        
        # Check second task
        self.assertEqual(tasks[1].title, 'SQL Injection')
        self.assertEqual(tasks[1].vulnerability_type, 'sql_injection')

    def test_create_tasks_empty_list(self):
        """Test creating tasks from empty vulnerability list."""
        tasks = self.parser.create_tasks([], self.repository)
        
        self.assertEqual(tasks, [])

    def test_create_tasks_not_saved(self):
        """Test that create_tasks does not save to database."""
        vulnerabilities = [
            {
                'type': 'xss',
                'title': 'Test',
                'description': 'Test',
                'file_path': 'test.py',
                'line_number': 1,
                'severity': 'low'
            }
        ]
        
        initial_count = Task.objects.count()
        tasks = self.parser.create_tasks(vulnerabilities, self.repository)
        final_count = Task.objects.count()
        
        # Count should not change
        self.assertEqual(initial_count, final_count)
        # But we should have task objects
        self.assertEqual(len(tasks), 1)


class TestResponseParserCreateAndSaveTasks(TestCase):
    """Test ResponseParser.create_and_save_tasks method."""

    def setUp(self):
        """Set up test data."""
        self.parser = ResponseParser()
        self.repository = Repository.objects.create(
            owner='test-owner',
            repo_name='test-repo',
            repo_url='https://github.com/test-owner/test-repo'
        )

    def test_create_and_save_tasks(self):
        """Test creating and saving tasks to database."""
        vulnerabilities = [
            {
                'type': 'xss',
                'title': 'XSS vulnerability',
                'description': 'User input not escaped',
                'file_path': 'app.py',
                'line_number': 42,
                'severity': 'high'
            },
            {
                'type': 'csrf',
                'title': 'CSRF missing',
                'description': 'No CSRF token',
                'file_path': 'forms.py',
                'line_number': 10,
                'severity': 'medium'
            }
        ]
        
        initial_count = Task.objects.count()
        tasks = self.parser.create_and_save_tasks(vulnerabilities, self.repository)
        final_count = Task.objects.count()
        
        # Tasks should be saved
        self.assertEqual(final_count, initial_count + 2)
        self.assertEqual(len(tasks), 2)
        
        # Verify tasks are in database
        saved_task = Task.objects.get(title='XSS vulnerability')
        self.assertEqual(saved_task.vulnerability_type, 'xss')
        self.assertEqual(saved_task.repository, self.repository)

    def test_create_and_save_empty_list(self):
        """Test with empty vulnerability list."""
        initial_count = Task.objects.count()
        tasks = self.parser.create_and_save_tasks([], self.repository)
        final_count = Task.objects.count()
        
        self.assertEqual(tasks, [])
        self.assertEqual(initial_count, final_count)

    @patch.object(ResponseParser, 'create_tasks')
    def test_uses_bulk_create(self, mock_create_tasks):
        """Test that bulk_create is used for efficiency."""
        mock_tasks = [Mock(spec=Task), Mock(spec=Task)]
        mock_create_tasks.return_value = mock_tasks
        
        vulnerabilities = [
            {'type': 'xss', 'title': 'Test', 'description': 'Test',
             'file_path': 'test.py', 'line_number': 1, 'severity': 'low'}
        ]
        
        with patch.object(Task.objects, 'bulk_create') as mock_bulk:
            self.parser.create_and_save_tasks(vulnerabilities, self.repository)
            mock_bulk.assert_called_once_with(mock_tasks)


class TestResponseParserVulnerabilityTypeMap(TestCase):
    """Test ResponseParser vulnerability type mapping."""

    def setUp(self):
        """Set up test parser."""
        self.parser = ResponseParser()

    def test_vulnerability_type_map_exists(self):
        """Test that vulnerability type map is defined."""
        self.assertIsNotNone(self.parser.VULNERABILITY_TYPE_MAP)
        self.assertIsInstance(self.parser.VULNERABILITY_TYPE_MAP, dict)

    def test_all_expected_types_mapped(self):
        """Test that all expected vulnerability types are in the map."""
        expected_types = [
            'xss', 'sql_injection', 'csrf', 'hardcoded_secret',
            'command_injection', 'path_traversal', 'insecure_deserialization'
        ]
        
        for vtype in expected_types:
            self.assertIn(vtype, self.parser.VULNERABILITY_TYPE_MAP)
