"""Small JSON database adapter for the MVP.

This is intentionally simple, but the rest of the project talks to repository
objects instead of file paths. A PostgreSQL adapter can later replace this.
"""

import json
from pathlib import Path
from typing import Any


class JsonDatabase:
    def __init__(self, storage_dir: Path | None = None) -> None:
        self.storage_dir = storage_dir or Path(__file__).resolve().parents[1] / "data" / "db"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def insert(self, collection: str, item_id: str, item: dict[str, Any]) -> dict[str, Any]:
        data = self._load_collection(collection)
        data[item_id] = item
        self._save_collection(collection, data)
        return item

    def update(self, collection: str, item_id: str, item: dict[str, Any]) -> dict[str, Any]:
        return self.insert(collection, item_id, item)

    def get(self, collection: str, item_id: str) -> dict[str, Any] | None:
        return self._load_collection(collection).get(item_id)

    def list(self, collection: str) -> list[dict[str, Any]]:
        return list(self._load_collection(collection).values())

    def _collection_path(self, collection: str) -> Path:
        safe_name = "".join(char for char in collection if char.isalnum() or char in ("-", "_"))
        return self.storage_dir / f"{safe_name}.json"

    def _load_collection(self, collection: str) -> dict[str, dict[str, Any]]:
        path = self._collection_path(collection)
        if not path.exists():
            return {}

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save_collection(self, collection: str, data: dict[str, dict[str, Any]]) -> None:
        path = self._collection_path(collection)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

