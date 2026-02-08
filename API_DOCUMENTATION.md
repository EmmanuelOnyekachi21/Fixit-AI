# API Documentation

## Overview

This document provides comprehensive documentation for the Security Vulnerability Analysis System API. The system analyzes GitHub repositories for security vulnerabilities, generates fixes, creates tests, and automatically creates pull requests.

**Base URL:** `http://localhost:8000/api/v1/`

**API Version:** v1

## Table of Contents

1. [Authentication](#authentication)
2. [Core APIs](#core-apis)
3. [Repository APIs](#repository-apis)
4. [Task APIs](#task-apis)
5. [Analysis Session APIs](#analysis-session-apis)
6. [WebSocket APIs](#websocket-apis)
7. [Data Models](#data-models)
8. [Error Handling](#error-handling)

---

## Authentication

### Validate Credentials

Validates Gemini API key and GitHub token before starting analysis.

**Endpoint:** `POST /api/v1/credentials/validate/`

**Request Body:**
```json
{
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```

**Response (Success - 200 OK):**
```json
{
  "valid": true,
  "message": "Credentials validated successfully"
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "valid": false,
  "error": "Gemini: Invalid Gemini API key; GitHub: Invalid GitHub token"
}
```

**Use Case:** Call this endpoint before starting repository analysis to ensure credentials are valid.

---

## Core APIs

### Setup GitHub Authentication

Configure GitHub authentication for the system.

**Endpoint:** `POST /api/v1/auth/github/`

**Request Body:**
```json
{
  "token": "ghp_..."
}
```

**Response (Success - 200 OK):**
```json
{
  "message": "Github authentication set up successfully",
  "username": "octocat"
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "error": "Token is required"
}
```

---

## Repository APIs

### Create Repository & Start Analysis

Creates a repository record and starts vulnerability analysis.

**Endpoint:** `POST /api/v1/repositories/`

**Request Body:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "create_prs": true,
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```

**Parameters:**
- `repo_url` (required): Full GitHub repository URL
- `create_prs` (optional, default: false): Automatically create PRs for verified fixes
- `gemini_key` (optional): Gemini API key for this analysis
- `github_token` (optional): GitHub token for this analysis

**Response (Success - 202 Accepted):**
```json
{
  "repository": {
    "id": 1,
    "owner": "owner",
    "repo_name": "repo",
    "repo_url": "https://github.com/owner/repo",
    "status": "analyzing",
    "created_at": "2026-02-08T10:30:00Z"
  },
  "task_id": "abc123-celery-task-id",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Analysis started in background. Use session_id to check status"
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "repo_url": ["This field is required."]
}
```

**Use Case:** Start analyzing a repository for security vulnerabilities. The analysis runs asynchronously in the background.

---

### List Repository Tasks

Retrieves all vulnerability tasks for a specific repository.

**Endpoint:** `GET /api/v1/repositories/{repository_id}/tasks/`

**Response (Success - 200 OK):**
```json
{
  "repository_id": 1,
  "total_task": 5,
  "tasks": [
    {
      "id": 1,
      "title": "SQL Injection in user query",
      "description": "User input is directly concatenated into SQL query",
      "vulnerability_type": "sql_injection",
      "file_path": "src/database.py",
      "line_number": 45,
      "severity": "critical",
      "status": "completed",
      "test_status": "passed",
      "fix_status": "verified",
      "original_code": "query = \"SELECT * FROM users WHERE id = \" + user_id",
      "fix_code": "query = \"SELECT * FROM users WHERE id = %s\"\ncursor.execute(query, (user_id,))",
      "fix_explanation": "Used parameterized query to prevent SQL injection",
      "test_code": "def test_sql_injection():\n    ...",
      "pr_url": "https://github.com/owner/repo/pull/123",
      "created_at": "2026-02-08T10:35:00Z"
    }
  ]
}
```

**Response (Error - 404 Not Found):**
```json
{
  "error": "Repository not found"
}
```

---

### Create Pull Requests for Repository

Creates pull requests for all verified fixes in a repository.

**Endpoint:** `POST /api/v1/repositories/{repository_id}/pull-requests/`

**Response (Success - 200 OK):**
```json
{
  "message": "Created 3 pull requests",
  "prs": [
    {
      "task_id": 1,
      "pr_url": "https://github.com/owner/repo/pull/123"
    },
    {
      "task_id": 2,
      "pr_url": "https://github.com/owner/repo/pull/124"
    }
  ]
}
```

**Response (No PRs to Create - 200 OK):**
```json
{
  "message": "No verified fixes to create PRs for",
  "prs": []
}
```

**Use Case:** Batch create PRs for all verified fixes after manual review.

---

## Task APIs

### Get Task Detail

Retrieves detailed information about a specific task.

**Endpoint:** `GET /api/v1/tasks/{task_id}/`

**Response (Success - 200 OK):**
```json
{
  "id": 1,
  "title": "SQL Injection in user query",
  "vulnerability_type": "sql_injection",
  "description": "User input is directly concatenated into SQL query",
  "file_path": "src/database.py",
  "line_number": 45,
  "severity": "critical",
  "original_code": "query = \"SELECT * FROM users WHERE id = \" + user_id",
  "fix_code": "query = \"SELECT * FROM users WHERE id = %s\"\ncursor.execute(query, (user_id,))",
  "fix_explanation": "Used parameterized query to prevent SQL injection",
  "test_code": "def test_sql_injection():\n    ...",
  "status": "completed",
  "test_status": "passed",
  "fix_status": "verified",
  "pr_url": "https://github.com/owner/repo/pull/123",
  "created_at": "2026-02-08T10:35:00Z",
  "repository": {
    "id": 1,
    "name": "owner/repo",
    "url": "https://github.com/owner/repo"
  }
}
```

**Response (Error - 404 Not Found):**
```json
{
  "error": "Task not found"
}
```

---

### Get Celery Task Status

Checks the status of a background Celery task.

**Endpoint:** `GET /api/v1/tasks/{celery_task_id}/status/`

**Response (Running):**
```json
{
  "task_id": "abc123-celery-task-id",
  "status": "PENDING"
}
```

**Response (Success):**
```json
{
  "task_id": "abc123-celery-task-id",
  "status": "SUCCESS",
  "result": {
    "message": "Analysis completed",
    "tasks_created": 5
  }
}
```

**Response (Failure):**
```json
{
  "task_id": "abc123-celery-task-id",
  "status": "FAILURE",
  "error": "Connection timeout"
}
```

---

### Verify and Fix Vulnerability

Runs the complete verification workflow: generate test, verify vulnerability, generate fix, verify fix.

**Endpoint:** `POST /api/v1/tasks/{task_id}/verify-and-fix/`

**Request Body:**
```json
{
  "create_pr": true
}
```

**Response (Success - 200 OK):**
```json
{
  "success": true,
  "task_id": 1,
  "status": "completed",
  "test_status": "passed",
  "fix_status": "verified",
  "message": "Verification completed"
}
```

**Response (Error - 404 Not Found):**
```json
{
  "error": "Task not found"
}
```

**Use Case:** Manually trigger verification for a specific task.

---

### Generate Fix for Task

Manually triggers fix generation for a single task (async).

**Endpoint:** `POST /api/v1/tasks/{task_id}/generate-fix/`

**Request Body:**
```json
{
  "create_pr": false,
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```

**Response (Success - 202 Accepted):**
```json
{
  "task_id": 1,
  "status": "processing",
  "celery_task_id": "xyz789-celery-task-id",
  "message": "Fix generation started"
}
```

**Response (Error - 404 Not Found):**
```json
{
  "error": "Task not found"
}
```

**Use Case:** Retry fix generation for a failed task or regenerate with different parameters.

---

### Create Pull Request for Task

Creates a pull request for a task that already has a verified fix.

**Endpoint:** `POST /api/v1/tasks/{task_id}/create-pr/`

**Request Body:**
```json
{
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```

**Response (Success - 201 Created):**
```json
{
  "task_id": 1,
  "pr_url": "https://github.com/owner/repo/pull/123",
  "message": "PR created successfully"
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "error": "Task does not have a fix yet. Run verification first."
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "error": "PR already exists for this task",
  "pr_url": "https://github.com/owner/repo/pull/123"
}
```

**Use Case:** Create PR after manual review of the fix, without re-running verification.

---

## Analysis Session APIs

### Get Session Status

Retrieves real-time progress and status of an analysis session.

**Endpoint:** `GET /api/v1/sessions/{session_id}/status/`

**Response (Success - 200 OK):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "repository": {
    "id": 1,
    "name": "repo",
    "url": "https://github.com/owner/repo"
  },
  "status": "running",
  "progress": {
    "total_files": 100,
    "files_analyzed": 45,
    "files_failed": 2,
    "percentage": 45.0
  },
  "results": {
    "vulnerabilities_found": 12,
    "tasks_created": 12,
    "prs_created": 0
  },
  "timestamps": {
    "started_at": "2026-02-08T10:30:00Z",
    "completed_at": null,
    "last_checkpoint_at": "2026-02-08T10:45:00Z"
  },
  "error_message": "",
  "retry_count": 0,
  "estimated_time_remaining_seconds": 1200,
  "estimated_time_remaining_minutes": 20.0
}
```

**Response (Error - 404 Not Found):**
```json
{
  "error": "Session not found."
}
```

**Use Case:** Poll this endpoint to track analysis progress in real-time.

---

### Resume Session

Resumes a failed or paused analysis session.

**Endpoint:** `POST /api/v1/sessions/{session_id}/resume/`

**Response (Success - 200 OK):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "new-celery-task-id",
  "message": "Session resumed successfully.",
  "progress": {
    "files_analyzed": 45,
    "total_files": 100,
    "percentage": 45.0
  }
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "error": "Cannot resume session with status 'completed'",
  "current_status": "completed",
  "message": "Only failed or paused sessions can be resumed."
}
```

**Use Case:** Recover from crashes or network failures by resuming from the last checkpoint.

---

### Process All Tasks in Session

Automatically processes all pending tasks in a session (generates fixes and optionally creates PRs).

**Endpoint:** `POST /api/v1/sessions/{session_id}/process-all/`

**Request Body:**
```json
{
  "create_pr": true,
  "gemini_key": "AIzaSy...",
  "github_token": "ghp_..."
}
```

**Response (Success - 202 Accepted):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_tasks": 12,
  "status": "processing",
  "celery_task_id": "batch-task-id",
  "message": "Processing 12 tasks"
}
```

**Response (Error - 404 Not Found):**
```json
{
  "error": "Session not found"
}
```

**Use Case:** Batch process all detected vulnerabilities after initial analysis completes.

---

### List All Sessions

Retrieves a list of all analysis sessions with summary statistics.

**Endpoint:** `GET /api/v1/sessions/?limit=10`

**Query Parameters:**
- `limit` (optional, default: 10): Number of recent sessions to return

**Response (Success - 200 OK):**
```json
{
  "sessions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "repository_name": "owner/repo",
      "status": "completed",
      "files_analyzed": 100,
      "vulnerabilities_found": 12,
      "prs_created": 8,
      "started_at": "2026-02-08T10:30:00Z"
    }
  ],
  "summary": {
    "total_scans": 25,
    "total_files": 2500,
    "total_vulnerabilities": 150,
    "total_prs": 120
  }
}
```

**Use Case:** Display dashboard with analysis history and overall statistics.

---

## WebSocket APIs

### Real-Time Session Progress

Connects to a WebSocket for real-time updates on analysis session progress.

**WebSocket URL:** `ws://localhost:8000/ws/sessions/{session_id}/`

**Connection Flow:**

1. **Client connects** to WebSocket
2. **Server sends initial status** immediately after connection
3. **Server broadcasts updates** as analysis progresses
4. **Client can send ping** to keep connection alive

**Message Types:**

#### Initial Status (Server → Client)
```json
{
  "type": "session_status",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "repository": {
      "id": 1,
      "name": "repo",
      "url": "https://github.com/owner/repo"
    },
    "status": "running",
    "progress": {
      "total_files": 100,
      "files_analyzed": 0,
      "files_failed": 0,
      "percentage": 0.0
    },
    "results": {
      "vulnerabilities_found": 0,
      "tasks_created": 0,
      "tests_created": 0,
      "fixes_generated": 0,
      "prs_created": 0
    },
    "timestamps": {
      "started_at": "2026-02-08T10:30:00Z",
      "completed_at": null,
      "last_checkpoint_at": null
    },
    "logs": [],
    "estimated_time_remaining_seconds": null
  }
}
```

#### Progress Update (Server → Client)
```json
{
  "type": "session_update",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "progress": {
      "files_analyzed": 45,
      "percentage": 45.0
    },
    "results": {
      "vulnerabilities_found": 12
    }
  }
}
```

#### New Log Entry (Server → Client)
```json
{
  "type": "new_log",
  "data": {
    "timestamp": "2026-02-08T10:35:00Z",
    "level": "info",
    "message": "Analyzing file: src/database.py",
    "file_path": "src/database.py"
  }
}
```

#### Analysis Complete (Server → Client)
```json
{
  "type": "analysis_complete",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "total_vulnerabilities": 12,
    "total_prs": 8
  }
}
```

#### Ping/Pong (Client ↔ Server)

**Client sends:**
```json
{
  "type": "ping"
}
```

**Server responds:**
```json
{
  "type": "pong"
}
```

#### Error (Server → Client)
```json
{
  "type": "error",
  "message": "Session not found"
}
```

**Use Case:** Display real-time progress bars, logs, and status updates in the UI without polling.

---

## Data Models

### Repository

```typescript
{
  id: number;
  owner: string;
  repo_name: string;
  repo_url: string;
  status: 'idle' | 'analyzing' | 'completed' | 'error' | 'paused';
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  last_analyzed_at: string | null; // ISO 8601
  analysis_progress: string | null;
}
```

### Task

```typescript
{
  id: number;
  repository: number; // Repository ID
  title: string;
  description: string;
  vulnerability_type: 'xss' | 'sql_injection' | 'csrf' | 'hardcoded_secret' | 
                      'command_injection' | 'path_traversal' | 
                      'authentication_bypass' | 'insecure_deserialization';
  file_path: string;
  line_number: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'running' | 'validating' | 'completed' | 
          'failed' | 'abandoned' | 'false_positive' | 'pr_created';
  test_code: string;
  test_status: 'pending' | 'generated' | 'failed' | 'passed' | 'error';
  fix_code: string;
  fix_status: 'pending' | 'generated' | 'applied' | 'verified' | 'failed';
  fix_explanation: string;
  original_code: string;
  pr_url: string | null;
  retry_count: number;
  validation_message: string;
  verified_at: string | null; // ISO 8601
  created_at: string; // ISO 8601
  started_at: string | null; // ISO 8601
  completed_at: string | null; // ISO 8601
}
```

### Analysis Session

```typescript
{
  session_id: string; // UUID
  repository: number; // Repository ID
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';
  total_files: number;
  files_analyzed: number;
  files_failed: number;
  vulnerabilities_found: number;
  task_created: number;
  tests_created: number;
  fixes_generated: number;
  prs_created: number;
  started_at: string | null; // ISO 8601
  completed_at: string | null; // ISO 8601
  last_checkpoint_at: string | null; // ISO 8601
  error_message: string;
  retry_count: number;
  create_prs: boolean;
  max_files: number;
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for async processing
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "error": "Detailed error message"
}
```

### Field Validation Errors

```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Another error message"]
}
```

---

## Workflow Examples

### Complete Analysis Workflow

1. **Validate credentials**
   ```
   POST /api/v1/credentials/validate/
   ```

2. **Start repository analysis**
   ```
   POST /api/v1/repositories/
   ```
   → Returns `session_id`

3. **Monitor progress via WebSocket**
   ```
   ws://localhost:8000/ws/sessions/{session_id}/
   ```

4. **Or poll session status**
   ```
   GET /api/v1/sessions/{session_id}/status/
   ```

5. **Process all detected vulnerabilities**
   ```
   POST /api/v1/sessions/{session_id}/process-all/
   ```

6. **View results**
   ```
   GET /api/v1/repositories/{repository_id}/tasks/
   ```

### Manual Task Processing

1. **Get task details**
   ```
   GET /api/v1/tasks/{task_id}/
   ```

2. **Generate fix**
   ```
   POST /api/v1/tasks/{task_id}/generate-fix/
   ```

3. **Create PR after review**
   ```
   POST /api/v1/tasks/{task_id}/create-pr/
   ```

---

## Rate Limiting

Currently, there are no rate limits enforced. For production deployment, consider implementing rate limiting based on:
- IP address
- API key
- User account

---

## Support

For issues or questions about the API, please refer to the main README.md or contact the development team.

**Last Updated:** February 8, 2026
