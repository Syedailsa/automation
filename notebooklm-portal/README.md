# NotebookLM Portal

A multi-user web portal that integrates with Google NotebookLM using browser automation + LLM agents. Users provide simple English or Roman Urdu input, the agent refines it, automates NotebookLM via Playwright, and shows generated outputs in a dashboard.

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend API | Python + FastAPI |
| AI Agent | LangChain + OpenAI/Claude |
| Browser Automation | Playwright |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy + Alembic |
| Real-time | WebSocket |
| Frontend | Laravel + Blade |
| Auth | Google OAuth 2.0 |

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

### One-Command Setup

```bash
git clone https://github.com/Syedailsa/automation.git
cd automation
make setup
```

### Start Development

```bash
make dev
```

This starts:
- **PostgreSQL** on port `5432`
- **FastAPI backend** on port `8000`
- **Nginx** on port `80`

### Verify Everything Works

```bash
make health
```

## Available Commands

```bash
make help           # Show all commands
make setup          # Full project setup
make dev            # Start development server (Docker)
make dev-local      # Start backend locally
make stop           # Stop Docker containers
make clean          # Remove containers + volumes
make migrate        # Run database migrations
make seed           # Seed test data
make test           # Run tests
make lint           # Run linter
make db-shell       # Connect to PostgreSQL
```

## Project Structure

```
notebooklm-portal/
├── backend/              # FastAPI (Python)
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── core/         # Security, deps, exceptions
│   │   ├── agents/       # LangChain AI agent
│   │   └── automation/   # Playwright browser automation
│   ├── alembic/          # Database migrations
│   └── tests/            # Python tests
├── frontend/             # Laravel (PHP)
├── docker/               # Docker configurations
├── docs/                 # Documentation
└── scripts/              # Setup scripts
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```bash
# Database (default works with Docker)
DATABASE_URL=postgresql+asyncpg://notebooklm:notebooklm_secret@localhost:5432/notebooklm_portal

# JWT Secret (change in production)
JWT_SECRET_KEY=your-secret-key

# Google OAuth (required for login)
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx

# LLM Keys (for AI agent)
OPENAI_API_KEY=sk-xxx
```

## Team Roles

| ID | Role | Owns |
|----|------|------|
| P1 | Backend Lead | `backend/app/api/*`, `backend/app/services/*`, `backend/app/models/*` |
| P2 | Frontend Dev | `frontend/*` |
| P3 | AI Agent Dev | `backend/app/agents/*`, prompts, LLM integration |
| P4 | Automation Eng | `backend/app/automation/*`, Playwright |
| P5 | DevOps + QA | `docker/*`, `.github/*`, tests, CI/CD |

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for branch naming, commit conventions, and PR process.

## License

MIT
