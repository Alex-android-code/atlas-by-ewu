import json
import os
from datetime import datetime, timezone

from .config import EWU_DATA_DIR
from .crm import ensure_dirs, log_error


def _learning_dir():
    ensure_dirs()
    path = os.path.join(EWU_DATA_DIR, "Learning")
    os.makedirs(path, exist_ok=True)
    return path


def _append_jsonl(filename, payload):
    path = os.path.join(_learning_dir(), filename)
    payload = {"time": datetime.now(timezone.utc).isoformat(), **payload}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return path


def save_feedback(user_id, lang, role, text, data=None):
    return _append_jsonl("feedback.jsonl", {
        "user_id": user_id,
        "lang": lang,
        "role": role,
        "text": text,
        "ewu_id": (data or {}).get("EWU_ID", ""),
    })


def save_learning_note(admin_id, text):
    return _append_jsonl("approved_notes.jsonl", {
        "admin_id": admin_id,
        "text": text.strip(),
    })


def learning_context(limit=12):
    path = os.path.join(_learning_dir(), "approved_notes.jsonl")
    if not os.path.exists(path):
        return ""
    notes = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f.readlines()[-limit:]:
                item = json.loads(line)
                text = (item.get("text") or "").strip()
                if text:
                    notes.append(f"- {text}")
    except Exception as exc:
        log_error("learning_context", exc)
    if not notes:
        return ""
    return "Approved EWU learning notes for future answers:\n" + "\n".join(notes)
