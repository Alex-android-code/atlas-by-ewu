"""Public tone rules for the ATLAS coordinator."""

from __future__ import annotations


ACKNOWLEDGEMENTS: dict[str, list[str]] = {
    "pl": ["Rozumiem.", "Dobrze.", "To wazne.", "Ustalmy jedna rzecz."],
    "uk": [
        "\u0417\u0440\u043e\u0437\u0443\u043c\u0456\u0432.",
        "\u0414\u043e\u0431\u0440\u0435.",
        "\u0426\u0435 \u0432\u0430\u0436\u043b\u0438\u0432\u043e.",
        "\u0423\u0442\u043e\u0447\u043d\u0456\u043c\u043e \u043e\u0434\u0438\u043d \u043c\u043e\u043c\u0435\u043d\u0442.",
    ],
    "ru": [
        "\u041f\u043e\u043d\u044f\u043b.",
        "\u0425\u043e\u0440\u043e\u0448\u043e.",
        "\u041e\u0442\u043b\u0438\u0447\u043d\u043e, \u044d\u0442\u043e \u0432\u0430\u0436\u043d\u043e.",
        "\u0423\u0442\u043e\u0447\u043d\u0438\u043c \u043e\u0434\u0438\u043d \u043c\u043e\u043c\u0435\u043d\u0442.",
    ],
    "en": ["Understood.", "Good.", "That helps.", "Let us clarify one thing."],
    "de": ["Verstanden.", "Gut.", "Das hilft.", "Klaren wir einen Punkt."],
    "es": ["Entendido.", "Bien.", "Eso ayuda.", "Aclaremos un punto."],
    "pt": ["Entendido.", "Certo.", "Isso ajuda.", "Vamos esclarecer um ponto."],
}


FORBIDDEN_PUBLIC_TERMS = (
    "trust score",
    "risk level",
    "crm status",
    "crm",
    "verification pipeline",
    "data completeness insufficient",
    "low trust",
    "internal matching status",
    "user entity extraction",
    "entity extraction",
    "vacancy quality",
)


SAFE_FALLBACKS = {
    "pl": "Rozumiem. Ustalmy jedna rzecz.",
    "uk": "\u0417\u0440\u043e\u0437\u0443\u043c\u0456\u0432. \u0423\u0442\u043e\u0447\u043d\u0456\u043c\u043e \u043e\u0434\u0438\u043d \u043c\u043e\u043c\u0435\u043d\u0442.",
    "ru": "\u041f\u043e\u043d\u044f\u043b. \u0423\u0442\u043e\u0447\u043d\u0438\u043c \u043e\u0434\u0438\u043d \u043c\u043e\u043c\u0435\u043d\u0442.",
    "en": "Understood. Let us clarify one thing.",
    "de": "Verstanden. Klaren wir einen Punkt.",
    "es": "Entendido. Aclaremos un punto.",
    "pt": "Entendido. Vamos esclarecer um ponto.",
}


ROLE_ACKNOWLEDGEMENTS: dict[str, dict[str, str]] = {
    "candidate": {
        "pl": "Rozumiem, pomoge Ci to spokojnie ulozyc.",
        "uk": "\u0420\u043e\u0437\u0443\u043c\u0456\u044e, \u0434\u043e\u043f\u043e\u043c\u043e\u0436\u0443 \u0441\u043f\u043e\u043a\u0456\u0439\u043d\u043e \u0446\u0435 \u0441\u043a\u043b\u0430\u0441\u0442\u0438.",
        "ru": "\u041f\u043e\u043d\u044f\u043b, \u043f\u043e\u043c\u043e\u0433\u0443 \u0441\u043f\u043e\u043a\u043e\u0439\u043d\u043e \u044d\u0442\u043e \u0441\u043e\u0431\u0440\u0430\u0442\u044c.",
        "en": "I understand, I will help you sort this out calmly.",
        "de": "Verstanden, ich helfe dir, das ruhig zu ordnen.",
        "es": "Entiendo, te ayudo a ordenar esto con calma.",
        "pt": "Entendo, vou ajudar voce a organizar isto com calma.",
    },
    "employer": {
        "pl": "Rozumiem, przygotujmy to jako konkretne zgloszenie rekrutacyjne.",
        "uk": "\u0420\u043e\u0437\u0443\u043c\u0456\u044e, \u043f\u0456\u0434\u0433\u043e\u0442\u0443\u0439\u043c\u043e \u0446\u0435 \u044f\u043a \u0447\u0456\u0442\u043a\u0443 \u0440\u0435\u043a\u0440\u0443\u0442\u0438\u043d\u0433\u043e\u0432\u0443 \u0437\u0430\u044f\u0432\u043a\u0443.",
        "ru": "\u041f\u043e\u043d\u044f\u043b, \u043e\u0444\u043e\u0440\u043c\u0438\u043c \u044d\u0442\u043e \u043a\u0430\u043a \u0447\u0435\u0442\u043a\u0443\u044e \u0440\u0435\u043a\u0440\u0443\u0442\u0438\u043d\u0433\u043e\u0432\u0443\u044e \u0437\u0430\u044f\u0432\u043a\u0443.",
        "en": "Understood, let us turn this into a clear recruitment request.",
        "de": "Verstanden, machen wir daraus eine klare Rekrutierungsanfrage.",
        "es": "Entendido, convirtamos esto en una solicitud de seleccion clara.",
        "pt": "Entendido, vamos transformar isto num pedido de recrutamento claro.",
    },
}


ROLE_SAFE_FALLBACKS: dict[str, dict[str, str]] = {
    "candidate": {
        "pl": "Jasne. Ustalmy jeden najwazniejszy krok.",
        "uk": "\u0414\u043e\u0431\u0440\u0435. \u0423\u0442\u043e\u0447\u043d\u0456\u043c\u043e \u043e\u0434\u0438\u043d \u043d\u0430\u0439\u0432\u0430\u0436\u043b\u0438\u0432\u0456\u0448\u0438\u0439 \u043a\u0440\u043e\u043a.",
        "ru": "\u0425\u043e\u0440\u043e\u0448\u043e. \u0423\u0442\u043e\u0447\u043d\u0438\u043c \u043e\u0434\u0438\u043d \u0441\u0430\u043c\u044b\u0439 \u0432\u0430\u0436\u043d\u044b\u0439 \u0448\u0430\u0433.",
        "en": "Sure. Let us clarify the most important next step.",
        "de": "Klar. Lass uns den wichtigsten nachsten Schritt klaren.",
        "es": "Claro. Aclaremos el siguiente paso mas importante.",
        "pt": "Claro. Vamos esclarecer o proximo passo mais importante.",
    },
    "employer": {
        "pl": "Rozumiem. Ustalmy jeden kluczowy parametr oferty.",
        "uk": "\u0420\u043e\u0437\u0443\u043c\u0456\u044e. \u0423\u0442\u043e\u0447\u043d\u0456\u043c\u043e \u043e\u0434\u0438\u043d \u043a\u043b\u044e\u0447\u043e\u0432\u0438\u0439 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440 \u0432\u0430\u043a\u0430\u043d\u0441\u0456\u0457.",
        "ru": "\u041f\u043e\u043d\u044f\u043b. \u0423\u0442\u043e\u0447\u043d\u0438\u043c \u043e\u0434\u0438\u043d \u043a\u043b\u044e\u0447\u0435\u0432\u043e\u0439 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440 \u0432\u0430\u043a\u0430\u043d\u0441\u0438\u0438.",
        "en": "Understood. Let us clarify one key vacancy parameter.",
        "de": "Verstanden. Klaren wir einen wichtigen Parameter der Stelle.",
        "es": "Entendido. Aclaremos un parametro clave de la vacante.",
        "pt": "Entendido. Vamos esclarecer um parametro-chave da vaga.",
    },
}


TONE_PROFILES: dict[str, dict[str, str]] = {
    "candidate": {
        "relationship": "talk to the worker like a reliable friend and practical helper",
        "style": "warm, simple, direct, supportive, no pressure",
        "avoid": "bureaucratic language, cold scoring, corporate labels",
    },
    "employer": {
        "relationship": "talk to the employer like a business partner",
        "style": "professional, concise, commercially useful, precise",
        "avoid": "over-familiar language, vague promises, hidden operational terms",
    },
}


def normalize_audience(audience: str | None) -> str:
    value = (audience or "").strip().lower()
    if value in {"candidate", "worker", "employee"}:
        return "candidate"
    if value in {"employer", "business", "partner"}:
        return "employer"
    return "general"


def acknowledgement_for(language: str | None, audience: str | None = None) -> str:
    normalized = normalize_audience(audience)
    if normalized in ROLE_ACKNOWLEDGEMENTS:
        return ROLE_ACKNOWLEDGEMENTS[normalized].get(language or "en", ROLE_ACKNOWLEDGEMENTS[normalized]["en"])
    return ACKNOWLEDGEMENTS.get(language or "en", ACKNOWLEDGEMENTS["en"])[0]


def safe_fallback_for(language: str | None, audience: str | None = None) -> str:
    normalized = normalize_audience(audience)
    if normalized in ROLE_SAFE_FALLBACKS:
        return ROLE_SAFE_FALLBACKS[normalized].get(language or "en", ROLE_SAFE_FALLBACKS[normalized]["en"])
    return SAFE_FALLBACKS.get(language or "en", SAFE_FALLBACKS["en"])


def tone_profile_for(audience: str | None) -> dict[str, str]:
    return TONE_PROFILES.get(normalize_audience(audience), {})
