"""
Commit service module.

This module handles committing fixes and tests to GitHub branches
with validation and safety checks.
"""
from github import Github, InputGitTreeElement


class CommitService:
    """
    Handles committing changes to Github.
    """

    def __init__(self, github_client: Github):
        self.client = github_client
    
    def commit_fix(
        self,
        owner: str,
        repo_name: str,
        branch_name: str,
        file_path: str,
        new_content: str,
        test_path: str,
        test_content: str,
        commit_message: str
    ) -> str:
        """
        Commit fix and test to branch

        Args:
            owner: Repo owner
            repo_name: Repo name
            branch_name: Branch to commit to
            file_path: Path to fixed file
            new_content: Fixed file content
            test_path: Path to test file
            test_content: Test file content
            commit_message: Commit message
        
        Returns:
            Commit SHA
        
        Raises:
            ValueError: If content validation fails
        """
        # VALIDATION: Check if fix content is not empty
        if not new_content or not new_content.strip():
            raise ValueError(
                f"Fix content is empty for {file_path}. "
                "Cannot commit empty file."
            )
        
        # VALIDATION: Check if test content is not empty
        if not test_content or not test_content.strip():
            raise ValueError(
                f"Test content is empty for {test_path}. "
                "Cannot commit empty test."
            )
        
        # VALIDATION: Check minimum length (basic sanity check)
        if len(new_content.strip()) < 50:
            raise ValueError(
                f"Fix content too short for {file_path}: "
                f"{len(new_content)} characters. "
                "This might indicate an incomplete fix."
            )
        
        if len(test_content.strip()) < 50:
            raise ValueError(
                f"Test content too short for {test_path}: "
                f"{len(test_content)} characters. "
                "This might indicate an incomplete test."
            )
        
        print(f"✓ Validation passed:")
        print(f"  - Fix content: {len(new_content)} characters")
        print(f"  - Test content: {len(test_content)} characters")
        
        repo = self.client.get_repo(f"{owner}/{repo_name}")
        
        # FETCH ORIGINAL FILE for comparison
        try:
            original_file = repo.get_contents(file_path, ref=branch_name)
            original_content = original_file.decoded_content.decode('utf-8')
            original_size = len(original_content)
            new_size = len(new_content)
            
            print(f"✓ Fetched original file:")
            print(f"  - Original size: {original_size} characters")
            print(f"  - New size: {new_size} characters")
            
            # VALIDATION: Warn if new file is significantly smaller
            if new_size < original_size * 0.5:  # Less than 50% of original
                print(f"⚠️  WARNING: New file is {int((1 - new_size/original_size) * 100)}% smaller than original")
                print(f"⚠️  This might indicate an incomplete fix")
                # Don't raise error, just warn - sometimes fixes can be shorter
                
        except Exception as e:
            print(f"⚠️  Could not fetch original file: {e}")
            print(f"⚠️  Proceeding with generated content only")

        # Get branch reference
        ref  = repo.get_git_ref(f"heads/{branch_name}")
        base_sha = ref.object.sha
        base_commit = repo.get_git_commit(base_sha)
        base_tree = base_commit.tree

        # Create tree elements for the file
        elements = []

        # Add fixed file
        elements.append(
            InputGitTreeElement(
                path=file_path,
                mode="100644",
                type="blob",
                content=new_content
            )
        )

        # Add test file
        elements.append(
            InputGitTreeElement(
                path=test_path,
                mode='100644',
                type='blob',
                content=test_content
            )
        )

        # create new tree
        new_tree = repo.create_git_tree(elements, base_tree)

        # Create commit
        new_commit = repo.create_git_commit(
            message=commit_message,
            tree=new_tree,
            parents=[base_commit]
        )

        # Update branch reference
        ref.edit(new_commit.sha)

        print(f"✓ Committed to {branch_name}: {commit_message}")
        return new_commit.sha
    
    def generate_commit_message(self, task) -> str:
        """
        Generate descriptive commit message.
        """
        return f"""Fix: {task.vulnerability_type} in {task.file_path}
Vulnerability: {task.description}

This commit:
- Fixes the {task.vulnerability_type} vulnerability
- Adds test to prevent regression
- Generated by FixIt AI Agent
"""


