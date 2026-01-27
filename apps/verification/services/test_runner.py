"""
Test execution service for vulnerability verification.

This module safely executes generated tests in an isolated environment
to verify vulnerabilities and fixes.
"""
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass


@dataclass
class TestResult:
    """
    Data class to hold test execution results.

    Attributes:
        passed: True if test passed, False if failed.
        output: stdout from pytest.
        error: stderr from pytest (if any).
        timed_out: True if test exceeded timeout.
    """
    passed: bool
    output: str
    error: str
    timed_out: bool = False


class TestRunner:
    """
    Safely executes tests in isolated environment.

    Current implementation uses subprocess for test execution.

    TODO - FUTURE ENHANCEMENT:
    Consider using Docker for better isolation and security:
    - Run tests in isolated Docker containers
    - Prevent malicious test code from affecting host system
    - Better resource control (CPU, memory limits)
    - Implementation: Use docker-py library to spin up containers
    - Example: docker run --rm -v /tmp/test.py:/test.py
              python:3.9 pytest /test.py
    """
    def __init__(self, timeout: int = 30):
        """
        Initialize TestRunner.

        Args:
            timeout: Maximum seconds to allow test to run (default 30).
        """
        self.timeout = timeout
        self._check_pytest_installed()
    
    def _check_pytest_installed(self):
        """
        Check if pytest is installed and available.
        
        Raises:
            RuntimeError: If pytest is not installed.
        """
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError(
                    "pytest is not installed. Install it with: pip install pytest"
                )
        except FileNotFoundError:
            raise RuntimeError(
                "Python executable not found"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "pytest check timed out"
            )

    def run_test(self, test_code: str, file_path: str) -> TestResult:
        """
        Execute tests and return results.

        Args:
            test_code: The source code of the test to be executed.
            file_path: The path to the file containing the test.

        Returns:
            TestResult: The result of the test execution with pass/fail
                       status.
        """
        # Create a temporary file for the test
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False  # Keep file until we're done.
        ) as temp_file:
            temp_file.write(test_code)
            temp_file_path = temp_file.name
        try:
            # Run pytest on the temporary file
            result = subprocess.run(
                ['python', '-m', 'pytest', temp_file_path, '-v'],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            # Parse the result
            # pytest returns 0 if all tests pass, non-zero if any fail
            passed = result.returncode == 0

            return TestResult(
                passed=passed,
                error=result.stderr,
                output=result.stdout,
                timed_out=False
            )
        except subprocess.TimeoutExpired:
            # Test took too long
            return TestResult(
                passed=False,
                output='',
                error=f"Test timed out after {self.timeout} seconds",
                timed_out=True
            )
        except Exception as e:
            # other errors (pytest not installed, etc.)
            return TestResult(
                passed=False,
                output='',
                error=str(e),
                timed_out=False
            )
        finally:
            # clean up: delete the temporary file
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass  # Ignore cleanup errors.
    
    def run_test_with_fix(
        self,
        test_code: str,
        file_path: str,
        fix_code: str
    ) -> TestResult:
        """
        Execute test with fix in an isolated temporary environment.
        
        This method:
        1. Creates a temporary directory
        2. Writes the fixed code to a temp file with the same name
        3. Writes the test code to a temp test file
        4. Runs the test in that directory
        5. Cleans up
        
        Args:
            test_code: The test code to execute.
            file_path: Original file path (used for naming only).
            fix_code: The fixed version of the code.
        
        Returns:
            TestResult: Result of test execution with fix applied.
        """
        temp_dir = None
        
        try:
            # Create temporary directory for isolated testing
            temp_dir = tempfile.mkdtemp(prefix='fixit_test_')
            
            # Extract just the filename from the path
            filename = os.path.basename(file_path)
            
            # Write fixed code to temp file
            fixed_file_path = os.path.join(temp_dir, filename)
            with open(fixed_file_path, 'w') as f:
                f.write(fix_code)
            
            # Write test code to temp test file
            test_file_path = os.path.join(temp_dir, f'test_{filename}')
            with open(test_file_path, 'w') as f:
                f.write(test_code)
            
            # Run pytest in the temp directory
            result = subprocess.run(
                ['python', '-m', 'pytest', test_file_path, '-v'],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=temp_dir  # Run in temp directory
            )
            
            passed = result.returncode == 0
            
            return TestResult(
                passed=passed,
                error=result.stderr,
                output=result.stdout,
                timed_out=False
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                passed=False,
                output='',
                error=f"Test timed out after {self.timeout} seconds",
                timed_out=True
            )
        except Exception as e:
            return TestResult(
                passed=False,
                output='',
                error=f"Error running test with fix: {str(e)}",
                timed_out=False
            )
        finally:
            # Clean up temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass  # Ignore cleanup errors
        

        
        

