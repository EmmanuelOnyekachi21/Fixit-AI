"""
Custom exceptions for Gemini analyzer module.
"""


class GeminiAnalyzerError(Exception):
    """Base exception for Gemini analyzer errors."""
    pass


class GeminiAPIError(GeminiAnalyzerError):
    """Raised when Gemini API call fails."""
    pass


class GeminiRateLimitError(GeminiAPIError):
    """Raised when Gemini API rate limit is exceeded."""
    pass


class GeminiNetworkError(GeminiAPIError):
    """Raised when network connection to Gemini fails."""
    pass


class ResponseParsingError(GeminiAnalyzerError):
    """Raised when response parsing fails."""
    pass


class InvalidVulnerabilityError(GeminiAnalyzerError):
    """Raised when vulnerability data is invalid."""
    pass
