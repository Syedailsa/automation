.PHONY: help setup dev stop clean migrate seed test lint docker-build docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Full project setup (backend + database)
	@echo "Setting up NotebookLM Portal..."
	@cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@cp -n backend/.env.example backend/.env 2>/dev/null || true
	@echo "Setup complete! Run 'make dev' to start."

dev: ## Start development server with Docker
	cd docker && docker compose -f docker-compose.dev.yml up --build

dev-local: ## Start backend locally (requires PostgreSQL running separately)
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

stop: ## Stop all Docker containers
	cd docker && docker compose -f docker-compose.dev.yml down

clean: ## Remove all containers, volumes, and caches
	cd docker && docker compose -f docker-compose.dev.yml down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

migrate: ## Run database migrations
	cd backend && source venv/bin/activate && alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MSG="add users table")
	cd backend && source venv/bin/activate && alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed database with test data
	cd backend && source venv/bin/activate && python scripts/seed.py

test: ## Run all tests
	cd backend && source venv/bin/activate && pytest -v

test-cov: ## Run tests with coverage
	cd backend && source venv/bin/activate && pytest --cov=app --cov-report=term-missing -v

lint: ## Run linter
	cd backend && source venv/bin/activate && ruff check .

lint-fix: ## Auto-fix lint issues
	cd backend && source venv/bin/activate && ruff check --fix .

format: ## Format code
	cd backend && source venv/bin/activate && ruff format .

docker-build: ## Build Docker images
	cd docker && docker compose build

docker-up: ## Start all services with Docker
	cd docker && docker compose up -d

docker-down: ## Stop all services with Docker
	cd docker && docker compose down

logs: ## View Docker logs
	cd docker && docker compose logs -f

db-shell: ## Connect to PostgreSQL shell
	docker exec -it notebooklm-postgres psql -U notebooklm -d notebooklm_portal

health: ## Check backend health
	curl -s http://localhost:8000/api/health | python -m json.tool
