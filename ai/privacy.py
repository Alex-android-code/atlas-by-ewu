"""Privacy helpers for safe AI context construction."""

from __future__ import annotations

import re
from dataclasses import asdict, is_dataclass
from typing import Any


SENSITIVE_KEYS = {
    "passport",
    "passport_number",
    "document_number",
    "pesel",
    "bank_account",
    "iban",
    "address",
    "home_address",
    "medical",
    "medical_data",
    "family",
    "children",
    "crm_notes",
    "internal_notes",
    "password",
    "api_key",
}

PURPOSE_ALLOWED_KEYS = {
    "job_search": {
        "profession",
        "profession_code",
        "experience_years",
        "country",
        "current_country_code",
        "desired_country_code",
        "city",
        "ready_to_relocate",
        "languages",
        "certificates",
        "documents",
        "desired_salary",
        "salary_currency",
        "ready_from",
        "requirements",
        "expectations",
    },
    "chat": {
        "profession",
        "profession_code",
        "experience_years",
        "country",
        "current_country_code",
        "desired_country_code",
        "language",
        "languages",
        "current_step",
        "progress",
    },
    "matching": {
        "candidate_id",
        "vacancy_id",
        "profession_code",
        "experience_years",
        "country_code",
        "desired_country_code",
        "salary_min",
        "salary_max",
        "desired_salary",
        "required_languages",
        "languages",
        "required_documents",
        "documents",
        "requirements",
        "certificates",
    },
}


def mask_email(value: str) -> str:
    return re.sub(r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", r"\1***\2", str(value))


def mask_phone(value: str) -> str:
    return re.sub(r"(?<!\w)(\+?\d[\d\s().-]{6,}\d)(?!\w)", lambda m: m.group(1)[:3] + "***" + m.group(1)[-2:], str(value))


def mask_document_number(value: str) -> str:
    return re.sub(r"\b([A-ZА-ЯІЇЄ]{1,3})?(\d{4,})\b", lambda m: (m.group(1) or "") + "***" + m.group(2)[-2:], str(value), flags=re.IGNORECASE)


def mask_sensitive_text(value: str) -> str:
    return mask_document_number(mask_phone(mask_email(value)))


def build_safe_ai_context(profile: Any, *, role: str, purpose: str) -> dict[str, Any]:
    data = _to_plain_dict(profile)
    allowed = PURPOSE_ALLOWED_KEYS.get(purpose) or PURPOSE_ALLOWED_KEYS["chat"]
    safe: dict[str, Any] = {
        "role": str(role or "candidate"),
        "purpose": str(purpose or "chat"),
    }
    for key, value in data.items():
        normalized_key = str(key)
        if normalized_key.lower() in SENSITIVE_KEYS or normalized_key not in allowed:
            continue
        safe[normalized_key] = _mask_value(value)
    return safe


def _to_plain_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, dict) else {}
    return {
        key: item
        for key, item in getattr(value, "__dict__", {}).items()
        if not key.startswith("_")
    }


def _mask_value(value: Any) -> Any:
    if isinstance(value, str):
        return mask_sensitive_text(value)
    if isinstance(value, list):
        return [_mask_value(item) for item in value[:30]]
    if isinstance(value, dict):
        return {
            key: _mask_value(item)
            for key, item in value.items()
            if str(key).lower() not in SENSITIVE_KEYS
        }
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return mask_sensitive_text(str(value))
