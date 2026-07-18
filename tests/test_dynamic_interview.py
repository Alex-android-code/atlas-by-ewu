import tempfile
import unittest
from pathlib import Path

from database.json_database import JsonDatabase
from database.repositories import (
    CompetencyRepository,
    DevelopmentPlanRepository,
    DevelopmentPlanStepRepository,
    DynamicInterviewSessionRepository,
    EmployerCompetencyRequirementRepository,
    SkillGapRepository,
    UserCompetencyRepository,
)
from services.competency_intelligence import CompetencyIntelligenceRepositories, CompetencyIntelligenceService
from services.dynamic_interview import DynamicInterviewService


class DynamicInterviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        competency_service = CompetencyIntelligenceService(
            CompetencyIntelligenceRepositories(
                competencies=CompetencyRepository(database),
                user_competencies=UserCompetencyRepository(database),
                employer_requirements=EmployerCompetencyRequirementRepository(database),
                skill_gaps=SkillGapRepository(database),
                development_plans=DevelopmentPlanRepository(database),
                development_plan_steps=DevelopmentPlanStepRepository(database),
            )
        )
        self.sessions = DynamicInterviewSessionRepository(database)
        self.user_competencies = UserCompetencyRepository(database)
        self.service = DynamicInterviewService(self.sessions, competency_service=competency_service)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_start_creates_one_question_session(self):
        result = self.service.start_or_resume("user-1", language="en")

        self.assertTrue(result["one_question_per_step"])
        self.assertEqual(result["session"]["current_field"], "professional_goal")
        self.assertEqual(result["session"]["status"], "active")

    def test_answer_moves_to_next_question_and_preserves_session(self):
        started = self.service.start_or_resume("user-1", language="en")
        session_id = started["session"]["id"]

        answered = self.service.answer_step(session_id, "I want to become a logistics coordinator.")
        resumed = self.service.start_or_resume("user-1", language="en")

        self.assertEqual(answered["session"]["current_field"], "experience_summary")
        self.assertEqual(resumed["session"]["id"], session_id)
        self.assertEqual(resumed["session"]["profile_data"]["professional_goal"], "I want to become a logistics coordinator.")

    def test_empty_answer_repeats_current_question(self):
        started = self.service.start_or_resume("user-1", language="en")

        result = self.service.answer_step(started["session"]["id"], "   ")

        self.assertEqual(result["warnings"], ["empty_answer"])
        self.assertEqual(result["session"]["current_field"], "professional_goal")

    def test_contradiction_is_not_marked_complete(self):
        started = self.service.start_or_resume("user-1", language="en")
        session_id = started["session"]["id"]
        self.service.answer_step(session_id, "I want logistics.")
        session = self.sessions.get(session_id)
        session.current_field = "professional_goal"
        self.sessions.update(session)

        result = self.service.answer_step(session_id, "Actually I only want finance.")

        self.assertEqual(result["analysis"]["contradictions"][0]["field"], "professional_goal")
        self.assertIn("professional_goal", result["session"]["completed_fields"])
        self.assertEqual(result["session"]["current_field"], "professional_goal")

    def test_competency_answer_extracts_and_persists_self_declared_competencies(self):
        started = self.service.start_or_resume("user-1", language="en")
        session_id = started["session"]["id"]
        self.service.answer_step(session_id, "Logistics coordinator")
        self.service.answer_step(session_id, "Three years in warehouse operations")

        result = self.service.answer_step(session_id, "route planning, safety leadership and inventory control")

        self.assertEqual(result["session"]["current_field"], "competency_evidence")
        self.assertEqual(len(self.user_competencies.list()), 3)
        self.assertTrue(all(item.source == "self_declared" for item in self.user_competencies.list()))
        self.assertTrue(all(item.verification_status == "unverified" for item in self.user_competencies.list()))


if __name__ == "__main__":
    unittest.main()
