import os

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def env(name, default=""):
    return os.getenv(name, default).strip()


def project_path(value):
    if not value:
        return value
    return value if os.path.isabs(value) else os.path.join(BASE_DIR, value)


TELEGRAM_TOKEN = env("TELEGRAM_TOKEN")
GEMINI_API_KEY = env("GEMINI_API_KEY")
GOOGLE_SCRIPT_URL = env("GOOGLE_SCRIPT_URL")
OPERATIONS_CHAT_ID = env("OPERATIONS_CHAT_ID")
LEADS_CHANNEL_ID = env("LEADS_CHANNEL_ID")
ADMIN_CHAT_ID = env("ADMIN_CHAT_ID")

DEFAULT_LANG = env("DEFAULT_LANG", "pl")
BANNER_FILE = project_path(env("BANNER_FILE", "assets/ewu_banner.png"))
MENU_FILE = project_path(env("MENU_FILE", "assets/ewu_menu.png"))
LOGO_FILE = project_path(env("LOGO_FILE", "assets/ewu_logo.png"))
EWU_DATA_DIR = project_path(env("EWU_DATA_DIR", "EWU_Data"))
LOCAL_BACKUP_FILE = project_path(env("LOCAL_BACKUP_FILE", "EWU_Data/Backups/local_backup_leads.jsonl"))
PDF_DIR = project_path(env("PDF_DIR", "EWU_Data/PDF"))

SUPPORTED_LANGS = ["pl", "ua", "ru", "en", "de", "es", "pt"]
