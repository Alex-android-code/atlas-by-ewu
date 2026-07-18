import json

try:
    import google.generativeai as genai
except Exception:
    genai = None

try:
    from config import GEMINI_API_KEY
except Exception:
    GEMINI_API_KEY = ""

try:
    from learning import learning_context
except Exception:
    def learning_context(limit=12):
        return ""


SYSTEM = (
    "You are EWU AI Coordinator 4.0 for European Welders Union. "
    "Be warm, concise and professional. "
    "Never promise employment, documents, permits, salaries or visas. "
    "Use human language, no bureaucracy. Very light humour is allowed rarely."
)

MODEL = None

if genai and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        pass


def fallback(lang):
    return {
        "pl": "Rozumiem. Zapisuję i przejdziemy dalej krok po kroku.",
        "ua": "Зрозумів. Зберігаю і рухаємося далі крок за кроком.",
        "ru": "Понял. Записываю и идём дальше шаг за шагом.",
        "de": "Verstanden. Ich speichere es und wir gehen Schritt für Schritt weiter.",
        "es": "Entendido. Lo guardo y seguimos paso a paso.",
        "pt": "Entendido. Vou guardar e seguimos passo a passo.",
    }.get(lang, "Understood. Saved. We will proceed step by step.")


def get_model():
    global MODEL
    if MODEL:
        return MODEL
    if not genai or not GEMINI_API_KEY:
        return None
    for name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]:
        try:
            genai.GenerativeModel(name).generate_content("OK")
            MODEL = name
            return MODEL
        except Exception:
            continue
    return None


def ai_reply(lang, role, state, user_text):
    name = get_model()
    if not name:
        return fallback(lang)
    try:
        prompt = (
            f"{SYSTEM}\nLanguage: {lang}\nRole/module: {role}\n"
            f"{learning_context()}\n"
            f"Known data: {json.dumps(state.get('data', {}), ensure_ascii=False)}\n"
            f"User message: {user_text}\n"
            "Reply in the selected language. Maximum 220 characters. "
            "Write only a natural human acknowledgement of the user's answer. "
            "Do not ask any question. Do not request any new data. "
            "Do not repeat the user's text word for word."
        )
        text = genai.GenerativeModel(name).generate_content(prompt).text or fallback(lang)
        return text.strip()[:1000]
    except Exception:
        return fallback(lang)


def ai_next_turn(lang, role, state, user_text, next_question, field):
    name = get_model()
    if not name:
        ack = fallback(lang) if user_text else ""
        return f"{ack}\n\n{next_question}".strip()
    try:
        asked = state.get("asked_fields", [])
        prompt = (
            f"{SYSTEM}\n"
            f"Language: {lang}\n"
            f"Role/module: {role}\n"
            f"{learning_context()}\n"
            f"Known data: {json.dumps(state.get('data', {}), ensure_ascii=False)}\n"
            f"Already asked fields: {json.dumps(asked, ensure_ascii=False)}\n"
            f"User just wrote: {user_text}\n"
            f"Next required CRM field: {field}\n"
            f"Base question meaning: {next_question}\n\n"
            "Write one natural chat message as a human EWU coordinator.\n"
            "If the user wrote something, briefly acknowledge it in a warm way.\n"
            "Then ask ONLY the base question, but phrase it naturally.\n"
            "Ask exactly one question. Do not ask about any other field.\n"
            "Do not repeat questions for fields already present in Known data.\n"
            "Do not sound like a form or questionnaire.\n"
            "Maximum 320 characters."
        )
        text = genai.GenerativeModel(name).generate_content(prompt).text or ""
        text = text.strip()
        return text[:1000] if text else f"{fallback(lang)}\n\n{next_question}".strip()
    except Exception:
        ack = fallback(lang) if user_text else ""
        return f"{ack}\n\n{next_question}".strip()


def ai_summary(lang, role, data, messages):
    name = get_model()
    if not name:
        return "AI summary unavailable. Manual verification required."
    try:
        prompt = (
            "Create a concise internal EWU coordinator summary in Polish. "
            "Mention risks, readiness, documents and next step. "
            f"{learning_context()}\n"
            f"Role/module: {role}\nData: {json.dumps(data, ensure_ascii=False)}\n"
            f"Recent messages: {json.dumps(messages[-10:], ensure_ascii=False)}"
        )
        text = genai.GenerativeModel(name).generate_content(prompt).text or ""
        return text.strip()[:2000] or "AI summary unavailable. Manual verification required."
    except Exception:
        return "AI summary unavailable. Manual verification required."


def ask_ai(lang, category, state, text):
    return ai_reply(lang, category, state, text)


def make_ai_summary(lang, category, data, messages):
    return ai_summary(lang, category, data, messages)
