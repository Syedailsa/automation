# Development Setup Guide

This guide walks you through setting up the NotebookLM Portal for local development.

## Prerequisites

### Required Software

| Software | Version | Install |
|----------|---------|---------|
| Python | 3.12+ | [python.org](https://python.org/downloads) |
| Docker | 24+ | [docker.com](https://docs.docker.com/get-docker) |
| Docker Compose | v2+ | Included with Docker Desktop |
| Git | 2.40+ | [git-scm.com](https://git-scm.com/downloads) |

### Verify Prerequisites

```bash
python3 --version    # Should show 3.12+
docker --version     # Should show 24+
docker compose version
git --version
```

## Step 1: Clone the Repository

```bash
git clone https://github.com/Syedailsa/automation.git
cd automation
git checkout phase-1
```

## Step 2: Run Setup Script

```bash
make setup
```

This will:
1. Create Python virtual environment
2. Install backend dependencies
3. Copy `.env.example` to `.env`
4. Start PostgreSQL via Docker

## Step 3: Configure Environment

Edit `backend/.env` with your settings:

```bash
# Database (defaults work with Docker)
DATABASE_URL=postgresql+asyncpg://notebooklm:notebooklm_secret@localhost:5432/notebooklm_portal

# JWT Secret (generate a new one for production)
JWT_SECRET_KEY=your-random-secret-key-here

# Google OAuth (required for authentication)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:80/auth/callback

# LLM API Keys (for AI agent features)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# CORS (frontend URL)
CORS_ORIGINS=http://localhost:80
```

### Getting Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Go to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth 2.0 Client ID**
5. Set application type to **Web application**
6. Add authorized redirect URI: `http://localhost:80/auth/callback`
7. Copy Client ID and Client Secret to `.env`

## Step 4: Start Development Server

```bash
make dev
```

This starts:
- PostgreSQL on `localhost:5432`
- FastAPI backend on `localhost:8000`
- Nginx on `localhost:80`

## Step 5: Verify Installation

```bash
# Check backend health
curl http://localhost:8000/api/health

# Or use the make command
make health
```

You should see:
```json
{"status": "ok"}
```

## Step 6: Access API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Development Tasks

### Database Migrations

```bash
# Apply pending migrations
make migrate

# Create a new migration
make migrate-create MSG="add new field to users"
```

### Seed Test Data

```bash
make seed
```

This creates:
- 2 test users (admin@notebooklm.local, dev@notebooklm.local)
- 3 sample notebooks
- 3 sample sources

### Run Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
cd backend && source venv/bin/activate && pytest tests/test_auth.py -v
```

### Code Quality

```bash
# Check linting
make lint

# Auto-fix lint issues
make lint-fix

# Format code
make format
```

### Database Access

```bash
# Connect to PostgreSQL shell
make db-shell

# Common psql commands
\dt              # List tables
\d users         # Describe users table
SELECT * FROM users;
\q               # Quit
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5432
lsof -i :5432

# Kill the process
kill -9 <PID>
```

### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
cd docker && docker compose -f docker-compose.dev.yml restart postgres

# Check logs
cd docker && docker compose -f docker-compose.dev.yml logs postgres
```

### Migration Errors

```bash
# Reset database (WARNING: destroys data)
cd docker && docker compose -f docker-compose.dev.yml down -v
cd docker && docker compose -f docker-compose.dev.yml up -d postgres
make migrate
make seed
```

### Virtual Environment Issues

```bash
# Recreate virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## IDE Configuration

### VS Code

Install these extensions:
- Python
- Pylance
- Docker
- PostgreSQL

Add to `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "editor.formatOnSave": true
}
```

### PyCharm

1. Open project root
2. Set Python interpreter to `backend/venv/bin/python`
3. Mark `backend/` as Sources Root
4. Configure Docker Compose interpreter

## Next Steps

1. Read [API Documentation](API.md) for endpoint details
2. Read [Architecture Overview](ARCHITECTURE.md) for system design
3. Read [Contributing Guidelines](CONTRIBUTING.md) for PR process
4. Join the team Slack/Discord channel
