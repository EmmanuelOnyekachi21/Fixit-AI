"""
Integration test for the verification workflow.

This script tests the complete verify-first workflow:
1. Generate test for a vulnerability
2. Run test (should fail, proving vulnerability exists)
3. Generate fix
4. Run test again (should pass, proving fix works)

NOTE: This makes real Gemini API calls and will use your API quota.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.repository.models import Repository
from apps.task.models import Task
from apps.verification.services.verification_orchestrator import VerificationOrchestrator


def create_test_task():
    """
    Create a test task with a simple SQL injection vulnerability.
    
    Returns:
        Task: A task object with a known vulnerability.
    """
    # Create or get test repository
    repo, created = Repository.objects.get_or_create(
        owner='test-user',
        repo_name='vulnerable-app',
        defaults={
            'repo_url': 'https://github.com/test-user/vulnerable-app',
            'status': 'idle'
        }
    )
    
    if created:
        print(f"✓ Created test repository: {repo}")
    else:
        print(f"✓ Using existing repository: {repo}")
    
    # Create a test task with SQL injection vulnerability
    task = Task.objects.create(
        repository=repo,
        title='SQL Injection in login endpoint',
        description=(
            'The login function directly concatenates user input into SQL query '
            'without sanitization, allowing SQL injection attacks. '
            'An attacker can bypass authentication by injecting SQL code.'
        ),
        vulnerability_type='sql_injection',
        file_path='auth/views.py',
        line_number=42,
        status='pending'
    )
    
    print(f"✓ Created test task: {task.id} - {task.title}")
    return task


def print_separator(title):
    """Print a visual separator."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_task_status(task):
    """Print current task status."""
    task.refresh_from_db()
    print(f"Task Status: {task.status}")
    print(f"Test Status: {task.test_status}")
    print(f"Fix Status: {task.fix_status}")
    print(f"Retry Count: {task.retry_count}")
    
    if task.test_code:
        print(f"\nGenerated Test Code (first 200 chars):")
        print(task.test_code[:200] + "..." if len(task.test_code) > 200 else task.test_code)
    
    if task.fix_code:
        print(f"\nGenerated Fix Code (first 200 chars):")
        print(task.fix_code[:200] + "..." if len(task.fix_code) > 200 else task.fix_code)
    
    if task.validation_message:
        print("\nValidation Message:")
        msg = task.validation_message
        if len(msg) > 300:
            print(msg[:300] + "...")
        else:
            print(msg)


def print_task_logs(task):
    """Print all logs for the task."""
    logs = task.logs.all().order_by('timestamp')
    
    if logs.exists():
        print("\nTask Logs:")
        print("-" * 70)
        for log in logs:
            print(f"[{log.timestamp.strftime('%H:%M:%S')}] {log.message}")
        print("-" * 70)
    else:
        print("\nNo logs found for this task.")


def run_verification_test():
    """
    Run the complete verification workflow test.
    """
    print_separator("VERIFICATION WORKFLOW TEST")
    
    print("This test will:")
    print("1. Create a test task with SQL injection vulnerability")
    print("2. Run the verification orchestrator")
    print("3. Show results at each step")
    print("\nNOTE: This makes real Gemini API calls!\n")
    
    # Create test task
    print_separator("Step 1: Creating Test Task")
    task = create_test_task()
    
    # Run verification workflow
    print_separator("Step 2: Running Verification Workflow")
    orchestrator = VerificationOrchestrator()
    
    print("Starting verification... (this may take 1-2 minutes)\n")
    
    try:
        success = orchestrator.verify_and_fix_vulnerability(task)
        
        # Show results
        print_separator("Step 3: Results")
        
        if success:
            print("✅ VERIFICATION WORKFLOW SUCCEEDED!\n")
        else:
            print("❌ VERIFICATION WORKFLOW FAILED\n")
        
        print_task_status(task)
        print_task_logs(task)
        
        # Summary
        print_separator("Summary")
        
        if success:
            print("✅ Test was generated")
            print("✅ Vulnerability was confirmed (test failed initially)")
            print("✅ Fix was generated")
            print("✅ Fix was verified (test passed after fix)")
            print("\n🎉 The verify-first workflow is working correctly!")
        else:
            print("The workflow did not complete successfully.")
            print("Check the task status and logs above for details.")
            
            if task.status == 'false_positive':
                print("\nNote: Task was marked as false positive.")
                print("This could mean:")
                print("- The test passed initially (vulnerability doesn't exist)")
                print("- The fix failed after retries")
        
        print(f"\nTask ID: {task.id}")
        print(f"You can view this task in Django admin: /admin/task/task/{task.id}/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTask status at time of error:")
        print_task_status(task)
        print_task_logs(task)
        raise


def cleanup_test_data():
    """
    Optional: Clean up test data.
    
    Uncomment the code below if you want to delete test data after running.
    """
    # Repository.objects.filter(owner='test-user', repo_name='vulnerable-app').delete()
    # print("\n✓ Cleaned up test data")
    pass


if __name__ == '__main__':
    try:
        run_verification_test()
        
        # Uncomment to clean up test data
        # cleanup_test_data()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        sys.exit(1)
