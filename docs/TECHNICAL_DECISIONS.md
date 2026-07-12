# TECHNICAL DECISIONS

## Initial Decisions

- ATLAS must use modular architecture.
- AI logic must be separated from UI components.
- UI language and conversation language must be separate.
- User-facing dashboards and admin dashboards must be separate.
- Candidate personal data must be protected by default.
- Matching logic should combine deterministic rules and AI explanations.
- Payments must unlock candidate access only after paid/admin-approved status.
- The system must be extendable without hardcoding professions.
- Taxonomy for professions, skills and services must be extendable later from admin.

## Architecture Boundaries

ATLAS must not be locked into:

- one profession;
- one country;
- one AI model;
- one recruitment workflow;
- one service provider.

## Data Protection Direction

Candidate private data, contacts, documents and photos should be treated as locked data.

Employer preview access should use anonymized candidate profiles until payment or admin approval is complete.

## I18n Direction

UI language, browser language and conversation language may differ. The system must keep these concepts explicit.

Initial language decisions:

- UI language and conversation language are separate.
- URL language overrides browser language.
- Manual user language choice is saved and overrides automatic browser detection.
- Default language is Polish (`pl`).
- Language switcher must not delete conversation or dashboard state.
- All visible UI strings must use i18n keys.

## Taxonomy Direction

Professions, skills, countries, services and partner categories should become admin-managed taxonomy, not fixed code lists.

## Conversation Behavior Direction

Conversation behavior is separated from data extraction.

Next-question logic should be deterministic first, using intent and known fields before any external AI classifier is introduced.

AI-generated or provider-generated public replies must be validated by the one-question rule before display.

Public chat helpers must not expose internal labels such as CRM status, risk level, trust score, verification pipeline or entity extraction.
