# ATLAS MVP Status

Date: 2026-08-02

| Function | Status | What Was Done | Changed Files | How To Verify | Known Limits | Next Action |
| --- | --- | --- | --- | --- | --- | --- |
| Technical audit | DONE | Current architecture, stack, working areas, risks and P0 plan documented. | `docs/ATLAS_TECHNICAL_AUDIT.md` | Read the audit; run `py -3.12 -m pytest -q`. | Audit is a point-in-time snapshot. | Keep updated after each P0/P1 change. |
| Test baseline | DONE | Existing backend suite was run after changes. | none | `py -3.12 -m pytest -q` -> `160 passed`. | Playwright test is not included in Python test command. | Add browser E2E to CI later. |
| Local startup | DONE | FastAPI was started on port `8010` and `/api/health` returned 200. | none | `py -3.12 -m uvicorn api.app:app --host 127.0.0.1 --port 8010`. | Render free tier can still cold-start. | Add deployment smoke check script. |
| Security headers | DONE | Added central middleware for browser security headers and tests. | `api/app.py`, `tests/test_security_headers.py` | `py -3.12 -m pytest tests/test_security_headers.py -q`. | CSP allows inline scripts/styles because current UI uses them. | Move inline JS/CSS to static files, then tighten CSP. |
| Runtime artifact hygiene | DONE | `.gitignore` now excludes runtime data, dist archives and temp files. | `.gitignore` | `git status --short` should not list `data/`, `dist/`, `.tmp-*`, `docs/verification/`. | Existing local artifacts remain on disk. | Keep release packaging from clean staging. |
| Worker onboarding | DONE | Existing workflow supports photo/CV/document upload, CV parsing, consents, Professional DNA and dashboard. | existing onboarding modules | Existing onboarding tests pass. | Uses MVP identity header/cookie. | Replace with real auth sessions. |
| Employer onboarding | DONE | Company profile, verification, locations, members and dashboard exist. | existing employer modules | Existing employer tests pass. | Production company verification still manual/admin. | Expand admin workflow and notification ledger. |
| Vacancies/applications/CRM | DONE | Recruitment pipeline covers vacancies, public job pages, applications, stages, interviews, evaluations and offers. | existing recruitment modules | Existing recruitment tests pass. | Some APIs are not under `/api/v1`. | Add versioned API layer. |
| AI matching | DONE | Deterministic explainable matching engine is tested. | existing matching modules | Existing matching tests pass. | AI explanations do not replace human decisions. | Add more production-scale indexing later. |
| RODO/GDPR flows | PARTIAL | Consent, notice, retention and request primitives exist. | existing RODO modules | Existing privacy tests pass. | Legal text requires lawyer review; deletion is not full background purge. | Add deletion worker and legal review. |
| Authentication | PARTIAL | Admin login has hash support, sessions and rate limit. | existing auth code | Existing admin security tests pass. | Worker/employer flows still rely on MVP identity header/cookie. | Implement real user auth and deprecate spoofable headers. |
| RBAC | PARTIAL | Admin and some ownership checks exist. | existing API/services | Authorization tests pass for covered flows. | No single central RBAC service for every endpoint. | Introduce canonical permission map. |
| Database | PARTIAL | Repository boundary exists with JSON storage. | existing database modules | Tests use JSON DB successfully. | No SQL migrations or transactional DB. | Add SQLAlchemy/Alembic baseline without deleting JSON data. |
| EWU Telegram bot | PARTIAL | Webhook bridge and secret validation exist; server health works when env is configured. | `api/ewu_bot_webhook.py`, `ewu_bot/*` | `/api/ewu-bot/health`. | Same Render web service as ATLAS; no separate queue. | Move to worker/queue when budget allows. |
| Solana/escrow demo | PARTIAL | Colosseum demo credential and escrow proof workflow exists. | `services/colosseum_mvp.py` | `/demo`, `/api/demo/status`. | Demo proof links are not real Anchor transactions. | Add real Devnet program/client when keys and program IDs exist. |
