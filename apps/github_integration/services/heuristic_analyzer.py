"""
Heuristic-based file prioritization analyzer.

This module provides pattern-based scoring for files to prioritize
security-sensitive files during analysis.
"""


class HeuristicAnalyzer:
    """
    Pattern-based file prioritization using keyword scoring.

    Assigns priority scores to files based on security-relevant keywords
    in their file paths (e.g., 'auth', 'password', 'payment').
    """
    PRIORITY_KEYWORDS = {
        'auth': 10,
        'login': 10,
        'session': 9,
        'password': 9,
        'token': 8,
        'api': 7,
        'views': 7,
        'models': 6,
        'admin': 6,
        'payment': 8,
        'billing': 7,
        'user': 5,
        'account': 5,
    }

    def score_filepath(self, filepath: str) -> int:
        """
        Score filepath based on naming patterns.

        Checks the filepath against security-relevant keywords and
        accumulates a priority score.

        Args:
            filepath: Path to score (e.g., "app/auth/views.py").

        Returns:
            int: Priority score (0-20+, higher means more important).
        """
        score = 0
        filepath_lower = filepath.lower()

        # check each keyword against entire filepath
        for keyword, kw_score in self.PRIORITY_KEYWORDS.items():
            if keyword in filepath_lower:
                score += kw_score

        return score


if __name__ == '__main__':
    filepath = 'utils/helpers.py'
    analyzer = HeuristicAnalyzer()
    score = analyzer.score_filepath(filepath)
    print(f'Filepath: {filepath}, Score: {score}')


