import unittest

from services.language_detector import LanguageDetectorService


class LanguageSelectionTests(unittest.TestCase):
    def test_saved_language_wins_over_message_language(self):
        detector = LanguageDetectorService()

        language = detector.detect(
            browser_language="en-US",
            saved_preference="ru",
            first_message="czekam na karte pobytu",
        )

        self.assertEqual(language, "ru")

    def test_ui_language_wins_over_english_message(self):
        detector = LanguageDetectorService()

        language = detector.detect(
            browser_language="en-US",
            saved_preference="uk",
            first_message="I need documents",
        )

        self.assertEqual(language, "uk")


if __name__ == "__main__":
    unittest.main()
