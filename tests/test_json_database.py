import json
import tempfile
import unittest
from pathlib import Path

from database.json_database import JsonDatabase


class JsonDatabaseTests(unittest.TestCase):
    def test_insert_writes_valid_json_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            database = JsonDatabase(Path(tmpdir))

            database.insert("candidates", "CAN-1", {"id": "CAN-1", "name": "Ana"})

            stored = json.loads((Path(tmpdir) / "candidates.json").read_text(encoding="utf-8"))
            self.assertEqual(stored["CAN-1"]["name"], "Ana")

    def test_empty_collection_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            database = JsonDatabase(Path(tmpdir))

            with self.assertRaises(ValueError):
                database.insert("../", "ID-1", {"id": "ID-1"})


if __name__ == "__main__":
    unittest.main()
