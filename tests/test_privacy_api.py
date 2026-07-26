import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app as app_module
import api.dependencies as dependencies
from database.json_database import JsonDatabase


class PrivacyApiTests(unittest.TestCase):
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

    def test_retention_and_consent_summary_endpoints(self) -> None:
        headers = {"X-ATLAS-User-Id": "privacy-user"}
        self.client.post(
            "/api/rodo/consents",
            headers=headers,
            json={
                "subject_id": "privacy-user",
                "language": "uk",
                "source": "web",
                "scopes": ["privacy_policy", "ai_profiling"],
                "accepted": True,
            },
        )

        retention = self.client.get("/api/privacy/retention")
        summary = self.client.get("/api/privacy/consent-summary", headers=headers)

        self.assertEqual(retention.status_code, 200)
        self.assertTrue(retention.json()["retention"])
        self.assertEqual(summary.json()["subject_id"], "privacy-user")
        self.assertTrue(next(item for item in summary.json()["consents"] if item["type"] == "privacy_policy")["granted"])


if __name__ == "__main__":
    unittest.main()
