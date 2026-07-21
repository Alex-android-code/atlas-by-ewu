import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app as app_module
import api.dependencies as dependencies
from core.models import Document, DocumentStatus
from database.json_database import JsonDatabase
from database.repositories import ActivityRepository, DocumentRepository, EmployerRepository
from services.employer_onboarding_workflow import EmployerOnboardingWorkflowService


def company_identity(name: str = "EWU Test") -> dict:
    return {
        "legal_name": name,
        "trading_name": name,
        "country_code": "PL",
        "registration_number": "KRS-123",
        "tax_number": "NIP-123",
        "official_email": "owner@example.com",
        "website": "https://ewu-test.example",
        "industry": "Logistics",
    }


def required_consents() -> dict:
    return {
        "required": {
            "termsForBusiness": True,
            "dataProcessing": True,
            "representativeAuthority": True,
            "lawfulCandidateUse": True,
            "nonDiscrimination": True,
        },
        "optional": {"aiMatching": True, "analytics": False},
    }


class EmployerOnboardingWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.documents = DocumentRepository(self.database)
        self.service = EmployerOnboardingWorkflowService(
            database=self.database,
            employers=EmployerRepository(self.database),
            documents=self.documents,
            activity=ActivityRepository(self.database),
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_completion_requires_company_membership_and_required_consents(self) -> None:
        self.service.patch_step("emp-user", "company_identity", company_identity())

        with self.assertRaises(ValueError) as error:
            self.service.complete("emp-user")

        self.assertIn("Incomplete employer onboarding steps", str(error.exception))
        self.assertIn("Required employer consents", str(error.exception))

    def test_successful_completion_creates_company_employer_and_dashboard(self) -> None:
        self.documents.add(Document(owner_id="emp-user", document_type="employer_document", country_code="PL", status=DocumentStatus.SUBMITTED, metadata={"employer_onboarding_file_id": "FIL-1", "original_name": "krs.pdf"}))
        self.service.patch_step("emp-user", "employer_agent", {"name": "Atlas Recruiter", "tasks": ["matching", "drafts"]})
        self.service.patch_step("emp-user", "company_identity", company_identity())
        self.service.patch_step("emp-user", "company_verification", {"documentFileIds": ["FIL-1"]})
        self.service.patch_step("emp-user", "company_profile", {"short_description": "International hiring", "benefits": ["housing"], "foreigner_support": True})
        self.service.patch_step("emp-user", "locations", {"locations": [{"type": "headquarters", "country": "PL", "city": "Warsaw"}]})
        self.service.patch_step("emp-user", "team", {"invitations": [{"email": "recruiter@example.com", "role": "recruiter"}]})
        self.service.patch_step("emp-user", "hiring_needs", {"profession": "Welder", "quantity": 3, "salary_min": 25, "salary_max": 35, "currency": "PLN"})
        self.service.patch_step("emp-user", "hiring_process", {})
        self.service.patch_step("emp-user", "consents", required_consents())

        completed = self.service.complete("emp-user")
        retried = self.service.complete("emp-user")
        dashboard = self.service.dashboard("emp-user")

        self.assertEqual(completed["session"]["status"], "completed")
        self.assertEqual(retried["employer"]["id"], completed["employer"]["id"])
        self.assertEqual(dashboard["onboarding"]["redirectTo"], None)
        self.assertEqual(dashboard["company"]["legalName"], "EWU Test")
        self.assertEqual(dashboard["verification"]["status"], "pending")
        self.assertEqual(dashboard["membership"]["role"], "company_owner")
        self.assertIn("members:manage", dashboard["membership"]["permissions"])
        self.assertEqual(dashboard["hiringNeeds"]["totalOpenings"], 3)
        self.assertTrue(dashboard["consents"]["requiredComplete"])
        self.assertTrue(dashboard["recentActivity"])

    def test_duplicate_company_is_not_created_automatically(self) -> None:
        self.service.patch_step("owner", "company_identity", company_identity("Atlas Duplicate"))
        session = self.service.patch_step("other", "company_identity", company_identity("Atlas Duplicate"))

        self.assertTrue(session["data"]["company_identity"]["duplicate_detected"])
        self.assertTrue(session["data"]["company_identity"]["safe_join_required"])

        with self.assertRaises(ValueError):
            self.service.complete("other")

    def test_invitation_token_is_hashed_single_use_and_owner_cannot_be_removed(self) -> None:
        self.service.patch_step("owner", "company_identity", company_identity())
        company_id = self.service.get_or_start("owner")["company_id"]
        invitation = self.service.invite_member("owner", company_id, {"email": "hr@example.com", "role": "hr_manager"})

        stored = self.database.get("company_invitations", invitation["id"])
        self.assertNotIn("token", stored)
        self.assertNotEqual(stored["tokenHash"], invitation["token"])

        accepted = self.service.accept_invitation("hr-user", invitation["token"])
        self.assertEqual(accepted["member"]["role"], "hr_manager")

        with self.assertRaises(ValueError):
            self.service.accept_invitation("hr-user-2", invitation["token"])

        owner_member = self.service.dashboard("owner")["membership"]["id"]
        with self.assertRaises(ValueError):
            self.service.remove_member("owner", company_id, owner_member)

    def test_tenant_isolation_blocks_foreign_company_access(self) -> None:
        self.service.patch_step("owner", "company_identity", company_identity())
        company_id = self.service.get_or_start("owner")["company_id"]

        with self.assertRaises(PermissionError):
            self.service.get_company("intruder", company_id)


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

    def test_employer_api_happy_path_company_routes_and_dashboard_guard(self) -> None:
        headers = {"X-ATLAS-User-Id": "employer-api-user"}
        start = self.client.get("/api/employer/dashboard", headers=headers)
        self.assertIn("/employer/onboarding?step=", start.json()["onboarding"]["redirectTo"])

        incomplete = self.client.post("/api/employer/onboarding/complete", headers=headers)
        self.assertEqual(incomplete.status_code, 400)

        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "employer_agent", "data": {"name": "API Recruiter"}})
        identity = self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "company_identity", "data": company_identity("Atlas Factory")})
        company_id = identity.json()["company_id"]
        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "company_profile", "data": {"industry": "Manufacturing", "short_description": "Factory"}})
        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "locations", "data": {"locations": [{"country": "PL", "city": "Gdansk"}]}})
        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "hiring_needs", "data": {"profession": "Welder", "quantity": 5, "salary_min": 20, "salary_max": 30}})
        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "hiring_process", "data": {}})
        self.client.patch("/api/employer/onboarding", headers=headers, json={"step": "consents", "data": required_consents()})

        completed = self.client.post("/api/employer/onboarding/complete", headers=headers)
        dashboard = self.client.get("/api/employer/dashboard", headers=headers)
        forbidden = self.client.get(f"/api/companies/{company_id}", headers={"X-ATLAS-User-Id": "other-user"})
        update = self.client.patch(f"/api/companies/{company_id}", headers=headers, json={"data": {"trading_name": "Atlas Factory PL"}})
        members = self.client.get(f"/api/companies/{company_id}/members", headers=headers)

        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.json()["session"]["status"], "completed")
        self.assertEqual(dashboard.json()["company"]["legalName"], "Atlas Factory")
        self.assertEqual(dashboard.json()["hiringNeeds"]["totalOpenings"], 5)
        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(update.json()["trading_name"], "Atlas Factory PL")
        self.assertEqual(members.status_code, 200)


if __name__ == "__main__":
    unittest.main()
