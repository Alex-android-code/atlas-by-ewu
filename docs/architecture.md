# ATLAS Colosseum MVP Architecture

ATLAS is a FastAPI-based MVP for a verified AI workforce flow:

`Profile -> Verify -> Match -> Hire -> Settle`

## Frontend

The current web layer is server-rendered HTML from `api/app.py` and static assets under `api/static/`. It includes landing pages, onboarding, employer recruitment, matching explanations, dashboards, and `/demo` for the Colosseum flow.

## Backend

FastAPI exposes the operational API. Runtime persistence uses `JsonDatabase` through repository classes so the MVP runs locally and on Render free tier. PostgreSQL/Alembic are planned for production scale.

## AI Layer

AI access is isolated in `ai/` and `services/gemini_service.py`. The matching engine is deterministic; AI may explain or assist, but must not hire, reject, verify credentials, sign transactions, or release escrow.

## Off-Chain Storage

Profiles, CV parse results, consents, credentials, escrow agreements, and audit events are stored off-chain. File uploads use private local storage under `ATLAS_DATA_DIR`.

## Solana Programs

The MVP has a Solana Devnet adapter in `services/colosseum_mvp.py`. It creates proof hashes and Explorer-ready Devnet links without storing PII on-chain. Anchor programs are documented placeholders for the next step:

- `atlas-credential`
- `atlas-escrow`

## Role Separation

Roles are candidate, employer, issuer, recruiter, and admin. Human confirmations are mandatory for profile confirmation, credential verification, hiring milestone approval, and escrow release.
