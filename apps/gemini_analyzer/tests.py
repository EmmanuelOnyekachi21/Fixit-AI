"""
Tests for Gemini Analyzer.
"""
from django.test import TestCase

from apps.gemini_analyzer.services import (
    CodeAnalyzer,
    GeminiClient,
    ResponseParser
)
from apps.repository.models import Repository
from apps.task.models import Task


class GeminiClientTests(TestCase):
    """Test GeminiClient functionality."""
    
    def setUp(self):
        self.client = GeminiClient()
    
    def test_parse_response_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        response_text = """```json
[
  {
    "type": "xss",
    "title": "XSS vulnerability",
    "description": "User input not escaped",
    "line_number": 42,
    "severity": "high"
  }
]
```"""
        
        result = self.client._parse_response(response_text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'xss')
        self.assertEqual(result[0]['line_number'], 42)
    
    def test_parse_response_plain_json(self):
        """Test parsing plain JSON without markdown."""
        response_text = (
            '[{"type": "sql_injection", "title": "SQL Injection", '
            '"description": "Test", "line_number": 10, '
            '"severity": "critical"}]'
        )

        result = self.client._parse_response(response_text)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'sql_injection')
    
    def test_parse_response_empty(self):
        """Test parsing empty response."""
        result = self.client._parse_response('[]')
        self.assertEqual(result, [])


class ResponseParserTests(TestCase):
    """Test ResponseParser functionality."""
    
    def setUp(self):
        self.parser = ResponseParser()
        self.repository = Repository.objects.create(
            owner='testuser',
            repo_name='testrepo',
            repo_url='https://github.com/testuser/testrepo'
        )
    
    def test_parse_vulnerabilities(self):
        """Test vulnerability parsing and validation."""
        gemini_response = [
            {
                'type': 'xss',
                'title': 'XSS in template',
                'description': 'User input not escaped',
                'line_number': 42,
                'severity': 'high'
            }
        ]
        
        result = self.parser.parse_vulnerabilities(
            gemini_response,
            'app/views.py'
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'xss')
        self.assertEqual(result[0]['file_path'], 'app/views.py')
    
    def test_create_tasks(self):
        """Test task creation from vulnerabilities."""
        vulnerabilities = [
            {
                'type': 'sql_injection',
                'title': 'SQL Injection',
                'description': 'Unsafe query',
                'file_path': 'app/models.py',
                'line_number': 10,
                'severity': 'critical'
            }
        ]
        
        tasks = self.parser.create_tasks(vulnerabilities, self.repository)
        
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].vulnerability_type, 'sql_injection')
        self.assertEqual(tasks[0].repository, self.repository)
        self.assertEqual(tasks[0].status, 'pending')


class CodeAnalyzerTests(TestCase):
    """Test CodeAnalyzer orchestration."""
    
    def setUp(self):
        self.repository = Repository.objects.create(
            owner='testuser',
            repo_name='testrepo',
            repo_url='https://github.com/testuser/testrepo'
        )
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = CodeAnalyzer()
        
        self.assertIsNotNone(analyzer.gemini_client)
        self.assertIsNotNone(analyzer.parser)
