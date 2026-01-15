import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.github_integration.services.github_client import GitHubClient

# Test with a known repository
client = GitHubClient()

print("Testing hybrid prioritization...")
print("=" * 60)

# Use a small public repo (or create your own test repo)
files = client.get_repo_files('django', 'django')

print(f"\nTotal files analyzed: {len(files)}")
print("\nPrioritized files:")
print("-" * 60)

for i, file_info in enumerate(files, 1):
    path = file_info['path']
    print(f"{i:2}. {path}")

print("\n" + "=" * 60)
print("✓ Test complete")

# Manual verification:
# - Are auth/login files near the top?
# - Are test files absent?
# - Is the list exactly 25 files (or fewer if repo is small)?
