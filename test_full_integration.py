"""
Test full integration: Prioritization + Vulnerability Analysis

This tests the complete flow:
1. Fetch repo files (with prioritization)
2. Analyze prioritized files for vulnerabilities
3. Create Task objects
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.analyzer_service import AnalyzerService
from apps.repository.models import Repository
from apps.task.models import Task


def test_full_integration():
    """Test the complete analysis workflow."""
    
    print("=" * 60)
    print("FULL INTEGRATION TEST")
    print("=" * 60)
    
    # Create or get test repository
    repo, created = Repository.objects.get_or_create(
        owner='django',
        repo_name='django',
        defaults={
            'repo_url': 'https://github.com/django/django',
            'status': 'idle'
        }
    )
    
    if created:
        print(f"✓ Created new repository: {repo}")
    else:
        print(f"✓ Using existing repository: {repo}")
        # Clear old tasks
        Task.objects.filter(repository=repo).delete()
        print("  Cleared old tasks")
    
    print()
    
    # Run analysis
    print("Starting full analysis...")
    print("-" * 60)
    
    analyzer = AnalyzerService()
    
    try:
        tasks = analyzer.analyze_repository(repo.id)
        
        print()
        print("=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Total vulnerabilities found: {len(tasks)}")
        print()
        
        if tasks:
            print("Sample vulnerabilities:")
            print("-" * 60)
            for i, task in enumerate(tasks[:5], 1):
                print(f"{i}. {task.title}")
                print(f"   File: {task.file_path}")
                print(f"   Severity: {task.severity}")
                print(f"   Line: {task.line_number}")
                print()
            
            if len(tasks) > 5:
                print(f"... and {len(tasks) - 5} more vulnerabilities")
        else:
            print("No vulnerabilities found (or Gemini rate limit hit)")
        
        print()
        print("=" * 60)
        print("REPOSITORY STATUS")
        print("=" * 60)
        repo.refresh_from_db()
        print(f"Status: {repo.status}")
        print(f"Last analyzed: {repo.last_analyzed_at}")
        print(f"Progress: {repo.analysis_progress}")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_full_integration()
