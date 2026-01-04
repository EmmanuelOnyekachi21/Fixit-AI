"""Tests for CodeAnalyzer service."""
from unittest.mock import Mock, patch

from django.test import TestCase

from apps.gemini_analyzer.services.code_analyzer import CodeAnalyzer
from apps.repository.models import Repository
from apps.task.models import Task


class TestCodeAnalyzerInit(TestCase):
    """Test CodeAnalyzer initialization."""

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_init_creates_dependencies(self, mock_client_class, mock_parser_class):
        """Test that CodeAnalyzer initializes with GeminiClient and ResponseParser."""
        analyzer = CodeAnalyzer()
        
        mock_client_class.assert_called_once()
        mock_parser_class.assert_called_once()
        self.assertIsNotNone(analyzer.gemini_client)
        self.assertIsNotNone(analyzer.parser)


class TestCodeAnalyzerAnalyzeFile(TestCase):
    """Test CodeAnalyzer.analyze_file method."""

    def setUp(self):
        """Set up test data."""
        self.repository = Repository.objects.create(
            owner='test-owner',
            repo_name='test-repo',
            repo_url='https://github.com/test-owner/test-repo'
        )

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_analyze_file_success(self, mock_client_class, mock_parser_class):
        """Test successful file analysis."""
        # Setup mocks
        mock_client = Mock()
        mock_parser = Mock()
        mock_client_class.return_value = mock_client
        mock_parser_class.return_value = mock_parser
        
        # Configure mock returns
        raw_vulns = [{'type': 'xss', 'title': 'XSS'}]
        validated_vulns = [{'type': 'xss', 'title': 'XSS', 'file_path': 'test.py'}]
        mock_tasks = [Mock(spec=Task)]
        
        mock_client.analyze_code.return_value = raw_vulns
        mock_parser.parse_vulnerabilities.return_value = validated_vulns
        mock_parser.create_and_save_tasks.return_value = mock_tasks
        
        # Test
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file(
            "def test(): pass",
            "test.py",
            self.repository
        )
        
        # Assertions
        self.assertEqual(result, mock_tasks)
        
        # Verify method calls
        mock_client.analyze_code.assert_called_once_with(
            "def test(): pass",
            "test.py"
        )
        mock_parser.parse_vulnerabilities.assert_called_once_with(
            raw_vulns,
            "test.py"
        )
        mock_parser.create_and_save_tasks.assert_called_once_with(
            validated_vulns,
            self.repository
        )

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_analyze_file_no_vulnerabilities(self, mock_client_class, mock_parser_class):
        """Test file analysis when no vulnerabilities are found."""
        mock_client = Mock()
        mock_parser = Mock()
        mock_client_class.return_value = mock_client
        mock_parser_class.return_value = mock_parser
        
        # Gemini returns empty list
        mock_client.analyze_code.return_value = []
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file(
            "def safe_code(): pass",
            "safe.py",
            self.repository
        )
        
        # Should return empty list
        self.assertEqual(result, [])
        
        # Parser methods should not be called
        mock_parser.parse_vulnerabilities.assert_not_called()
        mock_parser.create_and_save_tasks.assert_not_called()

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_analyze_file_empty_after_parsing(self, mock_client_class, mock_parser_class):
        """Test when vulnerabilities are filtered out during parsing."""
        mock_client = Mock()
        mock_parser = Mock()
        mock_client_class.return_value = mock_client
        mock_parser_class.return_value = mock_parser
        
        # Gemini returns data but parser filters it all out
        mock_client.analyze_code.return_value = [{'type': 'unknown'}]
        mock_parser.parse_vulnerabilities.return_value = []
        mock_parser.create_and_save_tasks.return_value = []
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file(
            "def test(): pass",
            "test.py",
            self.repository
        )
        
        self.assertEqual(result, [])


class TestCodeAnalyzerAnalyzeRepository(TestCase):
    """Test CodeAnalyzer.analyze_repository method."""

    def setUp(self):
        """Set up test data."""
        self.repository = Repository.objects.create(
            owner='test-owner',
            repo_name='test-repo',
            repo_url='https://github.com/test-owner/test-repo'
        )

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_analyze_repository_multiple_files(self, mock_client_class, mock_parser_class):
        """Test analyzing multiple files in a repository."""
        mock_client = Mock()
        mock_parser = Mock()
        mock_client_class.return_value = mock_client
        mock_parser_class.return_value = mock_parser
        
        # Setup mock returns
        mock_client.analyze_code.return_value = [{'type': 'xss'}]
        mock_parser.parse_vulnerabilities.return_value = [{'type': 'xss'}]
        
        # Create different tasks for each file
        task1 = Mock(spec=Task)
        task2 = Mock(spec=Task)
        mock_parser.create_and_save_tasks.side_effect = [[task1], [task2]]
        
        files_to_analyze = [
            {'path': 'file1.py', 'content': 'code1'},
            {'path': 'file2.py', 'content': 'code2'}
        ]
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_repository(self.repository, files_to_analyze)
        
        # Should return all tasks
        self.assertEqual(len(result), 2)
        self.assertIn(task1, result)
        self.assertIn(task2, result)
        
        # Verify analyze_code was called for each file
        self.assertEqual(mock_client.analyze_code.call_count, 2)

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_analyze_repository_missing_path(self, mock_client_class, mock_parser_class):
        """Test handling of files with missing path."""
        mock_client = Mock()
        mock_parser = Mock()
        mock_client_class.return_value = mock_client
        mock_parser_class.return_value = mock_parser
        
        files_to_analyze = [
            {'path': 'valid.py', 'content': 'code'},
            {'content': 'code without path'},  # Missing path
            {'path': 'another.py', 'content': 'more code'}
        ]
        
        mock_client.analyze_code.return_value = []
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_repository(self.repository, files_to_analyze)
        
        # Should only analyze files with both path and content
        self.assertEqual(mock_client.analyze_code.call_count, 2)

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_analyze_repository_missing_content(self, mock_client_class, mock_parser_class):
        """Test handling of files with missing content."""
        mock_client = Mock()
        mock_parser = Mock()
        mock_client_class.return_value = mock_client
        mock_parser_class.return_value = mock_parser
        
        files_to_analyze = [
            {'path': 'valid.py', 'content': 'code'},
            {'path': 'no_content.py'},  # Missing content
        ]
        
        mock_client.analyze_code.return_value = []
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_repository(self.repository, files_to_analyze)
        
        # Should only analyze the valid file
        self.assertEqual(mock_client.analyze_code.call_count, 1)

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_analyze_repository_error_handling(self, mock_client_class, mock_parser_class):
        """Test that errors in one file don't stop analysis of others."""
        mock_client = Mock()
        mock_parser = Mock()
        mock_client_class.return_value = mock_client
        mock_parser_class.return_value = mock_parser
        
        # First file raises exception, second succeeds
        task2 = Mock(spec=Task)
        mock_client.analyze_code.side_effect = [
            Exception("API Error"),
            [{'type': 'xss'}]
        ]
        mock_parser.parse_vulnerabilities.return_value = [{'type': 'xss'}]
        mock_parser.create_and_save_tasks.return_value = [task2]
        
        files_to_analyze = [
            {'path': 'error.py', 'content': 'code1'},
            {'path': 'success.py', 'content': 'code2'}
        ]
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_repository(self.repository, files_to_analyze)
        
        # Should continue and return task from second file
        self.assertEqual(len(result), 1)
        self.assertIn(task2, result)

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_analyze_repository_empty_list(self, mock_client_class, mock_parser_class):
        """Test analyzing empty file list."""
        mock_client = Mock()
        mock_parser = Mock()
        mock_client_class.return_value = mock_client
        mock_parser_class.return_value = mock_parser
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_repository(self.repository, [])
        
        self.assertEqual(result, [])
        mock_client.analyze_code.assert_not_called()

    @patch('apps.gemini_analyzer.services.code_analyzer.ResponseParser')
    @patch('apps.gemini_analyzer.services.code_analyzer.GeminiClient')
    def test_analyze_repository_mixed_results(self, mock_client_class, mock_parser_class):
        """Test repository analysis with mixed results (some files have vulns, some don't)."""
        mock_client = Mock()
        mock_parser = Mock()
        mock_client_class.return_value = mock_client
        mock_parser_class.return_value = mock_parser
        
        task1 = Mock(spec=Task)
        
        # First file has vulnerabilities, second doesn't
        mock_client.analyze_code.side_effect = [
            [{'type': 'xss'}],
            []
        ]
        mock_parser.parse_vulnerabilities.return_value = [{'type': 'xss'}]
        mock_parser.create_and_save_tasks.return_value = [task1]
        
        files_to_analyze = [
            {'path': 'vuln.py', 'content': 'vulnerable code'},
            {'path': 'safe.py', 'content': 'safe code'}
        ]
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_repository(self.repository, files_to_analyze)
        
        # Should only return task from first file
        self.assertEqual(len(result), 1)
        self.assertIn(task1, result)
