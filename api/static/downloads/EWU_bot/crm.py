import json
import os
import time
from datetime import datetime, timezone

import requests

from config import EWU_DATA_DIR, GOOGLE_SCRIPT_URL, LOCAL_BACKUP_FILE


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs():
    for name in ["Candidates", "Employers", "Photos", "PDF", "Backups", "Logs", "Learning"]:
        os.makedirs(os.path.join(EWU_DATA_DIR, name), exist_ok=True)


def log_error(source, error):
    ensure_dirs()
    payload = {"time": now_iso(), "source": source, "error": str(error)}
    path = os.path.join(EWU_DATA_DIR, "Logs", "errors.log")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def backup(table, data, reason="local backup"):
    ensure_dirs()
    os.makedirs(os.path.dirname(LOCAL_BACKUP_FILE), exist_ok=True)
    row = {"time": now_iso(), "table": table, "data": data, "reason": reason}
    with open(LOCAL_BACKUP_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def send_crm(action, table, data):
    backup(table, data, "before crm send")
    if not GOOGLE_SCRIPT_URL:
        return False, "NO_GOOGLE_SCRIPT_URL"

    payload = {"action": action, "table": table, "data": data}
    last_error = ""
    for attempt in range(1, 4):
        try:
            response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=25)
            text = response.text[:500]
            ok = response.status_code == 200 and '"ok":true' in response.text.replace(" ", "").lower()
            if ok:
                return True, text
            last_error = f"HTTP {response.status_code}: {text}"
            log_error("google_sheets", last_error)
        except Exception as exc:
            last_error = str(exc)
            log_error("google_sheets", exc)
        time.sleep(attempt)
    backup("EWU Backup", {"action": action, "table": table, "data": data, "error": last_error}, "crm failed")
    return False, last_error or "SHEETS_ERROR"


def update_status(eid, status, coordinator=""):
    return send_crm(
        "update_status",
        "Pipeline",
        {
            "EWU_ID": eid,
            "Current_stage": status,
            "Responsible_manager": coordinator,
            "Transition_date": now_iso(),
        },
    )


def load_backups(limit=50):
    if not os.path.exists(LOCAL_BACKUP_FILE):
        return []
    with open(LOCAL_BACKUP_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    result = []
    for line in lines:
        try:
            result.append(json.loads(line))
        except Exception:
            continue
    return result
