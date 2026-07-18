# ATLAS Stage 1 Security Foundation Report

Date: 2026-07-18

Status: in progress. This report covers the first security fixes implemented after the Stage 0 current-state audit.

## Implemented

1. Removed hardcoded admin access code from `api/app.py`.
   - The old literal `atlas` password is no longer accepted unless it is explicitly configured as an environment secret.
   - Admin login now reads from environment configuration.

2. Added server-side admin sessions.
   - Login creates an opaque `atlas_session` token.
   - Session lifetime is 8 hours.
   - Dashboard authorization no longer trusts a plain `atlas_role` cookie.

3. Kept service-token authorization for server/API use.
   - Requests with `x-atlas-admin-token` are still accepted when they match `ATLAS_ADMIN_TOKEN`.

4. Protected internal CRM endpoints.
   - `/api/dashboard`
   - `/api/candidates`
   - `/api/employers`
   - `/api/vacancies`
   - `/api/matches`
   - `/api/activity`
   - status, verification, document, match, and publish mutations.

5. Removed the public static EWU bot source package.
   - Deleted `api/static/downloads/EWU_bot/`.
   - Deleted `api/static/downloads/EWU_bot_public_files.zip`.
   - The real bot code remains in `ewu_bot/` and continues to run through the ATLAS webhook.

6. Added tests for admin security behavior.
   - `tests/test_admin_security.py`

7. Added admin login rate limiting.
   - Repeated login attempts from the same client are limited.
   - Excess attempts return HTTP `429`.

8. Added admin logout endpoint.
   - `/api/logout` clears the server-side admin session and browser cookie.

9. Added Telegram webhook body-size protection.
   - Oversized webhook payloads return HTTP `413`.
   - Invalid `content-length` returns HTTP `400`.

10. Added tests for Telegram webhook payload limits.
   - `tests/test_ewu_bot_webhook_security.py`

11. Added initial RODO/GDPR foundation.
   - Consent records.
   - Data subject request records.
   - Public privacy notice endpoint.
   - Public request intake for export/delete/rectification/restriction.
   - Admin-only request list, status update, and subject data export.

12. Added MVP storage hardening and backup foundation.
   - JSON writes now use locking plus atomic file replacement.
   - Added sanitized data backup script with manifest and checksums.

## Required Environment Variables

Production should define one of these:

- `ATLAS_ADMIN_PASSWORD_HASH`
- `ATLAS_ADMIN_PASSWORD`
- `ATLAS_ADMIN_TOKEN`

Recommended production setting:

- Use `ATLAS_ADMIN_PASSWORD_HASH` for dashboard login.
- Keep `ATLAS_ADMIN_TOKEN` only for trusted internal/API automation.

Supported hash format:

```text
pbkdf2_sha256$<iterations>$<salt>$<hex_digest>
```

## Verification

Commands run locally:

```bash
py -3.12 -m compileall -q api ewu_bot tests
py -3.12 -m unittest tests.test_admin_security
py -3.12 -m unittest discover -s tests
```

Result:

- New admin security tests: passed.
- New EWU bot webhook security tests: passed.
- Full existing unittest suite: passed.

## Remaining Security Work

- Add CSRF protection for dashboard mutations.
- Add failed-login audit events.
- Move JSON storage to PostgreSQL.
- Connect RODO consent prompts into Telegram and web UX.
- Add verified destructive deletion workflow.
- Add scheduled encrypted backup automation for Render persistent disk.
- Add dependency and secret scanning in CI.
