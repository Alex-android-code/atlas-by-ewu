# ATLAS Stage 2 Competency Intelligence Report

Date: 2026-07-18

Status: foundation implemented.

## Implemented

1. Added universal competency entities.
   - `CompetencyCategory`
   - `Competency`
   - `CompetencyRelationship`
   - `ProfessionProfile`
   - `ProfessionCompetencyModel`
   - `UserCompetency`
   - `CompetencyEvidence`
   - `CompetencyAssessment`
   - `CompetencyConfidenceHistory`
   - `SkillGap`
   - `DevelopmentPlan`
   - `DevelopmentPlanStep`
   - `EmployerCompetencyRequirement`
   - `WorkforceCompetencyGap`
   - `UpskillingOpportunity`

2. Added JSON-backed repositories for all competency collections.

3. Added `CompetencyIntelligenceService`.
   - Normalizes and deduplicates competency names.
   - Records user competencies with source, confidence, verification status, evidence reference, years of experience, and visibility.
   - Enforces the rule that `ai_inferred` competency is not automatically verified.
   - Records employer competency requirements.
   - Generates skill gaps from employer requirements.
   - Creates development plan steps from skill gaps.
   - Returns a user competency map.

4. Added admin-only API endpoints.
   - `GET /api/competencies/users/{user_id}`
   - `POST /api/competencies/users`
   - `POST /api/competencies/employer-requirements`
   - `POST /api/competencies/skill-gaps`
   - `POST /api/competencies/development-plans`

5. Added tests.
   - `tests/test_competency_intelligence.py`
   - Admin protection coverage in `tests/test_admin_security.py`

## Design Notes

This implementation does not create hardcoded logic for one profession. Competencies are normalized, stored, and linked to users, employers, vacancies, and future profession models through generic IDs.

AI-inferred competencies remain unverified with conservative confidence. Verified status is reserved for sources such as document, employer, test, portfolio, training, or certification verification.

## Remaining Work

- Connect competency extraction to the dynamic AI interview.
- Connect document extraction to `CompetencyEvidence`.
- Add confidence history updates when evidence changes.
- Build workforce-level competency gap analysis for corporate accounts.
- Add public/user-facing competency visibility controls.
- Migrate competency collections to PostgreSQL.
- Add UI surfaces for competency map, gaps, and development plans.

## Verification

Commands run locally:

```bash
py -3.12 -m unittest discover -s tests
py -3.12 -m compileall -q api core database services scripts tests
```

Result:

- Full unittest suite: passed, 41 tests.
- Compileall: passed after clearing a stale Windows `core/__pycache__` file.

