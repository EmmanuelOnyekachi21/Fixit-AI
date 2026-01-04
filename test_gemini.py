import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.gemini_analyzer.services.gemini_client import GeminiClient

# Sample vulnerable code
test_code = """
def login(request):
    username = request.GET['username']
    password = request.GET['password']
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    return cursor.fetchone()
"""

client = GeminiClient()
results = client.analyze_code(test_code, "auth.py")

print("Found vulnerabilities:")
for vuln in results:
    print(f"- {vuln['type']} at line {vuln['line']}: {vuln['description']}")
