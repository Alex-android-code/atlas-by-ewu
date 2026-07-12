"""Language detection for public ATLAS coordinator experience."""

from dataclasses import dataclass, field

from core.languages import DEFAULT_LANGUAGE
from services.language_service import LanguageService


@dataclass
class LanguageDetectorService:
    fallback_language: str = DEFAULT_LANGUAGE
    language_service: LanguageService = field(default_factory=LanguageService)

    def detect(
        self,
        browser_language: str | None = None,
        saved_preference: str | None = None,
        first_message: str | None = None,
    ) -> str:
        supported_languages = self._supported_languages()
        message_language = self._detect_from_message(first_message)

        # Explicit UI/conversation language wins when present. The current
        # message still helps when the interface has no saved preference yet.
        ordered = [
            self._normalize(saved_preference),
            message_language,
            self._normalize_browser_language(browser_language),
            self.fallback_language,
        ]
        for candidate in ordered:
            if candidate in supported_languages:
                return candidate
        return self.language_service.get_current_language()

    def _supported_languages(self) -> set[str]:
        return {language["code"] for language in self.language_service.get_available_languages()}

    @staticmethod
    def _normalize(value: str | None) -> str | None:
        if not value:
            return None
        return value.strip().lower().split("-")[0].split("_")[0]

    def _normalize_browser_language(self, value: str | None) -> str | None:
        return self._normalize(value)

    def _detect_from_message(self, message: str | None) -> str | None:
        if not message:
            return None
        text = message.lower()
        if any(ch in text for ch in "іїєґ") or any(
            word in text
            for word in ("потріб", "шукаю", "працю", "документ", "зварюв", "роботу", "працівник")
        ):
            return "uk"
        if any(
            word in text
            for word in ("работ", "нужн", "ищу", "сотрудник", "работник", "сварщик", "документ", "зарплат")
        ):
            return "ru"
        if any(word in text for word in ("praca", "pracownik", "spawacz", "zatrudn", "potrzeb", "dokument", "wynagrodz")):
            return "pl"
        if any(word in text for word in ("arbeit", "mitarbeiter", "dokument", "lohn")):
            return "de"
        if any(word in text for word in ("trabajo", "empleados", "documento", "salario")):
            return "es"
        if any(word in text for word in ("trabalho", "funcionarios", "funcionários", "documento", "salário")):
            return "pt"
        if any(word in text for word in ("job", "work", "employees", "workers", "salary", "documents")):
            return "en"
        return None
