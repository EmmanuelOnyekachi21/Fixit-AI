"""
Branch management service module.

This module handles creating and managing Git branches for fix commits.
"""
from github import Github
from github.GithubException import GithubException


class BranchManager:
    def __init__(self, github_client: Github):
        self.github_client = github_client

    def create_fix_branch(
        self, owner: str, repo_name: str, task_id: int, vulnerability_type: str
    ) -> str:
        """
        Create a new branch for a fix.

        Args:
            owner: Repo owner
            repo_name: Repository name
            task_id: Task ID
            vulnerability_type: Type of vulnerability
        
        Returns:
            Name of created branch
        """

        repo = self.github_client.get_repo(f"{owner}/{repo_name}")

        # Get default branch (main/master)
        default_branch = repo.default_branch
        base_ref = repo.get_git_ref(f'heads/{default_branch}')
        base_sha = base_ref.object.sha

        # Create branch name
        branch_name = self._generate_branch_name(
            task_id,
            vulnerability_type
        )

        try:
            # Create a new branch
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha
            )
            print(f"✓ Created branch: {branch_name}")
            return branch_name
        except GithubException as e:
            if "already exists" in str(e):
                # Branch exists, append timestamp
                import time
                branch_name = f"{branch_name}-{int(time.time())}"
                repo.create_git_ref(
                    ref=f"refs/heads/{branch_name}",
                    sha=base_sha
                )
                print(f"✓ Created branch: {branch_name} (with timestamp)")
                return branch_name
            raise

    def _generate_branch_name(self, task_id: int, vulnerability_type: str) -> str:
        """
        Generate descriptive branch name.
        """
        clean_type = vulnerability_type.lower().replace('_', '-')
        return f"fix/{clean_type}-task-{task_id}"
    
    def delete_branch(self, owner: str, repo_name: str, branch_name: str) -> None:
        """
        Delete a branch from repository.
    
        Args:
            owner: Repo owner
            repo_name: Repository name
            branch_name: Name of branch to delete
        """
        repo = self.github_client.get_repo(f"{owner}/{repo_name}")
        ref = repo.get_git_ref(f"heads/{branch_name}")
        ref.delete()
        print(f"✓ Deleted branch: {branch_name}")

