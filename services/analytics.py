"""Internal analytics and privacy-safe event helpers for ATLAS."""

from __future__ import annotations

import hashlib
import os
import re
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from core.models import ActivityEvent, Candidate, Employer, Match, Vacancy, utc_now_iso
from database.json_database import JsonDatabase
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


VISITORS_COLLECTION = "analytics_visitors"
SESSIONS_COLLECTION = "analytics_sessions"
PAGE_VIEWS_COLLECTION = "analytics_page_views"
ANALYTICS_EVENTS_COLLECTION = "analytics_events"
DAILY_SUMMARIES_COLLECTION = "analytics_daily_summaries"
PUBLIC_COUNTERS_COLLECTION = "analytics_public_counters"

SESSION_TIMEOUT_MINUTES = int(os.getenv("ATLAS_ANALYTICS_SESSION_MINUTES", "30"))
ONLINE_WINDOW_MINUTES = int(os.getenv("ATLAS_ANALYTICS_ONLINE_WINDOW_MINUTES", "5"))
ANALYTICS_CACHE_SECONDS = int(os.getenv("ATLAS_ANALYTICS_CACHE_SECONDS", "60"))
ANALYTICS_RETENTION_DAYS = int(os.getenv("ATLAS_ANALYTICS_RETENTION_DAYS", "180"))
ANALYTICS_ENABLED = os.getenv("ATLAS_ANALYTICS_ENABLED", "true").lower() not in {"0", "false", "no"}

BOT_USER_AGENT = re.compile(
    r"bot|crawl|spider|slurp|bingpreview|facebookexternalhit|telegrambot|whatsapp|"
    r"uptimerobot|pingdom|render|curl|wget|python-requests|httpclient",
    re.IGNORECASE,
)
STATIC_EXTENSIONS = {
    ".css",
    ".js",
    ".map",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".svg",
    ".ico",
    ".mp4",
    ".webm",
    ".woff",
    ".woff2",
    ".ttf",
}
EXCLUDED_PREFIXES = (
    "/api/health",
    "/health",
    "/static/",
    "/uploads/",
    "/favicon",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/admin",
    "/api/analytics",
    "/api/files",
    "/api/ewu-bot",
)

CONVERSION_EVENTS = {
    "registration": "visitor_to_registration",
    "profile_completed": "visitor_to_completed_profile",
    "job_application": "visitor_to_job_application",
    "vacancy_created": "employer_to_created_vacancy",
    "candidate_hired": "candidate_to_employment",
}

PUBLIC_COUNTER_DEFAULTS = {
    "total_visitors": {"label": "Visitors all time", "enabled": False},
    "registered_users": {"label": "Registered users", "enabled": False},
    "active_vacancies": {"label": "Active vacancies", "enabled": False},
    "successful_hires": {"label": "Successful employments", "enabled": False},
}


class WebsiteAnalyticsService:
    """Privacy-friendly first-party site analytics backed by the local database."""

    def __init__(self, database: JsonDatabase) -> None:
        self.database = database
        self._cache: dict[str, tuple[datetime, dict[str, Any]]] = {}
        self._rate_window: dict[str, list[datetime]] = defaultdict(list)

    def track_page_view(self, request: Any, response: Any) -> None:
        if not ANALYTICS_ENABLED or not self._should_track_request(request):
            return
        now = datetime.now(timezone.utc)
        visitor_id = _safe_id(request.cookies.get("atlas_vid")) or self._new_id("VIS")
        user_id = _request_user_id(request)
        ip_hash = self._ip_hash(request)
        rate_key = f"{visitor_id}:{ip_hash}"
        if self._rate_limited(rate_key, now):
            return

        session_id = _safe_id(request.cookies.get("atlas_sid"))
        session = self.database.get(SESSIONS_COLLECTION, session_id) if session_id else None
        if not session or self._session_expired(session, now):
            session_id = self._new_id("SES")
            session = self._new_session(session_id, visitor_id, user_id, request, now)
            self.database.insert(SESSIONS_COLLECTION, session_id, session)
        else:
            session["last_seen_at"] = _iso(now)
            session["user_id"] = session.get("user_id") or user_id
            session["page_view_count"] = int(session.get("page_view_count") or 0) + 1
            self.database.update(SESSIONS_COLLECTION, session_id, session)

        visitor = self.database.get(VISITORS_COLLECTION, visitor_id) or self._new_visitor(visitor_id, user_id, ip_hash, request, now)
        if user_id:
            visitor["user_id"] = user_id
        visitor["last_seen_at"] = _iso(now)
        visitor["visit_count"] = int(visitor.get("visit_count") or 0) + (1 if session.get("page_view_count") == 1 else 0)
        visitor["last_source"] = _traffic_source(request)
        visitor.setdefault("first_source", visitor["last_source"])
        self.database.update(VISITORS_COLLECTION, visitor_id, visitor)

        page_view = self._page_view(visitor_id, session_id, user_id, request, now)
        if self._is_duplicate_page_view(page_view, now):
            self._set_tracking_cookies(response, request, visitor_id, session_id)
            return
        self.database.insert(PAGE_VIEWS_COLLECTION, page_view["id"], page_view)
        self._update_daily_summary(page_view)
        self._cache.clear()
        self._set_tracking_cookies(response, request, visitor_id, session_id)

    def record_event(
        self,
        event_type: str,
        request: Any | None = None,
        params: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        safe_params = sanitize_event_params(params)
        visitor_id = _safe_id(request.cookies.get("atlas_vid")) if request else None
        session_id = _safe_id(request.cookies.get("atlas_sid")) if request else None
        user_id = user_id or (_request_user_id(request) if request else None)
        event = {
            "id": self._new_id("AEV"),
            "event_type": event_type,
            "conversion_type": CONVERSION_EVENTS.get(event_type),
            "anonymous_visitor_id": visitor_id or "unknown",
            "user_id": user_id,
            "session_id": session_id,
            "url": _request_url(request) if request else "",
            "page_name": _page_name(_request_path(request) if request else ""),
            "referrer": _safe_referrer(request) if request else "",
            "utm": _utm(request) if request else {},
            "device_type": _device_type(_user_agent(request) if request else ""),
            "browser": _browser(_user_agent(request) if request else ""),
            "operating_system": _operating_system(_user_agent(request) if request else ""),
            "anonymized_country": _country(request) if request else "unknown",
            "params": safe_params,
            "created_at": _iso(now),
        }
        self.database.insert(ANALYTICS_EVENTS_COLLECTION, event["id"], event)
        self._cache.clear()
        return event

    def summary(self, days: int = 30, filters: dict[str, str | None] | None = None) -> dict[str, Any]:
        days = max(1, min(int(days or 30), 365))
        filters = filters or {}
        cache_key = f"{days}:{sorted((key, value) for key, value in filters.items() if value)}"
        cached = self._cache.get(cache_key)
        now = datetime.now(timezone.utc)
        if cached and (now - cached[0]).total_seconds() < ANALYTICS_CACHE_SECONDS:
            return cached[1]

        page_views = [item for item in self.database.list(PAGE_VIEWS_COLLECTION) if self._matches_filters(item, filters)]
        sessions = [item for item in self.database.list(SESSIONS_COLLECTION) if self._matches_filters(item, filters)]
        visitors = {item["id"]: item for item in self.database.list(VISITORS_COLLECTION)}
        events = [item for item in self.database.list(ANALYTICS_EVENTS_COLLECTION) if self._matches_filters(item, filters)]

        result = self._build_summary(page_views, sessions, visitors, events, days, now)
        self._cache[cache_key] = (now, result)
        return result

    def public_counters(self) -> dict[str, Any]:
        settings = self.public_counter_settings()
        visitors = self.database.list(VISITORS_COLLECTION)
        users = self.database.list("users")
        vacancies = self.database.list("vacancies")
        events = self.database.list(ANALYTICS_EVENTS_COLLECTION)
        values = {
            "total_visitors": len(visitors),
            "registered_users": len(users),
            "active_vacancies": len([item for item in vacancies if item.get("status") in {"open", "published"}]),
            "successful_hires": len([item for item in events if item.get("event_type") == "candidate_hired"]),
        }
        return {
            "counters": [
                {"key": key, "label": cfg["label"], "value": values.get(key, 0), "enabled": bool(cfg.get("enabled"))}
                for key, cfg in settings.items()
                if cfg.get("enabled")
            ],
            "updated_at": utc_now_iso(),
        }

    def public_counter_settings(self) -> dict[str, dict[str, Any]]:
        stored = self.database.get(PUBLIC_COUNTERS_COLLECTION, "settings") or {}
        merged = {key: value.copy() for key, value in PUBLIC_COUNTER_DEFAULTS.items()}
        for key, value in stored.items():
            if key in merged and isinstance(value, dict):
                merged[key].update({"enabled": bool(value.get("enabled", merged[key]["enabled"]))})
        return merged

    def update_public_counter_settings(self, counters: dict[str, bool]) -> dict[str, dict[str, Any]]:
        settings = self.public_counter_settings()
        for key, enabled in counters.items():
            if key in settings:
                settings[key]["enabled"] = bool(enabled)
        self.database.update(PUBLIC_COUNTERS_COLLECTION, "settings", settings)
        return settings

    def cleanup_old_records(self) -> dict[str, int]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=ANALYTICS_RETENTION_DAYS)
        removed: dict[str, int] = {}
        for collection in (PAGE_VIEWS_COLLECTION, ANALYTICS_EVENTS_COLLECTION, SESSIONS_COLLECTION):
            kept = {}
            count = 0
            for item in self.database.list(collection):
                created = _parse_dt(item.get("created_at") or item.get("started_at"))
                if created and created < cutoff:
                    count += 1
                    continue
                kept[item["id"]] = item
            if count:
                self.database._save_collection(collection, kept)
            removed[collection] = count
        return removed

    def _build_summary(
        self,
        page_views: list[dict[str, Any]],
        sessions: list[dict[str, Any]],
        visitors: dict[str, dict[str, Any]],
        events: list[dict[str, Any]],
        days: int,
        now: datetime,
    ) -> dict[str, Any]:
        start = now - timedelta(days=days)
        previous_start = start - timedelta(days=days)
        views_in_period = [item for item in page_views if _in_range(item.get("created_at"), start, now)]
        previous_views = [item for item in page_views if _in_range(item.get("created_at"), previous_start, start)]
        all_time_unique = len({item.get("anonymous_visitor_id") for item in page_views if item.get("anonymous_visitor_id")})

        def unique_between(start_dt: datetime, end_dt: datetime) -> int:
            return len({item.get("anonymous_visitor_id") for item in page_views if _in_range(item.get("created_at"), start_dt, end_dt)})

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        active_cutoff = now - timedelta(minutes=ONLINE_WINDOW_MINUTES)
        active_sessions = [item for item in sessions if _parse_dt(item.get("last_seen_at")) and _parse_dt(item.get("last_seen_at")) >= active_cutoff]
        period_visitors = {item.get("anonymous_visitor_id") for item in views_in_period if item.get("anonymous_visitor_id")}
        new_visitors = {
            visitor_id
            for visitor_id in period_visitors
            if _parse_dt(visitors.get(visitor_id, {}).get("created_at")) and _parse_dt(visitors.get(visitor_id, {}).get("created_at")) >= start
        }
        session_durations = [_session_duration(item) for item in sessions if _in_range(item.get("started_at"), start, now)]
        conversion_counts = Counter(item.get("conversion_type") or item.get("event_type") for item in events if _in_range(item.get("created_at"), start, now))
        visitors_count = max(len(period_visitors), 1)
        by_day = Counter((_parse_dt(item.get("created_at")) or now).date().isoformat() for item in views_in_period)

        return {
            "period_days": days,
            "unique_visitors": {
                "today": unique_between(today_start, now),
                "yesterday": unique_between(yesterday_start, today_start),
                "7_days": unique_between(now - timedelta(days=7), now),
                "30_days": unique_between(now - timedelta(days=30), now),
                "all_time": all_time_unique,
            },
            "page_views": len(views_in_period),
            "page_views_all_time": len(page_views),
            "active_visitors_online": len({item.get("anonymous_visitor_id") for item in active_sessions}),
            "new_visitors": len(new_visitors),
            "returning_visitors": max(len(period_visitors) - len(new_visitors), 0),
            "average_session_duration_seconds": round(sum(session_durations) / len(session_durations), 2) if session_durations else 0,
            "top_pages": _counter_rows(Counter(item.get("url_path") or item.get("url") or "/" for item in views_in_period), "page"),
            "traffic_sources": _counter_rows(Counter(item.get("traffic_source") or "direct" for item in views_in_period), "source"),
            "devices": _counter_rows(Counter(item.get("device_type") or "unknown" for item in views_in_period), "device"),
            "browsers": _counter_rows(Counter(item.get("browser") or "unknown" for item in views_in_period), "browser"),
            "operating_systems": _counter_rows(Counter(item.get("operating_system") or "unknown" for item in views_in_period), "operating_system"),
            "countries": _counter_rows(Counter(item.get("anonymized_country") or "unknown" for item in views_in_period), "country"),
            "daily": [{"date": key, "page_views": by_day[key]} for key in sorted(by_day)],
            "conversions": {
                "visitor_to_registration": conversion_counts.get("visitor_to_registration", 0),
                "visitor_to_completed_profile": conversion_counts.get("visitor_to_completed_profile", 0),
                "visitor_to_job_application": conversion_counts.get("visitor_to_job_application", 0),
                "employer_to_created_vacancy": conversion_counts.get("employer_to_created_vacancy", 0),
                "candidate_to_employment": conversion_counts.get("candidate_to_employment", 0),
                "rates": {
                    "registration": _rate(conversion_counts.get("visitor_to_registration", 0), visitors_count),
                    "profile_completion": _rate(conversion_counts.get("visitor_to_completed_profile", 0), visitors_count),
                    "job_application": _rate(conversion_counts.get("visitor_to_job_application", 0), visitors_count),
                },
            },
            "comparison": {
                "previous_period_page_views": len(previous_views),
                "page_view_change_percent": _rate(len(views_in_period) - len(previous_views), len(previous_views)),
            },
            "privacy": {
                "ip_addresses": "anonymized_hash_only",
                "personal_data_in_summary": False,
                "retention_days": ANALYTICS_RETENTION_DAYS,
            },
        }

    def _should_track_request(self, request: Any) -> bool:
        if request.method.upper() != "GET":
            return False
        path = _request_path(request)
        if any(path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            return False
        if Path(path).suffix.lower() in STATIC_EXTENSIONS:
            return False
        if BOT_USER_AGENT.search(_user_agent(request)):
            return False
        accept = request.headers.get("accept", "")
        return "text/html" in accept or "*/*" in accept or not accept

    def _new_visitor(self, visitor_id: str, user_id: str | None, ip_hash: str, request: Any, now: datetime) -> dict[str, Any]:
        source = _traffic_source(request)
        return {
            "id": visitor_id,
            "anonymous_visitor_id": visitor_id,
            "user_id": user_id,
            "ip_hash": ip_hash,
            "first_source": source,
            "last_source": source,
            "device_type": _device_type(_user_agent(request)),
            "browser": _browser(_user_agent(request)),
            "operating_system": _operating_system(_user_agent(request)),
            "anonymized_country": _country(request),
            "visit_count": 0,
            "created_at": _iso(now),
            "last_seen_at": _iso(now),
        }

    def _new_session(self, session_id: str, visitor_id: str, user_id: str | None, request: Any, now: datetime) -> dict[str, Any]:
        return {
            "id": session_id,
            "anonymous_visitor_id": visitor_id,
            "user_id": user_id,
            "started_at": _iso(now),
            "last_seen_at": _iso(now),
            "page_view_count": 1,
            "traffic_source": _traffic_source(request),
            "device_type": _device_type(_user_agent(request)),
            "browser": _browser(_user_agent(request)),
            "operating_system": _operating_system(_user_agent(request)),
            "anonymized_country": _country(request),
            "created_at": _iso(now),
        }

    def _page_view(self, visitor_id: str, session_id: str, user_id: str | None, request: Any, now: datetime) -> dict[str, Any]:
        utm = _utm(request)
        return {
            "id": self._new_id("PV"),
            "event_type": "page_view",
            "anonymous_visitor_id": visitor_id,
            "user_id": user_id,
            "session_id": session_id,
            "url": _request_url(request),
            "url_path": _request_path(request),
            "page_name": _page_name(_request_path(request)),
            "referrer": _safe_referrer(request),
            "utm_source": utm.get("utm_source"),
            "utm_medium": utm.get("utm_medium"),
            "utm_campaign": utm.get("utm_campaign"),
            "utm_content": utm.get("utm_content"),
            "utm_term": utm.get("utm_term"),
            "traffic_source": _traffic_source(request),
            "device_type": _device_type(_user_agent(request)),
            "browser": _browser(_user_agent(request)),
            "operating_system": _operating_system(_user_agent(request)),
            "anonymized_country": _country(request),
            "language": request.query_params.get("lang") or request.headers.get("accept-language", "unknown")[:12],
            "created_at": _iso(now),
        }

    def _is_duplicate_page_view(self, page_view: dict[str, Any], now: datetime) -> bool:
        duplicate_cutoff = now - timedelta(seconds=2)
        for item in self.database.list(PAGE_VIEWS_COLLECTION):
            if (
                item.get("anonymous_visitor_id") == page_view["anonymous_visitor_id"]
                and item.get("session_id") == page_view["session_id"]
                and item.get("url_path") == page_view["url_path"]
                and (_parse_dt(item.get("created_at")) or duplicate_cutoff) >= duplicate_cutoff
            ):
                return True
        return False

    def _update_daily_summary(self, page_view: dict[str, Any]) -> None:
        day = (_parse_dt(page_view["created_at"]) or datetime.now(timezone.utc)).date().isoformat()
        summary = self.database.get(DAILY_SUMMARIES_COLLECTION, day) or {
            "id": day,
            "date": day,
            "page_views": 0,
            "unique_visitors": [],
            "sources": {},
            "devices": {},
            "countries": {},
            "updated_at": utc_now_iso(),
        }
        summary["page_views"] = int(summary.get("page_views") or 0) + 1
        if page_view["anonymous_visitor_id"] not in summary.setdefault("unique_visitors", []):
            summary["unique_visitors"].append(page_view["anonymous_visitor_id"])
        for key, field in (("sources", "traffic_source"), ("devices", "device_type"), ("countries", "anonymized_country")):
            value = page_view.get(field) or "unknown"
            summary.setdefault(key, {})[value] = int(summary.setdefault(key, {}).get(value) or 0) + 1
        summary["updated_at"] = utc_now_iso()
        self.database.update(DAILY_SUMMARIES_COLLECTION, day, summary)

    def _matches_filters(self, item: dict[str, Any], filters: dict[str, str | None]) -> bool:
        mapping = {
            "country": "anonymized_country",
            "source": "traffic_source",
            "device": "device_type",
            "language": "language",
        }
        for key, field in mapping.items():
            value = filters.get(key)
            if value and item.get(field) != value:
                return False
        user_type = filters.get("user_type")
        if user_type == "registered" and not item.get("user_id"):
            return False
        if user_type == "anonymous" and item.get("user_id"):
            return False
        return True

    def _session_expired(self, session: dict[str, Any], now: datetime) -> bool:
        last_seen = _parse_dt(session.get("last_seen_at"))
        return not last_seen or (now - last_seen) > timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    def _set_tracking_cookies(self, response: Any, request: Any, visitor_id: str, session_id: str) -> None:
        secure = request.url.scheme == "https"
        response.set_cookie("atlas_vid", visitor_id, httponly=True, secure=secure, samesite="lax", max_age=60 * 60 * 24 * 365)
        response.set_cookie("atlas_sid", session_id, httponly=True, secure=secure, samesite="lax", max_age=60 * SESSION_TIMEOUT_MINUTES)

    def _rate_limited(self, key: str, now: datetime) -> bool:
        cutoff = now - timedelta(minutes=1)
        window = [item for item in self._rate_window[key] if item >= cutoff]
        window.append(now)
        self._rate_window[key] = window
        return len(window) > 120

    def _ip_hash(self, request: Any) -> str:
        forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        ip = forwarded or (request.client.host if request.client else "unknown")
        salt = os.getenv("ATLAS_ANALYTICS_SALT") or os.getenv("ATLAS_ADMIN_TOKEN") or "atlas-local-analytics"
        return hashlib.sha256(f"{salt}:{ip}".encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:20]}"


def _request_path(request: Any) -> str:
    return str(request.url.path)


def _request_url(request: Any) -> str:
    return str(request.url.replace(query=""))


def _request_user_id(request: Any | None) -> str | None:
    if request is None:
        return None
    return _safe_id(
        request.headers.get("x-atlas-user-id")
        or request.headers.get("x-forwarded-user")
        or request.cookies.get("atlas_user_id")
    )


def _safe_id(value: str | None) -> str | None:
    if not value:
        return None
    safe = "".join(char for char in str(value) if char.isalnum() or char in ("-", "_"))[:96]
    return safe or None


def _user_agent(request: Any) -> str:
    return request.headers.get("user-agent", "")


def _safe_referrer(request: Any) -> str:
    referrer = request.headers.get("referer", "")
    if not referrer:
        return ""
    parsed = urlparse(referrer)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"[:240]


def _utm(request: Any) -> dict[str, str]:
    return {
        key: request.query_params.get(key, "")[:120]
        for key in ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")
        if request.query_params.get(key)
    }


def _traffic_source(request: Any) -> str:
    utm_source = (request.query_params.get("utm_source") or "").lower()
    if utm_source:
        return _normalize_source(utm_source)
    referrer = (request.headers.get("referer") or "").lower()
    if not referrer:
        return "direct"
    return _normalize_source(referrer)


def _normalize_source(value: str) -> str:
    if "google" in value:
        return "google"
    if "linkedin" in value:
        return "linkedin"
    if "facebook" in value or "fb." in value:
        return "facebook"
    if "telegram" in value or "t.me" in value:
        return "telegram"
    if "utm" in value or "campaign" in value or "ads" in value:
        return "campaign"
    return "other"


def _device_type(user_agent: str) -> str:
    ua = user_agent.lower()
    if "ipad" in ua or "tablet" in ua:
        return "tablet"
    if "mobi" in ua or "android" in ua or "iphone" in ua:
        return "phone"
    return "desktop"


def _browser(user_agent: str) -> str:
    ua = user_agent.lower()
    if "edg/" in ua:
        return "Edge"
    if "chrome/" in ua and "chromium" not in ua:
        return "Chrome"
    if "firefox/" in ua:
        return "Firefox"
    if "safari/" in ua and "chrome/" not in ua:
        return "Safari"
    return "Other"


def _operating_system(user_agent: str) -> str:
    ua = user_agent.lower()
    if "windows" in ua:
        return "Windows"
    if "android" in ua:
        return "Android"
    if "iphone" in ua or "ipad" in ua or "ios" in ua:
        return "iOS"
    if "mac os" in ua or "macintosh" in ua:
        return "macOS"
    if "linux" in ua:
        return "Linux"
    return "Other"


def _country(request: Any) -> str:
    country = (
        request.headers.get("cf-ipcountry")
        or request.headers.get("x-vercel-ip-country")
        or request.headers.get("x-atlas-country")
        or "unknown"
    )
    country = country.strip().upper()
    return country if re.fullmatch(r"[A-Z]{2}", country) else "unknown"


def _page_name(path: str) -> str:
    if path in {"", "/"}:
        return "home"
    return path.strip("/").split("/")[0][:80] or "home"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _in_range(value: str | None, start: datetime, end: datetime) -> bool:
    parsed = _parse_dt(value)
    return bool(parsed and start <= parsed < end)


def _session_duration(session: dict[str, Any]) -> float:
    started = _parse_dt(session.get("started_at"))
    last_seen = _parse_dt(session.get("last_seen_at"))
    if not started or not last_seen:
        return 0
    return max((last_seen - started).total_seconds(), 0)


def _counter_rows(counter: Counter, key_name: str) -> list[dict[str, Any]]:
    return [{key_name: key, "count": value} for key, value in counter.most_common(10)]
