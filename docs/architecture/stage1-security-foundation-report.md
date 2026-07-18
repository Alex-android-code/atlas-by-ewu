# ATLAS Stage 1 Security Foundation Report

Date: 2026-07-18

Status: started. This report covers the first security fixes implemented after the Stage 0 current-state audit.

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
- Full existing unittest suite: passed.

## Remaining Security Work

- Add CSRF protection for dashboard mutations.
- Add login rate limiting and failed-login audit events.
- Add request body size limit for Telegram webhook.
- Move JSON storage to PostgreSQL or add interim file locking.
- Add RODO consent/export/delete workflows.
- Add backup automation for Render persistent disk.
- Add dependency and secret scanning in CI.

