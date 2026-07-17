"""Backend-owned dialogue state for ATLAS public chat."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from core.models import utc_now_iso


FIELD_ORDER = [
    "profession",
    "current_country",
    "experience",
    "documents_status",
    "preferred_contact_method",
    "phone",
    "driving_license",
    "certificates",
    "relocation_readiness",
    "preferred_destination",
    "learning_readiness",
    "desired_salary",
    "ready_from",
    "accommodation_need",
    "photo",
    "document_files",
]

FIELD_ALIASES = {
    "profession": ("profession", "skills", "role"),
    "current_country": ("current_country", "country", "city", "currentLocation"),
    "experience": ("experience", "experience_years", "yearsOfExperience"),
    "documents_status": (
        "documents_status",
        "residence_document_status",
        "documents",
        "legalStatus",
        "documentsLegalStatus",
    ),
    "preferred_contact_method": ("preferred_contact_method",),
    "phone": ("phone", "phone_number", "contact", "phoneOrContact"),
    "driving_license": ("driving_license",),
    "certificates": ("certificates",),
    "relocation_readiness": ("relocation_readiness",),
    "preferred_destination": ("preferred_destination", "desired_country"),
    "learning_readiness": ("learning_readiness",),
    "desired_salary": ("desired_salary",),
    "ready_from": ("ready_from",),
    "accommodation_need": ("accommodation_need", "housing"),
    "photo": ("photo",),
    "document_files": ("document_files",),
}

QUESTION_TEXT = {
    "ru": {
        "profession": "\u041a\u0430\u043a\u0443\u044e \u0440\u0430\u0431\u043e\u0442\u0443 \u0432\u044b \u0438\u0449\u0435\u0442\u0435 \u0438 \u0447\u0442\u043e \u0443\u043c\u0435\u0435\u0442\u0435 \u0434\u0435\u043b\u0430\u0442\u044c?",
        "current_country": "\u0413\u0434\u0435 \u0432\u044b \u0441\u0435\u0439\u0447\u0430\u0441 \u043d\u0430\u0445\u043e\u0434\u0438\u0442\u0435\u0441\u044c?",
        "experience": "\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u0443 \u0432\u0430\u0441 \u043e\u043f\u044b\u0442\u0430 \u0440\u0430\u0431\u043e\u0442\u044b{profession}?",
        "documents_status": "\u041a\u0430\u043a\u0438\u0435 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b \u0443 \u0432\u0430\u0441 \u0441\u0435\u0439\u0447\u0430\u0441 \u0435\u0441\u0442\u044c?",
        "phone": "\u041a\u0430\u043a\u043e\u0439 \u043d\u043e\u043c\u0435\u0440 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430 \u0438\u043b\u0438 \u043a\u043e\u043d\u0442\u0430\u043a\u0442 \u043c\u043e\u0436\u043d\u043e \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c?",
        "ready_from": "\u041a\u043e\u0433\u0434\u0430 \u0432\u044b \u0433\u043e\u0442\u043e\u0432\u044b \u043d\u0430\u0447\u0430\u0442\u044c?",
    },
    "uk": {
        "profession": "\u042f\u043a\u0443 \u0440\u043e\u0431\u043e\u0442\u0443 \u0432\u0438 \u0448\u0443\u043a\u0430\u0454\u0442\u0435 \u0456 \u0449\u043e \u0432\u043c\u0456\u0454\u0442\u0435 \u0440\u043e\u0431\u0438\u0442\u0438?",
        "current_country": "\u0414\u0435 \u0432\u0438 \u0437\u0430\u0440\u0430\u0437 \u0437\u043d\u0430\u0445\u043e\u0434\u0438\u0442\u0435\u0441\u044f?",
        "experience": "\u0421\u043a\u0456\u043b\u044c\u043a\u0438 \u0443 \u0432\u0430\u0441 \u0434\u043e\u0441\u0432\u0456\u0434\u0443 \u0440\u043e\u0431\u043e\u0442\u0438{profession}?",
        "documents_status": "\u042f\u043a\u0456 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0438 \u0443 \u0432\u0430\u0441 \u0437\u0430\u0440\u0430\u0437 \u0454?",
        "phone": "\u042f\u043a\u0438\u0439 \u043d\u043e\u043c\u0435\u0440 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0443 \u0430\u0431\u043e \u043a\u043e\u043d\u0442\u0430\u043a\u0442 \u043c\u043e\u0436\u043d\u0430 \u0437\u0431\u0435\u0440\u0435\u0433\u0442\u0438?",
        "ready_from": "\u041a\u043e\u043b\u0438 \u0432\u0438 \u0433\u043e\u0442\u043e\u0432\u0456 \u043f\u043e\u0447\u0430\u0442\u0438?",
    },
    "pl": {
        "profession": "Jakiej pracy szukasz i co potrafisz robic?",
        "current_country": "Gdzie teraz jestes?",
        "experience": "Ile masz doswiadczenia w tej pracy?",
        "documents_status": "Jakie dokumenty masz teraz przy sobie?",
        "phone": "Jaki numer telefonu albo kontakt moge zapisac?",
        "ready_from": "Kiedy mozesz zaczac?",
    },
    "en": {
        "profession": "What work are you looking for and what can you do?",
        "current_country": "Where are you now?",
        "experience": "How much work experience do you have?",
        "documents_status": "Which documents do you already have?",
        "phone": "Which phone number or contact should I save?",
        "ready_from": "When are you ready to start?",
    },
}

DEFAULT_QUESTION = {
    "ru": "\u0414\u043e\u0431\u0430\u0432\u044c\u0442\u0435, \u043f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430, \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0443\u044e \u0434\u0435\u0442\u0430\u043b\u044c \u0434\u043b\u044f \u043f\u0440\u043e\u0444\u0438\u043b\u044f.",
    "uk": "\u0414\u043e\u0434\u0430\u0439\u0442\u0435, \u0431\u0443\u0434\u044c \u043b\u0430\u0441\u043a\u0430, \u043d\u0430\u0441\u0442\u0443\u043f\u043d\u0443 \u0434\u0435\u0442\u0430\u043b\u044c \u0434\u043b\u044f \u043f\u0440\u043e\u0444\u0456\u043b\u044e.",
    "pl": "Dodaj prosze kolejny szczegol do profilu.",
    "en": "Please add the next detail for your profile.",
}

DOCUMENT_CONFIRMATION = {
    "ru": "\u041f\u043e\u043d\u044f\u043b, \u0432\u044b \u043e\u0436\u0438\u0434\u0430\u0435\u0442\u0435 \u043a\u0430\u0440\u0442\u0443 \u043f\u043e\u0431\u044b\u0442\u0430.",
    "uk": "\u0417\u0440\u043e\u0437\u0443\u043c\u0456\u0432, \u0432\u0438 \u0447\u0435\u043a\u0430\u0454\u0442\u0435 \u043a\u0430\u0440\u0442\u0443 \u043f\u043e\u0431\u0438\u0442\u0443.",
    "pl": "Rozumiem, czekasz na karte pobytu.",
    "en": "Understood, you are waiting for the residence card.",
}

GENERIC_ACK = {
    "ru": "\u041f\u043e\u043d\u044f\u043b.",
    "uk": "\u0417\u0440\u043e\u0437\u0443\u043c\u0456\u0432.",
    "pl": "Rozumiem.",
    "en": "Understood.",
}

COMPLETE_REPLY = {
    "ru": "\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f \u0430\u043d\u043a\u0435\u0442\u0430 \u0441\u043e\u0431\u0440\u0430\u043d\u0430. \u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u043e\u0440 \u0441\u043c\u043e\u0436\u0435\u0442 \u043f\u0435\u0440\u0435\u0439\u0442\u0438 \u043a \u043f\u043e\u0434\u0431\u043e\u0440\u0443.",
    "uk": "\u041e\u0441\u043d\u043e\u0432\u043d\u0430 \u0430\u043d\u043a\u0435\u0442\u0430 \u0437\u0456\u0431\u0440\u0430\u043d\u0430. \u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u043e\u0440 \u0437\u043c\u043e\u0436\u0435 \u043f\u0435\u0440\u0435\u0439\u0442\u0438 \u0434\u043e \u043f\u0456\u0434\u0431\u043e\u0440\u0443.",
    "pl": "Podstawowy profil jest zebrany. Koordynator moze przejsc do dopasowania.",
    "en": "The basic profile is ready. A coordinator can move to matching.",
}

CLARIFY_DOCUMENTS = {
    "ru": "\u0423\u0442\u043e\u0447\u043d\u0438\u0442\u0435, \u043f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430: \u043a\u0430\u043a\u043e\u0439 \u0438\u043c\u0435\u043d\u043d\u043e \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u0432\u044b \u0436\u0434\u0451\u0442\u0435 \u0438\u043b\u0438 \u043a\u0430\u043a\u0438\u0435 \u0443\u0436\u0435 \u0435\u0441\u0442\u044c?",
    "uk": "\u0423\u0442\u043e\u0447\u043d\u0456\u0442\u044c, \u0431\u0443\u0434\u044c \u043b\u0430\u0441\u043a\u0430: \u044f\u043a\u0438\u0439 \u0441\u0430\u043c\u0435 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u0432\u0438 \u0447\u0435\u043a\u0430\u0454\u0442\u0435 \u0430\u0431\u043e \u044f\u043a\u0456 \u0432\u0436\u0435 \u0454?",
    "pl": "Doprecyzuj prosze, na jaki dokument czekasz albo jakie dokumenty juz masz?",
    "en": "Please clarify which document you are waiting for or which documents you already have.",
}


@dataclass
class DialogueResult:
    profile: dict[str, Any]
    reply: str
    current_step: str
    next_field: str | None
    completed_fields: list[str]
    field: str | None = None
    profile_updated: bool = False
    duplicate: bool = False
    request_id: str | None = None


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    return text.casefold().strip()


def get_completed_fields(profile: dict[str, Any]) -> list[str]:
    completed = set(profile.get("completed_fields") or [])
    for field in FIELD_ORDER:
        if _profile_has_field(profile, field):
            completed.add(field)
    return [field for field in FIELD_ORDER if field in completed]


def get_next_required_field(profile: dict[str, Any], completed_fields: list[str] | None = None) -> str | None:
    completed = set(completed_fields or get_completed_fields(profile))
    for field in FIELD_ORDER:
        if field not in completed and not _profile_has_field(profile, field):
            return field
    return None


def process_candidate_dialogue(
    profile: dict[str, Any],
    message: str,
    language: str,
    request_id: str | None = None,
) -> DialogueResult:
    language = language if language in QUESTION_TEXT else "en"
    if request_id:
        cached = _cached_response(profile, request_id)
        if cached:
            return DialogueResult(
                profile=profile,
                reply=str(cached.get("reply") or ""),
                current_step=str(profile.get("current_step") or "complete"),
                next_field=cached.get("next_field"),
                completed_fields=get_completed_fields(profile),
                field=cached.get("field"),
                profile_updated=bool(cached.get("profile_updated")),
                duplicate=True,
                request_id=request_id,
            )

    previous_step = str(profile.get("current_step") or "")
    field = _field_from_message(message, previous_step)
    profile_updated = False
    confirmation = GENERIC_ACK.get(language, GENERIC_ACK["en"])

    if field == "ambiguous_documents":
        _append_dialogue_message(profile, "user", message, field="documents_status", request_id=request_id, profile_updated=False)
        reply = CLARIFY_DOCUMENTS.get(language, CLARIFY_DOCUMENTS["en"])
        _append_dialogue_message(profile, "assistant", reply, field="documents_status", request_id=request_id, profile_updated=False)
        _cache_response(profile, request_id, reply, "documents_status", "documents_status", False)
        return DialogueResult(
            profile=profile,
            reply=reply,
            current_step="documents_status",
            next_field="documents_status",
            completed_fields=get_completed_fields(profile),
            field="documents_status",
            profile_updated=False,
            request_id=request_id,
        )

    if field == "documents_status":
        _apply_pending_residence_card(profile)
        profile_updated = True
        confirmation = DOCUMENT_CONFIRMATION.get(language, DOCUMENT_CONFIRMATION["en"])

    completed = get_completed_fields(profile)
    if field and field not in completed and profile_updated:
        completed.append(field)
    profile["completed_fields"] = [item for item in FIELD_ORDER if item in set(completed)]

    next_field = get_next_required_field(profile, profile["completed_fields"])
    profile["current_step"] = next_field or "complete"
    profile["dialogue_state"] = {
        "role": "candidate",
        "language": language,
        "current_step": profile["current_step"],
        "completed_fields": profile["completed_fields"],
        "next_field": next_field,
    }

    _append_dialogue_message(profile, "user", message, field=field, request_id=request_id, profile_updated=profile_updated)
    question = question_for_field(next_field, language, profile) if next_field else COMPLETE_REPLY.get(language, COMPLETE_REPLY["en"])
    reply = f"{confirmation} {question}".strip()
    _append_dialogue_message(profile, "assistant", reply, field=next_field, request_id=request_id, profile_updated=False)
    _cache_response(profile, request_id, reply, field, next_field, profile_updated)
    return DialogueResult(
        profile=profile,
        reply=reply,
        current_step=profile["current_step"],
        next_field=next_field,
        completed_fields=profile["completed_fields"],
        field=field,
        profile_updated=profile_updated,
        request_id=request_id,
    )


def question_for_field(field: str | None, language: str, profile: dict[str, Any]) -> str:
    if not field:
        return COMPLETE_REPLY.get(language, COMPLETE_REPLY["en"])
    language = language if language in QUESTION_TEXT else "en"
    template = QUESTION_TEXT.get(language, {}).get(field) or QUESTION_TEXT["en"].get(field) or DEFAULT_QUESTION.get(language, DEFAULT_QUESTION["en"])
    profession = ""
    if field == "experience" and profile.get("profession") and language in {"ru", "uk"}:
        profession = f" {str(profile.get('profession')).strip()}"
    return template.format(profession=profession)


def build_gemini_dialogue_context(
    profile: dict[str, Any],
    language: str,
    role: str,
    last_user_message: str,
    next_field: str | None,
) -> dict[str, Any]:
    return {
        "language": language,
        "role": role,
        "current_step": profile.get("current_step"),
        "saved_profile_data": {
            key: profile.get(key)
            for key in (
                "profession",
                "current_country",
                "country",
                "residence_document_status",
                "residence_document_type",
                "current_documents_note",
                "experience_years",
            )
            if profile.get(key) is not None
        },
        "completed_fields": profile.get("completed_fields") or [],
        "next_field": next_field,
        "last_user_message": last_user_message,
        "task": "confirm_saved_answer_and_ask_next_question",
        "rules": [
            "Do not ask for a field that is already in completed_fields.",
            "Ask only one next question.",
            "Do not invent data.",
        ],
    }


def _profile_has_field(profile: dict[str, Any], field: str) -> bool:
    for alias in FIELD_ALIASES.get(field, (field,)):
        value = profile.get(alias)
        if isinstance(value, (list, tuple, set, dict)):
            if value:
                return True
        elif value not in (None, "", False):
            return True
    return False


def _field_from_message(message: str, current_step: str) -> str | None:
    text = normalize_text(message)
    if _is_ambiguous_wait(text):
        return "ambiguous_documents"
    if _mentions_pending_residence_card(text):
        return "documents_status"
    if current_step in {"documents_status", "documentsLegalStatus"} and _mentions_document_context(text):
        return "documents_status"
    return None


def _mentions_pending_residence_card(text: str) -> bool:
    has_card = bool(re.search(r"\b(kart[auy]?|karte|karta|card)\b", text)) or "\u043a\u0430\u0440\u0442" in text
    has_residence = "pobyt" in text or "\u043f\u043e\u0431\u044b\u0442" in text or "\u043f\u043e\u0431\u0438\u0442" in text or "residence" in text
    has_pending = any(
        token in text
        for token in (
            "\u0436\u0434\u0443",
            "\u0436\u0434\u0435\u0442",
            "\u043e\u0436\u0438\u0434",
            "\u0447\u0435\u043a\u0430",
            "czekam",
            "czeka",
            "pending",
            "waiting",
            "trakcie",
            "\u043f\u0440\u043e\u0446\u0435\u0441",
            "wniosek",
            "decyzj",
            "\u0440\u0435\u0448\u0435\u043d",
            "\u0440\u0456\u0448\u0435\u043d",
            "\u043f\u043e\u0434\u0430\u043b",
            "\u043f\u043e\u0434\u0430\u0432",
            "zlozyl",
            "zlozylam",
        )
    )
    document_review = any(token in text for token in ("\u0440\u0430\u0441\u0441\u043c\u043e\u0442\u0440", "\u0440\u043e\u0437\u0433\u043b\u044f\u0434", "review"))
    return (has_card and has_residence and (has_pending or True)) or (has_pending and document_review)


def _mentions_document_context(text: str) -> bool:
    return _mentions_pending_residence_card(text) or any(
        token in text
        for token in (
            "passport",
            "visa",
            "work permit",
            "\u043f\u0430\u0441\u043f\u043e\u0440\u0442",
            "\u0432\u0438\u0437\u0430",
            "\u0432\u0456\u0437\u0430",
            "\u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442",
            "dokument",
        )
    )


def _is_ambiguous_wait(text: str) -> bool:
    return text in {"\u0436\u0434\u0443", "\u043e\u0436\u0438\u0434\u0430\u044e", "\u0447\u0435\u043a\u0430\u044e", "czekam", "waiting"}


def _apply_pending_residence_card(profile: dict[str, Any]) -> None:
    documents = set(profile.get("documents") or [])
    documents.add("karta_pobytu_pending")
    profile["documents"] = sorted(documents)
    profile["documents_status"] = "pending"
    profile["residence_document_status"] = "pending"
    profile["residence_document_type"] = "karta_pobytu"
    profile["current_documents_note"] = "\u041e\u0436\u0438\u0434\u0430\u0435\u0442 \u043a\u0430\u0440\u0442\u0443 \u043f\u043e\u0431\u044b\u0442\u0430"


def _append_dialogue_message(
    profile: dict[str, Any],
    role: str,
    content: str,
    field: str | None,
    request_id: str | None,
    profile_updated: bool,
) -> None:
    entry = {
        "role": role,
        "content": content,
        "timestamp": utc_now_iso(),
        "field": field,
        "request_id": request_id,
        "profile_updated": profile_updated,
    }
    history = list(profile.get("dialogue_history") or [])
    history.append(entry)
    profile["dialogue_history"] = history[-80:]


def _cached_response(profile: dict[str, Any], request_id: str) -> dict[str, Any] | None:
    cache = profile.get("request_cache") or {}
    cached = cache.get(request_id)
    return cached if isinstance(cached, dict) else None


def _cache_response(
    profile: dict[str, Any],
    request_id: str | None,
    reply: str,
    field: str | None,
    next_field: str | None,
    profile_updated: bool,
) -> None:
    if not request_id:
        return
    cache = dict(profile.get("request_cache") or {})
    cache[request_id] = {
        "reply": reply,
        "field": field,
        "next_field": next_field,
        "profile_updated": profile_updated,
        "timestamp": utc_now_iso(),
    }
    keys = list(cache.keys())[-40:]
    profile["request_cache"] = {key: cache[key] for key in keys}
    processed = list(profile.get("processed_request_ids") or [])
    if request_id not in processed:
        processed.append(request_id)
    profile["processed_request_ids"] = processed[-40:]
