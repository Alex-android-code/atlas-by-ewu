import tempfile
import unittest
from pathlib import Path

from core.models import Candidate, Employer, Vacancy
from crm.crm_service import CrmService
from database.json_database import JsonDatabase
from database.repositories import (
    ActivityRepository,
    CandidateRepository,
    DocumentRepository,
    EmployerRepository,
    MatchRepository,
    VacancyRepository,
)
from memory.memory_store import JsonMemoryStore
from services.product_architecture import ProductArchitectureService


class ProductArchitectureTests(unittest.TestCase):
    def test_role_navigation_is_config_driven(self):
        service = ProductArchitectureService()

        admin_nav = service.navigation_for_role("admin")
        candidate_nav = service.navigation_for_role("candidate")

        self.assertIn("command_center", [item["code"] for item in admin_nav])
        self.assertIn("ai_agent", [item["code"] for item in candidate_nav])
        self.assertNotIn("finance", [item["code"] for item in candidate_nav])

    def test_pipelines_are_centralized(self):
        pipelines = ProductArchitectureService().pipelines()["pipelines"]

        self.assertEqual(pipelines["candidate"][0], "new")
        self.assertIn("awaiting_approval", pipelines["vacancy"])
        self.assertIn("disputed", pipelines["deal"])

    def test_crm_workspace_builds_views_from_current_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            database = JsonDatabase(Path(tmpdir) / "db")
            crm = CrmService(
                candidates=CandidateRepository(database),
                employers=EmployerRepository(database),
                vacancies=VacancyRepository(database),
                matches=MatchRepository(database),
                documents=DocumentRepository(database),
                activity=ActivityRepository(database),
                memory_store=JsonMemoryStore(Path(tmpdir) / "memory"),
            )
            crm.candidates.add(
                Candidate(
                    first_name="Ana",
                    last_name="Worker",
                    email="ana@example.com",
                    phone="+48123123123",
                    country_code="PL",
                    profession_code="welder",
                    languages=["pl"],
                    status="documents_pending",
                )
            )
            crm.employers.add(
                Employer(
                    company_name="Atlas Works",
                    contact_email="hr@example.com",
                    contact_phone="+48111222333",
                    country_code="PL",
                    industry="manufacturing",
                )
            )
            crm.vacancies.add(
                Vacancy(
                    employer_id="EMP-1",
                    title="Welder",
                    country_code="PL",
                    profession_code="welder",
                    salary_min=5000,
                    salary_max=6500,
                    currency="PLN",
                    required_languages=["pl"],
                    status="pending_review",
                )
            )

            workspace = ProductArchitectureService().crm_workspace(crm)

        self.assertTrue(workspace["daily_brief"]["recommendations"])
        self.assertEqual(workspace["kanban_view"]["candidate"][2]["status"], "verification")
        self.assertEqual(workspace["kanban_view"]["candidate"][2]["count"], 1)
        self.assertEqual(workspace["intelligence_view"]["groups"][0]["count"], 1)


if __name__ == "__main__":
    unittest.main()
