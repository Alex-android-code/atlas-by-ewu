# Solana Devnet Integration

## Cluster

Default cluster: `devnet`

Environment variables:

- `SOLANA_RPC_URL`
- `SOLANA_CLUSTER`
- `SOLANA_CREDENTIAL_PROGRAM_ID`
- `SOLANA_ESCROW_PROGRAM_ID`
- `PLATFORM_TREASURY_PUBKEY`

## Credential Lifecycle

1. Candidate requests credential verification.
2. Issuer verifies or rejects.
3. ATLAS creates `credential_hash`.
4. Devnet proof is anchored through the Solana adapter.
5. UI/API returns transaction signature and Explorer link.

MVP adapter: deterministic Devnet proof links without private keys. Production adapter: Anchor client signed by authorized wallet/service signer.

## Escrow Lifecycle

1. Employer creates escrow agreement.
2. Employer funds escrow.
3. Employer explicitly approves milestone.
4. Employer releases funds.
5. Release signature and Explorer link are recorded.

Double release is blocked by application state.

## PII Rule

Only hashes and technical signatures may be on-chain. No CV content or personal profile fields are sent to Solana.
