# ATLAS Stage 1 RODO Foundation Report

Date: 2026-07-18

Status: initial foundation implemented.

## Implemented

1. Added RODO domain models.
   - `ConsentRecord`
   - `DataSubjectRequest`

2. Added JSON-backed repositories.
   - `ConsentRepository`
   - `DataSubjectRequestRepository`

3. Added `RodoService`.
   - Privacy notice metadata.
   - Consent recording.
   - Data subject request intake.
   - Admin status updates.
   - Admin subject data export.

4. Added public API endpoints.
   - `GET /api/privacy/notice`
   - `POST /api/rodo/consents`
   - `POST /api/rodo/requests`

5. Added admin-only API endpoints.
   - `GET /api/admin/rodo/requests`
   - `PATCH /api/admin/rodo/requests/{request_id}`
   - `GET /api/admin/rodo/export/{subject_id}`

6. Added tests.
   - `tests/test_rodo_service.py`
   - Admin protection coverage in `tests/test_admin_security.py`

## Important Boundaries

This stage does not automatically delete production data. Deletion is now represented as a controlled data subject request. Actual destructive deletion should be implemented after identity verification, retention rules, audit logging, and backup/restore controls are in place.

## Remaining Work

- Add consent prompts to Telegram and web onboarding.
- Add privacy notice UI links in user-facing flows.
- Add verified deletion workflow.
- Add export delivery workflow.
- Add retention policy enforcement.
- Add processor register document.
- Add AI data-minimization layer before Gemini calls.
- Move RODO records to PostgreSQL during storage migration.

## Verification

Commands run locally:

```bash
py -3.12 -m compileall -q api core database services tests
py -3.12 -m unittest discover -s tests
```

Result:

- Full unittest suite: passed, 33 tests.

