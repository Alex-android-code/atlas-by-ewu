import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app as app_module
import api.dependencies as dependencies
from core.models import Candidate, Employer, Vacancy
from database.json_database import JsonDatabase
from database.repositories import CandidateRepository, EmployerRepository, VacancyRepository


class ColosseumMVPApiTests(unittest.TestCase):
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
        self.headers = {"X-ATLAS-User-Id": "demo-operator", "X-ATLAS-Role": "admin"}

    def tearDown(self) -> None:
        for item in reversed(self.patches):
            item.stop()
        dependencies.get_database.cache_clear()
        self.tmpdir.cleanup()

    def test_demo_seed_creates_repeatable_colosseum_flow(self) -> None:
        response = self.client.post("/api/demo/seed", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["credential"]["status"], "verified")
        self.assertTrue(data["credential"]["credential_hash"])
        self.assertIn("explorer.solana.com/tx/", data["credential"]["explorer_url"])
        self.assertEqual(data["escrow"]["status"], "created")
        self.assertTrue(data["escrow"]["human_approval_required"])
        self.assertFalse(data["escrow"]["ai_release_allowed"])

        status = self.client.get("/api/demo/status").json()
        self.assertTrue(status["seeded"])
        self.assertEqual(status["credential_id"], data["credential"]["id"])

    def test_credential_lifecycle_requires_issuer_for_verification(self) -> None:
        candidate = CandidateRepository(self.database).add(
            Candidate(
                first_name="Demo",
                last_name="Worker",
                email="candidate@demo.atlas",
                phone="+4800",
                country_code="UA",
                profession_code="welder",
                languages=["pl"],
                user_id="candidate-demo",
            )
        )
        created = self.client.post(
            "/api/credentials/request",
            headers={"X-ATLAS-User-Id": "candidate-demo", "X-ATLAS-Role": "candidate"},
            json={"candidate_id": candidate.id, "title": "Welder certificate"},
        )
        self.assertEqual(created.status_code, 200)
        credential_id = created.json()["credential"]["id"]

        forbidden = self.client.post(
            f"/api/credentials/{credential_id}/verify",
            headers={"X-ATLAS-User-Id": "candidate-demo", "X-ATLAS-Role": "candidate"},
            json={"note": "try self verify"},
        )
        self.assertEqual(forbidden.status_code, 403)

        verified = self.client.post(
            f"/api/credentials/{credential_id}/verify",
            headers={"X-ATLAS-User-Id": "issuer-demo", "X-ATLAS-Role": "issuer"},
            json={"note": "issuer verified"},
        )
        self.assertEqual(verified.status_code, 200)
        self.assertEqual(verified.json()["credential"]["status"], "verified")

    def test_escrow_release_requires_funding_and_blocks_double_release(self) -> None:
        employer = EmployerRepository(self.database).add(
            Employer(
                company_name="Demo Employer",
                contact_email="employer@demo.atlas",
                contact_phone="+4800",
                country_code="PL",
                industry="manufacturing",
            )
        )
        candidate = CandidateRepository(self.database).add(
            Candidate(
                first_name="Demo",
                last_name="Candidate",
                email="worker@demo.atlas",
                phone="+4801",
                country_code="UA",
                profession_code="welder",
                languages=["pl"],
            )
        )
        vacancy = VacancyRepository(self.database).add(
            Vacancy(
                employer_id=employer.id,
                title="Welder",
                country_code="PL",
                profession_code="welder",
                salary_min=100,
                salary_max=100,
                currency="DEVNET_SOL",
                required_languages=["pl"],
            )
        )
        created = self.client.post(
            "/api/escrows",
            headers={"X-ATLAS-User-Id": "employer-demo", "X-ATLAS-Role": "employer"},
            json={
                "employer_id": employer.id,
                "recruiter_id": "recruiter-demo",
                "candidate_id": candidate.id,
                "job_id": vacancy.id,
                "total_amount": 100,
                "recruiter_share": 70,
                "partner_share": 10,
                "platform_share": 20,
            },
        )
        self.assertEqual(created.status_code, 200)
        escrow_id = created.json()["escrow"]["id"]

        early_release = self.client.post(
            f"/api/escrows/{escrow_id}/release",
            headers={"X-ATLAS-User-Id": "employer-demo", "X-ATLAS-Role": "employer"},
        )
        self.assertEqual(early_release.status_code, 400)

        funded = self.client.post(f"/api/escrows/{escrow_id}/fund", headers={"X-ATLAS-User-Id": "employer-demo", "X-ATLAS-Role": "employer"})
        self.assertEqual(funded.status_code, 200)
        approved = self.client.post(
            f"/api/escrows/{escrow_id}/approve-milestone",
            headers={"X-ATLAS-User-Id": "employer-demo", "X-ATLAS-Role": "employer"},
            json={"note": "candidate started"},
        )
        self.assertEqual(approved.status_code, 200)
        released = self.client.post(f"/api/escrows/{escrow_id}/release", headers={"X-ATLAS-User-Id": "employer-demo", "X-ATLAS-Role": "employer"})
        self.assertEqual(released.status_code, 200)
        self.assertIn("explorer.solana.com/tx/", released.json()["escrow"]["release_explorer_url"])

        double_release = self.client.post(f"/api/escrows/{escrow_id}/release", headers={"X-ATLAS-User-Id": "employer-demo", "X-ATLAS-Role": "employer"})
        self.assertEqual(double_release.status_code, 400)

    def test_privacy_aliases_return_export_and_delete_request(self) -> None:
        headers = {"X-ATLAS-User-Id": "privacy-demo"}
        export = self.client.get("/privacy/export", headers=headers)
        delete = self.client.post("/privacy/delete-request", headers=headers, json={"contact": "privacy@example.com"})
        revoke = self.client.post("/privacy/revoke-consent", headers=headers, json={"consent_type": "ai_profiling"})

        self.assertEqual(export.status_code, 200)
        self.assertFalse(export.json()["privacy_model"]["on_chain_pii"])
        self.assertEqual(delete.status_code, 200)
        self.assertEqual(delete.json()["request"]["request_type"], "delete")
        self.assertEqual(revoke.status_code, 200)
        self.assertEqual(revoke.json()["request"]["request_type"], "consent_withdrawal")


if __name__ == "__main__":
    unittest.main()
