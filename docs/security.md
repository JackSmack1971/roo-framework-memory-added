# Security SOP (v2025-08-28)

This document expands the brief guidance in `AGENTS.md` and defines **minimum** security practices across packages.

## 1) Secrets & configuration
- Never commit secrets. Use env vars; manage `.env*` via `.gitignore` and secret stores in CI/CD.
- Rotate credentials on compromise or suspected leak; keep shortâ€‘lived tokens where possible.
- Use separate service accounts per environment (dev/stage/prod); principle of least privilege.

## 2) Data protection
- TLS for all network hops that cross trust boundaries.
- Encrypt sensitive data at rest using managed KMS when available.
- Define PII/PHI data classes; log scrubbing for sensitive fields.

## 3) Secure coding
- Prefer highâ€‘level, vetted crypto libs; avoid custom primitives.
- Validate and sanitize input at trust boundaries; encode on output.
- Apply defenseâ€‘inâ€‘depth: parameterized queries, prepared statements, CSRF protection, content security policies (CSP) for web apps.

## 4) Static analysis & scanning
Use these tools where applicable; wire their outputs to CI artifacts:

```bash
# Semgrep â€” multiâ€‘language SAST
semgrep scan --config auto --json --json-output artifacts/sec/semgrep.json

# Bandit â€” Python security checks
bandit -r . -f json -o artifacts/sec/bandit.json

# Gitleaks â€” secret scanning
gitleaks detect --no-banner -f json -o artifacts/sec/gitleaks.json

# Hadolint â€” Dockerfile best practices
hadolint Dockerfile | tee artifacts/sec/hadolint.txt

# ShellCheck â€” shell script static analysis
shellcheck -S style -f gcc scripts/*.sh | tee artifacts/sec/shellcheck.txt
```

> Choose only the tools relevant to each package; set enforceable pass/fail thresholds over time.

## 5) Vulnerability management
- Track thirdâ€‘party dependencies; apply dependable/renovate or similar bots.
- Triage scanner findings by severity and exploitability; fix **High/Critical** before release.
- Use baselines only as a temporary measure while driving issues down.

## 6) Incident response (minimum playbook)
1. **Detect**: alert or scanner finds issue â†’ create incident ticket.
2. **Contain**: revoke tokens/rotate keys, isolate affected systems.
3. **Eradicate**: patch/fix root cause; add tests/guards.
4. **Recover**: restore normal ops; monitor.
5. **Postâ€‘mortem**: document timeline, impact, and preventive actions.

## 7) Compliance notes
- Keep audit trails for securityâ€‘relevant operations.
- Follow data retention policies; document deviations with approvals.

---

_This SOP is intentionally concise. For deeper guidance, add packageâ€‘specific annexes under `/docs/security/` (e.g., `backend.md`, `frontend.md`)._