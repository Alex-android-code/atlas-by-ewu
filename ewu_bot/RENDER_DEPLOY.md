# EWU bot on Render

EWU bot runs as a Render background worker from the same repository as ATLAS.

Render service:

- Name: `ewu-bot`
- Type: Background Worker
- Build command: `cd ewu_bot && pip install -r requirements.txt`
- Start command: `cd ewu_bot && python bot.py`
- Persistent disk: `/var/data/ewu_bot`

Required environment variables:

- `TELEGRAM_TOKEN`
- `GEMINI_API_KEY`
- `GOOGLE_SCRIPT_URL`
- `OPERATIONS_CHAT_ID`
- `LEADS_CHANNEL_ID`
- `ADMIN_CHAT_ID`

Runtime data is stored outside the repository in `/var/data/ewu_bot`.
