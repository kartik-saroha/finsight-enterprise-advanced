# FinSight Enterprise — Advanced Life Lab Edition

FinSight is a personal-finance intelligence application with a local-first browser interface plus an optional FastAPI service for server-side authentication, user-scoped records, audit events, and structured AI-agent orchestration.

## Open the app immediately (browser prototype)

- Open `index.html` in a modern browser. No frontend build step is required.
- Create a local profile at the login screen. This standalone mode keeps its data in browser `localStorage`.
- To explore the new modules, use **Load sample data** on Home, then open **Bills & EMI**, **Debt Freedom**, **Explainability**, and **Life Lab**.
- In **Backend & AI**, use `http://127.0.0.1:8000` as the API URL after starting the service below.

The direct HTML mode is useful for a quick preview but it is not server-secure and does not sync across devices. Never use a reused password or real account credentials in the local prototype.

## What's included

### Financial product modules
- Dashboard, transaction ledger, category breakdowns, CSV import/export, backups, savings goals, budgets, net worth, SIP/EMI calculators and themes.
- **Life Lab:** salary reduction/job-loss/one-off expense stress tests, emergency-fund runway and purchase planning.
- **Bills & EMI Early Warning:** obligation register, due dates, overdue flags and a simple 30-day cash estimate using recorded ledger averages plus user-specified cash. The forecast is not a bank balance or a guaranteed prediction.
- **Debt Freedom Simulator:** avalanche vs. snowball, estimated months to payoff and interest. Debt Lab records are separate from the app's existing net-worth liabilities.
- **Explainability:** findings show observed data, rule/calculation, assumptions, limits and suggested verification; analysis snapshots can be exported as JSON.
- **Backend & AI:** browser controls to check API health, create an API account, sign in and clear the locally stored bearer token.

### FastAPI backend
- Passwords hashed with Argon2 using `pwdlib`.
- Short-lived signed bearer tokens; endpoints check user ownership for obligations and audit records.
- PostgreSQL support through `DATABASE_URL`; SQLite is used by default for local development/tests.
- Input validation, generic auth failure messages, security headers, structured logs and per-user audit events.
- Agent orchestrator calls OpenRouter free models from the server when `OPENROUTER_API_KEY` is configured (default model route: `openrouter/free`); optional Anthropic support remains available. It validates the returned schema and uses explainable deterministic fallback findings if no key is configured or a provider response fails.
- Unit/integration tests for health, validation, authentication, ownership isolation, obligation status updates and AI fallback.

## Start the API locally (Python)

**Recommended Windows setup:** from the project root in PowerShell run ` .\start-api.ps1 `. The script installs backend dependencies, then securely prompts for an OpenRouter API key if `OPENROUTER_API_KEY` is not already set. The key is held only in that terminal session and is not written to a file. Leave it blank to use the rules-based fallback. Create a key at https://openrouter.ai/keys and choose a free model. OpenRouter currently lists a 50-request/day limit for free-plan free-model usage; limits and model availability can change. You can use `openrouter/free` to route to an available free model. Do not send highly sensitive financial or personal data to third-party AI providers. Never paste the key into the HTML, screenshots, chat, or GitHub.

Manual setup, from the project root in PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///./finsight_dev.db"
$env:JWT_SECRET_KEY = "replace-this-with-a-long-random-secret-before-use"
$env:ALLOW_DEV_SECRET = "1"
$env:OPENROUTER_MODEL = "openrouter/free"
$env:OPENROUTER_API_KEY = Read-Host "Paste OpenRouter API key (input visible; use start-api.ps1 for hidden input)"
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation and `http://127.0.0.1:8000/healthz` for health status. In the app's **Backend & AI** page, test the same base URL. If you host the HTML using a different origin, add that exact origin to `CORS_ORIGINS`.

### Run tests

```powershell
cd backend
$env:DATABASE_URL = "sqlite:///./finsight_test.db"
$env:JWT_SECRET_KEY = "unit-test-secret-key-with-enough-entropy-123456"
$env:ALLOW_DEV_SECRET = "1"
pytest -q
```

Tests use SQLite and do not require PostgreSQL or an AI key.

## Start PostgreSQL + API + web with Docker Compose

1. Copy `.env.example` to `.env`.
2. Replace `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` with strong random values. Do not commit `.env`.
3. Optionally set `OPENROUTER_API_KEY` in `.env`; without it the API agent endpoint uses the deterministic fallback. Use `OPENROUTER_MODEL=openrouter/free` for free-model routing.
4. From the project root run:

```powershell
docker compose up --build
```

Then open `http://localhost:8080`, API docs at `http://localhost:8000/docs`, and health at `http://localhost:8000/healthz`.

## API overview

- `POST /api/v1/auth/register` — create account (password minimum 12 characters).
- `POST /api/v1/auth/login` — obtain a short-lived bearer token.
- `GET /api/v1/me` — current account.
- `GET|POST /api/v1/obligations`, `PATCH /api/v1/obligations/{id}/paid`, `DELETE /api/v1/obligations/{id}` — user-scoped obligations.
- `GET|POST /api/v1/debts` — user-scoped debt records.
- `POST /api/v1/agents/orchestrate` — structured agent findings with evidence, assumptions and next steps.
- `GET /api/v1/audit/recent` — recent account audit events.

## Important production hardening still required

This is a serious academic foundation, **not a claim of production readiness**. Before real users store financial data:

- Add Alembic schema migrations, automated backups/restore drills, deployment secrets management and TLS.
- Add persistent rate limiting at the reverse proxy/API gateway, email verification, secure password recovery, account deletion/export workflows and session revocation/refresh-token strategy.
- Add CSRF protections if switching to cookie-based sessions, stricter CORS allowlists, monitoring/alerting, dependency scanning and independent security review.
- Review AI prompts, prompt-injection handling, sensitive-data minimisation, retention, model/provider data terms and evaluation datasets. AI output is advisory and not verified financial advice.
- Use a licensed provider and appropriate consent/compliance for bank aggregation; payment screens in the existing frontend are not a real payment gateway.
- Apply PostgreSQL migrations rather than relying on `create_all` for long-lived production schema management.

## Suggested review narrative

FinSight has a product layer (the web app), decision-support modules (Life Lab, obligation warnings and debt simulation), and a service layer (FastAPI, PostgreSQL-compatible persistence, Argon2 identity, user-scoped APIs, audit logging and a validated AI orchestrator). Explain the limits of each estimate and show the evidence behind a recommendation. Do not claim that browser-only mode is securely authenticated or that simulated payments move money.

## Interface and Copilot updates

- The navigation is now grouped into Workspace, Money, Intelligence, and Settings. It collapses to an icon rail on narrower screens; use the menu control to expand/collapse it.
- The AI Copilot now attempts the authenticated FastAPI `/api/v1/agents/orchestrate` endpoint when a backend token is present. Without a backend session it gives a clearly labelled local rules-based response instead of pretending a live LLM is running.
- For live model-assisted responses, run the backend, sign in under **Backend & AI**, and configure `ANTHROPIC_API_KEY` in the backend environment. The starter script prompts for it securely at launch. Keep the key on the server; never put it in HTML or commit it to Git.
- A provider key, network access, valid model name, and successful API authentication are required for live AI. If the provider is unavailable, the backend uses its deterministic fallback and marks the response accordingly.
