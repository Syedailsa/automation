# NotebookLM Portal — P1 to P5: 100% Completion Plan

**Target:** https://novaai.8.jugaar.ai
**Google OAuth Redirect:** https://novaai.8.jugaar.ai/auth/callback

---

## PRODUCTION DOMAIN CONFIG

| Setting | Value |
|---------|-------|
| Domain | `novaai.8.jugaar.ai` |
| Google OAuth Redirect URI | `https://novaai.8.jugaar.ai/auth/callback` |
| Backend API | `https://novaai.8.jugaar.ai/api/` |
| Frontend | `https://novaai.8.jugaar.ai/` |
| WebSocket | `wss://novaai.8.jugaar.ai/ws/` |

**Action for Google Cloud Console:**
Add these authorized redirect URIs:
```
https://novaai.8.jugaar.ai/auth/callback
http://localhost:80/auth/callback
```

---

## WHAT I NEED FROM EACH PERSON

### From P2 (Muhammad Taha) — Frontend
1. **Does NovaAI.jsx call your own backend API or Anthropic directly?** — Must proxy through FastAPI
2. **Does the Laravel frontend have a login page?** — Need to confirm auth flow exists
3. **Are the Blade components functional or just static HTML?** — Need to know if they make API calls
4. **Is there a FastApiClient service class?** — Earlier analysis showed it's empty

### From P3 (Muhammad Taha) — AI Agent
1. ✅ OPENROUTER_API_KEY provided
2. ✅ LLM settings provided
3. **Does the agent currently work end-to-end?** — Need to confirm refine + execute flows
4. **Is conversation memory wired into the workflow?** — Earlier analysis showed it's not

### From P4 — Automation
1. **Is Playwright installed and working in Docker?** — Need to verify browser ops work
2. **Are the test scripts actually runnable?** — Need evidence of test execution
3. **Is the monitoring wired to real alerting?** — Or just class definitions?

### From P5 — DevOps
1. **Is the server ready at novaai.8.jugaar.ai?** — Need DNS + SSL configured
2. **Is Docker installed on the server?** — For docker-compose deployment
3. **Do we have SSH access?** — For the deploy workflow
4. **Is PostgreSQL running on the server?** — Or should we use Docker for it?

---

## PHASE 2 COMPLETION (P2 Frontend — biggest gap)

### Step 1: Connect Frontend to Backend API
**Files to create/modify:**
- `frontend/app/Services/FastApiClient.php` — HTTP client for all API calls
- `frontend/app/Http/Middleware/ApiAuth.php` — JWT token from session
- `frontend/routes/web.php` — Update routes to use FastApiClient

**Tasks:**
1. Create `FastApiClient.php` with methods:
   - `getNotebooks()`, `createNotebook()`, `deleteNotebook()`
   - `getSources($notebookId)`, `addSource()`, `deleteSource()`
   - `getOutputs($notebookId)`, `deleteOutput()`
   - `agentRefine($input)`, `agentExecute($input)`
   - `getAgentStatus($executionId)`
2. Wire all Blade views to call FastApiClient instead of direct API
3. Add JWT token storage in Laravel session after login
4. Test login flow end-to-end

### Step 2: Connect NovaAI.jsx to Backend
**If NovaAI.jsx currently calls Anthropic directly:**
- Create a proxy endpoint in FastAPI: `POST /api/agent/chat`
- Update NovaAI.jsx to call `/api/agent/chat` instead of Anthropic API
- Add WebSocket connection for real-time agent status

### Step 3: Test All CRUD Operations
- Create notebook from UI → verify in database
- Add source → verify source created
- Run agent → verify execution log created
- Check outputs appear in UI

---

## PHASE 3 COMPLETION (P3 Agent + P4 Automation)

### Step 4: Wire Conversation Memory
**File:** `backend/app/agents/notebooklm_agent.py`
- Connect `generate_with_history()` to the workflow execution
- Store conversation context in execution_logs
- Pass previous context to LLM on subsequent calls

### Step 5: Verify Playwright in Docker
**File:** `backend/Dockerfile.prod`
- Confirm `playwright install --with-deps chromium` works
- Test browser login flow in container
- Verify session persistence

### Step 6: Wire Monitoring to Real Alerting
**Files:** `backend/app/automation/monitoring/alerting.py`
- Connect to email/Slack webhook
- Test alert on failure scenarios
- Verify health check endpoint returns real data

---

## PHASE 4 COMPLETION (P5 Testing)

### Step 7: E2E Test Suite
**Create:** `tests/e2e/` directory
- Playwright tests for login flow
- Playwright tests for notebook CRUD
- Playwright tests for source addition
- Playwright tests for agent execution

### Step 8: Load Testing
**Create:** `tests/load/` directory
- Locust configuration
- Test scenarios: 50 concurrent users, 100 concurrent users
- API endpoint benchmarks

### Step 9: Security Testing
- SQL injection tests on all inputs
- XSS tests on all form fields
- CSRF token verification
- Auth bypass attempts

---

## PHASE 5 COMPLETION (Deployment)

### Step 10: Server Setup
**On the server (novaai.8.jugaar.ai):**
1. Install Docker + Docker Compose
2. Clone repo
3. Create `.env` with production secrets
4. Run: `docker compose -f docker-compose.prod.yml up -d`
5. Run: `docker compose exec backend alembic upgrade head`

### Step 11: SSL Certificate
**Option A: Let's Encrypt (free)**
```bash
apt install certbot
certbot certonly --standalone -d novaai.8.jugaar.ai
```
**Option B: Cloudflare** — If domain is behind Cloudflare, SSL is automatic

### Step 12: Nginx SSL Config
Update `docker/nginx/default.conf` to add HTTPS server block with cert paths

### Step 13: Database Backup Cron
```bash
crontab -e
# Add: 0 2 * * * cd /app && bash scripts/backup.sh
```

### Step 14: DNS Setup
Point `novaai.8.jugaar.ai` A record to server IP

### Step 15: Deployment Verification
```bash
curl https://novaai.8.jugaar.ai/api/health
# Should return: {"status": "ok", "database": {"healthy": true}, "cache": {...}}
```

---

## EXECUTION ORDER

```
Week 1: P2 Frontend Integration (Steps 1-3)
Week 2: P3 Agent Memory + P4 Playwright (Steps 4-6)
Week 3: P5 Testing (Steps 7-9)
Week 4: Deployment (Steps 10-15)
```

---

## CREDENTIALS SUMMARY

| Credential | Value | Where to Add |
|-----------|-------|--------------|
| OPENROUTER_API_KEY | `sk-or-v1-your-key-here` | backend/.env |
| LLM_DEFAULT_PROVIDER | `openrouter` | backend/.env |
| LLM_DEFAULT_MODEL | `qwen/qwen3.7-max` | backend/.env |
| LLM_MAX_RETRIES | `3` | backend/.env |
| LLM_TIMEOUT_SECONDS | `60` | backend/.env |
| GOOGLE_REDIRECT_URI | `https://novaai.8.jugaar.ai/auth/callback` | backend/.env + Google Console |
| CORS_ORIGINS | `https://novaai.8.jugaar.ai` | backend/.env |
