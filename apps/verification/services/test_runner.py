"""
Test execution service for vulnerability verification.

This module safely executes generated tests in an isolated environment
to verify vulnerabilities and fixes.
"""
import os
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
        

        
        

