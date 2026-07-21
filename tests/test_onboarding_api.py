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
        self.assertEqual(parsed.json()["status"], "completed")

        self.client.post(
            "/api/cv/parse-jobs/accept",
            headers=headers,
            json={"accepted": {"email": {"value": "worker@example.com", "source": "user_confirmed_cv_review"}}},
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
        self.assertEqual(dashboard.json()["professional_dna"]["version"], "professional_dna_v1_rule_based")

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
        missing = self.client.get(file_data["download_url"])
        self.assertEqual(missing.status_code, 404)


if __name__ == "__main__":
    unittest.main()
