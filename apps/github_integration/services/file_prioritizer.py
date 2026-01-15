"""
File prioritization service module.

This module provides functionality to prioritize files for security analysis
based on various scoring mechanisms.
"""


from typing import List, Dict
from .ai_analyzer import AiAnalyzer
from .heuristic_analyzer import HeuristicAnalyzer
from .import_analyzer import ImportAnalyzer


class FilePrioritizer:
    """
    Hybrid file prioritization system.
    
    Tiered authority model:
    1. AI selections (absolute priority)
    2. Import-scored files (fill remaining)
    3. Heuristic (contributes to import scoring)
    """
    def __init__(self):
        self.ai_analyzer = AiAnalyzer()
        self.import_analyzer = ImportAnalyzer()
        self.heuristic_analyzer = HeuristicAnalyzer()
    
    def prioritize_files(
        self,
        files: List[Dict[str, str]],
        repo_name: str,
        max_files: int = 25
    ) -> List[str]:
        """
        Prioritize files using hybrid approach.
        
        Args:
            files: List of file dicts with 'path' and 'content'
            repo_name: Repository name
            max_files: Number of files to return
            
        Returns:
            Prioritized list of files
        """
        # if files <= max_files, return early if so
        if len(files) <= max_files:
            return files
        
        # Get AI suggestions
        print(f"Stage 1: Getting AI suggestions for top {max_files} files...")
        ai_suggested_paths = self.ai_analyzer.suggest_priority_files(
            files,
            repo_name,
            max_files
        )
        print(f"  AI suggested {len(ai_suggested_paths)} files")

        # Score all files with import + heuristic
        print(f"Scoring all files with import + heuristic analysis...")
        scored_files = self._score_all_files(files)
        print(f"  Scored {len(scored_files)} files")

        # Combine using tiered authority
        print("Combining priorities (AI first, then scored)..")
        prioritized_files = self._combine_priorities(
            files,
            ai_suggested_paths,
            scored_files,
            max_files
        )

        print(f"✓ Final selection: {len(prioritized_files)} files")
        return prioritized_files
    
    def _score_all_files(
        self,
        files: List[Dict[str, str]],
    ) -> List[tuple]:
        """
        Score files using import + heuristic analysis.

        Args:
            files: List of file dicts with 'path' and 'content'
        
        Returns:
            List of (file_dict, combined_score) tuples, sorted by score
        """
        scored = []

        # Loop through all files and score them.
        for file_dict in files:
            filepath = file_dict['path']
            content = file_dict['content']

            # Get import_score from ImportAnalyzer
            import_score = self.import_analyzer.score_file(
                content=content,
                file_path=filepath
            )

            # Get heuristic_score from HeuristicAnalyzer
            heuristic_score = self.heuristic_analyzer.score_filepath(filepath)

            # combine scores (import weighted 70%, heuristic 30%)
            combined_score = (import_score * 0.7) + (heuristic_score * 0.3)

            # Create (file_dict, combined_score) tuple
            scored.append((file_dict, combined_score))
        
        # Sort by score (highest first)
        scored.sort(key=lambda x: x[1], reverse=True)

        # return sorted list
        return scored
    
    def _combine_priorities(
        self,
        all_files: List[Dict],
        ai_paths: List[str],
        scored_files: List[tuple],
        max_files: int
    ) -> List[Dict]:
        """
        Merge AI suggestions with scored files (tiered authority).
        
        Strategy:
        1. Add all AI-suggested files first
        2. Fill remaining slots with highest-scored files
        3. No duplicates
        
        Args:
            all_files: All available files
            ai_paths: Paths suggested by AI
            scored_files: Files scored by import+heuristic
            max_files: Maximum files to return
            
        Returns:
            Combined prioritized file list
        """

        # create selected_files list and selected_paths set
        selected_files = []
        selected_paths = set()

        # Create a lookup map for quick file access by path
        file_map = {file['path']: file for file in all_files}

        # Tier 1 - Add AI-suggested files (up to max_files)
        for path in ai_paths:
            if len(selected_files) >= max_files:
                break

            if path in file_map and path not in selected_paths:
                selected_files.append(file_map['path'])
                selected_paths.add(path)
        
        # Tier 2 - Fill the remaining with scored_files
        for file_dict, score in scored_files:
            if len(selected_files) >= max_files:
                break

            filepath = file_dict['path']
            
            # skips duplicates
            if filepath not in selected_paths:
                selected_files.append(file_dict)
                selected_paths.add(filepath)
        

        # Return selected_files
        return selected_files
