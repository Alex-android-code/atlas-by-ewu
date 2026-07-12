"""Language state metadata prepared for future admin use."""

from dataclasses import dataclass

from core.languages import DEFAULT_LANGUAGE


@dataclass(frozen=True)
class UserLanguageMetadata:
    preferred_language: str = DEFAULT_LANGUAGE
    ui_language: str = DEFAULT_LANGUAGE
    conversation_language: str | None = None
    language_detected_at: str | None = None
    language_detection_confidence: float | None = None
