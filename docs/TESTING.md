# ATLAS Testing

## Backend Tests

```powershell
cd D:\ATLAS_EWU
py -3.12 -m pytest -q
```

Current verified result on 2026-08-02:

```text
160 passed, 1 warning, 7 subtests passed
```

## Focused Security Tests

```powershell
py -3.12 -m pytest tests/test_security_headers.py tests/test_admin_security.py -q
```

## Local Startup Smoke Test

```powershell
py -3.12 -m uvicorn api.app:app --host 127.0.0.1 --port 8010
```

Then open:

```text
http://127.0.0.1:8010/api/health
```

## Browser E2E

There is a Playwright onboarding script:

```text
tests/playwright_onboarding_happy_path.js
```

It is not yet wired into the default Python test command.

## Test Data Rule

Do not use production API keys, production Telegram tokens, or real personal data in tests.
