# ATLAS GDPR / RODO

ATLAS is designed according to GDPR/RODO privacy-by-design principles. This is not a final legal compliance claim and legal texts require lawyer review.

Implemented or partial:

- Privacy notice endpoint.
- Retention schedule endpoint.
- Consent records.
- Consent history.
- Data subject request creation.
- Data export primitives.
- Delete request primitive.
- Consent revocation primitive.
- Private file storage for documents.
- No PII in Colosseum/Solana demo proof hashes.
- First-party website analytics with anonymous visitor IDs, session cookies, bot/static request filtering, anonymized IP hashes, country-level-only location, aggregate reports, and no raw IP or personal data in public counters.

Website analytics privacy rules:

- `atlas_vid` identifies an anonymous visitor; `atlas_sid` identifies a 30-minute session.
- Raw IP addresses are not stored in analytics records; only a salted short hash is retained for abuse protection and deduplication.
- Public counters expose only enabled aggregate values: visitors, registered users, active vacancies, and successful employments.
- Optional external analytics snippets remain disabled unless their environment variables are configured and the consent flow permits them.
- Technical records should be retained only for the configured `ATLAS_ANALYTICS_RETENTION_DAYS` period, then deleted or aggregated.

Open items:

- Full background deletion worker.
- Legal review of policy texts.
- Processor/subprocessor register.
- User-facing account deletion confirmation flow.
- Production backup retention policy approval.
