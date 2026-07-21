import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app as app_module
import api.dependencies as dependencies
from database.json_database import JsonDatabase
from database.repositories import ActivityRepository, DocumentRepository, EmployerRepository
from services.employer_onboarding_workflow import EmployerOnboardingWorkflowService


class EmployerOnboardingWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.service = EmployerOnboardingWorkflowService(
            database=database,
            employers=EmployerRepository(database),
            documents=DocumentRepository(database),
            activity=ActivityRepository(database),
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_completion_requires_company_contact_hiring_and_consents(self) -> None:
        self.service.patch_step("emp-user", "company", {"company_name": "EWU Test", "country_code": "PL", "industry": "Logistics"})

        with self.assertRaises(ValueError) as error:
            self.service.complete("emp-user")

        self.assertIn("Incomplete employer onboarding steps", str(error.exception))
        self.assertIn("Required employer consents", str(error.exception))

    def test_successful_completion_creates_employer_once_and_dashboard(self) -> None:
        self.service.patch_step("emp-user", "company", {"company_name": "EWU Test", "country_code": "PL", "industry": "Logistics"})
        self.service.patch_step("emp-user", "contact", {"contact_person": "Anna", "contact_email": "anna@example.com", "contact_phone": "+48123"})
        self.service.patch_step("emp-user", "hiring_needs", {"profession": "Welder", "quantity": 3, "country_code": "PL", "salary_min": 25})
        self.service.patch_step("emp-user", "documents", {"files": [{"id": "FIL-1", "kind": "employer-document", "original_name": "nip.pdf", "stored_name": "nip.pdf"}]})
        self.service.patch_step("emp-user", "consents", {"terms": True, "privacy": True, "businessProcessing": True, "matching": False})

        completed = self.service.complete("emp-user")
        retried = self.service.complete("emp-user")
        dashboard = self.service.dashboard("emp-user")

        self.assertEqual(completed["session"]["status"], "completed")
        self.assertEqual(retried["employer"]["id"], completed["employer"]["id"])
        self.assertEqual(dashboard["onboarding"]["redirectTo"], None)
        self.assertEqual(dashboard["readiness"]["documentsStatus"], "uploaded")
        self.assertEqual(dashboard["readiness"]["verificationStatus"], "pending_review")
        self.assertEqual(len(dashboard["documents"]), 1)
        self.assertTrue(dashboard["recentActivity"])


class EmployerOnboardingApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.database = JsonDatabase(Path(self.tmpdir.name) / "db")
        dependencies.get_database.cache_clear()
        self.patches = [
            patch.object(dependencies, "get_database", return_value=self.database),
            patch.object(app_module, "get_database", return_value=self.database),
        ]
        for item in self.patches:
            item.start()
        self.client = TestClient(app_module.app)

    def tearDown(self) -> None:
        for item in reversed(self.patches):
            item.stop()
        dependencies.get_database.cache_clear()
        self.tmpdir.cleanup()

    def test_employer_api_happy_path_and_dashboard_guard(self) -> None:
        headers = {"X-ATLAS-User-Id": "employer-api-user"}
        start = self.client.get("/api/employer/dashboard", headers=headers)
        self.assertIn("/employer/onboarding?step=", start.json()["onboarding"]["redirectTo"])

        incomplete = self.client.post("/api/employer/onboarding/complete", headers=headers)
        self.assertEqual(incomplete.status_code, 400)

        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "company", "data": {"company_name": "Atlas Factory", "country_code": "PL", "industry": "Manufacturing"}})
        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "contact", "data": {"contact_person": "Ola", "contact_email": "ola@example.com"}})
        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "hiring_needs", "data": {"profession": "Welder", "quantity": 5, "country_code": "PL"}})
        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "consents", "data": {"terms": True, "privacy": True, "businessProcessing": True}})

        completed = self.client.post("/api/employer/onboarding/complete", headers=headers)
        dashboard = self.client.get("/api/employer/dashboard", headers=headers)

        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.json()["session"]["status"], "completed")
        self.assertEqual(dashboard.json()["employer"]["company_name"], "Atlas Factory")
        self.assertEqual(dashboard.json()["readiness"]["documentsStatus"], "missing")
        self.assertTrue(dashboard.json()["recommendedActions"])


if __name__ == "__main__":
    unittest.main()
