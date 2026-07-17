# ATLAS Strategic Transformation - Stage 1 Report

## 1. Current Architecture

ATLAS is a FastAPI application with server-rendered HTML screens and JSON-backed MVP storage.

- `api/app.py` exposes public pages, AI chat, CRM APIs, admin analytics, language APIs and the new personal AI agent APIs.
- `api/landing.py`, `api/chat.py`, `api/dashboard.py`, `api/employer.py`, `api/login.py` contain current HTML experiences.
- `core/models.py` contains domain dataclasses.
- `database/json_database.py` and `database/repositories.py` provide repository-based JSON storage.
- `memory/memory_store.py` stores dialogue memory.
- `ai/ai_gateway.py` already provides provider-neutral AI access with Gemini and mock fallback.
- `configs/languages/*.json` contain localization strings for the existing multilingual UI.
- Runtime data can be moved to a persistent server disk through `ATLAS_DATA_DIR`.

## 2. Changed Files

- `api/app.py`
- `api/dependencies.py`
- `api/landing.py`
- `api/schemas.py`
- `core/models.py`
- `data/db/activity.json`
- `database/__init__.py`
- `database/repositories.py`
- `configs/languages/de.json`
- `configs/languages/en.json`
- `configs/languages/es.json`
- `configs/languages/pl.json`
- `configs/languages/pt.json`
- `configs/languages/ru.json`
- `configs/languages/uk.json`

## 3. Created Files

- `api/agent.py`
- `configs/subscriptions.json`
- `docs/strategic_transformation_stage1_request.md`
- `docs/strategic_transformation_stage1_report.md`
- `services/agent_profile_service.py`
- `tests/test_agent_profile_service.py`
- backup archive: `D:\ATLAS_EWU_BACKUP_STAGE1_20260717-191510.zip`

## 4. Database Schema

Existing collections remain active:

- `candidates`
- `employers`
- `vacancies`
- `matches`
- `documents`
- `activity`

New strategic collections:

- `users`
- `professional_profiles`
- `agent_memories`
- `agent_actions`
- `agent_recommendations`
- `career_goals`
- `opportunities`
- `user_preferences`
- `subscriptions`

The storage is still JSON-backed for MVP speed, but repository boundaries make PostgreSQL migration possible later.

## 5. Professional DNA

`ProfessionalDNA` was added as a dedicated model, separate from a simple candidate CV.

It contains:

- personal and contact information
- current location and relocation preferences
- professional summary and work experience
- education, skills, languages, certificates, licenses
- salary expectations and preferred roles/countries/industries
- career goals, strengths and development areas
- document status, profile photo, uploaded CV
- agent memory references and recommendations
- profile completeness and verification status

The onboarding service updates this structure one answer at a time.

## 6. Agent Memory

`AgentMemoryRecord` was added with:

- `user_id`
- `memory_type`
- `content`
- `source`
- `importance`
- `created_at`
- `updated_at`
- `is_active`

Supported memory types are prepared in the service:

- `fact`
- `preference`
- `career_goal`
- `restriction`
- `document`
- `skill`
- `experience`
- `conversation_summary`
- `agent_observation`

Current implementation writes onboarding answers into memory. It does not yet use vector search.

## 7. Subscription Feature Flags

`configs/subscriptions.json` defines Start, Medium and Pro without displaying prices.

Start includes:

- AI agent creation
- basic Professional DNA
- basic chat
- limited recommendations
- basic opportunity search

Medium adds:

- extended memory
- document control
- career strategy
- CV adaptation
- interview preparation

Pro adds:

- company analysis
- negotiation module
- human review
- personal support
- priority opportunities
- advanced analytics

Feature flags are returned through `/api/subscriptions/features/{plan}`.

## 8. New Screens

### `/agent/onboarding`

Dialog-style onboarding:

- one question per screen
- progress indicator
- back button
- autosave to API on every answer
- completion message: "Ваш AI-агент створений. Тепер він починає формувати вашу професійну карту."

### `/agent/dashboard`

Personal AI agent dashboard:

- agent status
- current activity
- Professional DNA completeness
- next recommended action
- modules: My AI Agent, Professional DNA, Opportunities, Documents, Career Strategy, Agent Settings
- unavailable/incomplete modules are marked as test mode or in development

## 9. Launch Instructions

Local:

```powershell
cd D:\ATLAS_EWU
py -3.12 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/agent/onboarding`
- `http://127.0.0.1:8000/agent/dashboard`

Server:

- deploy with `render.yaml`
- set `GEMINI_API_KEY`
- set `ATLAS_ADMIN_TOKEN`
- keep `ATLAS_DATA_DIR=/var/data`

## 10. Already Working

- Landing CTA is repositioned toward personal AI agent creation.
- New onboarding API returns a 15-step schema.
- Onboarding answers update Professional DNA.
- Onboarding answers create agent memory records.
- Completion creates Start subscription and seed recommendations.
- Dashboard API returns agent status, Professional DNA, actions, memories, recommendations and feature flags.
- Existing candidate/employer/vacancy APIs remain in place.
- AI gateway already supports provider abstraction and Gemini fallback through mock.

## 11. Temporary Mock/Test Functions

- Opportunities are structural/test-mode only.
- Documents module is structural/test-mode only.
- Career strategy module is test-mode for Medium/Pro and in-development for Start.
- Recommendations are seed recommendations, not yet produced by a real background AI process.
- Agent actions are logged but not executed autonomously.
- No autonomous application, negotiation, employer contact or legal consent action is implemented.

## 12. Next Technical Steps

1. Move JSON collections to PostgreSQL before serious production use.
2. Add user authentication separate from the current simple admin code.
3. Add localized text keys for every new onboarding/dashboard label.
4. Connect Professional DNA to existing candidate records.
5. Add file upload handling for photo and CV.
6. Add privacy controls: export data, delete account, delete agent memory.
7. Add role-based access control.
8. Add consent confirmation before any critical action.
9. Add background agent jobs for recommendations.
10. Add audit logs for agent decisions and user confirmations.

## 13. Risks And Technical Debt

- JSON storage is not suitable for multi-instance production.
- New agent screens currently use MVP inline HTML/CSS/JS.
- New screens are Ukrainian-first; full localization keys must be added next.
- Profile photo and CV steps currently save references/text, not actual uploaded files.
- Existing login is too simple for production.
- Some legacy text and old positioning still exists in secondary screens.
- `api/landing.py` has a pre-existing Python warning about an invalid escaped slash.
- `data/db/activity.json` had an extra closing brace at the end; it was repaired and all JSON database files now parse correctly.
