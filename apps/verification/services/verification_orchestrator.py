"""
Verification orchestration service.

This module orchestrates the complete verify-first workflow for
vulnerability verification and fix generation with retry logic.
"""
from django.utils import timezone

from apps.task.models import Task
from apps.tasklog.models import TaskLog

from .fix_generator import FixGenerator
from .test_generator import TestGenerator
from .test_runner import TestRunner

from apps.github_integration.services.github_auth_service import GithubAuthService
from apps.github_integration.services.branch_manager import BranchManager
from apps.github_integration.services.commit_service import CommitService
from apps.github_integration.services.pr_creator import PRCreator


class VerificationOrchestrator:
    """
    Orchestrates the verify-first workflow.
    
    Coordinates test generation, execution, fix generation,
    and verification with retry logic.
    """
    
    MAX_RETRIES = 1  # Retry once if fix fails
    
    def __init__(self):
        """Initialize all service components."""
        self.test_generator = TestGenerator()
        self.fix_generator = FixGenerator()
        self.test_runner = TestRunner()
        self.github_client = GithubAuthService()
    
    def verify_and_fix_vulnerability(self, task: Task, create_pr: bool = False) -> bool:
        """
        Complete verify-first workflow for one task.
        
        Workflow:
        1. Generate test that proves vulnerability exists
        2. Run test (should fail, confirming vulnerability)
        3. Generate fix
        4. Run test again (should pass, confirming fix works)
        5. If fix fails, retry once
        6. If still fails, mark as false positive
        
        Args:
            task (Task): Task object with vulnerability details.
        
        Returns:
            bool: True if successfully verified and fixed, False otherwise.
        """
        self._log(task, "Starting verification workflow")
        
        # Step 1: Generate test
        if not self._generate_test(task):
            return False
        
        # Step 2: Run test (should fail, proving vulnerability exists)
        if not self._verify_vulnerability_exists(task):
            return False
        
        # Step 3: Generate and verify fix (with retry logic)
        if not self._generate_and_verify_fix(task):
            return False
        
        # Success!
        task.status = 'completed'
        task.verified_at = timezone.now()
        task.save()
        self._log(task, "Verification workflow completed successfully")

        # Create PR if requested
        if create_pr:
            try:
                self._create_github_pr(task)
            except Exception as e:
                self._log(
                    task,
                    f"Failed to create PR: {e}",
                    level='error'
                )
        
        return True
    
    def _generate_test(self, task: Task) -> bool:
        """
        Generate test for the vulnerability.
        
        Args:
            task (Task): Task to generate test for.
        
        Returns:
            bool: True if test generated successfully.
        """
        self._log(task, "Generating test...")
        
        try:
            test_code = self.test_generator.generate_test(task)
            
            if not test_code:
                self._log(task, "Failed to generate test", level="error")
                task.test_status = 'error'
                task.validation_message = "Failed to generate test code"
                task.save()
                return False
            
            task.test_code = test_code
            task.test_status = 'generated'
            task.save()
            
            self._log(task, "Test generated successfully")
            return True
            
        except Exception as e:
            self._log(task, f"Error generating test: {e}", level="error")
            task.test_status = 'error'
            task.validation_message = str(e)
            task.save()
            return False
    
    def _verify_vulnerability_exists(self, task: Task) -> bool:
        """
        Run test to verify vulnerability exists.
        
        Test should FAIL, proving the vulnerability is real.
        If test PASSES, it's a false positive.
        
        Args:
            task (Task): Task with generated test.
        
        Returns:
            bool: True if vulnerability confirmed (test failed).
        """
        self._log(task, "Running test to verify vulnerability exists...")
        
        try:
            result = self.test_runner.run_test(
                test_code=task.test_code,
                file_path=task.file_path
            )
            
            if result.passed:
                # Test passed = vulnerability doesn't exist (false positive)
                self._log(
                    task,
                    "Test passed - vulnerability does not exist "
                    "(false positive)",
                    level="warning"
                )
                task.test_status = 'passed'
                task.status = 'false_positive'
                task.validation_message = (
                    "Test passed on first run - vulnerability does not exist"
                )
                task.save()
                return False

            # Test failed = vulnerability confirmed!
            self._log(task, "Test failed - vulnerability confirmed")
            task.test_status = 'failed'
            task.validation_message = (
                f"Test output: {result.output}\n"
                f"Error: {result.error}"
            )
            task.save()

            return True

        except Exception as e:
            self._log(task, f"Error running test: {e}", level="error")
            task.test_status = 'error'
            task.validation_message = str(e)
            task.save()
            return False

    def _generate_and_verify_fix(self, task: Task) -> bool:
        """
        Generate fix and verify it works, with retry logic.

        Args:
            task: Task with confirmed vulnerability.

        Returns:
            bool: True if fix generated and verified successfully.
        """
        while task.retry_count <= self.MAX_RETRIES:
            attempt_num = task.retry_count + 1
            self._log(
                task,
                f"Fix attempt {attempt_num}/{self.MAX_RETRIES + 1}"
            )

            # Generate fix
            if not self._generate_fix(task):
                return False

            # Verify fix works
            if self._verify_fix(task):
                # Success!
                return True

            # Fix failed - retry?
            task.retry_count += 1
            task.save()

            if task.retry_count <= self.MAX_RETRIES:
                self._log(
                    task,
                    f"Fix failed, retrying... "
                    f"(attempt {task.retry_count + 1})"
                )
            else:
                self._log(
                    task,
                    "Fix failed after all retries - "
                    "marking as false positive",
                    level="warning"
                )
                task.status = 'false_positive'
                task.fix_status = 'failed'
                task.validation_message += (
                    "\n\nFailed after all retry attempts"
                )
                task.save()
                return False
        
        return False
    
    def _generate_fix(self, task: Task) -> bool:
        """
        Generate fix for the vulnerability.
        
        Args:
            task (Task): Task to generate fix for.
        
        Returns:
            bool: True if fix generated successfully.
        """
        self._log(task, "Generating fix...")
        
        try:
            fix_code = self.fix_generator.generate_fix(task)
            
            if not fix_code:
                self._log(task, "Failed to generate fix", level="error")
                task.fix_status = 'failed'
                task.validation_message = "Failed to generate fix code"
                task.save()
                return False
            
            task.fix_code = fix_code
            task.fix_status = 'generated'
            task.save()
            
            self._log(task, "Fix generated successfully")
            print(fix_code)
            return True
            
        except Exception as e:
            self._log(task, f"Error generating fix: {e}", level="error")
            task.fix_status = 'failed'
            task.validation_message = str(e)
            task.save()
            return False
    
    def _verify_fix(self, task: Task) -> bool:
        """
        Verify that the fix works by running the test again.
        
        Test should now PASS, proving the fix works.
        
        Args:
            task (Task): Task with generated fix.
        
        Returns:
            bool: True if fix verified (test passed).
        """
        self._log(task, "Verifying fix by running test again...")
        
        try:
            # Apply the fix temporarily to verify it works
            result = self.test_runner.run_test_with_fix(
                test_code=task.test_code,
                file_path=task.file_path,
                fix_code=task.fix_code
            )
            
            if result.passed:
                # Test passed = fix works!
                self._log(task, "Test passed - fix verified!")
                task.test_status = 'passed'
                task.fix_status = 'verified'
                task.validation_message = (
                    f"Fix verified successfully\n"
                    f"Test output: {result.output}"
                )
                task.save()
                return True
            else:
                # Test still fails = fix didn't work
                self._log(
                    task,
                    "Test still fails after fix - fix did not work",
                    level="WARNING"
                )
                task.fix_status = 'failed'
                task.validation_message = (
                    f"Fix did not resolve the issue\n"
                    f"Test output: {result.output}\n"
                    f"Error: {result.error}"
                )
                task.save()
                return False
                
        except Exception as e:
            self._log(task, f"Error verifying fix: {e}", level="error")
            task.fix_status = 'failed'
            task.validation_message = str(e)
            task.save()
            return False
    
    def _log(self, task: Task, message: str, level: str = "info"):
        """
        Log a message to TaskLog.
        
        Args:
            task (Task): Task to log for.
            message (str): Log message.
            level (str): Log level (INFO, WARNING, ERROR).
        """
        TaskLog.objects.create(
            task=task,
            message=f"[{level}] {message}"
        )
        print(f"Task {task.id} - {message}")
    
    def _create_github_pr(self, task):
        """
        Create Github PR for verified fix.

        Args:
            task (Task): Task with verified fix.
        """
        self._log(
            task,
            "Creating Github pull request..."
        )

        try:
            # Get authenticated Github client
            github_client = self.github_client.get_authenticated_client()

            # Create branch
            branch_manager = BranchManager(github_client)
            branch_name = branch_manager.create_fix_branch(
                task.repository.owner,
                task.repository.repo_name,
                task.id,
                task.vulnerability_type
            )
            self._log(
                task,
                f"Created branch: {branch_name}"
            )

            # Generate test file path
            import os
            file_dir = os.path.dirname(task.file_path) if task.file_path else ''
            file_name = os.path.basename(task.file_path) if task.file_path else 'fix'
            test_file_name = f"test_{file_name}"
            test_path = os.path.join(file_dir, test_file_name) if file_dir else test_file_name

            # Commit fix and test to branch
            commit_service = CommitService(github_client)
            commit_message = commit_service.generate_commit_message(task)
            
            commit_sha = commit_service.commit_fix(
                task.repository.owner,
                task.repository.repo_name,
                branch_name,
                task.file_path,
                task.fix_code,
                test_path,
                task.test_code,
                commit_message=commit_message
            )

            self._log(
                task,
                f"Committed fix to branch (SHA: {commit_sha[:7]})"
            )

            # Create pull request
            pr_creator = PRCreator(github_client)
            pr = pr_creator.create_pull_request(
                task=task,
                branch_name=branch_name,
                owner=task.repository.owner,
                repo_name=task.repository.repo_name
            )

            # Update task with PR info
            task.pr_url = pr.pr_url
            task.status = 'pr_created'
            task.save()

            self._log(
                task,
                f"Pull request created: {pr.pr_url}"
            )
            
        except Exception as e:
            self._log(
                task,
                f"Failed to create PR: {str(e)}",
                level="error"
            )
            task.status = 'completed'  # Still mark as completed, just no PR
            task.validation_message = (
                f"{task.validation_message or ''}\n"
                f"PR creation failed: {str(e)}"
            )
            task.save()
            raise
        
