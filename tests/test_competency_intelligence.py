import tempfile
import unittest
from pathlib import Path

from database.json_database import JsonDatabase
from database.repositories import (
    CompetencyRepository,
    DevelopmentPlanRepository,
    DevelopmentPlanStepRepository,
    EmployerCompetencyRequirementRepository,
    SkillGapRepository,
    UserCompetencyRepository,
)
from services.competency_intelligence import CompetencyIntelligenceRepositories, CompetencyIntelligenceService


class CompetencyIntelligenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.service = CompetencyIntelligenceService(
            CompetencyIntelligenceRepositories(
                competencies=CompetencyRepository(database),
                user_competencies=UserCompetencyRepository(database),
                employer_requirements=EmployerCompetencyRequirementRepository(database),
                skill_gaps=SkillGapRepository(database),
                development_plans=DevelopmentPlanRepository(database),
                development_plan_steps=DevelopmentPlanStepRepository(database),
            )
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_competency_names_are_normalized_and_deduplicated(self):
        first = self.service.get_or_create_competency("  TIG Welding  ")
        second = self.service.get_or_create_competency("tig welding")

        self.assertEqual(first.id, second.id)
        self.assertEqual(first.name, "tig welding")

    def test_ai_inferred_competency_is_not_verified_fact(self):
        user_competency = self.service.add_user_competency(
            user_id="user-1",
            competency_name="route planning",
            current_level=3,
            source="ai_inferred",
        )

        self.assertEqual(user_competency.verification_status, "unverified")
        self.assertIsNone(user_competency.last_verified_at)
        self.assertLess(user_competency.confidence_score, 0.5)

    def test_verified_source_marks_competency_verified(self):
        user_competency = self.service.add_user_competency(
            user_id="user-1",
            competency_name="forklift operation",
            current_level=4,
            source="certification_verified",
        )

        self.assertEqual(user_competency.verification_status, "verified")
        self.assertIsNotNone(user_competency.last_verified_at)

    def test_skill_gap_analysis_uses_employer_requirements_without_profession_templates(self):
        self.service.add_user_competency("user-1", "technical drawing", current_level=2)
        requirement = self.service.add_employer_requirement(
            employer_id="emp-1",
            vacancy_id="vac-1",
            competency_name="technical drawing",
            required_level=5,
            importance=5,
        )

        gaps = self.service.analyze_skill_gaps_for_user("user-1", [requirement])

        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0].gap_size, 3)
        self.assertEqual(gaps[0].priority, "high")

    def test_development_plan_orders_high_priority_gaps_first(self):
        low_requirement = self.service.add_employer_requirement("emp-1", "documentation", 2, importance=1)
        high_requirement = self.service.add_employer_requirement("emp-1", "safety leadership", 5, importance=5)
        gaps = self.service.analyze_skill_gaps_for_user("user-1", [low_requirement, high_requirement])

        result = self.service.create_development_plan_from_gaps("user-1", gaps)

        self.assertEqual(len(result["steps"]), 2)
        self.assertIn("safety leadership", result["steps"][0]["title"])


if __name__ == "__main__":
    unittest.main()
