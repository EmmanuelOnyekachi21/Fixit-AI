"""Tests for GeminiClient service."""
import json
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from apps.gemini_analyzer.services.gemini_client import GeminiClient
from apps.gemini_analyzer.tests.fixtures.sample_responses import (
    EMPTY_RESPONSE,
    INVALID_JSON_RESPONSE,
    MARKDOWN_NO_JSON_MARKER,
    MARKDOWN_WRAPPED_RESPONSE,
    NON_LIST_RESPONSE,
    VALID_GEMINI_RESPONSE,
)


class TestGeminiClientInit(SimpleTestCase):
    """Test GeminiClient initialization."""

    @patch('apps.gemini_analyzer.services.gemini_client.genai.Client')
    def test_init_with_valid_api_key(self, mock_client_class):
        """Test initialization with valid API key."""
        client = GeminiClient()
        
        self.assertIsNotNone(client.client)
        self.assertEqual(client.model_name, "gemini-3-flash-preview")
        self.assertIsNone(client.last_prompt)
        self.assertIsNone(client.last_response)
        self.assertIsNone(client.last_vulnerabilities)
        
        # Verify genai.Client was called with API key
        mock_client_class.assert_called_once()

    @override_settings(GEMINI_API_KEY=None)
    @patch('apps.gemini_analyzer.services.gemini_client.genai.Client')
    def test_init_without_api_key(self, mock_client_class):
        """Test initialization fails without API key."""
        with self.assertRaises(ValueError) as context:
            GeminiClient()
        
        self.assertIn("GEMINI_API_KEY not found", str(context.exception))


class TestGeminiClientAnalyzeCode(SimpleTestCase):
    """Test GeminiClient.analyze_code method."""

    @patch('apps.gemini_analyzer.services.gemini_client.genai.Client')
    def test_analyze_code_success(self, mock_client_class):
        """Test successful code analysis."""
        # Setup mock
        mock_instance = Mock()
        mock_client_class.return_value = mock_instance
        
        mock_response = Mock()
        mock_response.text = json.dumps(VALID_GEMINI_RESPONSE)
        mock_instance.models.generate_content.return_value = mock_response
        
        # Test
        client = GeminiClient()
        result = client.analyze_code("def test(): pass", "test.py")
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'sql_injection')
        self.assertEqual(result[1]['type'], 'xss')
        
        # Verify API was called
        mock_instance.models.generate_content.assert_called_once()
        call_args = mock_instance.models.generate_content.call_args
        self.assertEqual(call_args.kwargs['model'], "gemini-3-flash-preview")
        
        # Verify debug storage
        self.assertIsNotNone(client.last_prompt)
        self.assertIsNotNone(client.last_response)
        self.assertEqual(client.last_vulnerabilities, result)

    @patch('apps.gemini_analyzer.services.gemini_client.genai.Client')
    def test_analyze_code_api_error(self, mock_client_class):
        """Test handling of API errors."""
        # Setup mock to raise exception
        mock_instance = Mock()
        mock_client_class.return_value = mock_instance
        mock_instance.models.generate_content.side_effect = Exception("API Error")
        
        # Test
        client = GeminiClient()
        result = client.analyze_code("def test(): pass", "test.py")
        
        # Should return empty list on error
        self.assertEqual(result, [])

    @patch('apps.gemini_analyzer.services.gemini_client.genai.Client')
    def test_analyze_code_empty_response(self, mock_client_class):
        """Test handling of empty API response."""
        mock_instance = Mock()
        mock_client_class.return_value = mock_instance
        
        mock_response = Mock()
        mock_response.text = EMPTY_RESPONSE
        mock_instance.models.generate_content.return_value = mock_response
        
        client = GeminiClient()
        result = client.analyze_code("def test(): pass", "test.py")
        
        self.assertEqual(result, [])


class TestGeminiClientParseResponse(SimpleTestCase):
    """Test GeminiClient._parse_response method."""

    @patch('apps.gemini_analyzer.services.gemini_client.genai.Client')
    def setUp(self, mock_client_class):
        """Set up test client."""
        self.client = GeminiClient()

    def test_parse_clean_json(self):
        """Test parsing clean JSON response."""
        response_text = json.dumps(VALID_GEMINI_RESPONSE)
        result = self.client._parse_response(response_text)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'sql_injection')

    def test_parse_markdown_wrapped_json(self):
        """Test parsing JSON wrapped in markdown code block."""
        result = self.client._parse_response(MARKDOWN_WRAPPED_RESPONSE)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'xss')

    def test_parse_markdown_no_json_marker(self):
        """Test parsing markdown without 'json' marker."""
        result = self.client._parse_response(MARKDOWN_NO_JSON_MARKER)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'csrf')

    def test_parse_invalid_json(self):
        """Test handling of invalid JSON."""
        result = self.client._parse_response(INVALID_JSON_RESPONSE)
        
        self.assertEqual(result, [])

    def test_parse_empty_response(self):
        """Test handling of empty response."""
        result = self.client._parse_response(EMPTY_RESPONSE)
        
        self.assertEqual(result, [])

    def test_parse_none_response(self):
        """Test handling of None response."""
        result = self.client._parse_response(None)
        
        self.assertEqual(result, [])

    def test_parse_non_list_response(self):
        """Test handling of non-list JSON response."""
        result = self.client._parse_response(NON_LIST_RESPONSE)
        
        self.assertEqual(result, [])

    def test_parse_whitespace_response(self):
        """Test handling of whitespace-only response."""
        result = self.client._parse_response("   \n\t  ")
        
        self.assertEqual(result, [])


class TestGeminiClientBuildPrompt(SimpleTestCase):
    """Test GeminiClient._build_prompt method."""

    @patch('apps.gemini_analyzer.services.gemini_client.genai.Client')
    @patch('apps.gemini_analyzer.services.gemini_client.build_security_prompt')
    def test_build_prompt_calls_template(self, mock_build_prompt, mock_client_class):
        """Test that _build_prompt calls the prompt template function."""
        mock_build_prompt.return_value = "Test prompt"
        
        client = GeminiClient()
        result = client._build_prompt("code content", "test.py")
        
        mock_build_prompt.assert_called_once_with("code content", "test.py")
        self.assertEqual(result, "Test prompt")
