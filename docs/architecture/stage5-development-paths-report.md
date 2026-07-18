# ATLAS Stage 5 Development Paths Report

Date: 2026-07-18

Status: foundation implemented.

## Implemented

1. Added development-path entities.
   - `TrainingProvider`
   - `TrainingProgram`
   - `TrainingProgramCompetency`
   - `Certification`
   - `MentorshipProgram`
   - `InternalTrainingProgram`
   - `PracticalAssessment`
   - `DevelopmentResource`
   - `TrainingRecommendation`

2. Added repositories.
   - `training_providers`
   - `training_programs`
   - `training_program_competencies`
   - `certifications`
   - `mentorship_programs`
   - `internal_training_programs`
   - `practical_assessments`
   - `development_resources`
   - `training_recommendations`

3. Added `DevelopmentRecommendationService`.
   - Recommends a development method from a skill gap.
   - Uses matching training programs when they cover the target competency level.
   - If no ready-made course exists, returns a direct no-course message and builds an alternative plan.
   - Supports non-course development methods such as mentorship, supervised work, practical assignment, shadowing, job rotation, self-study, portfolio evidence, test verification, and license exam.

4. Added admin-only API endpoint.
   - `POST /api/development/recommendations`

5. Added tests.
   - `tests/test_development_recommendations.py`

## Required Recommendation Fields

`TrainingRecommendation` contains:

- reason;
- competency;
- current level;
- target level;
- career goal link;
- vacancy link;
- recommended development method;
- alternatives;
- duration;
- estimated cost;
- expected result;
- priority;
- confidence score;
- sources;
- explanation.

## Important Rule

Partner status of a training provider or training center does not automatically increase recommendation confidence. Recommendation confidence is based on fit to competency need, not commercial relationship.

## Remaining Work

- Add UI for development recommendations.
- Add provider/program creation endpoints.
- Add certification and license catalog.
- Connect internal company training and mentorship records.
- Connect recommendation acceptance/decline workflow.
- Update user competency after completed development.
- Add RODO consent handling for employer-funded training proposals.

## Verification

Commands run locally:

```bash
py -3.12 -m unittest tests.test_development_recommendations
py -3.12 -m unittest discover -s tests
py -3.12 -m compileall -q api core database services scripts tests
```

Result:

- Development recommendation tests: passed.
- Full unittest suite: passed, 55 tests.
- Compileall: passed.

