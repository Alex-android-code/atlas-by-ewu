import tempfile
import unittest
from pathlib import Path

from database.json_database import JsonDatabase
from database.repositories import (
    CustomerSubscriptionRepository,
    PlanFeatureRepository,
    SubscriptionFeatureRepository,
    SubscriptionPlanRepository,
)
from services.entitlements import EntitlementRepositories, EntitlementService


class EntitlementServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.service = EntitlementService(
            EntitlementRepositories(
                plans=SubscriptionPlanRepository(database),
                features=SubscriptionFeatureRepository(database),
                plan_features=PlanFeatureRepository(database),
                customer_subscriptions=CustomerSubscriptionRepository(database),
            )
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_catalog_has_four_required_plans(self):
        catalog = self.service.catalog()
        plan_codes = [plan["code"] for plan in catalog["plans"]]

        self.assertEqual(plan_codes, ["start", "medium", "pro", "enterprise"])

    def test_enterprise_has_enterprise_integrations(self):
        self.assertTrue(self.service.plan_has_feature("enterprise", "enterprise_integrations"))
        self.assertTrue(self.service.plan_has_feature("enterprise", "corporate_ai_agent"))
        self.assertFalse(self.service.plan_has_feature("start", "corporate_ai_agent"))

    def test_sync_catalog_creates_records(self):
        result = self.service.sync_catalog()

        self.assertEqual(result["plans"], 4)
        self.assertGreater(result["features"], 0)
        self.assertGreater(result["plan_features"], result["features"])

    def test_customer_subscription_controls_entitlement(self):
        self.assertFalse(self.service.has_entitlement("emp-1", "corporate_ai_agent", customer_type="employer"))

        self.service.set_customer_subscription("emp-1", "employer", "enterprise")

        self.assertTrue(self.service.has_entitlement("emp-1", "corporate_ai_agent", customer_type="employer"))

    def test_unknown_plan_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.set_customer_subscription("user-1", "user", "unknown")


if __name__ == "__main__":
    unittest.main()
