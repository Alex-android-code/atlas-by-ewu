import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.create_data_backup import create_backup


class BackupScriptTests(unittest.TestCase):
    def test_backup_skips_secrets_logs_and_caches(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "data"
            source.mkdir()
            (source / "records.json").write_text('{"ok": true}', encoding="utf-8")
            (source / ".env").write_text("SECRET=value", encoding="utf-8")
            (source / "debug.log").write_text("log", encoding="utf-8")
            cache = source / "__pycache__"
            cache.mkdir()
            (cache / "module.pyc").write_bytes(b"cache")
            output = root / "backup.zip"

            manifest = create_backup([source], output)

            with ZipFile(output) as archive:
                names = set(archive.namelist())

            self.assertIn("data/records.json", names)
            self.assertIn("backup_manifest.json", names)
            self.assertNotIn("data/.env", names)
            self.assertNotIn("data/debug.log", names)
            self.assertTrue(all("__pycache__" not in name for name in names))
            self.assertEqual(len(manifest["files"]), 1)


if __name__ == "__main__":
    unittest.main()
