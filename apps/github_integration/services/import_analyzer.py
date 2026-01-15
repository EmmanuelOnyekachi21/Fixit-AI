import re


class ImportAnalyzer:
    """
    Analyzes file imports and patterns to assess security risks.
    """

    RISKY_IMPORTS = {
        'subprocess': 10,
        'os.system': 10,
        'eval': 10,
        'exec': 10,
        'pickle': 8,
        '__import__': 9,
        'compile': 8,
        'sqlite3': 7,
        'psycopg2': 7,
        'django.db': 7,
        'django.contrib.auth': 8,
        'flask_login': 8,
        'jwt': 7,
        'cryptography': 6,
        'passlib': 7,
        'bcrypt': 7,
    }

    DANGEROUS_PATTERNS = {
        r'subprocess\.(call|run|Popen)\s*\(': 10,
        r'os\.system\s*\(': 10,
        r'eval\s*\(': 10,
        r'exec\s*\(': 10,
        r'\.execute\s*\(\s*["\']SELECT.*\+': 8,
        r'\.execute\s*\(\s*f["\']': 8,
        r'password\s*=\s*["\'][^"\']+["\']': 6,
        r'secret_?key\s*=\s*["\']': 6,
        r'api_?key\s*=\s*["\']': 6,
        r'pickle\.loads?\s*\(': 8,
        r'open\s*\(.*\+': 5,
    }

    def score_file(self, content: str, file_path: str) -> int:
        """
        Calculate risk score for a file.
        
        Args:
            content: File content as string
            filepath: File path for context
            
        Returns:
            Risk score (0-100)
        """
        import_score = self._score_imports(content)
        pattern_score = self._score_patterns(content)
        total_score = import_score + pattern_score
        total_score = min(total_score, 100)
        return total_score
    
    def _score_imports(self, content: str) -> int:
        """
        Calculate risk score based on imports.

        Args:
            content: File content as string

        Returns:
            Risk score (0-100)
        """
        score = 0

        # Check each risky import against the content
        for import_name, risk in ImportAnalyzer.RISKY_IMPORTS.items():
            # Match both "import X" and "from X import"
            # Using word boundaries to avoid partial matches
            
            import_pattern = rf'\b(import\s+{re.escape(import_name)}|from\s+{re.escape(import_name)})'
            if re.search(import_pattern, content):
                score += risk
        # Normalize the score to a 0-100 scale
        import_score = min(score, 100)
        return import_score

    def _score_patterns(self, content: str) -> int:
        """
        Calculate risk score based on patterns.

        Args:
            content: File content as string

        Returns:
            Risk score (0-100)
        """
        pattern_score = 0
        for patterns, score in ImportAnalyzer.DANGEROUS_PATTERNS.items():
            if re.search(patterns, content):
                pattern_score += score
        return pattern_score


    
