# ATLAS Privacy Model

ATLAS is designed according to GDPR/RODO privacy-by-design principles. This is not a final legal compliance claim without an external legal audit.

## Off-Chain Data

Personal profile data, CV text, documents, consents, matching explanations, and employer communications remain off-chain.

## On-Chain Data

Only technical proofs are allowed on-chain:

- credential hash;
- escrow proof hash;
- transaction signature;
- program/account identifiers.

Names, email, phone, CV content, profile photos, nationality, and other PII must not be written on-chain.

## Consent

Consent records are stored with policy version, scope, decision, timestamp, and hashed technical metadata where applicable.

## User Rights

MVP endpoints:

- `GET /privacy/export`
- `POST /privacy/delete-request`
- `POST /privacy/revoke-consent`

Physical deletion can be completed by a background job. The MVP creates a clear deletion request record and audit event.

## Retention

Retention rules are exposed through `/api/privacy/retention` and can later be automated by scheduled cleanup jobs.
