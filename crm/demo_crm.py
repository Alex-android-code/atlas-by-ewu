"""Run a small EWU CRM scenario."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.coordinator_agent import CoordinatorAgent
from core.models import Candidate, Employer, Vacancy
from crm.crm_service import CrmService
from database.json_database import JsonDatabase
from database.repositories import (
    CandidateRepository,
    ActivityRepository,
    DocumentRepository,
    EmployerRepository,
    MatchRepository,
    VacancyRepository,
)
from memory.memory_store import JsonMemoryStore


def build_crm() -> CrmService:
    database = JsonDatabase()
    memory_store = JsonMemoryStore()
    return CrmService(
        candidates=CandidateRepository(database),
        employers=EmployerRepository(database),
        vacancies=VacancyRepository(database),
        matches=MatchRepository(database),
        documents=DocumentRepository(database),
        activity=ActivityRepository(database),
        memory_store=memory_store,
    )


def main() -> None:
    crm = build_crm()

    candidate_1 = crm.create_candidate(
        Candidate(
            first_name="Ivan",
            last_name="Koval",
            email="ivan.koval@example.com",
            phone="+380501112233",
            country_code="UA",
            profession_code="welder",
            languages=["uk", "pl"],
            years_of_experience=5,
            user_id="candidate-ivan",
            documents=["DOC-001", "DOC-002"],
            metadata={
                "desired_country_code": "PL",
                "desired_salary": 6200,
                "salary_currency": "PLN",
                "ready_from": "2026-07-15",
                "document_types": ["passport_or_id", "cv"],
            },
        )
    )
    candidate_2 = crm.create_candidate(
        Candidate(
            first_name="Maria",
            last_name="Shevchenko",
            email="maria.shevchenko@example.com",
            phone="+380671112233",
            country_code="UA",
            profession_code="warehouse_worker",
            languages=["uk", "en"],
            years_of_experience=2,
            user_id="candidate-maria",
            metadata={
                "desired_country_code": "PL",
                "desired_salary": 4800,
                "salary_currency": "PLN",
                "ready_from": "2026-08-01",
                "document_types": ["passport_or_id", "cv"],
            },
        )
    )

    employer = crm.create_employer(
        Employer(
            company_name="Baltic Metal Works",
            contact_email="hr@baltic-metal.example",
            contact_phone="+48123123123",
            country_code="PL",
            industry="manufacturing",
            verified=False,
        )
    )
    vacancy = crm.create_vacancy(
        Vacancy(
            employer_id=employer.id,
            title="MIG/MAG Welder",
            country_code="PL",
            profession_code="welder",
            salary_min=5500,
            salary_max=7000,
            currency="PLN",
            required_languages=["pl"],
            required_documents=["passport_or_id", "cv"],
            location="Gdansk",
            metadata={
                "contract_type": "umowa_o_prace",
                "housing": True,
                "people_needed": 3,
                "requirements": ["mig_mag", "technical_drawing"],
            },
        )
    )

    matches = crm.find_matches_for_vacancy(vacancy.id)
    dashboard = crm.coordinator_dashboard()
    coordinator = CoordinatorAgent(JsonMemoryStore())
    context = coordinator.build_context(
        user_id="coordinator-main",
        metadata={"dashboard": dashboard},
    )
    summary = coordinator.respond("Build daily CRM summary.", context)

    print(
        {
            "created_candidates": [candidate_1.id, candidate_2.id],
            "created_employer": employer.id,
            "created_vacancy": vacancy.id,
            "matches": [match.to_dict() for match in matches],
            "coordinator_summary": summary["summary"],
        }
    )


if __name__ == "__main__":
    main()
