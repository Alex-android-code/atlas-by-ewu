# ATLAS Threat Model

## Assets

- candidate profile and CV data;
- credential evidence;
- employer vacancies;
- escrow agreement terms;
- API keys and session tokens;
- Solana wallet/signing authority;
- audit logs.

## Threats And Mitigations

| Threat | Mitigation |
| --- | --- |
| Malicious CV | file type allowlist, size limits, private storage, no prompt authority from CV |
| Prompt injection | AI output schema validation, deterministic matching scores, human review |
| Stolen session | server-side admin sessions, environment-backed admin token, rate limits |
| Unauthorized issuer | role checks on credential verify/reject/revoke/anchor |
| Forged credential | source document hash and issuer audit event |
| Double release | escrow state machine blocks release after released |
| Escrow manipulation | shares must equal total amount; demo max amount policy |
| Fake milestone approval | explicit employer action required and audited |
| Wallet substitution | AI never controls wallet keys; production signer must be policy-controlled |
| Exposed API keys | `.env.example` only, secrets through environment variables |
| Replay attack | future production Solana adapter should add nonce/account state checks |

## Residual Risks

The current MVP uses JSON storage and a demo Solana adapter. Production needs PostgreSQL, migrations, signed wallet integration, stricter RBAC, and external security review.
