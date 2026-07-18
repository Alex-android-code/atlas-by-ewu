import os
import time

from config import LEADS_CHANNEL_ID, OPERATIONS_CHAT_ID
from crm import log_error
from keyboards import status_keyboard


def _send_with_retry(fn, source):
    for attempt in range(1, 4):
        try:
            return fn()
        except Exception as exc:
            log_error(source, exc)
            time.sleep(attempt)
    return False


def operations(bot, text, document=None, ewu_id=None):
    if not OPERATIONS_CHAT_ID:
        return False

    def send():
        bot.send_message(
            OPERATIONS_CHAT_ID,
            text,
            reply_markup=status_keyboard(ewu_id) if ewu_id else None,
        )
        if document and os.path.exists(document):
            with open(document, "rb") as f:
                bot.send_document(OPERATIONS_CHAT_ID, f)
        return True

    return _send_with_retry(send, "operations_notify")


def leads(bot, text):
    if not LEADS_CHANNEL_ID:
        return False
    return _send_with_retry(lambda: bot.send_message(LEADS_CHANNEL_ID, text) or True, "leads_notify")
