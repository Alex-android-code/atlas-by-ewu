"""Internal analytics and privacy-safe event helpers for ATLAS."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from core.models import ActivityEvent, Candidate, Employer, Match, Vacancy, utc_now_iso
from database.repositories import ActivityRepository
from services.demo_data import is_demo_record


PII_KEYS = {
    "first_name",
    "last_name",
    "name",
    "email",
    "phone",
    "contact_email",
    "contact_phone",
    "documents",
    "document_files",
    "password",
    "token",
}

TRACKED_EVENTS = {
    "page_view",
    "landing_view",
    "create_profile_click",
    "employer_registration_click",
    "coordinator_click",
    "demo_click",
    "login_click",
    "language_change",
    "vacancy_list_view",
    "vacancy_view",
    "vacancy_apply_click",
    "profile_started",
    "profile_step_completed",
    "profile_completed",
    "profile_abandoned",
    "employer_form_started",
    "employer_form_completed",
    "vacancy_created",
    "vacancy_published",
    "vacancy_rejected",
    "form_error",
    "api_error",
}


def sanitize_event_params(params: dict[str, Any] | None) -> dict[str, Any]:
    """Drop PII before data is saved locally or sent to third-party analytics."""
    safe: dict[str, Any] = {}
    for key, value in (params or {}).items():
        normalized = key.lower()
        if normalized in PII_KEYS or any(marker in normalized for marker in ("email", "phone", "password", "token")):
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
    return safe


def record_event(
    activity: ActivityRepository,
    name: str,
    params: dict[str, Any] | None = None,
    actor_id: str = "system",
) -> ActivityEvent:
    event_name = name if name in TRACKED_EVENTS else "custom_event"
    safe_params = sanitize_event_params(params)
    return activity.add(
        ActivityEvent(
            entity_type="analytics",
            entity_id=event_name,
            action=event_name,
            old_value=None,
            new_value=None,
            actor_id=actor_id,
            note="privacy_safe_event",
            metadata=safe_params | {"recorded_at": utc_now_iso()},
        )
    )


def analytics_summary(
    candidates: list[Candidate],
    employers: list[Employer],
    vacancies: list[Vacancy],
    matches: list[Match],
    activity: list[ActivityEvent],
    days: int = 1,
    country: str | None = None,
    language: str | None = None,
    profession: str | None = None,
    traffic_source: str | None = None,
    user_role: str | None = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=max(days, 1))

    def in_range(value: str | None) -> bool:
        if not value:
            return False
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return False
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed >= since

    filtered_activity = [
        event
        for event in activity
        if in_range(event.created_at)
        and (not country or event.metadata.get("country") == country)
        and (not language or event.metadata.get("language") == language)
        and (not profession or event.metadata.get("profession") == profession)
        and (not traffic_source or event.metadata.get("traffic_source") == traffic_source)
        and (not user_role or event.metadata.get("user_role") == user_role)
    ]
    filtered_vacancies = [
        vacancy
        for vacancy in vacancies
        if in_range(vacancy.created_at)
        and not is_demo_record(vacancy)
        and (not country or vacancy.country_code == country)
        and (not profession or vacancy.profession_code == profession)
    ]
    filtered_candidates = [candidate for candidate in candidates if in_range(candidate.created_at)]
    filtered_employers = [employer for employer in employers if in_range(employer.created_at) and not is_demo_record(employer)]

    event_counts = Counter(event.action for event in filtered_activity)
    vacancy_status_counts = Counter(vacancy.status for vacancy in vacancies if not is_demo_record(vacancy))
    profile_created = len(filtered_candidates)
    profile_completed = event_counts.get("profile_completed", 0)
    profile_started = event_counts.get("profile_started", 0)

    return {
        "period_days": days,
        "has_data": bool(filtered_activity or filtered_vacancies or filtered_candidates or filtered_employers),
        "visits_today": event_counts.get("page_view", 0) + event_counts.get("landing_view", 0),
        "unique_users": len({event.actor_id for event in filtered_activity if event.actor_id != "system"}),
        "created_profiles": profile_created,
        "completed_profiles": profile_completed,
        "incomplete_profiles": max(profile_started - profile_completed, 0),
        "employers": len(filtered_employers),
        "new_vacancies": len(filtered_vacancies),
        "published_vacancies": vacancy_status_counts.get("published", 0),
        "pending_review_vacancies": vacancy_status_counts.get("pending_review", 0),
        "rejected_vacancies": vacancy_status_counts.get("rejected", 0),
        "vacancy_views": event_counts.get("vacancy_view", 0),
        "vacancy_apply_clicks": event_counts.get("vacancy_apply_click", 0),
        "profile_create_clicks": event_counts.get("create_profile_click", 0),
        "profile_creation_conversion": _rate(profile_created, event_counts.get("create_profile_click", 0)),
        "profile_completion_conversion": _rate(profile_completed, profile_started),
        "event_counts": dict(event_counts),
        "vacancy_status_counts": dict(vacancy_status_counts),
        "matches": len([match for match in matches if in_range(match.created_at)]),
    }


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 2)
