# ATLAS Stage 6 Corporate AI Agent Report

Date: 2026-07-18

Status: foundation implemented.

## Implemented

1. Added corporate data entities.
   - `CorporateDepartment`
   - `CorporatePosition`
   - `CorporateEmployeeProfile`
   - `WorkforceDemandForecast`
   - `CorporateRecommendation`

2. Added repositories.
   - `corporate_departments`
   - `corporate_positions`
   - `corporate_employee_profiles`
   - `workforce_demand_forecasts`
   - `corporate_recommendations`

3. Added services required by the brief.
   - `CorporateAIAgentService`
   - `WorkforceAnalysisService`
   - `WorkforceDemandForecastService`
   - `CorporateSkillGapService`
   - `TrainVsHireService`
   - `PromotionPotentialService`
   - `RetentionRiskService`
   - `WorkforceDevelopmentPlanService`

4. Added admin-only API endpoints.
   - `POST /api/corporate/departments`
   - `POST /api/corporate/positions`
   - `POST /api/corporate/employees`
   - `POST /api/corporate/analyze`

5. Added tests.
   - `tests/test_corporate_ai.py`

## Corporate AI Capabilities

The foundation can analyze:

- company departments;
- positions;
- role functions;
- employee profiles;
- current headcount against required headcount;
- employer competency requirements;
- verified employee competencies;
- workforce competency gaps;
- demand forecast based on missing headcount;
- retention risk signals;
- train-vs-hire advisory choices.

## Safety Boundary

The corporate AI agent is advisory only.

Every corporate recommendation includes:

- `requires_human_decision = true`;
- forbidden automatic actions:
  - `fire`;
  - `demote`;
  - `block`;
  - `reject`;
  - `discipline`.

The system must not automatically fire, demote, block, reject, or discipline an employee.

## Remaining Work

- Add tenant-aware company accounts.
- Add consent-aware connection between personal and corporate agents.
- Add workforce dashboards.
- Add corporate data import.
- Add production-grade RBAC for company admins.
- Add audit log for corporate recommendations.
- Add forecast models for 3, 6, and 12 months.
- Add train-vs-hire cost model.
- Add internal promotion and workforce reserve workflows.

## Verification

Commands run locally:

```bash
py -3.12 -m unittest tests.test_corporate_ai
py -3.12 -m unittest discover -s tests
py -3.12 -m compileall -q api core database services scripts tests
```

Result:

- Corporate AI tests: passed.
- Full unittest suite: passed, 60 tests.
- Compileall: passed after clearing a stale Windows `services/__pycache__` file.

