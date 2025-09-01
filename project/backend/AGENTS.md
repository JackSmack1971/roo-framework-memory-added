# AGENTS.md â€” Backend Package (Python) (v2025-08-28)

> Scope: this file **overrides/augments** the root `AGENTS.md` for this backend package. Follow **nearest file wins**.

## Stack
- Python **3.11** (recommended; 3.8+ compatible if stated in CI)
- Framework: FastAPI/Django (choose per package reality)
- DB: PostgreSQL (via SQLAlchemy/psycopg or Django ORM)
- Tests: `pytest` (+ `pytest-cov`)
- Linters: `ruff`, `flake8` (optional), type checks via `pyright` or `mypy`

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env || true
python -m pip install pre-commit && pre-commit install || true
```
Bring up services if `compose.yml` exists:
```bash
docker compose up -d db || true
```

## Dev commands
```bash
# Lint & type
ruff check .
pyright || mypy

# Tests (fast)
pytest -q

# Tests with coverage report
pytest -q --cov=. --cov-report=term-missing

# Run app
uvicorn app.main:app --reload --port 8000
```
**Performance budgets:** aim for p95 handler < 150ms locally (adjust per service).

## Migrations (if using Alembic/Django)
```bash
alembic revision -m "feat: ..." && alembic upgrade head
# or Django
python manage.py makemigrations && python manage.py migrate
```

## Security (package specifics)
- Enforce auth/authorization at routers/views
- Validate request payloads (Pydantic/DRF serializers)
- Avoid string SQL; prefer parameterized queries/ORM
- Enable CORS only as required; default deny
- Do not log secrets/PII; scrub sensitive fields
- Run local scans when touching securityâ€‘sensitive areas:
```bash
semgrep scan --config auto --json --json-output ../../artifacts/sec/backend.semgrep.json || true
bandit -r . -f json -o ../../artifacts/sec/backend.bandit.json || true
gitleaks detect -f json -o ../../artifacts/sec/backend.gitleaks.json || true
```
*Wire pass/fail to CI for this package.*

## PR checklist (backend)
- [ ] Unit tests updated/added
- [ ] Handler/ORM changes migrationâ€‘safe
- [ ] API surface documented (`/docs` or OpenAPI)
- [ ] Lint/type checks green
- [ ] Security notes updated (`/docs/security.md` if applicable)
