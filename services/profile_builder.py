"""Automatic UserProfile builder from natural conversation."""

import re
from typing import Any

from memory.user_memory import UserMemory


PUBLIC_TIMELINE_KEYS = [
    "timeline.start",
    "timeline.profile",
    "timeline.documents",
    "timeline.matching",
    "timeline.employer_review",
    "timeline.interview",
    "timeline.job_offer",
    "timeline.arrival",
    "timeline.support",
]

COUNTRY_ALIASES = {
    "poland": "PL",
    "polska": "PL",
    "польща": "PL",
    "польщу": "PL",
    "польша": "PL",
    "польшу": "PL",
    "germany": "DE",
    "deutschland": "DE",
    "німеччина": "DE",
    "німеччині": "DE",
    "німеччину": "DE",
    "германия": "DE",
    "германию": "DE",
    "spain": "ES",
    "espana": "ES",
    "іспанія": "ES",
    "испания": "ES",
    "portugal": "PT",
    "португалія": "PT",
    "португалия": "PT",
}

PROFESSION_ALIASES = {
    "welder": "Welder",
    "welding": "Welder",
    "звар": "Welder",
    "свар": "Welder",
    "warehouse": "Warehouse worker",
    "склад": "Warehouse worker",
    "driver": "Driver",
    "водій": "Driver",
    "водитель": "Driver",
    "electrician": "Electrician",
    "електрик": "Electrician",
    "электрик": "Electrician",
    "builder": "Construction worker",
    "будів": "Construction worker",
    "строит": "Construction worker",
}

LANGUAGE_ALIASES = {
    "polish": "pl",
    "polski": "pl",
    "польська": "pl",
    "польский": "pl",
    "english": "en",
    "англійська": "en",
    "английский": "en",
    "german": "de",
    "deutsch": "de",
    "німецька": "de",
    "немецкий": "de",
    "ukrainian": "uk",
    "українська": "uk",
    "украинский": "uk",
    "russian": "ru",
    "русский": "ru",
    "spanish": "es",
    "іспанська": "es",
    "испанский": "es",
    "portuguese": "pt",
    "португальська": "pt",
    "португальский": "pt",
}


def update_user_profile_from_message(
    memory: UserMemory,
    message: str,
    language: str = "uk",
) -> dict[str, Any]:
    profile = dict(memory.profile_data)
    text = message.lower()

    profile["user_id"] = memory.user_id
    profile["preferred_language"] = language
    profile["roles"] = _detect_roles(text, profile.get("roles", []))
    profile["intent"] = _detect_intent(text, profile)
    profile["profession"] = _first_alias(text, PROFESSION_ALIASES, profile.get("profession"))
    profile["country"] = _first_alias(text, COUNTRY_ALIASES, profile.get("country"))
    profile["languages"] = sorted(set(profile.get("languages", [])) | set(_detect_languages(text)))
    profile["documents"] = sorted(set(profile.get("documents", [])) | set(_detect_documents(text)))
    profile["desired_salary"] = _detect_salary(text, profile.get("desired_salary"))
    profile["experience_years"] = _detect_experience(text, profile.get("experience_years"))
    profile["ready_from"] = _detect_ready_from(text, profile.get("ready_from"))
    profile["timeline"] = build_human_timeline(profile)
    profile["employment_probability"] = estimate_employment_probability(profile)
    profile["improvements"] = build_improvements(profile)
    profile["progress"] = build_progress(profile)
    profile["cv_map"] = build_candidate_cv_map(profile)

    messages = profile.get("messages", [])
    messages.append({"role": "user", "content": message})
    profile["messages"] = messages[-20:]

    memory.profile_data = profile
    memory.conversation_summary = _append_summary(memory.conversation_summary, message)
    memory.preferences.update(
        {
            "preferred_language": language,
            "country": profile.get("country"),
            "desired_salary": profile.get("desired_salary"),
            "languages": profile.get("languages", []),
            "ready_from": profile.get("ready_from"),
        }
    )
    return profile


def update_candidate_profile_from_message(memory: UserMemory, message: str) -> dict[str, Any]:
    return update_user_profile_from_message(memory, message, language="uk")


def build_human_timeline(profile: dict[str, Any]) -> list[dict[str, Any]]:
    completed = {
        "timeline.start": True,
        "timeline.profile": bool(profile.get("profession") or profile.get("roles")),
        "timeline.documents": bool(profile.get("documents")),
        "timeline.matching": bool(profile.get("profession") and profile.get("country")),
        "timeline.employer_review": bool(profile.get("employer_review_started")),
        "timeline.interview": bool(profile.get("interview_started")),
        "timeline.job_offer": bool(profile.get("job_offer")),
        "timeline.arrival": bool(profile.get("arrival_confirmed")),
        "timeline.support": bool(profile.get("working_started")),
    }
    return [
        {"key": key, "name": key, "status": "complete" if completed[key] else "pending"}
        for key in PUBLIC_TIMELINE_KEYS
    ]


def build_progress(profile: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"key": "profile.profession", "complete": bool(profile.get("profession")), "value": profile.get("profession")},
        {"key": "profile.experience", "complete": bool(profile.get("experience_years")), "value": _years(profile.get("experience_years"))},
        {"key": "profile.country", "complete": bool(profile.get("country")), "value": profile.get("country")},
        {"key": "profile.documents", "complete": bool(profile.get("documents")), "value": ", ".join(profile.get("documents", []))},
        {"key": "profile.languages", "complete": bool(profile.get("languages")), "value": ", ".join(profile.get("languages", []))},
        {"key": "profile.ready", "complete": bool(profile.get("ready_from")), "value": profile.get("ready_from")},
    ]


def build_candidate_cv_map(profile: dict[str, Any]) -> dict[str, Any]:
    sections = [
        _cv_section("profile.profession", profile.get("profession"), 18, "profession"),
        _cv_section("profile.experience", _years(profile.get("experience_years")), 16, "experience"),
        _cv_section("profile.country", profile.get("country"), 14, "country"),
        _cv_section("profile.documents", ", ".join(profile.get("documents", [])), 16, "documents"),
        _cv_section("profile.languages", ", ".join(profile.get("languages", [])), 12, "languages"),
        _cv_section("profile.ready", profile.get("ready_from"), 10, "ready"),
        _cv_section("crm.salary", profile.get("desired_salary"), 8, "salary"),
        _cv_section("form.phone", profile.get("phone") or profile.get("phone_number") or profile.get("contact"), 6, "phone"),
    ]
    completed = [section for section in sections if section["complete"]]
    score = sum(section["weight"] for section in completed)
    missing = [section for section in sections if not section["complete"]]
    highlights = [
        section["label_key"]
        for section in completed
        if section["field"] in {"profession", "experience", "documents", "languages", "ready"}
    ][:4]
    return {
        "score": min(score, 100),
        "completed_count": len(completed),
        "total_count": len(sections),
        "sections": sections,
        "missing": missing[:4],
        "highlights": highlights,
        "status_key": "profile.ready_for_matching" if score >= 74 else "smart.profile_score_hint",
    }


def estimate_employment_probability(profile: dict[str, Any]) -> dict[str, Any]:
    score = 18
    weights = {
        "profession": 18,
        "experience_years": 16,
        "country": 14,
        "documents": 14,
        "languages": 12,
        "ready_from": 8,
    }
    for key, value in weights.items():
        if profile.get(key):
            score += value
    score = min(score, 96)
    level = "profile.chance_high" if score >= 75 else "profile.chance_medium" if score >= 50 else "profile.chance_initial"
    return {"score": score, "level": level}


def build_improvements(profile: dict[str, Any]) -> list[str]:
    improvements = []
    if "certificate_photo" not in profile.get("documents", []):
        improvements.append("profile.default_tip_documents")
    if not profile.get("ready_from"):
        improvements.append("profile.default_tip_ready")
    if not profile.get("country"):
        improvements.append("profile.default_tip_country")
    if not profile.get("profession"):
        improvements.append("profile.default_tip_profession")
    return improvements[:4]


def _detect_roles(text: str, current_roles: list[str]) -> list[str]:
    roles = set(current_roles or [])
    if any(word in text for word in ("роботу", "работу", "job", "work", "працювати", "звар", "свар", "склад", "driver", "водій", "водитель")):
        roles.add("candidate")
    if any(word in text for word in ("працівників", "работников", "employees", "workers", "людей", "hire")):
        roles.add("employer")
    if any(word in text for word in ("консульта", "advice", "consultation")):
        roles.add("consultant")
    return sorted(roles or {"candidate"})


def _cv_section(label_key: str, value: Any, weight: int, field: str) -> dict[str, Any]:
    display_value = value
    if isinstance(value, (list, tuple, set)):
        display_value = ", ".join(str(item) for item in value if str(item).strip())
    if display_value is not None:
        display_value = str(display_value).strip()
    complete = bool(display_value)
    return {
        "field": field,
        "label_key": label_key,
        "value": display_value if complete else None,
        "complete": complete,
        "weight": weight,
    }


def _first_alias(text: str, aliases: dict[str, str], current: str | None) -> str | None:
    for phrase, value in aliases.items():
        if phrase in text:
            return value
    return current


def _detect_intent(text: str, profile: dict[str, Any]) -> str:
    if any(word in text for word in ("employees", "workers", "кандидат", "людей", "працівник", "работник", "hire")):
        return "find_employees"
    if any(word in text for word in ("job", "work", "робот", "праця", "працювати", "звар", "свар")):
        return "find_job"
    if any(word in text for word in ("консульта", "advice", "consultation")):
        return "consultation"
    return profile.get("intent", "career_support")


def _detect_languages(text: str) -> list[str]:
    return [code for phrase, code in LANGUAGE_ALIASES.items() if phrase in text]


def _detect_documents(text: str) -> list[str]:
    documents = []
    if any(word in text for word in ("passport", "паспорт")):
        documents.append("passport")
    if any(word in text for word in ("cv", "resume", "резюме")):
        documents.append("cv")
    if any(word in text for word in ("certificate", "сертифікат", "сертификат")):
        documents.append("certificate_photo")
    if any(word in text for word in ("visa", "віза", "виза")):
        documents.append("work_permit")
    return documents


def _detect_salary(text: str, current: Any) -> int | None:
    match = re.search(r"(\d{4,6})\s?(eur|euro|pln|zl|zł)?", text)
    if match:
        return int(match.group(1))
    return current


def _detect_experience(text: str, current: Any) -> int | None:
    match = re.search(r"(\d{1,2})\s?(years|year|лет|года|років|роки|lata|lat)", text)
    if match:
        return int(match.group(1))
    return current


def _detect_ready_from(text: str, current: Any) -> str | None:
    if any(word in text for word in ("now", "сейчас", "зараз", "immediately")):
        return "now"
    if any(word in text for word in ("july", "июл", "лип")):
        return "july"
    if any(word in text for word in ("august", "август", "серп")):
        return "august"
    return current


def _append_summary(current: str, message: str) -> str:
    message = message.strip()
    if not message:
        return current
    return f"{current}\nUser: {message}".strip()


def _years(value: Any) -> str | None:
    if not value:
        return None
    return f"{value} years"
