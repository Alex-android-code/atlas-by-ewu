"""Storage adapters for user memory.

Agents depend on the MemoryStore protocol, not on JSON files. A PostgreSQL
adapter can later implement the same load/save interface.
"""

import json
import os
from pathlib import Path
from typing import Protocol

from memory.user_memory import UserMemory


class MemoryStore(Protocol):
    def load(self, user_id: str) -> UserMemory:
        ...

    def save(self, memory: UserMemory) -> None:
        ...


class JsonMemoryStore:
    def __init__(self, storage_dir: Path | None = None) -> None:
        self.storage_dir = storage_dir or _default_storage_dir()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def load(self, user_id: str) -> UserMemory:
        path = self._path_for(user_id)

        if not path.exists():
            return UserMemory(user_id=user_id)

        with path.open("r", encoding="utf-8") as file:
            return UserMemory.from_dict(json.load(file))

    def save(self, memory: UserMemory) -> None:
        path = self._path_for(memory.user_id)

        with path.open("w", encoding="utf-8") as file:
            json.dump(memory.to_dict(), file, ensure_ascii=False, indent=2)

    def _path_for(self, user_id: str) -> Path:
        safe_user_id = "".join(char for char in user_id if char.isalnum() or char in ("-", "_"))
        return self.storage_dir / f"{safe_user_id}.json"


def _default_storage_dir() -> Path:
    data_dir = os.getenv("ATLAS_DATA_DIR")
    if data_dir:
        return Path(data_dir) / "memory"
    return Path(__file__).resolve().parents[1] / "data" / "memory"
