# AGENTS.md: AI Collaboration Guide (v2025-08-28)

> This repository uses the **AGENTS.md** convention: a simple, agent‑facing runbook placed at the repo root. Subprojects may include their own `AGENTS.md`; the **nearest file wins**. This document provides essential context for AI models interacting with this project to ensure consistency, maintain code quality, and enable autonomous operation.

---

## 0. Ground Rules & Bootstrap (Do-This-First)

### Critical Operating Principles
- Keep commands **deterministic** and **idempotent**
- Prefer **fast local checks**, run **full suites in CI**  
- If a guardrail fails twice after auto‑fix → **STOP** and create a remediation task
- **Monorepo precedence:** if a subpackage has its own `AGENTS.md`, follow it for work in that subtree

### Idempotent Bootstrap (Run in repo root)
```bash
# 1) Dependencies
python -m pip install -U pip
pip install -r requirements.txt
npm ci || npm install

# 2) Make helper scripts executable
chmod +x scripts/*.sh || true

# 3) Initialize a project (interactive/safe to re‑run)
./scripts/setup_project.sh

# 4) Validate target project config (replace <project-id>)
python scripts/validate_config.py <project-id>

# 5) Quick gates
pytest -q
ruff check .
npm run -s lint || npx eslint .

# 6) Full test suite
pytest -q && npm test
```

---

## 1. Project Overview & Purpose

* **Primary Goal:** A 99% autonomous AI development framework orchestrating specialized AI agents through an intelligent control plane for enterprise-grade software development with minimal human intervention.
* **Business Domain:** AI/ML Development Tools, Software Engineering Automation, Enterprise Development Platforms.
* **Key Features:** 
  - Multi-agent orchestration with SPARC methodology
  - Autonomous code generation, testing, and quality assurance
  - Intelligent conflict resolution between AI specialists
  - Continuous learning and pattern recognition
  - Enterprise security and compliance integration
  - Multi-stack project support (Python, Node.js, TypeScript, etc.)

---

## 2. Core Technologies & Stack

* **Languages:** Python 3.8+ (recommended 3.11+), TypeScript 5.x, JavaScript ES2023, Node.js 20+ LTS
* **Frameworks & Runtimes:** 
  - **Backend:** FastAPI, Django 5.2+, Django REST Framework
  - **Frontend:** React 18.x, Vite, Next.js, React Native (Expo SDK 51+)
  - **Testing:** pytest, pytest-cov, vitest, jest, @testing-library
* **Databases:** PostgreSQL (primary), Redis (caching, Celery broker)
* **Key Libraries/Dependencies:**
  - **Python:** ruff, pyright/mypy, SQLAlchemy, psycopg, django-allauth, Celery
  - **Node/TypeScript:** ESLint, Prettier, zod, react-navigation, react-native-paper
* **Package Managers:** pip/uv (Python), npm (Node.js, CI uses `npm ci`)
* **Platforms:** Linux containers, Android/iOS (via Expo), Web, Windows/macOS development

---

## 3. Architectural Patterns & Structure

* **Overall Architecture:** Autonomous multi-agent system with intelligent orchestration layer managing specialist AI agents (specification writers, architects, security specialists, code implementers, QA coordinators). Backend services support agent coordination while frontend provides human oversight interfaces.

* **Directory Structure Philosophy:**
  - `/project/<id>/` — per‑project code, tests, and configs
  - `/scripts/` — setup & validation utilities (`setup_project.sh`, `validate_config.py`)
  - `/docs/` — human‑oriented guides (architecture, security SOPs, playbooks)
  - `/artifacts/` — local outputs (test reports, security scans); CI uploads to pipeline storage
  - `/config/` — shared schemas and templates
  - `/backend/` — Python/Django source code (when present)
  - `/frontend/` — React/TypeScript source code (when present)
  - `/tests/` — All unit and integration tests (parallel to source)

* **Module Organization:** 
  - **Backend:** Django apps structure (feature-specific apps like `agents/`, `orchestration/`, `quality/`)
  - **Frontend:** Feature-centric structure (`src/features/auth`, `src/screens/Home`, `src/components/`)
  - **Monorepo:** Each project under `/project/<id>/` can have its own stack and `AGENTS.md`

* **Common Patterns & Idioms:**
  - **Autonomous Workflows:** Agent delegation with quality gates and escalation paths
  - **Memory Management:** Python GC-managed types, React Hooks for state management
  - **Concurrency:** Python async/await, Celery for background tasks, React concurrent features
  - **Error Handling:** Python exceptions with custom `Error` types, TypeScript Result types
  - **Security-by-Design:** Input validation at boundaries, encoding on output, principle of least privilege

---

## 4. Coding Conventions & Style Guide

* **Formatting:** 
  - **Python:** Follow PEP 8, use Black/ruff. Max line length: 88 characters. Use 4-space indentation.
  - **TypeScript/JavaScript:** Prettier with 2-space indentation, single quotes, trailing commas. Max line length: 100 characters.

* **Naming Conventions:** 
  - **Python:** Variables/functions: `snake_case`; Classes: `PascalCase`; Constants: `SCREAMING_SNAKE_CASE`; Files: `snake_case.py`
  - **TypeScript:** Variables/functions: `camelCase`; Types/Interfaces: `PascalCase`; Constants: `SCREAMING_SNAKE_CASE`; Files: `kebab-case.ts` or `PascalCase.tsx` for components

* **API Design Principles:** 
  - **Consistency:** Follow RESTful conventions for HTTP APIs
  - **Type Safety:** Strict TypeScript mode, Pydantic for Python validation
  - **Documentation:** JSDoc for TypeScript, Python docstrings (Google style)
  - **Extensibility:** Design for plugin architecture and agent specialization

* **Error Handling:**
  - **Python:** Use custom exception hierarchy, structured logging, avoid bare `except:`
  - **TypeScript:** Prefer Result types or explicit error handling, avoid silent failures

* **Forbidden Patterns:**
  - **NEVER** use `@ts-expect-error` or `@ts-ignore` to suppress type errors
  - **NEVER** use `git push --force` on main branch
  - **NEVER** commit secrets or hardcode API keys
  - **NEVER** push directly to main branch; use pull requests
  - **DO NOT** touch production databases directly without migration scripts

---

## 5. Key Files & Entrypoints

* **Main Entrypoints:**
  - **Orchestrator:** `src/orchestration/main.py` (SPARC orchestrator)
  - **Backend API:** `src/api/main.py` (FastAPI) or `manage.py` (Django)
  - **Frontend:** `src/index.tsx` (React), `App.tsx` (React Native)
  - **Scripts:** `scripts/setup_project.sh`, `scripts/validate_config.py`

* **Configuration:**
  - **Python:** `nim.cfg`, `config.nims`, `.env` files, `settings/` directory for Django
  - **Node:** `.env.local`, `package.json`, `tsconfig.json`, `vite.config.ts`
  - **CI/CD:** `.github/workflows/main.yml`, PR CI workflow

* **Quality & Security:**
  - **Linting:** `.flake8`, `pyproject.toml`, `eslint.config.mjs`, `.prettierrc`
  - **Testing:** `pytest.ini`, `vitest.config.ts`, test files follow `*.test.ts` or `test_*.py` conventions

---

## 6. Development & Testing Workflow

### Local Development Environment

**Python Backend:**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
cp .env.example .env || true
python -m pip install pre-commit && pre-commit install || true
```

**Node/TypeScript Frontend:**
```bash
npm ci || npm install
cp .env.example .env.local || true
npm run -s dev
```

**Database Setup (if applicable):**
```bash
docker compose up -d db || true
# Django migrations
python manage.py makemigrations && python manage.py migrate
# or Alembic
alembic revision -m "feat: ..." && alembic upgrade head
```

### Task Configuration & Commands

**Python:**
- **Test:** `pytest -q` (fast), `pytest -q --cov=. --cov-report=term-missing` (with coverage)
- **Lint:** `ruff check .` (auto-fix: `ruff check . --fix`)
- **Type:** `pyright` or `mypy`
- **Run:** `uvicorn app.main:app --reload --port 8000`

**Node/TypeScript:**
- **Scripts:** `npm run lint` (ESLint), `npm test` (vitest/jest), `npm run build` (production)
- **Type:** `npm run -s typecheck` or `tsc -p . --noEmit`
- **Dev:** `npm run -s dev`

### Testing Requirements
- **Coverage:** Maintain ≥90% coverage on critical paths
- **Test Structure:** New code requires corresponding unit tests
- **File Conventions:** `*.test.ts`, `*.spec.ts`, `test_*.py` under `/tests` directory
- **Mocking:** Use Mock Service Worker (MSW), `vi.fn()` for mocking to avoid external calls
- **Accessibility:** Frontend tests must include a11y checks (no new violations)

### CI/CD Process
- **Required Checks:** Config validation, linting (ruff, ESLint), unit tests, type checking, build validation
- **Quality Gates:** All checks must pass before PR approval
- **Coverage:** Enforce thresholds per package in CI
- **Security Scans:** Automated security scanning with pass/fail criteria

---

## 7. Security & Compliance

### Core Security Principles
- **Never commit secrets** — Use environment injection in CI/CD, `.env` files excluded by VCS
- **Validate & sanitize inputs** at boundaries; **encode on output**
- **Crypto & auth:** Use vetted libraries; no custom primitives
- **Transport & storage:** TLS in transit; encrypt sensitive data at rest
- **Rate-limit** and audit externally exposed endpoints

### Secrets & Configuration Management
- Never commit secrets or API keys
- Use separate service accounts per environment (dev/stage/prod)
- Rotate credentials on compromise; prefer short-lived tokens
- Principle of least privilege for all access

### Data Protection
- **TLS** for all network hops crossing trust boundaries
- **Encrypt sensitive data at rest** using managed KMS when available
- **Define PII/PHI data classes**; implement log scrubbing for sensitive fields

### Security Scanning (Automated)
```bash
# Static analysis / SAST
semgrep scan --config auto --json --json-output artifacts/sec/semgrep.json || true

# Python security
bandit -r . -f json -o artifacts/sec/bandit.json || true

# Secret scanning
gitleaks detect --no-banner -f json -o artifacts/sec/gitleaks.json || true

# Dockerfile and shell scripts
hadolint Dockerfile | tee artifacts/sec/hadolint.txt || true
shellcheck -S style -f gcc scripts/*.sh | tee artifacts/sec/shellcheck.txt || true
```

### Frontend-Specific Security
- **XSS Prevention:** Sanitize/escape user-generated content
- **Safe HTTP:** Use `fetch` wrappers with proper `credentials` and headers
- **URL Validation:** Validate all external URLs; block inline event handlers
- **CORS:** Enable CORS only as required; default deny

### Backend-Specific Security
- **Authentication/Authorization:** Enforce at routers/views level
- **Request Validation:** Use Pydantic/DRF serializers for payload validation
- **SQL Safety:** Avoid string SQL; prefer parameterized queries/ORM
- **Logging:** Do not log secrets/PII; scrub sensitive fields

---

## 8. Quality Assurance & Performance

### Performance Budgets
- **Backend:** p95 handler < 150ms locally (adjust per service)
- **Frontend:** Lighthouse targets (local) — **Perf ≥95, Access ≥90, Best ≥100, SEO ≥100**
- **Bundle Size:** Keep bundle size budgets and track in CI
- **Main Thread:** Avoid blocking main thread; prefer suspense/lazy for heavy modules

### Accessibility Requirements
- Enforce a11y rules (`eslint-plugin-jsx-a11y`)
- New code cannot introduce accessibility violations
- Test with screen readers and keyboard navigation

### Code Quality Standards
- **Rule of 500:** If any single file exceeds ~500 lines, prefer **refactor/split** before adding features
- **Function Guideline:** Keep functions under ~50 lines; extract helpers once exceeded
- **Prefer small PRs:** Land refactors first when splitting large files
- Use descriptive naming; avoid unnecessary abbreviations

---

## 9. Autonomy Guardrails & Escalation

### Stop Conditions (Agents MUST STOP and escalate)
- Config validation fails **twice** after auto-fix attempts
- Tests or lints cannot be made green **within current change scope**
- Coverage on critical paths drops below policy and cannot be recovered without architectural change
- Security scans show **high-severity** findings that are not false positives
- Performance regressions exceed budgets/SLOs
- Any action risks **data loss, credential exposure, or production impact**

### Delegation Map
- `sparc-orchestrator` → task decomposition, routing, final assembly
- `sparc-code-implementer` → code changes when delegated by orchestrator
- `security-architect` → auth/crypto/PII & high-severity triage
- `qa-validator` → flaky tests, test strategy, coverage
- `performance-engineer` → profiling & regressions
- `data-steward` → schema/migrations/retention

### Incident Response (Minimum Playbook)
1. **Detect:** Alert or scanner finds issue → create incident ticket
2. **Contain:** Revoke tokens/rotate keys, isolate affected systems
3. **Eradicate:** Patch/fix root cause; add tests/guards
4. **Recover:** Restore normal ops; monitor
5. **Post-mortem:** Document timeline, impact, and preventive actions

---

## 10. Specific Instructions for AI Collaboration

### Contribution Guidelines
- Follow existing code style and architectural patterns
- Ensure all new functionality includes comprehensive tests
- Update documentation (`/docs/`) when changing public behavior or interfaces
- Submit pull requests against appropriate branch (typically `main` or `develop`)
- Use conventional commit messages (e.g., `feat:`, `fix:`, `docs:`, `refactor:`)

### Dependencies Management
- **Python:** Use `pip install <package>` or `uv add <library>` if uv is configured
- **Node:** Use `npm install <package>` (CI will use `npm ci`)
- When adding new dependencies, consider security, licensing, and maintenance burden
- Update lock files appropriately (`package-lock.json`, `yarn.lock`, `requirements.txt`)

### Commit Messages & Pull Requests
- **Format:** Follow Conventional Commits specification or Chris Beams style
- **PR Title:** `[<project>/<pkg>] <concise change description>`
- **PR Description:** What changed, why, risk assessment, test evidence
- **Status:** All required checks must be green before merge
- **Breaking Changes:** Clearly document any breaking changes

### Debugging Guidance
- For bugs, paste the **full stack trace** to identify the failing line
- Do not guess; review the codebase directly for context
- Use structured logging to aid in debugging
- Include reproduction steps in bug reports

### Parallel Task Execution
- Tasks that touch different files can run simultaneously
- Ensure clear naming for separate task logs
- Coordinate database migrations and schema changes
- Avoid concurrent modifications to shared configuration files

### Pass/Fail Criteria
- **Finish Line Definition:** Tests pass, linter clean, TypeScript compiler green
- Stop work only when all quality checks pass
- If checks fail twice after auto-fix → escalate per guardrails

### Breaking Down Large Work
- Break large features into small, incremental pull requests
- Each step should have its own tests and be independently deployable
- Prefer feature flags over long-running branches
- Ensure each PR provides business value or clear technical progress

---

## 11. Monorepo Guidelines

### Precedence Rules
This is the **root** runbook. If working inside a subpackage with its own `AGENTS.md`, follow the **nearest file wins** principle.

### Project Structure
Each project under `/project/<id>/` may have:
- Its own technology stack
- Specific `AGENTS.md` overrides
- Independent CI/CD pipelines
- Separate dependency management

### Cross-Project Dependencies
- Minimize coupling between projects
- Use well-defined APIs for inter-project communication
- Document shared utilities and common patterns
- Coordinate breaking changes across dependent projects

---

*This document prioritizes **executable steps** and **guardrails** to enable AI agents to act quickly and safely. For detailed security SOPs, see `/docs/security.md`. For implementation details, see project-specific documentation.*