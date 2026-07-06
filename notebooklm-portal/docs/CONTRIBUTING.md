# Contributing Guidelines

Thank you for contributing to NotebookLM Portal! This document covers the process for making contributions.

## Branch Naming Convention

Use the following format:

```
<type>/<role>-<description>
```

**Types:**
- `feature` - New functionality
- `fix` - Bug fixes
- `refactor` - Code restructuring
- `docs` - Documentation only
- `test` - Adding tests
- `chore` - Maintenance tasks

**Roles:**
- `p1` - Backend Lead
- `p2` - Frontend Dev
- `p3` - AI Agent Dev
- `p4` - Automation Eng
- `p5` - DevOps/QA

**Examples:**
```
feature/p1-backend-auth
feature/p2-dashboard-ui
fix/p4-selector-chrome-update
docs/p5-api-documentation
```

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting (no code change)
- `refactor` - Code restructuring
- `test` - Adding tests
- `chore` - Maintenance

**Scopes:**
- `auth` - Authentication
- `api` - API endpoints
- `models` - Database models
- `agent` - AI agent
- `automation` - Playwright automation
- `frontend` - Laravel frontend
- `docker` - Docker configuration
- `ci` - CI/CD pipeline

**Examples:**
```
feat(auth): add Google OAuth login flow
fix(api): handle missing notebook_id gracefully
docs(api): update endpoint documentation
test(auth): add JWT validation tests
chore(docker): update PostgreSQL to 15.4
```

## Pull Request Process

### 1. Create Your Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/p1-backend-notebooks
```

### 2. Make Your Changes

- Write clean, documented code
- Follow existing code style
- Add tests for new functionality
- Update documentation if needed

### 3. Run Checks Locally

```bash
# Run linter
make lint

# Run tests
make test

# Format code
make format
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat(api): add notebook CRUD endpoints"
```

### 5. Push and Create PR

```bash
git push origin feature/p1-backend-notebooks
```

Then create a Pull Request on GitHub targeting the `develop` branch.

### 6. PR Description

Use the PR template and include:

- **What** does this PR do?
- **Why** is this change needed?
- **How** to test it?
- **Screenshots** (if UI changes)

### 7. Code Review

- At least 1 approval required
- Address all review comments
- CI must pass

### 8. Merge

Squash merge to `develop`:

```
feat(api): add notebook CRUD endpoints (#42)
```

## Code Style

### Python (Backend)

- Use type hints on all functions
- Follow PEP 8 style guide
- Use `ruff` for linting
- Maximum line length: 100 characters
- Use async/await for all I/O operations
- Add docstrings to public functions

### PHP (Frontend)

- Follow PSR-12 coding standard
- Use Laravel collections
- Type hint all methods
- Use Blade components for reusable UI

### Git

- Never commit directly to `develop` or `main`
- Keep commits atomic and focused
- Write meaningful commit messages
- Don't commit secrets or API keys

## Testing

### Backend Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test
cd backend && pytest tests/test_auth.py -v
```

### Writing Tests

- Place tests in `backend/tests/`
- Name test files `test_<module>.py`
- Use descriptive test function names
- Test both success and error cases

Example:
```python
async def test_create_notebook_success():
    """Test creating a new notebook with valid data."""
    # Arrange
    notebook_data = {"title": "Test Notebook"}
    
    # Act
    response = await client.post("/api/notebooks", json=notebook_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["title"] == "Test Notebook"
```

## Database Changes

### Creating Migrations

```bash
make migrate-create MSG="add new field to users"
```

### Best Practices

- Always review auto-generated migrations
- Never delete or modify existing migrations in production
- Add indexes for frequently queried columns
- Use foreign keys for relationships
- Consider backward compatibility

## Getting Help

- Check existing documentation in `/docs`
- Search existing issues before creating new ones
- Ask questions in team Slack/Discord
- Tag relevant team members in PRs

## Code of Conduct

- Be respectful and constructive
- Focus on the code, not the person
- Welcome newcomers and help them learn
- Give credit where it's due
