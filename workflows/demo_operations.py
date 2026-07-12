"""Demo for the EWU operations workflow."""

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
from services.country_config_loader import CountryConfigLoader
from workflows.operations_workflow import OperationsWorkflow


def build_workflow() -> OperationsWorkflow:
    demo_dir = Path(tempfile.mkdtemp(prefix="atlas_ewu_operations_"))
    database = JsonDatabase(demo_dir / "db")
    memory_store = JsonMemoryStore(demo_dir / "memory")
    crm = CrmService(
        candidates=CandidateRepository(database),
        employers=EmployerRepository(database),
        vacancies=VacancyRepository(database),
        matches=MatchRepository(database),
        documents=DocumentRepository(database),
        activity=ActivityRepository(database),
        memory_store=memory_store,
    )
    return OperationsWorkflow(
        crm=crm,
        memory_store=memory_store,
        country_loader=CountryConfigLoader(),
    )


def main() -> None:
    workflow = build_workflow()

    candidate_result = workflow.onboard_candidate(
        Candidate(
            first_name="Oleh",
            last_name="Bondar",
            email="oleh.bondar@example.com",
            phone="+380991112233",
            country_code="UA",
            profession_code="welder",
            languages=["uk", "pl"],
            years_of_experience=6,
            user_id="candidate-oleh",
            metadata={
                "desired_country_code": "PL",
                "desired_salary": 6400,
                "salary_currency": "PLN",
                "ready_from": "2026-07-20",
                "document_types": ["passport_or_id", "cv"],
            },
        )
    )

    employer_result = workflow.onboard_employer(
        Employer(
            company_name="North Steel Group",
            contact_email="jobs@north-steel.example",
            contact_phone="+48111222333",
            country_code="PL",
            industry="manufacturing",
            verified=False,
        )
    )

    employer_id = employer_result["employer"]["id"]
    pipeline_result = workflow.process_vacancy_pipeline(
        Vacancy(
            employer_id=employer_id,
            title="Welder",
            country_code="PL",
            profession_code="welder",
            salary_min=5800,
            salary_max=7200,
            currency="PLN",
            required_languages=["pl"],
            required_documents=["passport_or_id", "cv"],
            location="Poznan",
            metadata={
                "contract_type": "umowa_o_prace",
                "work_permission_status": "to_be_verified",
                "housing": True,
                "housing_terms": "Employer provides shared housing with written terms.",
                "salary_confirmed": True,
                "people_needed": 4,
                "requirements": ["mig_mag", "technical_drawing"],
            },
        )
    )

    print(
        {
            "candidate_onboarding": candidate_result,
            "employer_onboarding": employer_result,
            "vacancy_pipeline": pipeline_result,
        }
    )


if __name__ == "__main__":
    main()
