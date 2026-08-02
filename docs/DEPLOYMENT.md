# ATLAS Deployment

## Local Run

```powershell
cd D:\ATLAS_EWU
py -3.12 -m pip install -r requirements.txt
py -3.12 -m uvicorn api.app:app --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/api/health`

## Required Environment Variables

Minimum:

```env
ATLAS_DATA_DIR=./data
ATLAS_AI_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
GEMINI_API_KEY=
ATLAS_ADMIN_TOKEN=
ATLAS_ADMIN_PASSWORD_HASH=
ATLAS_FILE_SIGNING_SECRET=
```

EWU bot server mode:

```env
TELEGRAM_TOKEN=
EWU_BOT_WEBHOOK_URL=https://atlas-by-ewu.onrender.com/api/ewu-bot/webhook
EWU_BOT_WEBHOOK_SECRET=
GOOGLE_SCRIPT_URL=
OPERATIONS_CHAT_ID=
LEADS_CHANNEL_ID=
ADMIN_CHAT_ID=
```

Optional:

```env
SENTRY_DSN=
NEXT_PUBLIC_SENTRY_DSN=
SOLANA_CLUSTER=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
```

Do not commit real secret values.

## Render

Current Render config is in `render.yaml`.

Health check:

```text
/api/health
```

Start command:

```text
uvicorn api.app:app --host 0.0.0.0 --port $PORT
```

Persistent disk:

```text
/var/data
```

## Production Notes

- Keep `ATLAS_DATA_DIR=/var/data`.
- Set all secret values in Render environment variables.
- Do not deploy from a dirty artifact folder.
- Run `py -3.12 -m pytest -q` before pushing.
- Add PostgreSQL before serious multi-user commercial traffic.
