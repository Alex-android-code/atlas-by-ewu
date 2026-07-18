import unittest

from memory.user_memory import UserMemory
from services.profile_builder import update_user_profile_from_message


class PublicProfileSyncTests(unittest.TestCase):
    def test_candidate_message_saves_phone_without_turning_it_into_salary(self):
        memory = UserMemory(user_id="public-sync-test")

        profile = update_user_profile_from_message(
            memory,
            "Я сварщик, сейчас в Украине, хочу работу в Польше, телефон +380671112233",
            language="ru",
        )

        self.assertEqual(profile["phone"], "+380671112233")
        self.assertIsNone(profile.get("desired_salary"))
        self.assertEqual(profile["profession"], "Welder")


if __name__ == "__main__":
    unittest.main()
