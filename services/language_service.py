"""Configuration-driven language and translation service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.languages import DEFAULT_LANGUAGE


class LanguageService:
    """Loads enabled languages and translations without hardcoded UI language lists."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or Path(__file__).resolve().parents[1] / "configs" / "languages"
        self.languages_file = self.config_dir / "languages.json"

    def get_available_languages(self) -> list[dict[str, Any]]:
        languages = self._read_json(self.languages_file, fallback=[])
        return [language for language in languages if language.get("enabled") is True]

    def get_current_language(
        self,
        selected_language: str | None = None,
        browser_language: str | None = None,
    ) -> str:
        available_codes = {language["code"] for language in self.get_available_languages()}
        normalized_selected = self._normalize_code(selected_language)
        if normalized_selected in available_codes:
            return normalized_selected

        normalized_browser = self._normalize_code(browser_language)
        if normalized_browser in available_codes:
            return normalized_browser

        default_language = self._default_language()
        if default_language in available_codes:
            return default_language

        if DEFAULT_LANGUAGE in available_codes:
            return DEFAULT_LANGUAGE
        if "en" in available_codes:
            return "en"
        return next(iter(available_codes), DEFAULT_LANGUAGE)

    def set_language(self, code: str) -> str:
        normalized_code = self._normalize_code(code)
        available_codes = {language["code"] for language in self.get_available_languages()}
        if normalized_code not in available_codes:
            return self.get_current_language()
        return normalized_code

    def load_translations(self, code: str) -> dict[str, str]:
        current = self._read_translation(self._normalize_code(code))
        default = self._read_translation(DEFAULT_LANGUAGE)
        english = self._read_translation("en")
        merged: dict[str, str] = {}
        for source in (default, english, current):
            merged.update(source)
        return merged

    def translate(self, key: str, code: str) -> str:
        translations = self.load_translations(code)
        return translations.get(key, key)

    def bootstrap(
        self,
        selected_language: str | None = None,
        browser_language: str | None = None,
    ) -> dict[str, Any]:
        current_language = self.get_current_language(
            selected_language=selected_language,
            browser_language=browser_language,
        )
        return {
            "languages": self.get_available_languages(),
            "current_language": current_language,
            "translations": self.load_translations(current_language),
        }

    def _default_language(self) -> str | None:
        for language in self.get_available_languages():
            if language.get("default") is True:
                return language.get("code")
        return None

    def _read_translation(self, code: str) -> dict[str, str]:
        path = self.config_dir / f"{code}.json"
        return self._read_json(path, fallback={})

    @staticmethod
    def _normalize_code(code: str | None) -> str:
        if not code:
            return ""
        return code.strip().lower().split("-")[0].split("_")[0]

    @staticmethod
    def _read_json(path: Path, fallback: Any) -> Any:
        if not path.exists():
            return fallback
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
