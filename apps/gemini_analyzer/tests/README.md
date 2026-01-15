# Gemini Analyzer Tests

This directory contains comprehensive unit tests for the gemini_analyzer service layer.

## Test Structure

```
tests/
├── __init__.py
├── README.md                          # This file
├── fixtures/                          # Test data and mock responses
│   ├── __init__.py
│   ├── sample_code.py                # Sample code snippets
│   └── sample_responses.py           # Mock Gemini API responses
└── test_services/                    # Service layer tests
    ├── __init__.py
    ├── test_gemini_client.py         # Tests for GeminiClient
    ├── test_response_parser.py       # Tests for ResponseParser
    └── test_code_analyzer.py         # Tests for CodeAnalyzer
```

## Running Tests

Run all service tests:
```bash
python manage.py test apps.gemini_analyzer.tests.test_services
```

Run specific test file:
```bash
python manage.py test apps.gemini_analyzer.tests.test_services.test_gemini_client
```

Run specific test class:
```bash
python manage.py test apps.gemini_analyzer.tests.test_services.test_gemini_client.TestGeminiClientParseResponse
```

Run with verbose output:
```bash
python manage.py test apps.gemini_analyzer.tests.test_services --verbosity=2
```

## Test Coverage

### test_gemini_client.py (17 tests)
Tests for the `GeminiClient` service that interacts with Google's Gemini API.

**Key areas tested:**
- Initialization with/without API key
- API call success and error handling
- Response parsing (clean JSON, markdown-wrapped, invalid JSON)
- Edge cases (empty, None, whitespace responses)

**Mocking strategy:** Uses `unittest.mock.patch` to mock `genai.Client` to avoid actual API calls.

### test_response_parser.py (13 tests)
Tests for the `ResponseParser` service that transforms Gemini responses into Task objects.

**Key areas tested:**
- Vulnerability parsing and validation
- Type mapping and case-insensitivity
- Default values and field truncation
- Task creation (with and without saving)
- Bulk create operations

**Mocking strategy:** Minimal mocking needed since this is mostly data transformation logic. Uses real database for save operations.

### test_code_analyzer.py (10 tests)
Tests for the `CodeAnalyzer` orchestration service.

**Key areas tested:**
- Dependency initialization
- Single file analysis workflow
- Repository-wide analysis
- Error handling and recovery
- Missing/invalid file data handling

**Mocking strategy:** Mocks both `GeminiClient` and `ResponseParser` to test orchestration logic in isolation.

## Test Statistics

- **Total tests:** 40
- **All passing:** ✓
- **Test execution time:** ~0.4 seconds

## Key Testing Patterns Used

1. **Arrange-Act-Assert:** Standard test structure
2. **Mock external dependencies:** Avoid API calls and isolate units
3. **Test edge cases:** Empty inputs, None values, malformed data
4. **Test error handling:** Exceptions, invalid data, API failures
5. **Test data transformation:** Validation, mapping, truncation
6. **Test orchestration:** Method call order and data flow
