import tempfile
import unittest
from pathlib import Path

from database.json_database import JsonDatabase
from database.repositories import (
    ActivityRepository,
    AgentActionRepository,
    AgentMemoryRepository,
    AgentRecommendationRepository,
    CareerGoalRepository,
    ConsentRepository,
    DocumentRepository,
    ProfessionalDNARepository,
    SubscriptionRepository,
    UserPreferenceRepository,
)
from services.agent_profile_service import AgentProfileService
from services.onboarding_workflow import OnboardingWorkflowService


class OnboardingWorkflowServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        agent_profiles = AgentProfileService(
            profiles=ProfessionalDNARepository(database),
            memories=AgentMemoryRepository(database),
            actions=AgentActionRepository(database),
            recommendations=AgentRecommendationRepository(database),
            goals=CareerGoalRepository(database),
            preferences=UserPreferenceRepository(database),
            subscriptions=SubscriptionRepository(database),
        )
        self.service = OnboardingWorkflowService(
            database=database,
            agent_profiles=agent_profiles,
            consents=ConsentRepository(database),
            documents=DocumentRepository(database),
            activity=ActivityRepository(database),
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_persists_step_progress(self) -> None:
        started = self.service.get_or_start("user-1")
        self.assertEqual(started["status"], "not_started")

        saved = self.service.patch_step("user-1", step="agent", data={"name": "Ava"})
        reloaded = self.service.get_or_start("user-1")

        self.assertEqual(saved["current_step"], "profile_photo")
        self.assertEqual(reloaded["data"]["agent"]["name"], "Ava")
        self.assertGreater(reloaded["progress"]["percent"], 0)

    def test_cv_parse_uses_only_confirmed_data(self) -> None:
        file_data = {"id": "ONB-CV", "original_name": "cv.pdf", "stored_name": "ONB-CV.pdf"}
        self.service.patch_step("user-1", step="cv", data={"file": file_data})

        job = self.service.parse_cv("user-1", "ONB-CV")

        self.assertEqual(job["status"], "completed")
        self.assertEqual(job["result"]["fullName"]["value"], "")
        self.assertEqual(job["result"]["confidence"], "low")
        self.assertIn("did not invent", job["result"]["warnings"][0])

    def test_required_consents_are_enforced(self) -> None:
        with self.assertRaises(ValueError):
            self.service.patch_step("user-1", step="consents", data={"terms": True})

        saved = self.service.patch_step(
            "user-1",
            step="consents",
            data={"terms": True, "privacy": True, "aiProcessing": True, "marketing": False},
        )
        self.assertIn("privacy", saved["consents"])

    def test_generates_dna_and_completes(self) -> None:
        self.service.patch_step("user-1", step="agent", data={"name": "Ava"})
        self.service.patch_step("user-1", step="profession", data={"skills": ["Python"]})

        dna = self.service.generate_dna("user-1")
        completed = self.service.complete("user-1")

        self.assertEqual(dna["version"], "professional_dna_v1_rule_based")
        self.assertEqual(completed["session"]["status"], "completed")
        self.assertEqual(completed["session"]["current_step"], "completed")


if __name__ == "__main__":
    unittest.main()
