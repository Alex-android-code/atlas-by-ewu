"""Stable Gemini integration for ATLAS backend."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
from time import sleep
from typing import Any

from services.env_loader import load_env_file


load_env_file()

FALLBACK_MESSAGES = {
    "uk": "AI-помічник тимчасово недоступний, але ви можете продовжити заповнення профілю.",
    "ru": "AI-помощник временно недоступен, но вы можете продолжить заполнение профиля.",
    "pl": "Asystent AI jest chwilowo niedostępny, ale możesz kontynuować uzupełnianie profilu.",
    "en": "The AI assistant is temporarily unavailable, but you can continue completing your profile.",
    "de": "Der KI-Assistent ist vorübergehend nicht verfügbar. Sie können Ihr Profil trotzdem weiter ausfüllen.",
    "es": "El asistente de IA no está disponible temporalmente, pero puedes seguir completando tu perfil.",
    "pt": "O assistente de IA está temporariamente indisponível, mas pode continuar a preencher o seu perfil.",
}

ALLOWED_LANGUAGES = set(FALLBACK_MESSAGES)
ALLOWED_ROLES = {"candidate", "employer", "coordinator", "matching", "legal", "document"}
RETRY_DELAYS_SECONDS = (1, 2, 4)
MAX_MESSAGE_LENGTH = 2000


class GeminiServiceError(Exception):
    def __init__(self, message: str, error_type: str = "unknown", retryable: bool = True) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.retryable = retryable


@dataclass
class GeminiJsonResponse:
    message: str
    next_field: str | None
    profile_updates: dict[str, Any]
    warnings: list[str]
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "next_field": self.next_field,
            "profile_updates": self.profile_updates,
            "warnings": self.warnings,
            "confidence": self.confidence,
        }


class GeminiService:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.timeout_seconds = timeout_seconds or int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))
        self.max_retries = max(1, max_retries or int(os.getenv("GEMINI_MAX_RETRIES", "3")))
        self._client: Any | None = None

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str, language: str = "en") -> str:
        if not self.is_configured():
            raise GeminiServiceError("Gemini API key is not configured", "not_configured", retryable=False)
        prompt = sanitize_user_text(prompt, max_length=6000)
        if not prompt:
            raise GeminiServiceError("Gemini prompt is empty", "empty_prompt", retryable=False)
        last_error: GeminiServiceError | None = None
        attempts = min(self.max_retries, len(RETRY_DELAYS_SECONDS))
        for attempt in range(attempts):
            try:
                text = self._call_model(prompt)
                if not text.strip():
                    raise GeminiServiceError("Gemini returned empty response", "empty_response", retryable=True)
                return text.strip()
            except GeminiServiceError as error:
                last_error = error
                if not error.retryable or attempt == attempts - 1:
                    raise
                sleep(RETRY_DELAYS_SECONDS[attempt])
        raise last_error or GeminiServiceError("Gemini failed", "unknown", retryable=True)

    def generate_json(self, prompt: str, language: str = "en") -> GeminiJsonResponse:
        response_text = self.generate_text(prompt, language=language)
        parsed = self._parse_json_response(response_text)
        if parsed:
            return parsed
        repair_prompt = (
            "Repair the following response into valid JSON only. "
            "Use keys: message, next_field, profile_updates, warnings, confidence.\n\n"
            f"Response:\n{response_text[:3000]}"
        )
        repaired_text = self.generate_text(repair_prompt, language=language)
        repaired = self._parse_json_response(repaired_text)
        if repaired:
            return repaired
        raise GeminiServiceError("Gemini returned invalid JSON", "invalid_json", retryable=True)

    def analyze_candidate(self, candidate: dict[str, Any], language: str = "en") -> GeminiJsonResponse:
        return self.generate_json(
            build_structured_prompt(
                language=language,
                user_role="candidate",
                current_step="profile_review",
                profile_data=candidate,
                recent_messages=[],
                task="analyze_candidate",
            ),
            language=language,
        )

    def analyze_vacancy(self, vacancy: dict[str, Any], language: str = "en") -> GeminiJsonResponse:
        return self.generate_json(
            build_structured_prompt(
                language=language,
                user_role="employer",
                current_step="vacancy_review",
                profile_data=vacancy,
                recent_messages=[],
                task="analyze_vacancy",
            ),
            language=language,
        )

    def explain_match(self, match: dict[str, Any], language: str = "en") -> GeminiJsonResponse:
        return self.generate_json(
            build_structured_prompt(
                language=language,
                user_role="matching",
                current_step="match_explanation",
                profile_data=match,
                recent_messages=[],
                task="explain_match",
            ),
            language=language,
        )

    def translate_text(self, text: str, target_language: str) -> str:
        language = normalize_language(target_language)
        return self.generate_text(
            f"Translate the following text to {language}. Return only the translation.\n\n{sanitize_user_text(text)}",
            language=language,
        )

    def health_check(self, ping: bool = False) -> dict[str, Any]:
        if not self.is_configured():
            return {"status": "degraded", "provider": "gemini", "model": self.model, "error_type": "not_configured"}
        if not ping:
            return {"status": "ok", "provider": "gemini", "model": self.model, "configured": True}
        try:
            text = self.generate_text("Reply with exactly: OK", language="en")
            return {
                "status": "ok" if "OK" in text.upper() else "degraded",
                "provider": "gemini",
                "model": self.model,
            }
        except GeminiServiceError as error:
            return {"status": "degraded", "provider": "gemini", "model": self.model, "error_type": error.error_type}

    def _client_instance(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            from google import genai
        except Exception as error:  # pragma: no cover - depends on optional package install
            raise GeminiServiceError("google-genai package is not installed", "missing_sdk", retryable=False) from error
        self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _call_model(self, prompt: str) -> str:
        def invoke() -> str:
            response = self._client_instance().models.generate_content(model=self.model, contents=prompt)
            return extract_text(response)

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(invoke)
        shutdown_started = False
        try:
            return future.result(timeout=self.timeout_seconds)
        except FutureTimeout as error:
            future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
            shutdown_started = True
            raise GeminiServiceError("Gemini request timed out", "timeout", retryable=True) from error
        except Exception as error:
            executor.shutdown(wait=False, cancel_futures=True)
            shutdown_started = True
            raise classify_gemini_error(error) from error
        finally:
            if not shutdown_started and future.done():
                executor.shutdown(wait=False, cancel_futures=True)

    @staticmethod
    def _parse_json_response(text: str) -> GeminiJsonResponse | None:
        raw = extract_json_candidate(text)
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return validate_gemini_json(data)


def build_structured_prompt(
    language: str,
    user_role: str,
    current_step: str,
    profile_data: dict[str, Any],
    recent_messages: list[dict[str, str]],
    task: str,
) -> str:
    system_prompt = load_system_prompt()
    context = minimal_context(
        language=language,
        user_role=user_role,
        current_step=current_step,
        profile_data=profile_data,
        recent_messages=recent_messages,
        task=task,
    )
    return (
        f"{system_prompt}\n\n"
        "Use this context only. Do not invent missing data.\n"
        f"{json.dumps(context, ensure_ascii=False)}\n\n"
        "Return valid JSON only with keys: message, next_field, profile_updates, warnings, confidence."
    )


def minimal_context(
    language: str,
    user_role: str,
    current_step: str,
    profile_data: dict[str, Any],
    recent_messages: list[dict[str, str]],
    task: str,
) -> dict[str, Any]:
    return {
        "language": normalize_language(language),
        "user_role": user_role if user_role in ALLOWED_ROLES else "candidate",
        "current_step": sanitize_token(current_step) or "unknown",
        "profile_data": sanitize_profile_data(profile_data),
        "recent_messages": sanitize_recent_messages(recent_messages),
        "task": sanitize_token(task) or "ask_next_question",
    }


def validate_gemini_json(data: Any) -> GeminiJsonResponse | None:
    if not isinstance(data, dict):
        return None
    message = str(data.get("message") or "").strip()
    if not message:
        return None
    profile_updates = data.get("profile_updates")
    warnings = data.get("warnings")
    try:
        confidence = float(data.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    return GeminiJsonResponse(
        message=message[:2000],
        next_field=sanitize_token(data.get("next_field")),
        profile_updates=profile_updates if isinstance(profile_updates, dict) else {},
        warnings=[str(item)[:240] for item in warnings] if isinstance(warnings, list) else [],
        confidence=max(0.0, min(confidence, 1.0)),
    )


def fallback_message(language: str) -> str:
    return FALLBACK_MESSAGES.get(normalize_language(language), FALLBACK_MESSAGES["en"])


def normalize_language(language: str | None) -> str:
    normalized = str(language or "en").lower().split("-")[0]
    return normalized if normalized in ALLOWED_LANGUAGES else "en"


def sanitize_user_text(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> str:
    cleaned = re.sub(r"<\s*/?\s*(script|iframe|object|embed)[^>]*>", "", str(text or ""), flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    return cleaned.strip()[:max_length]


def sanitize_token(value: Any) -> str | None:
    if value is None:
        return None
    token = re.sub(r"[^a-zA-Z0-9_.-]", "_", str(value).strip())[:80]
    return token or None


def sanitize_recent_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    safe = []
    for item in (messages or [])[-6:]:
        if not isinstance(item, dict):
            continue
        role = "assistant" if item.get("role") == "assistant" else "user"
        content = sanitize_user_text(str(item.get("content") or ""), max_length=600)
        if content:
            safe.append({"role": role, "content": content})
    return safe


def sanitize_profile_data(profile_data: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "profession",
        "experience_years",
        "country",
        "languages",
        "documents",
        "desired_salary",
        "ready_from",
        "vacancy",
        "employer",
        "progress",
    }
    safe: dict[str, Any] = {}
    for key, value in (profile_data or {}).items():
        if key not in allowed:
            continue
        if key in {"employer", "vacancy"} and isinstance(value, dict):
            safe[key] = {
                sub_key: sub_value
                for sub_key, sub_value in value.items()
                if sub_key not in {"contact_email", "contact_phone", "phone", "email"}
            }
        elif isinstance(value, (str, int, float, bool, list, dict)) or value is None:
            safe[key] = value
    return safe


def extract_json_candidate(text: str) -> str | None:
    stripped = str(text or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return stripped[start : end + 1]
    return None


def extract_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return str(text)
    candidates = getattr(response, "candidates", None) or []
    parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            part_text = getattr(part, "text", None)
            if part_text:
                parts.append(str(part_text))
    return "\n".join(parts).strip()


def classify_gemini_error(error: Exception) -> GeminiServiceError:
    text = str(error).lower()
    if "429" in text or "rate" in text or "quota" in text:
        return GeminiServiceError("Gemini rate limit", "rate_limited", retryable=True)
    if "timeout" in text:
        return GeminiServiceError("Gemini timeout", "timeout", retryable=True)
    if "401" in text or "403" in text or "api key" in text or "permission" in text or "unauthorized" in text:
        return GeminiServiceError("Gemini authorization failed", "auth_error", retryable=False)
    if "not found" in text or "model" in text and "invalid" in text:
        return GeminiServiceError("Gemini configuration error", "configuration_error", retryable=False)
    return GeminiServiceError("Gemini temporary error", "temporary_unavailable", retryable=True)


def load_system_prompt() -> str:
    path = Path(__file__).resolve().parents[1] / "ai" / "prompts" / "atlas_system_prompt.txt"
    return path.read_text(encoding="utf-8")
