import tempfile
import unittest
from pathlib import Path

from core.models import Candidate, Employer
from database.json_database import JsonDatabase
from database.repositories import (
    CandidateRepository,
    ConsentRepository,
    DataSubjectRequestRepository,
    EmployerRepository,
    UserRepository,
)
from services.rodo_service import DEFAULT_CONSENT_SCOPES, PRIVACY_NOTICE_VERSION, RodoService


class RodoServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.candidates = CandidateRepository(database)
        self.employers = EmployerRepository(database)
        self.service = RodoService(
            consents=ConsentRepository(database),
            data_subject_requests=DataSubjectRequestRepository(database),
            candidates=self.candidates,
            employers=self.employers,
            users=UserRepository(database),
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_privacy_notice_exposes_current_version_and_rights(self):
        notice = self.service.privacy_notice(language="uk")

        self.assertEqual(notice["version"], PRIVACY_NOTICE_VERSION)
        self.assertIn("export", notice["rights"])
        self.assertIn("Render", notice["processors"])

    def test_record_consent_uses_default_scopes_and_hashes_ip(self):
        consent = self.service.record_consent(
            subject_id="user-1",
            language="uk",
            source="web",
            scopes=None,
            ip_address="127.0.0.1",
            user_agent="tests",
        )

        self.assertEqual(consent.scopes, DEFAULT_CONSENT_SCOPES)
        self.assertTrue(consent.accepted)
        self.assertNotEqual(consent.metadata["ip_hash"], "127.0.0.1")

    def test_rejects_unsupported_data_subject_request_type(self):
        with self.assertRaises(ValueError):
            self.service.create_data_subject_request(
                subject_id="user-1",
                request_type="unknown",
                contact="user@example.com",
            )

    def test_export_subject_data_collects_matching_records(self):
        self.service.record_consent(subject_id="user-1", language="uk", source="web")
        self.service.create_data_subject_request("user-1", "export", "user@example.com")
        self.candidates.add(
            Candidate(
                first_name="Ana",
                last_name="Test",
                email="ana@example.com",
                phone="+100",
                country_code="PL",
                profession_code="welder",
                languages=["pl"],
                user_id="user-1",
            )
        )
        self.employers.add(
            Employer(
                company_name="TestCo",
                contact_email="company@example.com",
                contact_phone="+200",
                country_code="PL",
                industry="welding",
            )
        )

        exported = self.service.export_subject_data("user-1")

        self.assertEqual(len(exported["consents"]), 1)
        self.assertEqual(len(exported["data_subject_requests"]), 1)
        self.assertEqual(len(exported["candidates"]), 1)
        self.assertEqual(exported["employers"], [])


if __name__ == "__main__":
    unittest.main()
