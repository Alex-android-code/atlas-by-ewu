import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from services.onboarding_file_storage import OnboardingFileStorage


def png_1x1() -> bytes:
    output = BytesIO()
    Image.new("RGB", (1, 1), (212, 175, 55)).save(output, format="PNG")
    return output.getvalue()


class OnboardingFileStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.storage = OnboardingFileStorage(Path(self.tmpdir.name))

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_saves_private_profile_photo_with_unique_url(self) -> None:
        stored = self.storage.save(
            owner_id="user-1",
            kind="profile_photo",
            filename="avatar.png",
            mime_type="image/png",
            stream=BytesIO(png_1x1()),
        )

        self.assertTrue(stored.id.startswith("ONB-"))
        self.assertEqual(stored.mime_type, "image/png")
        self.assertIn("/api/onboarding/files/", stored.to_dict()["url"])
        self.assertTrue(self.storage.path_for(stored.id, "user-1").exists())

    def test_rejects_access_by_different_owner(self) -> None:
        stored = self.storage.save(
            owner_id="user-1",
            kind="cv",
            filename="cv.pdf",
            mime_type="application/pdf",
            stream=BytesIO(b"%PDF-1.7\n%%EOF"),
        )

        with self.assertRaises(FileNotFoundError):
            self.storage.path_for(stored.id, "user-2")

    def test_rejects_unsafe_photo_extension(self) -> None:
        with self.assertRaises(ValueError):
            self.storage.save(
                owner_id="user-1",
                kind="profile_photo",
                filename="avatar.exe",
                mime_type="image/png",
                stream=BytesIO(png_1x1()),
            )


if __name__ == "__main__":
    unittest.main()
