from pathlib import Path
import tempfile

from fastapi import HTTPException

from api import app as app_module
from api.schemas import CountryCreate
from core.models import Candidate, Vacancy
from database.json_database import JsonDatabase
from database.repositories import CandidateRepository, CountryRepository, VacancyRepository
from services.country_config_loader import CountryConfigLoader
from services.country_management import CountryManagementService
from tests.test_admin_security import request


def build_service(tmpdir: str) -> CountryManagementService:
    database = JsonDatabase(Path(tmpdir) / "db")
    return CountryManagementService(
        countries=CountryRepository(database),
        candidates=CandidateRepository(database),
        vacancies=VacancyRepository(database),
        config_loader=CountryConfigLoader(),
    )


def test_country_management_persists_public_countries_with_live_counts():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = build_service(tmpdir)
        service.create_country(
            {
                "code": "IT",
                "name": "Italy",
                "latitude": 41.8719,
                "longitude": 12.5674,
                "status": "active",
                "languages": ["it", "en"],
                "currency": "EUR",
                "services": ["recruitment"],
                "legalization_available": True,
                "training_available": True,
                "route": "/countries/it",
            }
        )
        service.candidates.add(
            Candidate(
                first_name="Ada",
                last_name="Atlas",
                email="ada@example.com",
                phone="+3900000",
                country_code="IT",
                profession_code="welder",
                languages=["it"],
            )
        )
        service.vacancies.add(
            Vacancy(
                employer_id="EMP-1",
                title="Welder",
                country_code="IT",
                profession_code="welder",
                salary_min=1000,
                salary_max=2000,
                currency="EUR",
                required_languages=["it"],
            )
        )

        country = service.public_countries()[0]

        assert country["code"] == "IT"
        assert country["status"] == "active"
        assert country["vacancies_count"] == 1
        assert country["candidates_count"] == 1


def test_country_admin_endpoints_require_authorization_and_support_lifecycle():
    try:
        app_module.admin_create_country(
            CountryCreate(code="NL", name="Netherlands", status="launching", latitude=52.1, longitude=5.2),
            request(),
        )
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("admin endpoint must require authorization")

    with tempfile.TemporaryDirectory() as tmpdir:
        service = build_service(tmpdir)
        created = service.create_country({"code": "NL", "name": "Netherlands", "status": "launching"})
        assert created.code == "NL"
        assert service.set_status(created.id, "active").status == "active"
        assert service.set_visibility(created.id, False).is_visible is False
        archived = service.archive_country(created.id)
        assert archived.config["archived"] is True


def test_landing_contains_globe_api_integration():
    from api.main_interface import LANDING_HTML, country_detail_html

    assert "ATLAS у світі" in LANDING_HTML
    assert "atlas-globe" in LANDING_HTML
    assert "/api/public/countries" in LANDING_HTML
    assert "prefers-reduced-motion" in LANDING_HTML
    assert "globe-fallback-list" in LANDING_HTML

    country_page = country_detail_html({"code": "PL", "name": "Poland", "status": "active", "route": "/countries/pl"})
    assert "Poland" in country_page
    assert "Для працівника" in country_page
