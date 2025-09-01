# AGENTS.md — Frontend Package (Web App) (v2025-08-28)

> Scope: this file **overrides/augments** the root `AGENTS.md` for this frontend package. Follow **nearest file wins**.

## Stack
- Node **20+** (LTS)
- Framework: React/Vite/Next.js (choose per package reality)
- TypeScript strict mode recommended
- Tests: `vitest`/`jest` + `@testing-library`
- Lint/format: ESLint + Prettier

## Quick start
```bash
npm ci || npm install
cp .env.example .env.local || true
npm run -s dev
```

## Dev commands
```bash
# Lint & type
npm run -s lint
npm run -s typecheck || tsc -p . --noEmit

# Tests (fast)
npm test

# Build
npm run -s build
```

## Accessibility & performance
- Enforce a11y rules (`eslint-plugin-jsx-a11y`)
- Lighthouse targets (local): **Perf ≥95, Access ≥90, Best ≥100, SEO ≥100**
- Avoid blocking main‑thread; prefer suspense/lazy for heavy modules
- Keep bundle size budgets and track in CI

## Security (package specifics)
- Sanitize/escape user‑generated content (XSS)
- Prefer `fetch` wrappers that set `credentials` and headers safely
- Validate all external URLs; block inline event handlers
- Run dependency checks if configured (e.g., `npm audit --audit-level=high`)

## PR checklist (frontend)
- [ ] Unit/UI tests updated/added
- [ ] a11y checks pass (no new violations)
- [ ] Lint/type checks green
- [ ] Build passes; bundle size within budget
