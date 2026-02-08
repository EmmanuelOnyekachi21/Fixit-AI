# API Endpoint Map

Visual map of all API endpoints in the Fixit system.

```
/api/v1/
│
├── credentials/
│   └── validate/                    [POST]   Validate Gemini & GitHub credentials
│
├── auth/
│   └── github/                      [POST]   Setup GitHub authentication
│
├── repositories/
│   ├── /                            [POST]   Create repository & start analysis
│   └── {repository_id}/
│       ├── tasks/                   [GET]    List all tasks for repository
│       └── pull-requests/           [POST]   Create PRs for all verified fixes
│
├── tasks/
│   └── {task_id}/
│       ├── /                        [GET]    Get detailed task information
│       ├── details/                 [GET]    Get task details (legacy)
│       ├── verify-and-fix/          [POST]   Run complete verification workflow
│       ├── generate-fix/            [POST]   Generate fix (async)
│       └── create-pr/               [POST]   Create PR for verified fix
│   └── {celery_task_id}/
│       └── status/                  [GET]    Check Celery task status
│
└── sessions/
    ├── /                            [GET]    List all sessions with summary
    └── {session_id}/
        ├── status/                  [GET]    Get real-time session status
        ├── resume/                  [POST]   Resume failed/paused session
        └── process-all/             [POST]   Process all tasks in session

WebSocket:
ws://host/ws/sessions/{session_id}/           Real-time session updates
```

## Endpoint Details

### Core APIs

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/api/v1/credentials/validate/` | Validate API credentials | No |
| POST | `/api/v1/auth/github/` | Setup GitHub auth | No |

### Repository APIs

| Method | Endpoint | Purpose | Async |
|--------|----------|---------|-------|
| POST | `/api/v1/repositories/` | Create repo & start analysis | Yes |
| GET | `/api/v1/repositories/{id}/tasks/` | List repository tasks | No |
| POST | `/api/v1/repositories/{id}/pull-requests/` | Batch create PRs | No |

### Task APIs

| Method | Endpoint | Purpose | Async |
|--------|----------|---------|-------|
| GET | `/api/v1/tasks/{id}/` | Get task details | No |
| GET | `/api/v1/tasks/{id}/status/` | Check Celery task status | No |
| POST | `/api/v1/tasks/{id}/verify-and-fix/` | Run verification workflow | No |
| POST | `/api/v1/tasks/{id}/generate-fix/` | Generate fix | Yes |
| POST | `/api/v1/tasks/{id}/create-pr/` | Create PR | No |

### Session APIs

| Method | Endpoint | Purpose | Async |
|--------|----------|---------|-------|
| GET | `/api/v1/sessions/` | List all sessions | No |
| GET | `/api/v1/sessions/{id}/status/` | Get session status | No |
| POST | `/api/v1/sessions/{id}/resume/` | Resume session | Yes |
| POST | `/api/v1/sessions/{id}/process-all/` | Process all tasks | Yes |

### WebSocket APIs

| Protocol | Endpoint | Purpose | Bidirectional |
|----------|----------|---------|---------------|
| WS | `ws://host/ws/sessions/{id}/` | Real-time updates | Yes |

## API Flow Diagrams

### 1. Repository Analysis Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    REPOSITORY ANALYSIS                      │
└─────────────────────────────────────────────────────────────┘

1. POST /api/v1/credentials/validate/
   └─> Validate credentials
       └─> ✓ Valid

2. POST /api/v1/repositories/
   └─> Create repository
       └─> Returns: session_id, task_id
           └─> Background: Celery task starts

3. WS ws://host/ws/sessions/{session_id}/
   └─> Connect WebSocket
       └─> Receive real-time updates
           ├─> session_status (initial)
           ├─> session_update (progress)
           ├─> new_log (logs)
           └─> analysis_complete (done)

4. GET /api/v1/sessions/{session_id}/status/
   └─> Poll status (alternative to WebSocket)
       └─> Returns: progress, results, timestamps

5. POST /api/v1/sessions/{session_id}/process-all/
   └─> Process all detected vulnerabilities
       └─> Returns: celery_task_id
           └─> Background: Generate fixes & create PRs
```

### 2. Manual Task Processing Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   MANUAL TASK PROCESSING                    │
└─────────────────────────────────────────────────────────────┘

1. GET /api/v1/repositories/{id}/tasks/
   └─> List all tasks
       └─> Select task_id

2. GET /api/v1/tasks/{task_id}/
   └─> Get task details
       └─> Review vulnerability

3. POST /api/v1/tasks/{task_id}/generate-fix/
   └─> Generate fix
       └─> Returns: celery_task_id
           └─> Background: AI generates fix

4. GET /api/v1/tasks/{celery_task_id}/status/
   └─> Check fix generation status
       └─> Wait for SUCCESS

5. GET /api/v1/tasks/{task_id}/
   └─> Review generated fix
       └─> Verify fix_code looks good

6. POST /api/v1/tasks/{task_id}/create-pr/
   └─> Create pull request
       └─> Returns: pr_url
```

### 3. Session Recovery Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     SESSION RECOVERY                        │
└─────────────────────────────────────────────────────────────┘

1. GET /api/v1/sessions/
   └─> List all sessions
       └─> Find failed session

2. GET /api/v1/sessions/{session_id}/status/
   └─> Check session status
       └─> status: "failed"
           └─> See: files_analyzed, error_message

3. POST /api/v1/sessions/{session_id}/resume/
   └─> Resume from checkpoint
       └─> Returns: new task_id
           └─> Background: Continues from last checkpoint

4. WS ws://host/ws/sessions/{session_id}/
   └─> Monitor resumed session
       └─> Receive updates from checkpoint
```

## Request/Response Patterns

### Synchronous Endpoints
```
Request  ──────────> Server
                      │
                      ├─> Process
                      │
Response <────────── Server
```
**Examples:** GET endpoints, credential validation

### Asynchronous Endpoints
```
Request  ──────────> Server
                      │
                      ├─> Enqueue Celery Task
                      │
Response <────────── Server (202 Accepted + task_id)
                      │
                      └─> Celery Worker
                           │
                           ├─> Process in background
                           │
                           └─> Update database
```
**Examples:** Repository analysis, fix generation, batch processing

### WebSocket Communication
```
Client ─────connect────> Server
       <────status─────
       <────update─────
       <────update─────
       ─────ping──────>
       <────pong───────
       <────complete───
```
**Use Case:** Real-time progress monitoring

## HTTP Methods Usage

| Method | Usage | Idempotent | Safe |
|--------|-------|------------|------|
| GET | Retrieve data | Yes | Yes |
| POST | Create/trigger action | No | No |

**Note:** This API follows REST conventions where:
- GET = Read operations (safe, no side effects)
- POST = Write operations (creates resources, triggers actions)

## Response Codes by Endpoint Type

### Read Operations (GET)
- `200 OK` - Success
- `404 Not Found` - Resource doesn't exist

### Write Operations (POST)
- `200 OK` - Synchronous success
- `201 Created` - Resource created
- `202 Accepted` - Async task started
- `400 Bad Request` - Invalid input
- `404 Not Found` - Parent resource doesn't exist

## API Versioning

Current version: **v1**

All endpoints are prefixed with `/api/v1/`

Future versions will use `/api/v2/`, `/api/v3/`, etc.

## Related Documentation

- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Complete API reference
- [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) - Quick command reference
- [README.md](./README.md) - Project overview
