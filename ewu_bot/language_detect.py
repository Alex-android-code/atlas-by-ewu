SUPPORTED_LANGS = {"pl", "ua", "uk", "ru", "en", "de", "es", "pt"}


def normalize_lang(code, default="pl"):
    value = (code or "").lower().split("-", 1)[0]
    if value == "uk":
        return "ua"
    if value in SUPPORTED_LANGS:
        return value
    return default


def detect_lang(text, default="pl"):
    s = (text or "").lower()

    ua_chars = set("іїєґ")
    if any(ch in s for ch in ua_chars) or any(
        word in s for word in ["робота", "звар", "документи", "працівник", "потрібна", "допомога"]
    ):
        return "ua"

    if any(
        word in s for word in ["работ", "свар", "документ", "помощ", "семья", "нужна", "нужен"]
    ):
        return "ru"

    if any(word in s for word in ["praca", "spawacz", "dokumenty", "pomoc", "rodzina"]):
        return "pl"

    if any(word in s for word in ["arbeit", "schweißer", "schweisser", "unterkunft", "hilfe"]):
        return "de"

    if any(word in s for word in ["trabajo", "soldador", "empresa", "familia", "ayuda"]):
        return "es"

    if any(word in s for word in ["trabalho", "soldador", "empresa", "família", "familia", "ajuda"]):
        return "pt"

    if any(word in s for word in ["work", "welder", "employer", "family", "support", "help"]):
        return "en"

    return default
