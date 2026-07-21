import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app as app_module
import api.dependencies as dependencies
from core.models import Candidate
from database.json_database import JsonDatabase
from database.repositories import ActivityRepository, CandidateRepository, VacancyRepository
from services.recruitment_workflow import RecruitmentWorkflowService


def seed_company(database: JsonDatabase, owner: str = "owner-user") -> str:
    company_id = "CMP-TEST"
    database.insert(
        "companies",
        company_id,
        {
            "id": company_id,
            "legal_name": "Atlas Jobs",
            "trading_name": "Atlas Jobs",
            "country_code": "PL",
            "verification_status": "unverified",
            "industry": "Recruitment",
        },
    )
    database.insert(
        "company_members",
        "MBR-OWNER",
        {"id": "MBR-OWNER", "companyId": company_id, "userId": owner, "role": "company_owner", "status": "active"},
    )
    for key in ["termsForBusiness", "dataProcessing", "representativeAuthority", "lawfulCandidateUse", "nonDiscrimination"]:
        database.insert(
            "employer_consents",
            f"ECON-{key}",
            {"id": f"ECON-{key}", "companyId": company_id, "key": key, "type": "required", "granted": True},
        )
    return company_id


def vacancy_payload(company_id: str) -> dict:
    return {
        "companyId": company_id,
        "title": "Welder",
        "professionLabel": "Welder",
        "description": "Work with steel structures in a verified production environment.",
        "responsibilities": ["Welding", "Reading technical drawings"],
        "requirements": [{"category": "skill", "label": "MIG/MAG welding", "required": True, "weight": 5}],
        "employmentTypes": ["contract"],
        "workModes": ["onsite"],
        "locationIds": ["LOC-WAW"],
        "quantity": 2,
        "salary": {"visible": True, "minimum": 24, "maximum": 36, "currency": "PLN", "period": "hour", "grossNet": "net", "negotiable": False},
        "housing": {"provided": True, "paidBy": "shared"},
        "transport": {"provided": True, "paidBy": "employer"},
        "legalization": {"provided": True},
        "screeningQuestions": [{"type": "yes_no", "label": "Do you have work authorization?", "required": True}],
    }


class RecruitmentWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.company_id = seed_company(self.database)
        self.candidates = CandidateRepository(self.database)
        self.candidates.add(Candidate(first_name="Ivan", last_name="Worker", email="ivan@example.com", phone="+4800", country_code="UA", profession_code="welder", languages=["uk", "pl"], user_id="candidate-user"))
        self.service = RecruitmentWorkflowService(
            database=self.database,
            vacancies=VacancyRepository(self.database),
            candidates=self.candidates,
            activity=ActivityRepository(self.database),
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_vacancy_publish_application_pipeline_interview_offer_hire(self) -> None:
        draft = self.service.create_vacancy("owner-user", vacancy_payload(self.company_id))
        self.assertEqual(draft["status"], "draft")
        self.assertTrue(draft["versionHistory"])

        published = self.service.publish_vacancy("owner-user", draft["id"])
        self.assertEqual(published["status"], "published")
        public = self.service.get_public_job(draft["id"])
        self.assertNotIn("pipelineId", public["job"])

        application = self.service.submit_application(
            "candidate-user",
            draft["id"],
            {"consentAccepted": True, "coverLetter": "Ready to work", "sharedData": {"name": "Ivan Worker", "skills": ["MIG/MAG"]}},
        )
        app_id = application["application"]["id"]
        self.assertEqual(application["application"]["status"], "submitted")
        self.assertEqual(application["snapshot"]["data"]["name"], "Ivan Worker")
        self.assertTrue(application["consent"]["accepted"])

        with self.assertRaises(ValueError):
            self.service.submit_application("candidate-user", draft["id"], {"consentAccepted": True})

        moved = self.service.transition_stage("owner-user", app_id, {"toStageId": "interview", "comment": "Invite"})
        self.assertEqual(moved["application"]["status"], "interview")
        interview = self.service.schedule_interview("owner-user", app_id, {"date": "2026-08-01", "time": "10:00", "timezone": "Europe/Warsaw", "participants": ["owner-user", "candidate-user"]})
        self.assertEqual(interview["status"], "scheduled")
        evaluation = self.service.submit_evaluation("owner-user", app_id, {"scores": {"welding": 5}, "recommendation": "yes", "comments": "Good fit"})
        self.assertEqual(evaluation["recommendation"], "yes")

        with self.assertRaises(ValueError):
            self.service.transition_stage("owner-user", app_id, {"toStageId": "hired"})

        self.service.transition_stage("owner-user", app_id, {"toStageId": "offer"})
        offer = self.service.create_offer("owner-user", app_id, {"employmentType": "contract"})
        sent = self.service.send_offer("owner-user", offer["id"])
        self.assertEqual(sent["status"], "sent")
        accepted = self.service.accept_offer("candidate-user", offer["id"])
        self.assertEqual(accepted["status"], "accepted")
        detail = self.service.application_detail("candidate-user", app_id, candidate=True)
        self.assertEqual(detail["application"]["status"], "hired")

    def test_compliance_salary_consent_and_tenant_guards(self) -> None:
        bad_salary = vacancy_payload(self.company_id)
        bad_salary["salary"] = {"visible": True, "minimum": 40, "maximum": 20, "currency": "PLN", "period": "hour", "grossNet": "net", "negotiable": False}
        with self.assertRaises(ValueError):
            self.service.create_vacancy("owner-user", bad_salary)

        discriminatory = vacancy_payload(self.company_id)
        discriminatory["description"] = "Welder under 30 only."
        draft = self.service.create_vacancy("owner-user", discriminatory)
        with self.assertRaises(ValueError):
            self.service.publish_vacancy("owner-user", draft["id"])

        with self.assertRaises(PermissionError):
            self.service.create_vacancy("intruder", vacancy_payload(self.company_id))

        no_consent_company = "CMP-NOCONSENT"
        self.database.insert("companies", no_consent_company, {"id": no_consent_company, "legal_name": "No Consent"})
        self.database.insert("company_members", "MBR-NOCONSENT", {"id": "MBR-NOCONSENT", "companyId": no_consent_company, "userId": "owner-user", "role": "company_owner", "status": "active"})
        draft_no_consent = self.service.create_vacancy("owner-user", vacancy_payload(no_consent_company))
        with self.assertRaises(ValueError):
            self.service.publish_vacancy("owner-user", draft_no_consent["id"])

    def test_rejection_requires_safe_reason_and_withdraw_closes_application(self) -> None:
        draft = self.service.create_vacancy("owner-user", vacancy_payload(self.company_id))
        self.service.publish_vacancy("owner-user", draft["id"])
        application = self.service.submit_application("candidate-user", draft["id"], {"consentAccepted": True, "sharedData": {"name": "Ivan"}})
        app_id = application["application"]["id"]

        with self.assertRaises(ValueError):
            self.service.transition_stage("owner-user", app_id, {"toStageId": "rejected"})
        rejected = self.service.transition_stage("owner-user", app_id, {"toStageId": "rejected", "reasonCode": "requirements_not_met"})
        self.assertEqual(rejected["application"]["status"], "rejected")

        second = self.service.submit_application("candidate-user", draft["id"], {"consentAccepted": True, "sharedData": {"name": "Ivan"}})
        withdrawn = self.service.withdraw_application("candidate-user", second["application"]["id"])
        self.assertEqual(withdrawn["application"]["status"], "withdrawn")


class RecruitmentApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.company_id = seed_company(self.database)
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

    def test_api_e2e_happy_path_and_public_job(self) -> None:
        owner_headers = {"X-ATLAS-User-Id": "owner-user"}
        candidate_headers = {"X-ATLAS-User-Id": "candidate-api"}
        created = self.client.post("/api/vacancies", headers=owner_headers, json={"data": vacancy_payload(self.company_id)})
        self.assertEqual(created.status_code, 200)
        vacancy_id = created.json()["id"]

        published = self.client.post(f"/api/vacancies/{vacancy_id}/publish", headers=owner_headers)
        public = self.client.get(f"/api/public/jobs/{vacancy_id}")
        job_page = self.client.get(f"/jobs/{vacancy_id}")
        application = self.client.post(
            f"/api/vacancies/{vacancy_id}/applications",
            headers=candidate_headers,
            json={"data": {"consentAccepted": True, "sharedData": {"name": "Candidate API"}, "answers": [{"questionId": "q1", "value": True}]}},
        )
        app_id = application.json()["application"]["id"]
        forbidden = self.client.get(f"/api/applications/{app_id}", headers={"X-ATLAS-User-Id": "other-company-user"})
        stage = self.client.patch(f"/api/applications/{app_id}/stage", headers=owner_headers, json={"data": {"toStageId": "interview"}})
        interview = self.client.post(f"/api/applications/{app_id}/interviews", headers=owner_headers, json={"data": {"date": "2026-08-01", "time": "12:00"}})
        evaluation = self.client.post(f"/api/applications/{app_id}/evaluations", headers=owner_headers, json={"data": {"scores": {"skill": 4}, "recommendation": "yes"}})
        self.client.patch(f"/api/applications/{app_id}/stage", headers=owner_headers, json={"data": {"toStageId": "offer"}})
        offer = self.client.post(f"/api/applications/{app_id}/offers", headers=owner_headers, json={"data": {"employmentType": "contract"}})
        sent = self.client.post(f"/api/offers/{offer.json()['id']}/send", headers=owner_headers)
        accepted = self.client.post(f"/api/offers/{offer.json()['id']}/accept", headers=candidate_headers)
        candidate_apps = self.client.get("/api/applications?view=candidate", headers=candidate_headers)

        self.assertEqual(published.json()["status"], "published")
        self.assertEqual(public.json()["job"]["title"], "Welder")
        self.assertIn("Welder", job_page.text)
        self.assertEqual(application.status_code, 200)
        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(stage.json()["application"]["status"], "interview")
        self.assertEqual(interview.json()["status"], "scheduled")
        self.assertEqual(evaluation.json()["recommendation"], "yes")
        self.assertEqual(sent.json()["status"], "sent")
        self.assertEqual(accepted.json()["status"], "accepted")
        self.assertEqual(candidate_apps.json()["items"][0]["displayStatus"], "decision")


if __name__ == "__main__":
    unittest.main()
