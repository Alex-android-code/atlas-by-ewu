import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app as app_module
import api.dependencies as dependencies
from core.models import Candidate, ProfessionalDNA, Vacancy
from database.json_database import JsonDatabase
from database.repositories import ActivityRepository, CandidateRepository, MatchRepository, ProfessionalDNARepository, VacancyRepository
from services.matching_engine import MatchingEngineService


def vacancy(company_id: str = "CMP-MATCH", **overrides) -> Vacancy:
    data = {
        "companyId": company_id,
        "status": "published",
        "title": "Welder",
        "normalizedProfessionKey": "welder",
        "professionLabel": "Welder",
        "description": "Welding steel structures.",
        "requirements": [
            {"category": "skill", "label": "MIG/MAG", "normalizedKey": "mig_mag", "required": True},
            {"category": "experience", "label": "3 years", "minimumYears": 3, "required": True},
            {"category": "certificate", "label": "welder certificate", "normalizedKey": "welder_certificate", "required": True},
        ],
        "languageRequirements": [{"language": "pl", "level": "b1"}],
        "workAuthorizationRequirements": ["pl_work_permit"],
        "locationCountries": ["pl"],
        "workModes": ["onsite"],
        "quantity": 2,
        "salary": {"visible": True, "minimum": 25, "maximum": 35, "currency": "PLN", "period": "hour", "grossNet": "net", "negotiable": False},
        "employmentTypes": ["contract"],
        "updatedAt": "2026-07-21T00:00:00+00:00",
    }
    data.update(overrides)
    return Vacancy(
        employer_id=company_id,
        title=data["title"],
        country_code="PL",
        profession_code="welder",
        salary_min=25,
        salary_max=35,
        currency="PLN",
        required_languages=["pl"],
        status="published",
        metadata={"recruitment": data},
    )


def candidate(user_id: str = "candidate-user", country_code: str = "PL", **metadata) -> Candidate:
    base = {
        "skills": ["mig_mag"],
        "work_authorization": ["pl_work_permit"],
        "desired_country_code": "PL",
        "desired_salary": 30,
        "salary_currency": "PLN",
        "contract_types": ["contract"],
        "schedule": ["day_shift"],
    }
    base.update(metadata)
    return Candidate(
        first_name="Ivan",
        last_name="Worker",
        email=f"{user_id}@example.com",
        phone="+4800",
        country_code=country_code,
        profession_code="welder",
        languages=["pl"],
        years_of_experience=8,
        user_id=user_id,
        documents=["welder_certificate"],
        metadata=base,
    )


class MatchingEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.candidates = CandidateRepository(self.database)
        self.vacancies = VacancyRepository(self.database)
        self.profiles = ProfessionalDNARepository(self.database)
        self.matches = MatchRepository(self.database)
        self.service = MatchingEngineService(
            candidates=self.candidates,
            vacancies=self.vacancies,
            profiles=self.profiles,
            matches=self.matches,
            activity=ActivityRepository(self.database),
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_strong_match_is_explainable_and_human_review_only(self) -> None:
        saved_candidate = self.candidates.add(candidate())
        saved_vacancy = self.vacancies.add(vacancy())
        self.profiles.add(ProfessionalDNA(user_id=saved_candidate.user_id, skills=["mig_mag"], certificates=[{"name": "welder_certificate"}], profile_completeness=90))

        result = self.service.run(candidate_id=saved_candidate.id, vacancy_id=saved_vacancy.id)
        match = result["matches"][0]

        self.assertGreaterEqual(match["score"], 85)
        self.assertIn(match["recommendation"]["code"], {"strong_match", "recommended"})
        self.assertTrue(match["explanation"]["humanDecisionRequired"])
        self.assertFalse(match["humanReview"]["aiFinalDecision"])
        self.assertIn("skills", match["explanation"]["componentScores"])
        self.assertTrue(match["explanation"]["positiveReasons"])

    def test_missing_skills_salary_country_and_language_lower_scores(self) -> None:
        saved_candidate = self.candidates.add(candidate(country_code="DE", skills=[], desired_salary=50, desired_country_code="DE", work_authorization=[]))
        saved_vacancy = self.vacancies.add(vacancy(languageRequirements=[{"language": "de", "level": "b2"}], locationCountries=["pl"]))

        match = self.service.run(candidate_id=saved_candidate.id, vacancy_id=saved_vacancy.id)["matches"][0]

        self.assertLess(match["componentScores"]["skills"]["score"], 50)
        self.assertLess(match["componentScores"]["salary"]["score"], 100)
        self.assertLess(match["componentScores"]["location"]["score"], 80)
        self.assertLess(match["componentScores"]["languages"]["score"], 100)
        self.assertTrue(match["explanation"]["risks"])
        self.assertTrue(match["candidateView"]["whatToImprove"])

    def test_protected_fields_are_ignored_and_recalculate_is_idempotent(self) -> None:
        saved_candidate = self.candidates.add(candidate(age=22, gender="female", nationality="UA", photo="face.png"))
        saved_vacancy = self.vacancies.add(vacancy())

        match = self.service.run(candidate_id=saved_candidate.id, vacancy_id=saved_vacancy.id)["matches"][0]
        recalculated = self.service.recalculate(match["id"])

        self.assertEqual(match["id"], recalculated["id"])
        self.assertEqual(recalculated["biasProtection"]["protectedFieldsUsed"], [])
        self.assertIn("age", recalculated["biasProtection"]["protectedFieldsIgnored"])
        self.assertIn("gender", recalculated["biasProtection"]["protectedFieldsIgnored"])

    def test_performance_smoke_for_larger_batch(self) -> None:
        for index in range(8):
            self.candidates.add(candidate(user_id=f"candidate-{index}", desired_salary=25 + index % 10))
        for index in range(5):
            self.vacancies.add(vacancy(title=f"Welder {index}"))

        started = time.perf_counter()
        result = self.service.run(limit=1000)
        elapsed = time.perf_counter() - started

        self.assertEqual(result["count"], 40)
        self.assertLess(elapsed, 5)
        self.assertGreater(result["analytics"]["averageMatch"], 0)
        self.assertIn("cacheKeyStrategy", result["scaling"])


class MatchingApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.candidates = CandidateRepository(self.database)
        self.vacancies = VacancyRepository(self.database)
        self.saved_candidate = self.candidates.add(candidate())
        self.saved_vacancy = self.vacancies.add(vacancy())
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

    def test_matching_api_run_get_explanation_recalculate_and_pages(self) -> None:
        headers = {"X-ATLAS-User-Id": "admin"}
        run = self.client.post("/api/matching/run", headers=headers, json={"candidate_id": self.saved_candidate.id, "vacancy_id": self.saved_vacancy.id})
        match = run.json()["matches"][0]
        get_match = self.client.get(f"/api/matching/{match['id']}")
        explanation = self.client.get(f"/api/matching/{match['id']}/explanation")
        recalculated = self.client.post(f"/api/matching/{match['id']}/recalculate", headers=headers)
        employer_page = self.client.get(f"/employer/matching/{match['id']}")
        candidate_page = self.client.get(f"/agent/matching/{match['id']}")

        self.assertEqual(run.status_code, 200)
        self.assertEqual(get_match.json()["id"], match["id"])
        self.assertIn("componentScores", explanation.json())
        self.assertEqual(recalculated.json()["id"], match["id"])
        self.assertIn("Human decision required", employer_page.text)
        self.assertIn("AI recommends, human decides", candidate_page.text)


if __name__ == "__main__":
    unittest.main()
