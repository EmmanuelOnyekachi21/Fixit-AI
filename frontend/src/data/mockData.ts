import type { Repository, Task, AnalysisSession, LogEntry } from '../types';

export const mockRepositories: Repository[] = [
  {
    id: 1,
    name: 'django/django',
    owner: 'django',
    url: 'https://github.com/django/django',
    status: 'completed',
    files_analyzed: 87,
    vulnerabilities_found: 23,
    prs_created: 19,
    started_at: '2026-01-29T10:30:00Z',
  },
  {
    id: 2,
    name: 'flask/flask',
    owner: 'flask',
    url: 'https://github.com/flask/flask',
    status: 'running',
    files_analyzed: 42,
    vulnerabilities_found: 8,
    prs_created: 5,
    started_at: '2026-01-29T14:15:00Z',
  },
  {
    id: 3,
    name: 'fastapi/fastapi',
    owner: 'fastapi',
    url: 'https://github.com/fastapi/fastapi',
    status: 'failed',
    files_analyzed: 15,
    vulnerabilities_found: 3,
    prs_created: 0,
    started_at: '2026-01-29T09:00:00Z',
  },
];

export const mockTasks: Task[] = [
  {
    id: 1,
    vulnerability_type: 'SQL Injection',
    severity: 'critical',
    file_path: 'app/auth/views.py',
    line_number: 42,
    description: 'User input directly concatenated into SQL query without parameterization',
    original_code: `def login(request):
    username = request.POST['username']
    password = request.POST['password']
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    cursor.execute(query)`,
    fix_code: `def login(request):
    username = request.POST['username']
    password = request.POST['password']
    query = "SELECT * FROM users WHERE username=%s AND password=%s"
    cursor.execute(query, (username, password))`,
    test_code: `def test_sql_injection_prevention():
    malicious_input = "admin' OR '1'='1"
    response = client.post('/login', {'username': malicious_input, 'password': 'test'})
    assert response.status_code == 401
    assert User.objects.filter(username=malicious_input).count() == 0`,
    test_status: 'passed',
    fix_status: 'pr_created',
    status: 'pr_created',
    pr_url: 'https://github.com/django/django/pull/1234',
  },
  {
    id: 2,
    vulnerability_type: 'XSS (Cross-Site Scripting)',
    severity: 'high',
    file_path: 'app/templates/profile.html',
    line_number: 15,
    description: 'User-generated content rendered without escaping, allowing script injection',
    original_code: `<div class="bio">
    {{ user.bio }}
</div>`,
    fix_code: `<div class="bio">
    {{ user.bio|escape }}
</div>`,
    test_code: `def test_xss_prevention():
    malicious_bio = '<script>alert("XSS")</script>'
    user.bio = malicious_bio
    user.save()
    response = client.get(f'/profile/{user.id}')
    assert '<script>' not in response.content.decode()
    assert '&lt;script&gt;' in response.content.decode()`,
    test_status: 'passed',
    fix_status: 'verified',
    status: 'completed',
  },
  {
    id: 3,
    vulnerability_type: 'Path Traversal',
    severity: 'high',
    file_path: 'app/files/views.py',
    line_number: 28,
    description: 'File path constructed from user input without validation',
    original_code: `def download_file(request, filename):
    file_path = os.path.join(MEDIA_ROOT, filename)
    return FileResponse(open(file_path, 'rb'))`,
    fix_code: `def download_file(request, filename):
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(MEDIA_ROOT, safe_filename)
    if not os.path.abspath(file_path).startswith(MEDIA_ROOT):
        raise PermissionDenied()
    return FileResponse(open(file_path, 'rb'))`,
    test_code: `def test_path_traversal_prevention():
    malicious_path = '../../../etc/passwd'
    response = client.get(f'/download/{malicious_path}')
    assert response.status_code == 403`,
    test_status: 'passed',
    fix_status: 'pr_created',
    status: 'pr_created',
    pr_url: 'https://github.com/django/django/pull/1235',
  },
  {
    id: 4,
    vulnerability_type: 'Insecure Deserialization',
    severity: 'critical',
    file_path: 'app/api/serializers.py',
    line_number: 67,
    description: 'Pickle deserialization of untrusted data can lead to remote code execution',
    original_code: `import pickle

def load_session(session_data):
    return pickle.loads(session_data)`,
    fix_code: `import json

def load_session(session_data):
    return json.loads(session_data)`,
    test_code: `def test_safe_deserialization():
    malicious_pickle = b"cos\\nsystem\\n(S'rm -rf /'\\ntR."
    with pytest.raises(json.JSONDecodeError):
        load_session(malicious_pickle)`,
    test_status: 'passed',
    fix_status: 'generated',
    status: 'completed',
  },
  {
    id: 5,
    vulnerability_type: 'Hardcoded Credentials',
    severity: 'medium',
    file_path: 'app/config/database.py',
    line_number: 12,
    description: 'Database credentials hardcoded in source code',
    original_code: `DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'admin123',
    'database': 'production'
}`,
    fix_code: `import os

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}`,
    test_code: `def test_no_hardcoded_credentials():
    import ast
    with open('app/config/database.py') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Str):
            assert 'password' not in node.s.lower()`,
    test_status: 'pending',
    fix_status: 'pending',
    status: 'pending',
  },
];

export const createMockSession = (repositoryId: number): AnalysisSession => ({
  session_id: `session-${repositoryId}-${Date.now()}`,
  repository_id: repositoryId,
  status: 'running',
  total_files: 150,
  files_analyzed: 0,
  vulnerabilities_found: 0,
  progress_percentage: 0,
  estimated_time_remaining: 300,
  current_file: 'app/__init__.py',
  logs: [],
});

export const vulnerabilityTypes = [
  'SQL Injection',
  'XSS (Cross-Site Scripting)',
  'Path Traversal',
  'Insecure Deserialization',
  'Hardcoded Credentials',
  'CSRF',
  'Command Injection',
  'XXE (XML External Entity)',
  'SSRF',
  'Broken Authentication',
];

export const generateMockLog = (fileNumber: number, totalFiles: number): LogEntry => {
  const types = ['success', 'info'] as const;
  const messages = [
    `✓ Analyzed ${getRandomFile()} - Found ${Math.floor(Math.random() * 3)} vulnerabilities`,
    `✓ Generated test for SQL injection in ${getRandomFile()}`,
    `✓ Fix verified - test passing for ${getRandomFile()}`,
    `✓ Created PR for ${getRandomFile()}`,
    `→ Scanning ${getRandomFile()}...`,
  ];
  
  return {
    id: fileNumber,
    timestamp: new Date().toISOString(),
    message: messages[Math.floor(Math.random() * messages.length)],
    type: types[Math.floor(Math.random() * types.length)],
  };
};

const getRandomFile = () => {
  const files = [
    'auth/login.py',
    'api/views.py',
    'models/user.py',
    'utils/helpers.py',
    'middleware/security.py',
    'templates/base.html',
    'forms/validation.py',
  ];
  return files[Math.floor(Math.random() * files.length)];
};
