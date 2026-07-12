"""Vacancy moderation, quality checks, and duplicate detection."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

from core.models import Employer, Vacancy


VACANCY_STATUSES = {
    "draft",
    "pending_review",
    "verified",
    "published",
    "rejected",
    "expired",
    "archived",
}

PUBLISHABLE_STATUSES = {"verified", "published"}
REJECTION_REASONS = {
    "insufficient_information",
    "suspicious_employer",
    "incorrect_contacts",
    "duplicate",
    "expired_or_not_actual",
    "illegal_or_discriminatory_content",
    "other",
}

SOURCE_VALUES = {
    "employer_manual",
    "coordinator_manual",
    "admin_manual",
    "partner_api",
    "external_import",
    "unknown",
}


def normalize_source(source: str | None) -> str:
    if source in SOURCE_VALUES:
        return source
    return "unknown"


def prepare_new_vacancy(
    vacancy: Vacancy,
    existing_vacancies: list[Vacancy],
    employer: Employer | None = None,
    source: str = "employer_manual",
) -> tuple[Vacancy, dict[str, Any]]:
    vacancy.status = "pending_review"
    vacancy.metadata["source"] = normalize_source(vacancy.metadata.get("source") or source)
    vacancy.metadata["verification_status"] = "pending_review"
    vacancy.metadata["last_updated_at"] = vacancy.metadata.get("last_updated_at") or vacancy.created_at
    if employer:
        vacancy.metadata["employer_verified"] = employer.verified
        vacancy.metadata["employer_name"] = employer.company_name
    report = analyze_vacancy(vacancy, existing_vacancies, employer)
    vacancy.metadata["quality_report"] = report
    vacancy.metadata["quality_warnings"] = report["warnings"]
    vacancy.metadata["recommended_status"] = report["recommended_status"]
    return vacancy, report


def analyze_vacancy(
    vacancy: Vacancy,
    existing_vacancies: list[Vacancy],
    employer: Employer | None = None,
) -> dict[str, Any]:
    warnings: list[dict[str, str]] = []
    required_checks = {
        "title": vacancy.title,
        "description": vacancy.metadata.get("description") or vacancy.metadata.get("requirements"),
        "country": vacancy.country_code,
        "city_or_region": vacancy.location,
        "contract_type": vacancy.metadata.get("contract_type"),
        "salary": vacancy.salary_max or vacancy.metadata.get("salary_calculation"),
        "schedule": vacancy.metadata.get("schedule") or vacancy.metadata.get("work_schedule"),
        "requirements": vacancy.metadata.get("requirements"),
        "housing": vacancy.metadata.get("housing"),
        "contact_person": vacancy.metadata.get("contact_person") or (employer.company_name if employer else None),
        "phone_or_email": _contact_available(vacancy, employer),
        "employer_name": employer.company_name if employer else vacancy.metadata.get("employer_name"),
    }
    for key, value in required_checks.items():
        if _empty(value):
            warnings.append({"code": f"missing_{key}", "message": f"Required field is missing: {key}"})

    description = " ".join(str(item) for item in _as_list(vacancy.metadata.get("requirements")))
    description += " " + str(vacancy.metadata.get("description") or "")
    if len(description.strip()) < 40:
        warnings.append({"code": "short_description", "message": "Vacancy description is too short."})
    if _has_suspicious_link(description):
        warnings.append({"code": "suspicious_link", "message": "Suspicious link found in vacancy text."})
    if vacancy.salary_min and vacancy.salary_max and vacancy.salary_min > vacancy.salary_max:
        warnings.append({"code": "salary_range_invalid", "message": "Salary minimum is higher than maximum."})
    if vacancy.currency and vacancy.country_code == "PL" and vacancy.currency not in {"PLN", "EUR"}:
        warnings.append({"code": "salary_currency_mismatch", "message": "Salary currency does not match vacancy country."})
    duplicate_ids = find_potential_duplicates(vacancy, existing_vacancies)
    for duplicate_id in duplicate_ids:
        warnings.append({"code": "possible_duplicate", "message": f"Possible duplicate vacancy: {duplicate_id}"})

    recommended = "pending_review"
    if any(item["code"] == "possible_duplicate" for item in warnings):
        recommended = "pending_review"
    if any(item["code"].startswith("missing_") for item in warnings):
        recommended = "pending_review"

    return {
        "vacancy_id": vacancy.id,
        "complete": not any(item["code"].startswith("missing_") for item in warnings),
        "warnings": warnings,
        "possible_duplicate_ids": duplicate_ids,
        "recommended_status": recommended,
    }


def find_potential_duplicates(vacancy: Vacancy, existing_vacancies: list[Vacancy]) -> list[str]:
    duplicates: list[str] = []
    for existing in existing_vacancies:
        if existing.id == vacancy.id:
            continue
        same_core = (
            existing.employer_id == vacancy.employer_id
            and existing.profession_code == vacancy.profession_code
            and (existing.location or "").casefold() == (vacancy.location or "").casefold()
            and float(existing.salary_min or 0) == float(vacancy.salary_min or 0)
            and float(existing.salary_max or 0) == float(vacancy.salary_max or 0)
        )
        existing_text = " ".join(_as_list(existing.metadata.get("requirements"))) + " " + str(existing.metadata.get("description") or "")
        vacancy_text = " ".join(_as_list(vacancy.metadata.get("requirements"))) + " " + str(vacancy.metadata.get("description") or "")
        similar_description = bool(existing_text.strip() and vacancy_text.strip()) and SequenceMatcher(
            None,
            existing_text.casefold(),
            vacancy_text.casefold(),
        ).ratio() >= 0.72
        if same_core or similar_description:
            duplicates.append(existing.id)
    return duplicates


def first_vacancies_report(vacancies: list[Vacancy], employers: list[Employer], limit: int = 5) -> list[dict[str, Any]]:
    employer_by_id = {employer.id: employer for employer in employers}
    ordered = sorted(vacancies, key=lambda item: item.created_at)[:limit]
    report: list[dict[str, Any]] = []
    for vacancy in ordered:
        employer = employer_by_id.get(vacancy.employer_id)
        analysis = analyze_vacancy(vacancy, vacancies, employer)
        report.append(
            {
                "vacancy_id": vacancy.id,
                "title": vacancy.title,
                "employer": employer.company_name if employer else vacancy.employer_id,
                "source": vacancy.metadata.get("source", "unknown"),
                "created_at": vacancy.created_at,
                "data_complete": analysis["complete"],
                "risks": analysis["warnings"],
                "recommended_status": "pending_review" if vacancy.status not in PUBLISHABLE_STATUSES else vacancy.status,
            }
        )
    return report


def _contact_available(vacancy: Vacancy, employer: Employer | None) -> bool:
    return bool(
        vacancy.metadata.get("contact_phone")
        or vacancy.metadata.get("contact_email")
        or (employer and (employer.contact_phone or employer.contact_email))
    )


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def _empty(value: Any) -> bool:
    if value is False:
        return False
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return len(value) == 0
    return False


def _has_suspicious_link(text: str) -> bool:
    lowered = text.casefold()
    return any(marker in lowered for marker in ("bit.ly", "tinyurl", "t.me/", "wa.me/", "http://"))
