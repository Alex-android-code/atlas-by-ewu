# ATLAS Stage 4 Skill Gap Analysis Report

Date: 2026-07-18

Status: foundation implemented.

## Implemented

1. Added services required by the brief.
   - `SkillGapService`
   - `VacancyFitService`
   - `CareerPathAnalysisService`
   - `CompetencyVerificationService`

2. Extended skill gap analysis beyond a simple level difference.
   - Existing competencies.
   - Missing competencies.
   - Insufficiently verified competencies.
   - Expired certificates.
   - Gap criticality.
   - Employability now.
   - Training need.
   - Practice need.
   - Testing/verification need.
   - Confirmation-only cases.
   - Estimated time to close.
   - Estimated cost band.
   - Salary impact.
   - Available vacancies impact.
   - Alternative paths.

3. Extended API request model.
   - `/api/competencies/skill-gaps` now accepts saved employer/vacancy filters and ad-hoc target requirements.
   - Supports career goal and target country context.

4. Preserved the universal design.
   - The analysis is based on competencies and requirements, not hardcoded profession templates.
   - It can compare current user competencies against vacancy, employer, professional standard, future market, country, certification, and career-goal requirements once those requirement sources are connected.

5. Added tests.
   - `tests/test_skill_gap_analysis.py`

## API

Endpoint:

```text
POST /api/competencies/skill-gaps
```

Authorization:

- Admin-only.

Input supports:

- `user_id`
- `employer_id`
- `vacancy_id`
- `career_goal`
- `target_country`
- `target_requirements`

Output includes:

- `existing_competencies`
- `missing_competencies`
- `insufficiently_verified_competencies`
- `expired_certificates`
- `skill_gaps`
- `vacancy_fit`
- `training_needed`
- `practice_needed`
- `testing_needed`
- `confirmation_only`
- `alternative_paths`

## Important Boundaries

This stage does not yet search external course catalogs or certification databases. It classifies the gap and recommends the type of next action. Task 5 will expand development paths beyond courses.

The service does not make automatic employment decisions. It provides analysis for a coordinator, personal agent, or corporate agent.

## Remaining Work

- Connect country-specific certification requirements.
- Connect market demand signals.
- Connect profession standard requirements.
- Add salary and vacancy impact based on real market data.
- Add user-facing explanations in all supported languages.
- Connect results to development plans and training recommendations.
- Add corporate workforce-level skill gap aggregation.

## Verification

Commands run locally:

```bash
py -3.12 -m unittest tests.test_skill_gap_analysis
py -3.12 -m unittest discover -s tests
py -3.12 -m compileall -q api core database services scripts tests
```

Result:

- Skill gap tests: passed.
- Full unittest suite: passed, 51 tests.
- Compileall: passed.

