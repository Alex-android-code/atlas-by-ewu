# ATLAS Stage 3 Dynamic AI Dialogue Report

Date: 2026-07-18

Status: foundation implemented.

## Implemented

1. Added persistent dynamic interview session model.
   - `DynamicInterviewSession`
   - Stores user, role, language, status, current field, completed fields, profile data, contradictions, and history.

2. Added repository.
   - `DynamicInterviewSessionRepository`
   - Collection: `dynamic_interview_sessions`

3. Added services required by the brief.
   - `DynamicInterviewService`
   - `QuestionGenerationService`
   - `AnswerAnalysisService`
   - `CompetencyExtractionService`
   - `ContradictionDetectionService`
   - `ProfessionalProfileBuilder`

4. Added dynamic interview rules.
   - One question per step.
   - Skip fields that are already known.
   - Preserve unfinished sessions.
   - Return to the same field when an answer is empty.
   - Detect contradictions and keep the interview on the field that needs clarification.
   - Extract competency names from the competency step.
   - Persist extracted competencies as `self_declared`, not verified facts.

5. Added public API endpoints.
   - `POST /api/interview/start`
   - `POST /api/interview/answer`

6. Added tests.
   - `tests/test_dynamic_interview.py`

## Important Boundaries

This stage creates the deterministic interview engine foundation. It does not yet replace all existing public chat behavior and does not yet call Gemini for question generation.

The design keeps AI replaceable: future LLM-based analysis can plug into `QuestionGenerationService` and `AnswerAnalysisService` while preserving the one-question rule, contradiction handling, and persistence model.

## Remaining Work

- Connect the web/Telegram UX to `/api/interview/start` and `/api/interview/answer`.
- Add RODO consent gate before starting profile interview.
- Add AI-assisted question generation behind the deterministic guardrails.
- Add richer answer parsing for experience, dates, documents, countries, and employer requirements.
- Connect evidence answers to `CompetencyEvidence`.
- Add interview depth modes.
- Add resume UI for unfinished interviews.
- Add language-specific natural phrasing for more languages.

## Verification

Commands run locally:

```bash
py -3.12 -m unittest tests.test_dynamic_interview
py -3.12 -m unittest discover -s tests
py -3.12 -m compileall -q api core database services scripts tests
```

Result:

- Dynamic interview tests: passed.
- Full unittest suite: passed, 46 tests.
- Compileall: passed.

