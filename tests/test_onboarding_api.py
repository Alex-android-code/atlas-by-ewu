import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from api import app as app_module
import api.dependencies as dependencies
from database.json_database import JsonDatabase
from services.onboarding_file_storage import OnboardingFileStorage


def png_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (420, 420), (212, 175, 55)).save(output, format="PNG")
    return output.getvalue()


class OnboardingApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.storage = OnboardingFileStorage(Path(self.tmpdir.name) / "uploads")
        dependencies.get_database.cache_clear()
        self.patches = [
            patch.object(dependencies, "get_database", return_value=self.database),
            patch.object(app_module, "get_database", return_value=self.database),
            patch.object(app_module, "ONBOARDING_FILE_STORAGE", self.storage),
        ]
        for item in self.patches:
            item.start()
        self.client = TestClient(app_module.app)

    def tearDown(self) -> None:
        for item in reversed(self.patches):
            item.stop()
        dependencies.get_database.cache_clear()
        self.tmpdir.cleanup()

    def test_full_api_happy_path_to_dashboard(self) -> None:
        registered = self.client.post("/api/auth/register", json={"preferred_language": "uk"})
        self.assertEqual(registered.status_code, 200)
        user_id = registered.json()["user_id"]
        headers = {"X-ATLAS-User-Id": user_id}

        session = self.client.get("/api/onboarding", headers=headers).json()
        self.assertEqual(session["current_step"], "welcome")

        photo = self.client.post(
            "/api/files/upload",
            headers=headers,
            data={"kind": "profile-photo"},
            files={"file": ("avatar.png", png_bytes(), "image/png")},
        )
        self.assertEqual(photo.status_code, 200)
        self.assertTrue(photo.json()["file"]["thumbnail_url"])

        cv = self.client.post(
            "/api/files/upload",
            headers=headers,
            data={"kind": "cv"},
            files={"file": ("cv.pdf", b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF", "application/pdf")},
        )
        self.assertEqual(cv.status_code, 200)
        cv_file = cv.json()["file"]

        self.client.patch("/api/onboarding", headers=headers, json={"step": "agent", "data": {"name": "Ava"}})
        self.client.patch("/api/onboarding", headers=headers, json={"step": "profile_photo", "data": {"file": photo.json()["file"]}})
        self.client.patch("/api/onboarding", headers=headers, json={"step": "cv", "data": {"file": cv_file}})

        parsed = self.client.post(f"/api/cv/{cv_file['id']}/parse", headers=headers)
        self.assertEqual(parsed.status_code, 200)
        self.assertEqual(parsed.json()["status"], "queued")
        job = self.client.get(f"/api/cv/parse-jobs/{parsed.json()['id']}", headers=headers)
        self.assertEqual(job.json()["status"], "awaiting_review")
        result = self.client.get(f"/api/cv/parse-jobs/{parsed.json()['id']}/result", headers=headers)
        self.assertEqual(result.status_code, 200)

        self.client.post(
            f"/api/cv/parse-jobs/{parsed.json()['id']}/confirm",
            headers=headers,
            json={
                "acceptedFields": {"email": {"value": "worker@example.com", "sourceText": "worker@example.com"}},
                "editedFields": {},
                "rejectedFields": [],
            },
        )
        self.client.patch(
            "/api/onboarding",
            headers=headers,
            json={
                "step": "cv_review",
                "data": {"accepted_parsed_data": {"email": {"value": "worker@example.com", "source": "user_confirmed_cv_review"}}},
            },
        )
        self.client.patch(
            "/api/onboarding",
            headers=headers,
            json={"step": "consents", "data": {"terms": True, "privacy": True, "aiProcessing": True}},
        )
        dna = self.client.post("/api/professional-dna/generate", headers=headers)
        self.assertEqual(dna.status_code, 200)
        self.assertIn("formula", dna.json())

        completed = self.client.post("/api/onboarding/complete", headers=headers)
        self.assertEqual(completed.json()["session"]["status"], "completed")

        dashboard = self.client.get("/api/agent/dashboard", headers=headers)
        self.assertEqual(dashboard.status_code, 200)
        self.assertTrue(dashboard.json()["documents"])
        self.assertEqual(dashboard.json()["profile"]["contact_information"]["email"], "worker@example.com")
        self.assertEqual(dashboard.json()["professional_dna"]["version"], "professional_dna_v1_rule_based")

    def test_cv_parse_reject_endpoint_records_decision(self) -> None:
        registered = self.client.post("/api/auth/register", json={"preferred_language": "uk"})
        headers = {"X-ATLAS-User-Id": registered.json()["user_id"]}
        cv = self.client.post(
            "/api/files/upload",
            headers=headers,
            data={"kind": "cv"},
            files={"file": ("cv.pdf", b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF", "application/pdf")},
        )
        cv_file = cv.json()["file"]
        self.client.patch("/api/onboarding", headers=headers, json={"step": "cv", "data": {"file": cv_file}})
        parsed = self.client.post(f"/api/cv/{cv_file['id']}/parse", headers=headers).json()

        rejected = self.client.post(
            "/api/cv/parse-jobs/accept",
            headers=headers,
            json={"action": "reject", "job_id": parsed["id"], "accepted": {}},
        )

        self.assertEqual(rejected.status_code, 200)
        self.assertTrue(rejected.json()["data"]["cv"]["parse_rejected"])
        job = self.client.get(f"/api/cv/parse-jobs/{parsed['id']}", headers=headers)
        self.assertEqual(job.json()["status"], "rejected")

    def test_cv_parse_job_is_owner_scoped(self) -> None:
        registered = self.client.post("/api/auth/register", json={"preferred_language": "uk"})
        owner_headers = {"X-ATLAS-User-Id": registered.json()["user_id"]}
        other_headers = {"X-ATLAS-User-Id": "other-user"}
        cv = self.client.post(
            "/api/files/upload",
            headers=owner_headers,
            data={"kind": "cv"},
            files={"file": ("cv.rtf", b"{\\rtf1 Owner owner@example.com}", "application/rtf")},
        )
        cv_file = cv.json()["file"]
        self.client.patch("/api/onboarding", headers=owner_headers, json={"step": "cv", "data": {"file": cv_file}})
        parsed = self.client.post(f"/api/cv/{cv_file['id']}/parse", headers=owner_headers).json()

        foreign = self.client.get(f"/api/cv/parse-jobs/{parsed['id']}", headers=other_headers)

        self.assertEqual(foreign.status_code, 404)

    def test_universal_file_api_delete_and_signed_download(self) -> None:
        registered = self.client.post("/api/auth/register", json={"preferred_language": "uk"})
        user_id = registered.json()["user_id"]
        headers = {"X-ATLAS-User-Id": user_id}
        uploaded = self.client.post(
            "/api/files/upload",
            headers=headers,
            data={"kind": "document"},
            files={"file": ("worker.pdf", b"%PDF-1.7\n%%EOF", "application/pdf")},
        )
        self.assertEqual(uploaded.status_code, 200)
        file_data = uploaded.json()["file"]

        downloaded = self.client.get(file_data["download_url"])
        self.assertEqual(downloaded.status_code, 200)
        deleted = self.client.delete(f"/api/files/{file_data['id']}?kind=document", headers=headers)
        self.assertEqual(deleted.status_code, 200)

    def test_profile_section_api_validation_and_completeness(self) -> None:
        registered = self.client.post("/api/auth/register", json={"preferred_language": "uk"})
        headers = {"X-ATLAS-User-Id": registered.json()["user_id"]}

        invalid = self.client.patch("/api/profile/personal-data", headers=headers, json={"data": {"firstName": "123", "email": "bad"}})
        self.assertEqual(invalid.status_code, 400)

        personal = self.client.patch(
            "/api/profile/personal-data",
            headers=headers,
            json={"data": {"firstName": "Olena", "lastName": "Worker", "email": "olena@example.com", "phone": "48123456789"}},
        )
        self.assertEqual(personal.status_code, 200)
        self.assertEqual(personal.json()["profile"]["contact_information"]["phone"], "+48123456789")

        profession = self.client.patch(
            "/api/profile/profession",
            headers=headers,
            json={"data": {"profession": "HR coordinator", "skills": ["Python", "Python", "Recruiting"], "qualificationLevel": "senior"}},
        )
        self.assertEqual(profession.status_code, 200)
        self.assertEqual(profession.json()["data"]["normalizedProfession"], "hr_coordinator")
        self.assertEqual(profession.json()["profile"]["skills"], ["Python", "Recruiting"])

        created = self.client.post(
            "/api/profile/experience",
            headers=headers,
            json={"data": {"position": "Coordinator", "companyName": "EWU", "startDate": "2022-01-01", "endDate": "2023-01-01"}},
        )
        self.assertEqual(created.status_code, 200)
        record_id = created.json()["id"]
        updated = self.client.patch(f"/api/profile/experience/{record_id}", headers=headers, json={"data": {"city": "Warsaw"}})
        self.assertEqual(updated.json()["city"], "Warsaw")
        listed = self.client.get("/api/profile/experience", headers=headers)
        self.assertEqual(len(listed.json()["items"]), 1)
        deleted = self.client.delete(f"/api/profile/experience/{record_id}", headers=headers)
        self.assertTrue(deleted.json()["success"])

        credential = self.client.post(
            "/api/profile/credentials",
            headers=headers,
            json={"data": {"type": "certificate", "name": "Forklift", "expiresAt": "2000-01-01"}},
        )
        self.assertEqual(credential.json()["status"], "expired")

        profile = self.client.get("/api/profile", headers=headers)
        self.assertIn("completeness", profile.json())
        self.assertIn("missing_sections", profile.json()["completeness"])

    def test_consent_api_and_professional_dna_explanation(self) -> None:
        registered = self.client.post("/api/auth/register", json={"preferred_language": "uk"})
        headers = {"X-ATLAS-User-Id": registered.json()["user_id"]}

        center = self.client.get("/api/consents", headers=headers)
        self.assertEqual(center.status_code, 200)
        self.assertEqual(center.json()["policyVersion"], "atlas-rodo-v2")
        self.assertFalse(center.json()["canContinue"])
        self.assertEqual(len(center.json()["required"]), 5)

        missing = self.client.post("/api/consents", headers=headers, json={"consents": {"terms": True}})
        self.assertEqual(missing.status_code, 400)

        saved = self.client.post(
            "/api/consents",
            headers=headers,
            json={
                "consents": {
                    "terms": True,
                    "privacy": True,
                    "platformProcessing": True,
                    "profileStorage": True,
                    "documentProcessing": True,
                    "aiCvAnalysis": False,
                    "aiMatching": True,
                    "marketing": False,
                },
                "language": "uk",
                "source": "dashboard",
            },
        )
        self.assertEqual(saved.status_code, 200)
        optional = {item["type"]: item for item in saved.json()["center"]["optional"]}
        self.assertFalse(optional["aiCvAnalysis"]["selected"])
        self.assertTrue(optional["aiMatching"]["selected"])

        withdrawn = self.client.post("/api/consents/aiMatching/withdraw", headers=headers, json={"reason": "pause matching"})
        self.assertEqual(withdrawn.status_code, 200)
        self.assertIn("matching", withdrawn.json()["consequence"].lower())
        history = self.client.get("/api/consents/history", headers=headers)
        self.assertGreaterEqual(len(history.json()["history"]), 12)

        dna = self.client.post("/api/professional-dna/generate", headers=headers)
        self.assertEqual(dna.status_code, 200)
        explanation = self.client.get("/api/professional-dna/explanation", headers=headers)
        self.assertEqual(explanation.status_code, 200)
        self.assertIn("formula", explanation.json())
        self.assertEqual(sum(explanation.json()["formula"]["weights"].values()), 100)

    def test_privacy_request_api_creates_rodo_foundation_record(self) -> None:
        registered = self.client.post("/api/auth/register", json={"preferred_language": "uk"})
        headers = {"X-ATLAS-User-Id": registered.json()["user_id"]}

        created = self.client.post(
            "/api/privacy/requests",
            headers=headers,
            json={"request_type": "data_export", "contact": "worker@example.com", "note": "Need a copy"},
        )

        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.json()["request"]["request_type"], "export")
        self.assertEqual(created.json()["request"]["status"], "requested")


if __name__ == "__main__":
    unittest.main()
