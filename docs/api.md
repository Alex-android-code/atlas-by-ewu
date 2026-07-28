# ATLAS MVP API Overview

## Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

## Candidate And Profile

- `POST /api/auth/register`
- `GET /api/onboarding`
- `PATCH /api/onboarding`
- `POST /api/files/upload`
- `POST /api/cv/{file_id}/parse`
- `POST /api/cv/parse-jobs/{job_id}/confirm`
- `POST /api/onboarding/complete`

## Jobs And Matching

- `GET /jobs`
- `POST /jobs`
- `GET /jobs/{id}` public HTML page
- `GET /jobs/{id}.json` API alias
- `PATCH /jobs/{id}`
- `POST /jobs/{id}/match`
- `GET /jobs/{id}/candidates`
- `POST /api/matching/run`
- `GET /api/matching/{id}`
- `GET /api/matching/{id}/explanation`

## Credentials

- `POST /api/credentials/request`
- `GET /api/credentials`
- `GET /api/credentials/{id}`
- `POST /api/credentials/{id}/verify`
- `POST /api/credentials/{id}/reject`
- `POST /api/credentials/{id}/revoke`
- `POST /api/credentials/{id}/anchor-solana`

## Escrow

- `POST /api/escrows`
- `GET /api/escrows`
- `GET /api/escrows/{id}`
- `POST /api/escrows/{id}/fund`
- `POST /api/escrows/{id}/approve-milestone`
- `POST /api/escrows/{id}/release`
- `POST /api/escrows/{id}/dispute`
- `POST /api/escrows/{id}/refund`

## Privacy

- `GET /privacy/export`
- `POST /privacy/delete-request`
- `POST /privacy/revoke-consent`

## Demo

- `GET /demo`
- `POST /api/demo/seed`
- `POST /api/demo/reset`
- `GET /api/demo/status`
