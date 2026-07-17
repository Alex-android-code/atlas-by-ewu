import tempfile
import unittest
from pathlib import Path

from database.json_database import JsonDatabase
from database.repositories import (
    AgentActionRepository,
    AgentMemoryRepository,
    AgentRecommendationRepository,
    CareerGoalRepository,
    ProfessionalDNARepository,
    SubscriptionRepository,
    UserPreferenceRepository,
)
from services.agent_profile_service import AgentProfileService


class AgentProfileServiceTest(unittest.TestCase):
    def build_service(self) -> AgentProfileService:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        return AgentProfileService(
            profiles=ProfessionalDNARepository(database),
            memories=AgentMemoryRepository(database),
            actions=AgentActionRepository(database),
            recommendations=AgentRecommendationRepository(database),
            goals=CareerGoalRepository(database),
            preferences=UserPreferenceRepository(database),
            subscriptions=SubscriptionRepository(database),
        )

    def tearDown(self) -> None:
        if hasattr(self, "tmpdir"):
            self.tmpdir.cleanup()

    def test_onboarding_builds_professional_dna_and_memory(self) -> None:
        service = self.build_service()

        result = service.save_onboarding_answer(
            user_id="user-test",
            field="full_name",
            value="Oleksandr Atlas",
            language="uk",
        )

        self.assertEqual(result["progress"]["completed"], 1)
        self.assertEqual(result["profile"]["personal_information"]["full_name"], "Oleksandr Atlas")
        dashboard = service.agent_dashboard("user-test")
        self.assertEqual(dashboard["professional_dna"]["profile_completeness"], 7)
        self.assertEqual(dashboard["memories"][0]["memory_type"], "fact")

    def test_complete_onboarding_creates_subscription_and_recommendations(self) -> None:
        service = self.build_service()

        complete = service.complete_onboarding("user-test")

        self.assertIn("dashboard", complete)
        dashboard = complete["dashboard"]
        self.assertEqual(dashboard["subscription"]["plan"], "start")
        self.assertTrue(dashboard["feature_flags"]["agent_creation"])
        self.assertTrue(dashboard["recommendations"])


if __name__ == "__main__":
    unittest.main()
