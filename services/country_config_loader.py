"""Country configuration loader.

Countries are added by placing a JSON file in configs/countries. Business code
loads countries by ISO code and does not branch on country names.
"""

import json
from pathlib import Path
from typing import Any


class CountryConfigError(Exception):
    """Raised when a country config is missing or invalid."""


class CountryConfigLoader:
    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or Path(__file__).resolve().parents[1] / "configs" / "countries"
        self._cache_by_code: dict[str, dict[str, Any]] = {}

    def load_all(self) -> dict[str, dict[str, Any]]:
        configs: dict[str, dict[str, Any]] = {}

        for config_path in sorted(self.config_dir.glob("*.json")):
            config = self._load_file(config_path)
            code = self._validate_config(config, config_path)
            configs[code] = config

        self._cache_by_code.update(configs)
        return configs

    def load_by_code(self, country_code: str) -> dict[str, Any]:
        normalized_code = country_code.upper()

        if normalized_code not in self._cache_by_code:
            self.load_all()

        if normalized_code not in self._cache_by_code:
            available = ", ".join(sorted(self._cache_by_code)) or "none"
            raise CountryConfigError(
                f"Country config '{normalized_code}' is not available. Available: {available}"
            )

        return self._cache_by_code[normalized_code]

    @staticmethod
    def _load_file(config_path: Path) -> dict[str, Any]:
        with config_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _validate_config(config: dict[str, Any], config_path: Path) -> str:
        required_keys = {"code", "name", "currency", "languages", "documents", "compliance"}
        missing = required_keys - set(config)

        if missing:
            missing_keys = ", ".join(sorted(missing))
            raise CountryConfigError(f"{config_path.name} is missing keys: {missing_keys}")

        code = str(config["code"]).upper()
        if len(code) != 2:
            raise CountryConfigError(f"{config_path.name} must use a 2-letter ISO country code")

        config["code"] = code
        return code

