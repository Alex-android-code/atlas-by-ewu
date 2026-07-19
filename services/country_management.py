"""Country Management service for public globe and CRM administration."""

from __future__ import annotations

from typing import Any

from core.models import Candidate, Country, Vacancy, utc_now_iso
from database.repositories import CandidateRepository, CountryRepository, VacancyRepository
from services.country_config_loader import CountryConfigLoader


ALLOWED_COUNTRY_STATUSES = {"active", "launching", "planned"}

DEFAULT_COUNTRY_COORDINATES = {
    "DE": (51.1657, 10.4515),
    "PL": (51.9194, 19.1451),
    "PT": (39.3999, -8.2245),
    "ES": (40.4637, -3.7492),
    "UA": (48.3794, 31.1656),
}

DEFAULT_COUNTRY_STATUSES = {
    "PL": "active",
    "DE": "launching",
    "PT": "planned",
    "ES": "planned",
    "UA": "active",
}


class CountryManagementService:
    def __init__(
        self,
        countries: CountryRepository,
        candidates: CandidateRepository,
        vacancies: VacancyRepository,
        config_loader: CountryConfigLoader,
    ) -> None:
        self.countries = countries
        self.candidates = candidates
        self.vacancies = vacancies
        self.config_loader = config_loader

    def public_countries(self) -> list[dict[str, Any]]:
        return [
            self._with_live_counts(country).to_dict()
            for country in self._ordered_countries()
            if country.is_visible and not country.config.get("archived")
        ]

    def admin_countries(self) -> list[dict[str, Any]]:
        return [self._with_live_counts(country).to_dict() for country in self._ordered_countries()]

    def get_public_country(self, country_id_or_code: str) -> dict[str, Any] | None:
        country = self._find(country_id_or_code)
        if country is None or not country.is_visible or country.config.get("archived"):
            return None
        return self._with_live_counts(country).to_dict()

    def get_admin_country(self, country_id_or_code: str) -> dict[str, Any] | None:
        country = self._find(country_id_or_code)
        return self._with_live_counts(country).to_dict() if country else None

    def create_country(self, data: dict[str, Any]) -> Country:
        country = self._country_from_data(data)
        existing = self._find(country.code)
        if existing:
            raise ValueError(f"Country '{country.code}' already exists")
        now = utc_now_iso()
        country.created_at = now
        country.updated_at = now
        return self.countries.add(country)

    def update_country(self, country_id_or_code: str, data: dict[str, Any]) -> Country:
        country = self._require(country_id_or_code)
        for key, value in data.items():
            if value is None or not hasattr(country, key) or key in {"id", "created_at"}:
                continue
            setattr(country, key, self._normalized_value(key, value))
        country.updated_at = utc_now_iso()
        return self.countries.update(country)

    def set_status(self, country_id_or_code: str, status: str) -> Country:
        return self.update_country(country_id_or_code, {"status": status})

    def set_visibility(self, country_id_or_code: str, is_visible: bool) -> Country:
        return self.update_country(country_id_or_code, {"is_visible": is_visible})

    def archive_country(self, country_id_or_code: str) -> Country:
        country = self._require(country_id_or_code)
        country.is_visible = False
        country.config["archived"] = True
        country.config["archived_at"] = utc_now_iso()
        country.updated_at = utc_now_iso()
        return self.countries.update(country)

    def ensure_seed_countries(self) -> None:
        if self.countries.list():
            return
        for config in self.config_loader.load_all().values():
            code = str(config.get("code", "")).upper()
            lat, lon = DEFAULT_COUNTRY_COORDINATES.get(code, (0.0, 0.0))
            country = Country(
                code=code,
                name=str(config.get("name", code)),
                localized_names={"en": str(config.get("name", code))},
                flag_url=f"https://flagcdn.com/w80/{code.lower()}.png",
                latitude=lat,
                longitude=lon,
                status=DEFAULT_COUNTRY_STATUSES.get(code, "planned"),
                languages=list(config.get("languages", [])),
                currency=str(config.get("currency", "")),
                services=["recruitment", "candidate_profile", "document_support"],
                legalization_available=bool(config.get("documents")),
                training_available=True,
                partners=[],
                route=f"/countries/{code.lower()}",
                display_order=10 if code in {"PL", "UA"} else 40,
                seo_title=f"ATLAS {config.get('name', code)}",
                seo_description=f"ATLAS services and workforce operations in {config.get('name', code)}.",
                emergency_number=config.get("emergency_number"),
                config={"source": "country_config_seed"},
            )
            self.countries.add(country)

    def _ordered_countries(self) -> list[Country]:
        self.ensure_seed_countries()
        return sorted(self.countries.list(), key=lambda item: (item.display_order, item.name))

    def _with_live_counts(self, country: Country) -> Country:
        country.vacancies_count = sum(1 for vacancy in self.vacancies.list() if vacancy.country_code.upper() == country.code.upper())
        country.candidates_count = sum(1 for candidate in self.candidates.list() if candidate.country_code.upper() == country.code.upper())
        return country

    def _find(self, country_id_or_code: str) -> Country | None:
        normalized = str(country_id_or_code).strip().upper()
        for country in self.countries.list():
            if country.id == country_id_or_code or country.code.upper() == normalized:
                return country
        return None

    def _require(self, country_id_or_code: str) -> Country:
        country = self._find(country_id_or_code)
        if country is None:
            raise ValueError(f"Country '{country_id_or_code}' was not found")
        return country

    def _country_from_data(self, data: dict[str, Any]) -> Country:
        normalized = {key: self._normalized_value(key, value) for key, value in data.items() if value is not None}
        if not normalized.get("code") or not normalized.get("name"):
            raise ValueError("Country code and name are required")
        return Country(**normalized)

    @staticmethod
    def _normalized_value(key: str, value: Any) -> Any:
        if key == "code":
            return str(value).strip().upper()
        if key == "status":
            normalized = str(value or "planned").strip().lower()
            if normalized not in ALLOWED_COUNTRY_STATUSES:
                raise ValueError("Country status must be active, launching or planned")
            return normalized
        if key in {"latitude", "longitude"}:
            return float(value)
        if key in {"vacancies_count", "candidates_count", "display_order"}:
            return int(value)
        if key in {"legalization_available", "training_available", "is_visible"}:
            return bool(value)
        if key in {"languages", "services", "partners"}:
            return value if isinstance(value, list) else [str(value)]
        if key in {"localized_names", "config"}:
            return value if isinstance(value, dict) else {}
        return value
