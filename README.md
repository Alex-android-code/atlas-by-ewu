# ATLAS/EWU

ATLAS/EWU is a modular, country-configured platform skeleton for European worker and employer matching.

## Structure

- `bot.py` - example entry point and candidate registration flow.
- `agents/` - logical personal AI-agent roles.
- `memory/` - per-user memory model and storage adapters.
- `core/` - domain models.
- `api/` - FastAPI backend and coordinator dashboard.
- `configs/countries/` - country JSON configs.
- `configs/languages/` - language JSON files.
- `configs/professions/` - profession dictionaries.
- `services/` - business workflows and config loaders.
- `database/` - JSON MVP database and repositories.
- `ai/` - matching, scoring, summaries, and risk detection.
- `crm/` - coordinator pipeline logic.
- `notifications/` - message and channel adapters.
- `workflows/` - end-to-end operational workflows.

## Country Scaling Rule

Do not add logic like `if country == "Poland"`.

To add a country:

1. Add a JSON file to `configs/countries/`.
2. Use a 2-letter ISO country code.
3. Define documents, compliance, languages, currency, and work model.
4. Business services will load the config through `CountryConfigLoader`.

## Personal AI Agents

A personal AI agent in ATLAS is not a separate bot, account, or Telegram process.

It is a logical role inside one ATLAS Core. The same codebase routes each user to the right agent type and loads that user's own profile, memory, preferences, risks, last offers, and coordinator notes.

The principle is:

- one codebase;
- one database layer;
- separate memory and context per `user_id`;
- many agent roles inside ATLAS.

Current agent roles:

- `CandidateAgent` - works with profession, experience, current country, desired work country, documents, salary, ready date, languages, and offered vacancy history.
- `EmployerAgent` - works with company data, vacancies, people needed, rate, housing, contract type, requirements, and candidate history.
- `MatchingAgent` - compares `CandidateProfile` and `VacancyProfile`, then returns `match_score`, `reasons`, `risks`, and `recommendation`.
- `LegalAgent` - performs risk triage only. It does not provide final legal decisions.
- `CoordinatorAgent` - summarizes new candidates, employers, strong matches, risky cases, and manual-contact queues.
- `DocumentAgent` - checks required documents from country configs.

## Why This Is Not a Separate Bot

ATLAS should not create a separate Telegram bot for each candidate.

Telegram, WhatsApp, email, web chat, and CRM can all become channels connected to the same backend. Agents live in backend logic, not in a specific messaging platform.

## Adding a New Agent Type

1. Create a new file in `agents/`.
2. Inherit from `BaseAgent`.
3. Implement `respond()`.
4. Add the new role to `AgentRouter`.
5. Keep country-specific rules in JSON configs or compliance services, not inside the agent.

## Future OpenAI or Gemini Integration

The current agents use deterministic Python logic plus `MockAIProvider` through AI Gateway, so the architecture is testable without external AI credentials.

Later, real AI providers can be added behind the gateway adapter interface:

- `OpenAIProvider`;
- `GeminiModelProvider`.

Agents should call the provider for text generation, extraction, or reasoning, while profile loading, memory saving, routing, and compliance checks stay inside ATLAS Core.

## AI Gateway

AI Gateway is implemented in `ai/ai_gateway.py`.

Agents call:

```python
send_message_to_ai(user_id, agent_type, context, message)
```

The response format is:

```json
{
  "reply": "string",
  "action": "string or null",
  "confidence": 0.72,
  "handoff_required": false,
  "metadata": {}
}
```

Current provider:

- `MockAIProvider` - returns local test responses and does not call any external AI.

Future providers:

- `OpenAIProvider`
- `GeminiProvider`
- `ClaudeProvider`
- `LocalAIProvider`

Providers are connected through registry/adapter pattern. Do not add `if provider == "openai"` logic inside agents.

Run AI Gateway demo:

```bash
py -3.12 ai/demo_ai_gateway.py
```

## CRM Engine

The first CRM engine is implemented in `crm/crm_service.py`.

It can:

- create candidates;
- create employers;
- create vacancies;
- create documents;
- find candidates for a vacancy;
- save matches;
- build a coordinator dashboard.

The MVP uses `JsonDatabase` and repository classes:

- `CandidateRepository`;
- `EmployerRepository`;
- `VacancyRepository`;
- `MatchRepository`;
- `DocumentRepository`.

This keeps storage behind a repository layer, so PostgreSQL can later replace JSON files without rewriting agents or CRM workflows.

## Run Example

```bash
py -3.12 bot.py
```

## Run CRM Demo

```bash
py -3.12 crm/demo_crm.py
```

The demo creates two candidates, one employer, one vacancy, runs matching, saves the strongest match, and prints a coordinator summary.

## Run Operations Workflow Demo

```bash
py -3.12 workflows/demo_operations.py
```

The operations demo connects candidate onboarding, document checking, employer onboarding, legal risk triage, vacancy publishing, matching, and coordinator summary.

## API and Dashboard

Install API dependencies:

```bash
py -3.12 -m pip install -r requirements.txt
```

Run the API:

```bash
py -3.12 -m uvicorn api.app:app --reload --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/` - AI-first landing page.
- `http://127.0.0.1:8000/ai` - personal AI coordinator chat.
- `http://127.0.0.1:8000/dashboard` - coordinator dashboard after login.
- `http://127.0.0.1:8000/docs` - OpenAPI docs.

Coordinator demo login:

- access code: `atlas`

## AI Experience

The public user experience is built around conversation, not forms.

Flow:

1. Landing page.
2. AI chat.
3. Automatic profile builder.
4. Candidate timeline.
5. Matching.
6. Coordinator dashboard.
7. Employer dashboard later.

The chat endpoint is:

- `POST /api/ai/chat`

It calls AI Gateway with `MockAIProvider`, then updates candidate memory and profile automatically.

Candidate timeline steps:

- Registration
- Documents
- Matching
- Employer Review
- Interview
- Job Offer
- Arrival
- Working

The coordinator dashboard can:

- create candidates;
- create employers;
- create vacancies;
- run matching for a selected vacancy;
- update candidate, employer, vacancy, and match statuses;
- mark candidate documents as received;
- show activity log;
- show manual-contact cases, risky cases, open vacancies, and strong matches.

Initial endpoints:

- `GET /api/health`
- `POST /api/ai/chat`
- `GET /api/dashboard`
- `GET /api/candidates`
- `POST /api/candidates`
- `PATCH /api/candidates/{candidate_id}/status`
- `PATCH /api/candidates/{candidate_id}/documents-received`
- `GET /api/employers`
- `POST /api/employers`
- `PATCH /api/employers/{employer_id}/verify`
- `GET /api/vacancies`
- `POST /api/vacancies`
- `PATCH /api/vacancies/{vacancy_id}/status`
- `POST /api/vacancies/{vacancy_id}/match`
- `GET /api/matches`
- `PATCH /api/matches/{match_id}/status`
- `GET /api/activity`
- `POST /api/demo/seed`
