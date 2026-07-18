"""Telegram webhook bridge for the EWU bot."""

from __future__ import annotations

import importlib
import os
from functools import lru_cache

from fastapi import APIRouter, Header, HTTPException, Request

router = APIRouter()


@lru_cache(maxsize=1)
def _bot_module():
    return importlib.import_module("ewu_bot.bot")


def _webhook_secret() -> str:
    return os.getenv("EWU_BOT_WEBHOOK_SECRET", "").strip()


def configure_ewu_bot_webhook() -> None:
    webhook_url = os.getenv("EWU_BOT_WEBHOOK_URL", "").strip()
    telegram_token = os.getenv("TELEGRAM_TOKEN", "").strip()
    if not webhook_url or not telegram_token:
        return
    try:
        module = _bot_module()
        module.ensure_dirs()
        module.bot.remove_webhook()
        module.bot.set_webhook(
            url=webhook_url,
            secret_token=_webhook_secret() or None,
            drop_pending_updates=True,
        )
    except Exception as exc:
        print(f"EWU bot webhook configuration failed: {exc}", flush=True)


@router.get("/api/ewu-bot/health")
def ewu_bot_health() -> dict[str, bool | str]:
    return {
        "status": "ok",
        "telegram_configured": bool(os.getenv("TELEGRAM_TOKEN", "").strip()),
        "webhook_url_configured": bool(os.getenv("EWU_BOT_WEBHOOK_URL", "").strip()),
    }


@router.post("/api/ewu-bot/webhook")
async def ewu_bot_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, str]:
    expected_secret = _webhook_secret()
    if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

    module = _bot_module()
    body = await request.body()
    update = module.telebot.types.Update.de_json(body.decode("utf-8"))
    module.bot.process_new_updates([update])
    return {"status": "ok"}
