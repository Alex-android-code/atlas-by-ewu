# ATLAS Stage 7 Agent Collaboration Report

Date: 2026-07-18

Status: foundation implemented.

## Implemented

1. Added consent-aware collaboration entities.
   - `AgentCollaborationProposal`
   - `AgentConsentGrant`
   - `AgentCollaborationAuditEvent`

2. Added repositories.
   - `agent_collaboration_proposals`
   - `agent_consent_grants`
   - `agent_collaboration_audit_events`

3. Added services required by the brief.
   - `AgentCollaborationService`
   - `UpskillingOpportunityService`
   - `EmployerFundedTrainingService`
   - `ConsentAwareMatchingService`

4. Added API endpoints.
   - `POST /api/agent-collaboration/proposals`
   - `POST /api/agent-collaboration/consents/grant`
   - `POST /api/agent-collaboration/consents/revoke`
   - `GET /api/agent-collaboration/proposals/{proposal_id}`

5. Added tests.
   - `tests/test_agent_collaboration.py`

## Consent-Aware Rules

Personal and corporate agents can collaborate only when:

- there is a defined legal basis;
- the consent scope is explicit;
- the data categories are allowed;
- an active grant exists;
- audit events are recorded;
- consent can be revoked.

Allowed data categories are intentionally narrow:

- `competency_summary`
- `skill_gap_summary`
- `development_preferences`
- `availability_window`

Unsupported broad categories such as full private profile are rejected.

## User Control

Before consent:

- employer-funded training can be prepared only as an offer;
- personal data cannot be shared with the employer/corporate agent.

After consent:

- sharing permission becomes active for the approved scope.

After revocation:

- permission is disabled again;
- proposal status changes to `consent_revoked`;
- audit event is written.

## Remaining Work

- Add UI and Telegram consent buttons.
- Add identity verification before consent grant/revoke.
- Connect grants to RODO `ConsentRecord` versioning.
- Add expiry and renewal of collaboration grants.
- Add consent-aware employer-funded training workflows.
- Add employee acceptance/decline workflow.
- Add audit export for enterprise compliance.

## Verification

Commands run locally:

```bash
py -3.12 -m unittest tests.test_agent_collaboration
py -3.12 -m unittest discover -s tests
py -3.12 -m compileall -q api core database services scripts tests
```

Result:

- Agent collaboration tests: passed.
- Full unittest suite: passed, 65 tests.
- Compileall: passed.

