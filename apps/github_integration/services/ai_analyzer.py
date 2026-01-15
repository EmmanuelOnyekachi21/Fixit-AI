"""
AI-based file analysis module.

This module provides AI-powered analysis capabilities for assessing
file security and prioritization.
"""
import json
import re
from typing import List, Dict
from collections import defaultdict

from apps.gemini_analyzer.services.gemini_client import GeminiClient



class AiAnalyzer:
    """
    Uses Gemini to intelligently prioritize files.
    """
    def __init__(self):
        """
        Initializes the AiAnalyzer class.
        """
        self.gemini_client = GeminiClient()
    
    def suggest_priority_files(
        self,
        files: List[Dict[str, str]],
        repo_name: str,
        max_files: int = 25
    ) -> List[str]:
        """
        Use AI to identify highest risk files.

        Args:
            files: List of dicts with 'path' and 'content' keys
            repo_name: Repository name
            max_files: Number of files to suggest

        Returns:
            List of filepaths in priority order
        """
        try:
            # Build prompt
            prompt = self._build_prompt(files, repo_name, max_files)

            # Call Gemini API
            response = self.gemini_client.client.models.generate_content(
                model=self.gemini_client.model_name,
                contents=[prompt]
            )

            # Parse response
            suggested_paths = self._parse_response(
                response.text,
                max_files
            )

            # Validate paths exist in file list.
            validated_paths = {
                file['path'] for file in files
            }
            valid_file_paths = [
                path for path in suggested_paths
                if path in valid_paths
            ]

            # return valid file paths

            return valid_file_paths
        except Exception as e:
            print(f"Error in suggest_priority_files: {e}")
            return []
    
    def _build_prompt(
        self,
        files: List[Dict[str, str]],
        repo_name,
        max_files: int
    ):
        """
        Builds a prompt for the Gemini API.

        Args:
            files: List of dicts with 'path' and 'content' keys
            repo_name: Repository name
            max_files: Number of files to suggest

        Returns:
            Formatted prompt string.
        """
        # Extract file paths from files list
        file_paths = [file['path'] for file in files]

        # Organize into tree structure
        tree_structure = self._organize_file_tree(file_paths)

        # Create prompt asking for highest-risk files with JSON output
        prompt = f"""You are a security expert analyzing a Python repository called "{repo_name}".

Below is the file structure of the repository:

{tree_structure}

Your task: Identify the {max_files} files that are MOST LIKELY to contain security vulnerabilities.

Consider these factors:
- Authentication and authorization code
- Password/token handling
- Database queries and ORM usage
- API endpoints and views
- Payment/billing logic
- User input handling
- File operations
- Subprocess/command execution
- Cryptographic operations

Return ONLY a JSON array of file paths, ordered from highest to lowest risk.
Format: ["path/to/file1.py", "path/to/file2.py", ...]

Do not include any explanation, just the JSON array."""

        return prompt
    
    def _organize_file_tree(self, paths: List[str]) -> str:
        """
        Format paths as indented tree structure.

        Args:
            paths: list of the file paths
        
        Returns:
            Formatted tree string.
        """
        # Group files by directory
        tree = defaultdict(list)

        for path in paths:
            if '/' in path:
                directory = '/'.join(path.split('/')[:-1])
                filename = path.split('/')[-1]
                tree[directory].append(filename)
            else:
                tree[''].append(path)
        
        # Format as tree with indentation
        lines = []

        # sort directories for consistent output
        for directory in sorted(tree.keys()):
            if directory:
                lines.append(f"{directory}/")
                for filename in sorted(tree[directory]):
                    lines.append(f"{' ' * 4}{filename}")
            else:
                # Root level files
                for filename in sorted(tree['']):
                    lines.append(filename)
        # Return formatted string
        return '\n'.join(lines)
    
    def _parse_response(
        self,
        response_text: str,
        max_files: int
    ):
        """
        Extract file paths from Gemini's response.

        Args:
            response_text: Raw response from Gemini
            expected_count: Expected number of paths
        
        Returns:
            List of file paths (up to max_files)
        """

        try:
            # Strip markdown formatting with (```json ...```)
            cleaned = response_text.strip()

            # Match markdown code blocks
            json_match = re.search(
                r"```(?:json)?\s*(\[.*?\])\s*```",
                cleaned,
                re.DOTALL
            )

            if json_match:
                cleaned = json_match.group(1)
            
            # Remove any remaining backticks
            cleaned = cleaned.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON array
            parsed = json.loads(cleaned)
            
            # Validate it's a list of strings
            if not isinstance(parsed, list):
                print(f"Warning: Expected list, got {type(parsed)}")
                return []
            
            # Ensure all items are strings
            paths = [str(item) for item in parsed if isinstance(item, str)]
            
            # Return up to expected_count paths
            return paths[:max_files]
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Attempted to parse: {response_text[:200]}...")
            return []
        except Exception as e:
            print(f"Error parsing response: {e}")
            return []

