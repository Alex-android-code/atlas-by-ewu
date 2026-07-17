import unittest

from services.dialogue_state import (
    get_completed_fields,
    get_next_required_field,
    process_candidate_dialogue,
)


class DialogueStateTests(unittest.TestCase):
    def test_pending_karta_pobytu_ru_is_saved_and_moves_next(self):
        profile = {
            "profession": "\u043a\u043b\u0438\u043d\u0435\u0440",
            "country": "PL",
            "current_step": "documents_status",
        }

        result = process_candidate_dialogue(
            profile,
            "\u0416\u0434\u0443 \u043a\u0430\u0440\u0442\u0443 \u043f\u043e\u0431\u044b\u0442\u0430",
            "ru",
            "req-1",
        )

        self.assertTrue(result.profile_updated)
        self.assertEqual(profile["residence_document_status"], "pending")
        self.assertEqual(profile["residence_document_type"], "karta_pobytu")
        self.assertIn("documents_status", profile["completed_fields"])
        self.assertEqual(profile["current_step"], "experience")
        self.assertIn("\u043e\u043f\u044b\u0442", result.reply.casefold())
        self.assertNotIn(
            "\u041a\u0430\u043a\u0438\u0435 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b",
            result.reply,
        )

    def test_pending_karta_pobytu_uk_is_recognized(self):
        profile = {"profession": "Recruiter", "country": "PL"}

        result = process_candidate_dialogue(
            profile,
            "\u0427\u0435\u043a\u0430\u044e \u043a\u0430\u0440\u0442\u0443 \u043f\u043e\u0431\u0438\u0442\u0443",
            "uk",
            "req-uk",
        )

        self.assertEqual(profile["documents_status"], "pending")
        self.assertIn("documents_status", result.completed_fields)

    def test_pending_karta_pobytu_pl_is_recognized(self):
        profile = {"profession": "Welder", "country": "PL"}

        result = process_candidate_dialogue(
            profile,
            "czekam na karte pobytu",
            "pl",
            "req-pl",
        )

        self.assertEqual(profile["residence_document_status"], "pending")
        self.assertIn("documents_status", result.completed_fields)

    def test_ambiguous_wait_does_not_update_documents(self):
        profile = {
            "profession": "\u043a\u043b\u0438\u043d\u0435\u0440",
            "country": "PL",
            "current_step": "documents_status",
        }

        result = process_candidate_dialogue(profile, "\u0436\u0434\u0443", "ru", "req-ambiguous")

        self.assertFalse(result.profile_updated)
        self.assertNotIn("residence_document_status", profile)
        self.assertEqual(profile["current_step"], "documents_status")

    def test_duplicate_request_id_does_not_duplicate_history(self):
        profile = {"profession": "Cleaner", "country": "PL", "current_step": "documents_status"}

        first = process_candidate_dialogue(profile, "czekam na karte pobytu", "pl", "same-req")
        history_len = len(profile["dialogue_history"])
        second = process_candidate_dialogue(profile, "czekam na karte pobytu", "pl", "same-req")

        self.assertFalse(first.duplicate)
        self.assertTrue(second.duplicate)
        self.assertEqual(len(profile["dialogue_history"]), history_len)
        self.assertEqual(second.reply, first.reply)

    def test_get_next_required_field_completes_when_all_fields_exist(self):
        profile = {
            "profession": "Welder",
            "country": "PL",
            "experience_years": 4,
            "documents_status": "pending",
            "preferred_contact_method": "phone",
            "phone": "+48123456789",
            "driving_license": "B",
            "certificates": ["welding"],
            "relocation_readiness": True,
            "preferred_destination": "PL",
            "learning_readiness": True,
            "desired_salary": 5000,
            "ready_from": "now",
            "accommodation_need": True,
            "photo": "later",
            "document_files": ["later"],
        }

        completed = get_completed_fields(profile)

        self.assertIsNone(get_next_required_field(profile, completed))


if __name__ == "__main__":
    unittest.main()
