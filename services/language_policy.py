"""Language policy utilities for ATLAS by EWU.

This module mirrors the frontend i18n rules so backend tests and future admin
metadata can reason about UI language and conversation language separately.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import parse_qs

from core.languages import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES


SUPPORTED_LANGUAGE_SET = set(SUPPORTED_LANGUAGES)


@dataclass(frozen=True)
class LanguageState:
    ui_language: str
    conversation_language: str | None
    source: str
    confidence: float
    language_detected_at: str


def is_supported_language(lang: str | None) -> bool:
    return normalize_language_code(lang) in SUPPORTED_LANGUAGE_SET


def normalize_language_code(value: str | None) -> str | None:
    if not value:
        return None
    code = value.strip().lower().split("-")[0].split("_")[0]
    return code if code in SUPPORTED_LANGUAGE_SET else None


def get_language_from_url(pathname: str = "", query_string: str = "") -> str | None:
    prefix = normalize_language_code((pathname or "/").strip("/").split("/")[0])
    if prefix:
        return prefix
    query = parse_qs((query_string or "").lstrip("?"))
    return normalize_language_code((query.get("lang") or [None])[0])


def detect_initial_ui_language(
    *,
    saved_language: str | None = None,
    url_pathname: str = "",
    url_query_string: str = "",
    browser_language: str | None = None,
) -> LanguageState:
    url_language = get_language_from_url(url_pathname, url_query_string)
    ordered = (
        ("url", url_language),
        ("saved", normalize_language_code(saved_language)),
        ("browser", normalize_language_code(browser_language)),
        ("default", DEFAULT_LANGUAGE),
    )
    for source, language in ordered:
        if language in SUPPORTED_LANGUAGE_SET:
            return LanguageState(
                ui_language=language,
                conversation_language=None,
                source=source,
                confidence=0.95 if source in {"url", "saved"} else 0.75,
                language_detected_at=datetime.now(timezone.utc).isoformat(),
            )
    return LanguageState(
        ui_language=DEFAULT_LANGUAGE,
        conversation_language=None,
        source="default",
        confidence=0.5,
        language_detected_at=datetime.now(timezone.utc).isoformat(),
    )


def detect_conversation_language_from_text(text: str | None) -> str | None:
    if not text:
        return None
    value = text.lower()
    if any(ch in value for ch in "іїєґ") or any(word in value for word in ("потріб", "шукаю", "працю", "зварюв")):
        return "uk"
    if any(word in value for word in ("работ", "нужн", "ищу", "сотрудник", "сварщик", "зарплат")):
        return "ru"
    if any(ch in value for ch in "ąćęłńóśźż") or any(word in value for word in ("praca", "pracownik", "spawacz", "potrzeb", "wynagrodz")):
        return "pl"
    if any(ch in value for ch in "äöüß") or any(word in value for word in ("arbeit", "mitarbeiter", "lohn")):
        return "de"
    if any(ch in value for ch in "ñáéíóú") or any(word in value for word in ("trabajo", "empleados", "salario")):
        return "es"
    if any(ch in value for ch in "ãõç") or any(word in value for word in ("trabalho", "funcionários", "funcionarios", "salário")):
        return "pt"
    if any(word in value for word in ("job", "work", "employees", "workers", "salary", "documents")):
        return "en"
    return None
