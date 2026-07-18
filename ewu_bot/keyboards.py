from telebot import types
from i18n import t


MAIN_MENU = [
    "candidate", "employer",
    "legalization", "relocation",
    "family", "business",
    "help", "language",
]

LANG_FLAGS = {
    "pl": "🇵🇱",
    "ua": "🇺🇦",
    "ru": "🇷🇺",
    "en": "🇬🇧",
    "de": "🇩🇪",
    "es": "🇪🇸",
    "pt": "🇵🇹",
}


def menu_label(lang, key):
    label = t(lang, key)
    if key == "language":
        return f"{LANG_FLAGS.get(lang, '🌐')} {label}"
    return label


def role_keyboard(lang="pl"):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(MAIN_MENU), 2):
        left = MAIN_MENU[i]
        right = MAIN_MENU[i + 1]
        kb.row(
            types.InlineKeyboardButton(menu_label(lang, left), callback_data=f"role:{left}"),
            types.InlineKeyboardButton(menu_label(lang, right), callback_data=f"role:{right}"),
        )
    kb.row(
        types.InlineKeyboardButton(menu_label(lang, "education"), callback_data="role:education"),
        types.InlineKeyboardButton(menu_label(lang, "protection"), callback_data="role:protection"),
    )
    kb.row(
        types.InlineKeyboardButton(menu_label(lang, "membership"), callback_data="role:membership"),
        types.InlineKeyboardButton(menu_label(lang, "referral"), callback_data="role:referral"),
    )
    kb.row(types.InlineKeyboardButton(menu_label(lang, "qualification"), callback_data="role:qualification"))
    return kb


def lang_keyboard(lang="pl"):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton("🇵🇱 Polski", callback_data="lang:pl"),
        types.InlineKeyboardButton("🇺🇦 Українська", callback_data="lang:ua"),
    )
    kb.row(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
    )
    kb.row(
        types.InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang:de"),
        types.InlineKeyboardButton("🇪🇸 Español", callback_data="lang:es"),
    )
    kb.row(types.InlineKeyboardButton("🇵🇹 Português", callback_data="lang:pt"))
    return kb


def contact_keyboard(lang="pl"):
    labels = {
        "pl": "Udostępnij telefon", "ua": "Поділитися телефоном", "ru": "Отправить телефон",
        "en": "Share phone", "de": "Telefon teilen", "es": "Enviar teléfono", "pt": "Enviar telefone",
    }
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(labels.get(lang, "Share phone"), request_contact=True))
    return kb


def yes_no_keyboard(lang="pl", prefix="yn"):
    yes = {"pl": "Tak", "ua": "Так", "ru": "Да", "en": "Yes", "de": "Ja", "es": "Sí", "pt": "Sim"}
    no = {"pl": "Nie", "ua": "Ні", "ru": "Нет", "en": "No", "de": "Nein", "es": "No", "pt": "Não"}
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(yes.get(lang, "Yes"), callback_data=f"{prefix}:yes"),
        types.InlineKeyboardButton(no.get(lang, "No"), callback_data=f"{prefix}:no"),
    )
    return kb


def status_keyboard(eid):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for stage in [
        "New Lead", "Application Completed", "Documents Verified", "Vacancy Matching",
        "Interview", "Contract Signed", "Departure", "Working", "Archived",
    ]:
        kb.add(types.InlineKeyboardButton(stage, callback_data=f"status:{eid}:{stage}"))
    return kb


def admin_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton("Search", callback_data="admin:help"),
        types.InlineKeyboardButton("Export", callback_data="admin:export"),
    )
    return kb
