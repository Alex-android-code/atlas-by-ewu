# ATLAS Security Notes

## Implemented In MVP

- password hashing for admin login;
- server-side admin sessions;
- admin token support through environment variables;
- upload type and size validation in Universal File Upload;
- owner checks for private files;
- no secrets in frontend;
- audit logging for credential, escrow, privacy, and demo actions;
- role checks for Colosseum credential and escrow APIs;
- no AI access to wallet keys;
- no PII on-chain.

## Role Controls

Credential verification requires issuer role. Escrow creation, funding, milestone approval, and release require employer role. AI cannot perform final approval actions.

## Secrets

Secrets must be provided only through environment variables. `.env.example` contains variable names and safe defaults, not production keys.

## Incident Basics

If a token or key is exposed:

1. Rotate the key at the provider.
2. Remove it from Render/local env.
3. Audit activity logs.
4. Redeploy after confirming no secret is committed.
