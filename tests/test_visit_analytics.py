import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app as app_module
from database.json_database import JsonDatabase
from services.analytics import WebsiteAnalyticsService


class WebsiteAnalyticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.analytics = WebsiteAnalyticsService(self.database)
        self.service_patch = patch.object(app_module, "get_website_analytics_service", return_value=self.analytics)
        self.db_patch = patch.object(app_module, "get_database", return_value=self.database)
        self.env_patch = patch.dict("os.environ", {"ATLAS_ADMIN_TOKEN": "test-admin-token"})
        self.service_patch.start()
        self.db_patch.start()
        self.env_patch.start()
        self.client = TestClient(app_module.app)

    def tearDown(self) -> None:
        self.service_patch.stop()
        self.db_patch.stop()
        self.env_patch.stop()
        self.tmpdir.cleanup()

    def admin_headers(self) -> dict[str, str]:
        return {"x-atlas-admin-token": "test-admin-token"}

    def test_unique_visitor_is_not_counted_twice_inside_one_session(self) -> None:
        first = self.client.get("/", headers={"user-agent": "Mozilla/5.0 Chrome/120"})
        second = self.client.get("/employee", headers={"user-agent": "Mozilla/5.0 Chrome/120"})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        summary = self.client.get("/api/admin/analytics/visits", headers=self.admin_headers()).json()

        self.assertEqual(summary["unique_visitors"]["today"], 1)
        self.assertEqual(summary["page_views"], 2)

    def test_known_bots_are_excluded_from_regular_statistics(self) -> None:
        self.client.get("/", headers={"user-agent": "Googlebot/2.1"})

        summary = self.client.get("/api/admin/analytics/visits", headers=self.admin_headers()).json()

        self.assertEqual(summary["unique_visitors"]["today"], 0)
        self.assertEqual(summary["page_views"], 0)

    def test_users_without_admin_rights_cannot_see_visit_analytics(self) -> None:
        response = self.client.get("/api/admin/analytics/visits")

        self.assertEqual(response.status_code, 403)

    def test_utm_parameters_are_stored_and_aggregated(self) -> None:
        self.client.get("/?utm_source=telegram&utm_medium=social&utm_campaign=launch")

        summary = self.client.get("/api/admin/analytics/visits", headers=self.admin_headers()).json()
        page_views = self.database.list("analytics_page_views")

        self.assertEqual(page_views[0]["utm_source"], "telegram")
        self.assertIn({"source": "telegram", "count": 1}, summary["traffic_sources"])

    def test_public_counter_can_be_disabled(self) -> None:
        self.client.get("/")
        enable = self.client.patch(
            "/api/admin/analytics/public-counters",
            json={"counters": {"total_visitors": True}},
            headers=self.admin_headers(),
        )
        enabled = self.client.get("/api/public/counters").json()
        disable = self.client.patch(
            "/api/admin/analytics/public-counters",
            json={"counters": {"total_visitors": False}},
            headers=self.admin_headers(),
        )
        disabled = self.client.get("/api/public/counters").json()

        self.assertEqual(enable.status_code, 200)
        self.assertEqual(disable.status_code, 200)
        self.assertEqual(enabled["counters"][0]["key"], "total_visitors")
        self.assertEqual(disabled["counters"], [])

    def test_personal_data_is_not_exposed_in_aggregate_statistics(self) -> None:
        self.client.post("/api/auth/register", json={"email": "private@example.com", "phone": "+48123123123"})

        summary = self.client.get("/api/admin/analytics/visits", headers=self.admin_headers()).json()
        serialized = str(summary)

        self.assertNotIn("private@example.com", serialized)
        self.assertNotIn("+48123123123", serialized)
        self.assertFalse(summary["privacy"]["personal_data_in_summary"])

    def test_analytics_failure_does_not_break_page_load(self) -> None:
        class BrokenAnalytics:
            def track_page_view(self, request, response):
                raise RuntimeError("analytics down")

        with patch.object(app_module, "get_website_analytics_service", return_value=BrokenAnalytics()):
            response = self.client.get("/")

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
