"""Build employer vacancy profile from conversation."""

from __future__ import annotations

import re
from typing import Any

from core.models import new_id, utc_now_iso
from memory.user_memory import UserMemory
from services.profile_builder import COUNTRY_ALIASES, PROFESSION_ALIASES


def update_employer_profile_from_message(memory: UserMemory, message: str, language: str = "en") -> dict[str, Any]:
    profile = dict(memory.profile_data)
    employer = dict(profile.get("employer") or {})
    vacancy = dict(profile.get("vacancy") or {})
    text = message.lower()

    profile["user_id"] = memory.user_id
    profile["preferred_language"] = language
    roles = set(profile.get("roles") or [])
    roles.add("employer")
    profile["roles"] = sorted(roles)
    profile["intent"] = "find_employees"

    employer["company_name"] = _detect_company(message, employer.get("company_name"))
    employer["country"] = _first_alias(text, COUNTRY_ALIASES, employer.get("country"))
    employer["contact_email"] = _detect_email(message, employer.get("contact_email"))
    employer["contact_phone"] = _detect_phone(message, employer.get("contact_phone"))

    vacancy["profession"] = _first_alias(text, PROFESSION_ALIASES, vacancy.get("profession"))
    vacancy["quantity"] = _detect_quantity(text, vacancy.get("quantity"))
    vacancy["country"] = _first_alias(text, COUNTRY_ALIASES, vacancy.get("country") or employer.get("country"))
    vacancy["salary"] = _detect_salary(text, vacancy.get("salary"))
    vacancy["housing"] = _detect_boolean(text, vacancy.get("housing"), yes=("housing", "accommodation", "житло", "жилье", "mieszkanie"), no=("no housing", "без житла", "без жилья"))
    vacancy["transport"] = _detect_boolean(text, vacancy.get("transport"), yes=("transport", "транспорт", "dojazd"), no=("no transport", "без транспорту", "без транспорта"))
    vacancy["start_date"] = _detect_start_date(text, vacancy.get("start_date"))
    vacancy["requirements"] = sorted(set(vacancy.get("requirements", [])) | set(_detect_requirements(text)))
    if _has_vacancy_signal(vacancy):
        vacancy.setdefault("id", new_id("VAC-DRAFT"))
        vacancy.setdefault("status", "draft")
        vacancy.setdefault("created_at", utc_now_iso())

    profile["employer"] = employer
    profile["vacancy"] = vacancy
    messages = profile.get("messages", [])
    messages.append({"role": "user", "content": message})
    profile["messages"] = messages[-20:]
    memory.profile_data = profile
    memory.conversation_summary = f"{memory.conversation_summary}\nEmployer: {message}".strip()
    memory.preferences.update({"preferred_language": language, "role": "employer"})
    return profile


def _first_alias(text: str, aliases: dict[str, str], current: Any) -> Any:
    for phrase, value in aliases.items():
        if phrase in text:
            return value
    return current


def _detect_quantity(text: str, current: Any) -> int | None:
    match = re.search(r"(\d{1,3})\s?(people|workers|employees|pracownik|osob|osób|людей|працівник|работник)?", text)
    if match:
        return int(match.group(1))
    return current


def _detect_salary(text: str, current: Any) -> int | None:
    match = re.search(r"(\d{3,6})\s?(eur|euro|pln|zl|zł)?", text)
    if match:
        return int(match.group(1))
    return current


def _detect_boolean(text: str, current: Any, yes: tuple[str, ...], no: tuple[str, ...]) -> bool | None:
    if any(token in text for token in no):
        return False
    if any(token in text for token in yes):
        return True
    return current


def _detect_start_date(text: str, current: Any) -> str | None:
    if any(token in text for token in ("now", "immediately", "asap", "зараз", "сейчас", "od zaraz")):
        return "now"
    if any(token in text for token in ("july", "lipiec", "липень", "июль")):
        return "july"
    if any(token in text for token in ("august", "sierpień", "серпень", "август")):
        return "august"
    date = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    return date.group(1) if date else current


def _detect_requirements(text: str) -> list[str]:
    requirements = []
    if any(token in text for token in ("certificate", "certyfikat", "сертифікат", "сертификат")):
        requirements.append("certificate")
    if any(token in text for token in ("experience", "doświadczenie", "досвід", "опыт")):
        requirements.append("experience")
    if any(token in text for token in ("language", "język", "мова", "язык")):
        requirements.append("language")
    return requirements


def _detect_email(text: str, current: Any) -> str | None:
    match = re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", text)
    return match.group(0) if match else current


def _detect_phone(text: str, current: Any) -> str | None:
    match = re.search(r"\+?\d[\d\s().-]{7,}\d", text)
    return match.group(0) if match else current


def _detect_company(message: str, current: Any) -> str | None:
    match = re.search(r"(?:company|firma|компанія|компания)\s+([A-Za-zА-Яа-яІіЇїЄєҐґ0-9 .'-]{2,60})", message, flags=re.IGNORECASE)
    return match.group(1).strip() if match else current


def _has_vacancy_signal(vacancy: dict[str, Any]) -> bool:
    return any(
        vacancy.get(key)
        for key in ("profession", "quantity", "country", "salary", "housing", "transport", "start_date", "requirements")
    )
