# API Quick Reference

Quick reference guide for the most commonly used API endpoints.

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication

### Validate Credentials
```bash
POST /api/v1/credentials/validate/
```
```json
{
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```

## Repository Analysis

### Start Analysis
```bash
POST /api/v1/repositories/
```
```json
{
  "repo_url": "https://github.com/owner/repo",
  "create_prs": true,
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```
**Returns:** `session_id` for tracking

### Get Repository Tasks
```bash
GET /api/v1/repositories/{repository_id}/tasks/
```

### Create PRs for Repository
```bash
POST /api/v1/repositories/{repository_id}/pull-requests/
```

## Session Management

### Check Session Status
```bash
GET /api/v1/sessions/{session_id}/status/
```

### Resume Failed Session
```bash
POST /api/v1/sessions/{session_id}/resume/
```

### Process All Tasks
```bash
POST /api/v1/sessions/{session_id}/process-all/
```
```json
{
  "create_pr": true,
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```

### List All Sessions
```bash
GET /api/v1/sessions/?limit=10
```

## Task Management

### Get Task Details
```bash
GET /api/v1/tasks/{task_id}/
```

### Generate Fix for Task
```bash
POST /api/v1/tasks/{task_id}/generate-fix/
```
```json
{
  "create_pr": false,
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```

### Create PR for Task
```bash
POST /api/v1/tasks/{task_id}/create-pr/
```
```json
{
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```

### Check Celery Task Status
```bash
GET /api/v1/tasks/{celery_task_id}/status/
```

## WebSocket

### Connect to Session Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/sessions/{session_id}/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.data);
};

// Keep alive
setInterval(() => {
  ws.send(JSON.stringify({ type: 'ping' }));
}, 30000);
```

## Common Workflows

### 1. Complete Analysis Flow
```bash
# 1. Validate credentials
curl -X POST http://localhost:8000/api/v1/credentials/validate/ \
  -H "Content-Type: application/json" \
  -d '{"gemini_key":"AIzaSy...","github_token":"ghp_..."}'

# 2. Start analysis
curl -X POST http://localhost:8000/api/v1/repositories/ \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/owner/repo","create_prs":true}'

# 3. Monitor progress (use session_id from step 2)
curl http://localhost:8000/api/v1/sessions/{session_id}/status/

# 4. Process all tasks
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/process-all/ \
  -H "Content-Type: application/json" \
  -d '{"create_pr":true}'

# 5. View results
curl http://localhost:8000/api/v1/repositories/{repository_id}/tasks/
```

### 2. Manual Task Processing
```bash
# 1. Get task details
curl http://localhost:8000/api/v1/tasks/{task_id}/

# 2. Generate fix
curl -X POST http://localhost:8000/api/v1/tasks/{task_id}/generate-fix/ \
  -H "Content-Type: application/json" \
  -d '{"create_pr":false}'

# 3. Create PR after review
curl -X POST http://localhost:8000/api/v1/tasks/{task_id}/create-pr/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async processing) |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

## Data Models

### Task Status Values
- `pending` - Not yet processed
- `running` - Currently processing
- `validating` - Running verification
- `completed` - Successfully completed
- `failed` - Processing failed
- `pr_created` - PR created

### Vulnerability Types
- `xss` - Cross-Site Scripting
- `sql_injection` - SQL Injection
- `csrf` - CSRF
- `hardcoded_secret` - Hardcoded Secret
- `command_injection` - Command Injection
- `path_traversal` - Path Traversal
- `authentication_bypass` - Authentication Bypass
- `insecure_deserialization` - Insecure Deserialization

### Severity Levels
- `low`
- `medium`
- `high`
- `critical`

## Tips

1. **Always validate credentials first** before starting analysis
2. **Use WebSocket** for real-time updates instead of polling
3. **Store session_id** to resume interrupted analyses
4. **Check task status** before creating PRs
5. **Use batch operations** (`process-all`) for efficiency

For complete documentation, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
