# ATLAS by EWU Deployment

## Recommended free option: Render

Render supports free Python web services and can deploy directly from GitHub.
Recommended public service name:

- `atlas-by-ewu`
- Default Render URL: `https://atlas-by-ewu.onrender.com`

Later, attach a custom domain such as:

- `atlasbyewu.com`
- `atlas-ewu.com`
- `app.atlasbyewu.com`

Use these settings:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn api.app:app --host 0.0.0.0 --port $PORT`
- Health check path: `/api/health`
- Root directory: repository root containing `api/`, `requirements.txt`, and `render.yaml`

The included `render.yaml` can be used as a Blueprint.

During Blueprint creation, Render will ask for:

- `GEMINI_API_KEY`

Paste the real key into Render as a secret value. Do not commit `.env`.

## Alternative: Koyeb

Koyeb can deploy FastAPI from GitHub or Docker.

Use:

- Run command: `uvicorn api.app:app --host 0.0.0.0 --port 8000`
- Port: `8000`

The included `Dockerfile` is portable for Koyeb, Fly.io, and other container hosts.

## Important

The current project uses JSON files for demo storage. Free hosts may reset local filesystem data on redeploy.
For a stable production system, move runtime data to PostgreSQL.

## Optional analytics and monitoring

Set these environment variables on the server when ready:

- `NEXT_PUBLIC_GA_MEASUREMENT_ID` for Google Analytics 4.
- `NEXT_PUBLIC_CLARITY_PROJECT_ID` for Microsoft Clarity.
- `NEXT_PUBLIC_SENTRY_DSN` for Sentry browser error monitoring.
- `ATLAS_ADMIN_TOKEN` for protected admin analytics API access without browser cookie login.

ATLAS does not send names, phone numbers, emails, documents, passwords, or tokens to analytics.
