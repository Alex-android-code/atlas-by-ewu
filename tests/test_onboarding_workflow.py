import tempfile
import unittest
import zipfile
import json
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
from services.onboarding_workflow import DNA_SCORING_CONFIG, OnboardingWorkflowService


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

        self.assertEqual(job["status"], "awaiting_review")
        self.assertIsNone(job["result"]["fullName"]["value"])
        self.assertEqual(job["result"]["confidence"], 0)
        self.assertIn("only facts", job["result"]["warnings"][0])
        self.assertIn("parser", job["result"])
        self.assertIn("fullName", job["result"]["notFoundFields"])

    def test_accepting_cv_syncs_only_confirmed_fields_to_profile(self) -> None:
        file_data = {"id": "ONB-CV", "original_name": "cv.pdf", "stored_name": "ONB-CV.pdf"}
        self.service.patch_step("user-1", step="cv", data={"file": file_data})
        job = self.service.parse_cv("user-1", "ONB-CV")

        saved = self.service.accept_cv_parse(
            "user-1",
            {
                "email": {"value": "worker@example.com", "source": "user_confirmed_cv_review", "confidence": "medium"},
                "skills": {"value": ["Python", "Logistics"], "source": "user_confirmed_cv_review", "confidence": "medium"},
                "summary": {"value": "", "source": "user_confirmed_cv_review", "confidence": "low"},
            },
            action="accept_selected",
            job_id=job["id"],
        )

        profile = self.service.agent_profiles.get_or_create_profile("user-1")
        reloaded_job = self.service.get_parse_job("user-1", job["id"])
        self.assertEqual(saved["data"]["personal_data"]["email"], "worker@example.com")
        self.assertEqual(profile.contact_information["email"], "worker@example.com")
        self.assertEqual(profile.skills, ["Python", "Logistics"])
        self.assertNotIn("summary", saved["data"]["cv"]["accepted_parsed_data"])
        self.assertEqual(reloaded_job["status"], "confirmed")

    def test_rejecting_cv_parse_persists_decision_without_profile_sync(self) -> None:
        file_data = {"id": "ONB-CV", "original_name": "cv.pdf", "stored_name": "ONB-CV.pdf"}
        self.service.patch_step("user-1", step="cv", data={"file": file_data})
        job = self.service.parse_cv("user-1", "ONB-CV")

        saved = self.service.accept_cv_parse("user-1", {}, action="reject", job_id=job["id"])

        profile = self.service.agent_profiles.get_or_create_profile("user-1")
        reloaded_job = self.service.get_parse_job("user-1", job["id"])
        self.assertTrue(saved["data"]["cv"]["parse_rejected"])
        self.assertEqual(saved["data"]["cv"]["accepted_parsed_data"], {})
        self.assertEqual(profile.contact_information.get("email"), None)
        self.assertEqual(reloaded_job["status"], "rejected")

    def test_docx_cv_extraction_populates_review_fields(self) -> None:
        cv_path = Path(self.tmpdir.name) / "cv.docx"
        with zipfile.ZipFile(cv_path, "w") as archive:
            archive.writestr(
                "word/document.xml",
                "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"><w:body><w:p>Olena Worker</w:p><w:p>Email: olena@example.com</w:p><w:p>Skills: Python, Logistics</w:p></w:body></w:document>",
            )
        file_data = {"id": "ONB-DOCX", "original_name": "cv.docx", "stored_name": "ONB-DOCX.docx"}
        self.service.patch_step("user-1", step="cv", data={"file": file_data})

        job = self.service.parse_cv("user-1", "ONB-DOCX", cv_path)

        self.assertEqual(job["status"], "awaiting_review")
        self.assertEqual(job["result"]["email"]["value"], "olena@example.com")
        self.assertEqual(job["result"]["skills"][0]["value"], "Python")

    def test_scanned_pdf_falls_back_to_ocr_without_inventing_data(self) -> None:
        cv_path = Path(self.tmpdir.name) / "scan.pdf"
        cv_path.write_bytes(b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF")
        file_data = {"id": "ONB-SCAN", "original_name": "scan.pdf", "stored_name": "ONB-SCAN.pdf"}
        self.service.patch_step("user-1", step="cv", data={"file": file_data})

        job = self.service.parse_cv("user-1", "ONB-SCAN", cv_path)

        self.assertEqual(job["status"], "awaiting_review")
        self.assertIn("native_pdf_text_empty", job["extraction_errors"])
        self.assertIsNone(job["result"]["email"]["value"])

    def test_corrupted_document_can_be_retried(self) -> None:
        cv_path = Path(self.tmpdir.name) / "broken.docx"
        cv_path.write_bytes(b"PK\x03\x04broken")
        file_data = {"id": "ONB-BROKEN", "original_name": "broken.docx", "stored_name": "ONB-BROKEN.docx"}
        self.service.patch_step("user-1", step="cv", data={"file": file_data})

        job = self.service.parse_cv("user-1", "ONB-BROKEN", cv_path)
        retried = self.service.retry_cv_parse("user-1", job["id"])

        self.assertEqual(job["status"], "failed_extraction")
        self.assertEqual(retried["status"], "queued")

    def test_required_consents_are_enforced(self) -> None:
        with self.assertRaises(ValueError):
            self.service.patch_step("user-1", step="consents", data={"terms": True})

        saved = self.service.patch_step(
            "user-1",
            step="consents",
            data={"terms": True, "privacy": True, "aiProcessing": True, "marketing": False},
        )
        self.assertIn("privacy", saved["consents"])

    def test_consent_center_tracks_optional_decline_and_withdrawal_history(self) -> None:
        choices = {
            "terms": True,
            "privacy": True,
            "platformProcessing": True,
            "profileStorage": True,
            "documentProcessing": True,
            "aiCvAnalysis": False,
            "aiMatching": True,
            "marketing": False,
        }

        saved = self.service.save_consent_choices("user-1", choices, source="dashboard")
        withdrawn = self.service.withdraw_consent("user-1", "aiMatching", reason="manual opt-out")
        center = self.service.consent_center("user-1")
        history = self.service.consent_history("user-1")

        optional = {item["type"]: item for item in center["optional"]}
        self.assertTrue(saved["center"]["canContinue"])
        self.assertFalse(optional["aiCvAnalysis"]["selected"])
        self.assertEqual(optional["aiMatching"]["status"], "withdrawn")
        self.assertIn("matching", withdrawn["consequence"].lower())
        self.assertGreaterEqual(len(history), 12)
        self.assertEqual(history[-1]["metadata"]["reason"], "manual opt-out")

    def test_cv_parse_policy_guard_blocks_external_ai_without_consent(self) -> None:
        file_data = {"id": "ONB-CV", "original_name": "cv.pdf", "stored_name": "ONB-CV.pdf"}
        self.service.patch_step("user-1", step="cv", data={"file": file_data})

        job = self.service.parse_cv("user-1", "ONB-CV")

        self.assertFalse(job["policy_guard"]["aiCvAnalysis"])
        self.assertFalse(job["policy_guard"]["externalAiUsed"])

    def test_profile_forms_sync_structured_records_without_duplicates(self) -> None:
        experience = {"records": [{"title": "Coordinator", "organization": "EWU", "period": "2022-2024", "note": "Logistics"}]}
        education = {"records": [{"title": "Logistics course", "organization": "ATLAS Academy", "period": "2023"}]}
        languages = {"records": [{"title": "English", "organization": "B2", "period": "Work", "note": ""}]}

        self.service.patch_step("user-1", step="experience", data=experience)
        self.service.patch_step("user-1", step="experience", data=experience)
        self.service.patch_step("user-1", step="education", data=education)
        self.service.patch_step("user-1", step="languages", data=languages)
        self.service.patch_step("user-1", step="preferences", data={"careerGoal": "Logistics lead", "countries": ["PL"], "format": "hybrid", "salary": "5000 PLN"})

        profile = self.service.agent_profiles.get_or_create_profile("user-1")
        self.assertEqual(len(profile.work_experience), 1)
        self.assertEqual(profile.work_experience[0]["title"], "Coordinator")
        self.assertEqual(profile.education[0]["title"], "Logistics course")
        self.assertEqual(profile.languages[0]["title"], "English")
        self.assertEqual(profile.relocation_preferences["preferred_work"], "hybrid")

    def test_generates_dna_and_completes(self) -> None:
        self.service.patch_step("user-1", step="agent", data={"name": "Ava"})
        self.service.patch_step("user-1", step="profile_photo", data={"file": {"id": "PHOTO", "original_name": "avatar.png"}})
        self.service.patch_step("user-1", step="cv", data={"file": {"id": "CV", "original_name": "cv.pdf"}})
        job = self.service.parse_cv("user-1", "CV")
        self.service.patch_step("user-1", step="cv_review", data={"job_id": job["id"], "accepted_parsed_data": {"email": {"value": "worker@example.com"}}})
        self.service.patch_step("user-1", step="personal_data", data={"fullName": "Ava Worker", "email": "worker@example.com"})
        self.service.patch_step("user-1", step="profession", data={"profession": "Logistics coordinator", "skills": ["Python"]})
        self.service.patch_step("user-1", step="preferences", data={"countries": ["PL"], "minimumSalary": "5000"})
        self.service.patch_step(
            "user-1",
            step="consents",
            data={"terms": True, "privacy": True, "platformProcessing": True, "profileStorage": True, "documentProcessing": True},
        )

        dna = self.service.generate_dna("user-1")
        completed = self.service.complete("user-1")
        retried = self.service.complete("user-1")
        dashboard = self.service.dashboard("user-1")

        self.assertEqual(dna["version"], "professional_dna_v1_rule_based")
        self.assertIn("formula", dna)
        self.assertEqual(completed["session"]["status"], "completed")
        self.assertEqual(completed["session"]["current_step"], "completed")
        self.assertEqual(retried["session"]["status"], "completed")
        self.assertEqual(dashboard["onboarding"]["redirectTo"], None)
        self.assertIn("readiness", dashboard)
        self.assertIn("recommendedActions", dashboard)
        self.assertNotIn("raw_text", json.dumps(dashboard).lower())

    def test_completion_requires_mandatory_steps_and_consents(self) -> None:
        self.service.patch_step("user-1", step="agent", data={"name": "Ava"})

        with self.assertRaises(ValueError) as error:
            self.service.complete("user-1")

        self.assertIn("Incomplete onboarding steps", str(error.exception))
        self.assertIn("Required consents", str(error.exception))

    def test_dashboard_redirects_unfinished_onboarding(self) -> None:
        self.service.patch_step("user-1", step="agent", data={"name": "Ava"})

        dashboard = self.service.dashboard("user-1")

        self.assertEqual(dashboard["onboarding"]["status"], "in_progress")
        self.assertIn("/agent/onboarding?step=", dashboard["onboarding"]["redirectTo"])

    def test_professional_dna_uses_configured_weights_and_structured_explanation(self) -> None:
        config = json.loads(DNA_SCORING_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(sum(config["weights"].values()), 100)
        self.service.patch_step("user-1", step="profession", data={"profession": "Logistics coordinator", "skills": ["CRM", "Logistics"]})
        self.service.patch_step("user-1", step="experience", data={"records": [{"title": "Coordinator", "note": "Operations"}]})
        self.service.patch_step("user-1", step="languages", data={"records": [{"title": "Polish", "organization": "B2"}]})

        dna = self.service.generate_dna("user-1")
        explanation = self.service.dna_explanation("user-1")

        self.assertGreaterEqual(dna["overallScore"], 0)
        self.assertLessEqual(dna["overallScore"], 100)
        self.assertEqual(dna["scoringConfigVersion"], config["version"])
        self.assertEqual(set(dna["components"]), set(config["weights"]))
        self.assertTrue(dna["strengths"])
        self.assertIn("formula", explanation)
        self.assertIn("recommendations", explanation)


if __name__ == "__main__":
    unittest.main()
