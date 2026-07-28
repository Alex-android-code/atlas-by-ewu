# 2-3 Minute Colosseum Demo Flow

1. Open `/demo`.
2. Click `Seed Demo`.
3. Show demo status: candidate, employer, vacancy, credential, escrow.
4. Open the credential block and point to:
   - `status: verified`;
   - `credential_hash`;
   - `solana_signature`;
   - `explorer_url`.
5. Open escrow block and point to:
   - total commission;
   - recruiter, partner, and platform shares;
   - `human_approval_required`;
   - `ai_release_allowed: false`.
6. Run matching through `/api/matching/run` or the employer matching UI.
7. Explain the control model:
   - AI suggested;
   - user confirmed;
   - issuer verified;
   - employer approved;
   - on-chain confirmed.
8. Click `Reset` to return the demo to its start state.

Core message: ATLAS connects AI profile structuring, explainable matching, human credential verification, and Devnet-settled recruitment commission proof.
