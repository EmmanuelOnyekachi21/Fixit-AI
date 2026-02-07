<div align="center">

# 🛠️ Fixit: The Autonomous Security Agent

**State-Aware AI Agent for Continuous Security Maintenance**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![Gemini](https://img.shields.io/badge/AI-Gemini%203-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-010101?style=for-the-badge&logo=socket.io&logoColor=white)](https://channels.readthedocs.io/)

---

<p align="center">
  <em>Built for the Gemini API Developer Competition</em><br>
  <b>Fixit</b> autonomously scans codebases, verifies vulnerabilities, generates fixes, and creates pull requests—all without human intervention.
</p>

[🎥 Demo Video](#) • [📚 Documentation](#documentation) • [🚀 Quick Start](#-quick-start)

</div>

---

## 📖 Table of Contents

- [About](#-about)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [API Documentation](#-api-documentation)
- [Real-Time Features](#-real-time-features)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📖 About

**Fixit** is an autonomous AI-powered security agent that revolutionizes how development teams handle security vulnerabilities. Unlike traditional static analysis tools that simply report issues, Fixit takes action:

🔍 **Scans** your codebase for security vulnerabilities  
🧪 **Verifies** each vulnerability with automated tests  
🛠️ **Generates** production-ready fixes  
✅ **Validates** fixes work correctly  
🚀 **Creates** pull requests automatically  
📊 **Tracks** everything with real-time progress updates

### Why Fixit?

**The Problem:**
- Security scanners generate false positives
- Developers spend hours manually fixing vulnerabilities
- Fixes often break existing functionality
- No automated verification that fixes actually work

**The Solution:**
Fixit implements a **verify-first workflow** that ensures every fix is:
1. ✅ Proven to address a real vulnerability (not a false positive)
2. ✅ Tested to work correctly
3. ✅ Ready for production deployment

---

## 🚀 Key Features

### 1. 🔍 Intelligent Vulnerability Detection
- **Deep Code Analysis**: Uses Gemini 3 to analyze entire codebases
- **Context-Aware**: Understands code relationships and data flow
- **Multi-Language Support**: Python, JavaScript, and more
- **Common Vulnerabilities**: SQL Injection, XSS, Path Traversal, Insecure Deserialization, etc.

### 2. 🧪 Verify-First Protocol (Zero False Positives)
Fixit doesn't just report vulnerabilities—it **proves** they exist:

```
┌─────────────────────────────────────────────────────────┐
│  VERIFY-FIRST WORKFLOW                                  │
├─────────────────────────────────────────────────────────┤
│  1. Generate Test → Prove vulnerability exists          │
│  2. Run Test → Should FAIL (confirms vulnerability)     │
│  3. Generate Fix → Create secure code                   │
│  4. Run Test Again → Should PASS (confirms fix works)   │
│  5. Create PR → Only if verified                        │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Eliminates false positives automatically
- ✅ Ensures fixes actually work
- ✅ Provides test coverage for every fix
- ✅ Builds confidence in automated changes

### 3. 🔄 Self-Correcting with Retry Logic
If a fix doesn't work:
1. Fixit analyzes why it failed
2. Generates an improved fix
3. Retries verification
4. Marks as false positive if still failing

*This mimics how senior engineers debug and iterate.*

### 4. 🎯 In-Memory Testing (No Cloning Required)
**Innovation**: Tests run without cloning repositories!

- Original code stored during analysis
- Tests execute in isolated temporary directories
- No disk space wasted
- Faster execution
- Better security isolation

### 5. 📊 Real-Time Progress Tracking
**WebSocket-powered live updates:**
- See files being analyzed in real-time
- Watch vulnerabilities being discovered
- Monitor fix generation progress
- Track PR creation status

**Technologies:**
- Django Channels for WebSocket support
- Redis for message broadcasting
- React frontend with live updates

### 6. 🤖 Autonomous PR Creation
**Fully automated GitHub integration:**
- Creates feature branches automatically
- Commits fixes with descriptive messages
- Generates comprehensive PR descriptions
- Includes vulnerability details and test code
- Links back to analysis session

### 7. 💾 Persistent State Management
**Never lose progress:**
- Every step saved to PostgreSQL
- Resume from any interruption
- Checkpoint system for long analyses
- Full audit trail of all actions

### 8. ⚡ Asynchronous Task Processing
**Powered by Celery:**
- Background processing for long-running tasks
- Parallel vulnerability analysis
- Queue management for batch operations
- Retry logic for failed tasks

---

## 🏗️ Architecture

```mermaid
graph TD
    A[🧠 Brain: Gemini 3 API] -->|Reasoning| B(Orchestrator: Django);
    B -->|State & Queue| C[(PostgreSQL)];
    B -->|Executes Code| D[📦 Isolated Testing];
    B -->|Creates PRs| E[Action Layer: GitHub];
    D -->|Test Results| B;
    E -->|Updates| F[User Repo];
```

- **Brain**: Powered by **Gemini 3 API** for deep reasoning and long-context codebase analysis.
- **Orchestrator (Django)**: Manages the state machine, task queuing, and persistent memory.
- **Isolated Testing**: In-memory temporary environments where Fixit safely executes and tests code.
- **Action Layer**: GitHub Integration for automated Pull Request (PR) creation.

### 🔑 Key Implementation Details

**In-Memory Testing (No Cloning Required)**
- Original code is stored in the database during analysis
- Tests run in isolated temporary directories
- Fixed code and test code are written to temp files
- Tests execute in isolation, then cleanup automatically
- No need to clone entire repositories to disk

**AI Coordination**
- Test generator sees original code to write accurate imports
- Fix generator sees the same code to create proper fixes
- Both coordinate through shared context for consistency

---

## 📅 Development Roadmap

- [x] **Week 1: Foundation** - Persistent State Machine & Repo Ingestion.
- [x] **Week 2: The Auditor** - Deep scanning and Vulnerability Identification.
- [x] **Week 3: The Prover** - Automated Unit Test generation for proof-of-concept.
- [x] **Week 4: The Fixer** - Self-correcting patches and validation loops.
- [ ] **Week 5: The Marathon** - 6-hour autonomous stress tests on large-scale repositories.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Framework** | Django 5.0 (REST Framework) |
| **AI Model** | Gemini 3 API |
| **Database** | PostgreSQL |
| **Testing** | pytest (Isolated Environments) |
| **Version Control** | GitHub API Integration |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL
- Git
- Gemini API Key
- GitHub Bot Token

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fixit.git
cd fixit
```

2. **Set up virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_BOT_TOKEN=your_github_token_here
```

5. **Set up database**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run the server**
```bash
python manage.py runserver
```

### Usage

1. **Add a repository**
```bash
curl -X POST http://localhost:8000/api/create/repository/ \
-H "Content-Type: application/json" \
-d '{"repo_url": "https://github.com/username/repo"}'
```

2. **Verify and fix vulnerabilities**
```bash
curl -X POST http://localhost:8000/api/tasks/{task_id}/verify-and-fix/ \
-H "Content-Type: application/json" \
-d '{"create_pr": true}'
```

3. **Monitor progress**
Visit `http://localhost:8000/admin` to view tasks, logs, and PRs.

---

<div align="center">
  <sub>Built with ❤️ by the Fixit Team</sub>
</div>