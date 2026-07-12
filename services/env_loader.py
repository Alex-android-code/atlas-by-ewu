"""Small .env loader for portable ATLAS deployments."""

from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: str | Path | None = None, override: bool = False) -> Path | None:
    env_path = Path(path) if path else default_env_path()
    if not env_path or not env_path.exists():
        return None
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        if override or not os.environ.get(key):
            os.environ[key] = value
    return env_path


def default_env_path() -> Path | None:
    explicit = os.getenv("ATLAS_ENV_FILE")
    if explicit:
        return Path(explicit)
    root = Path(__file__).resolve().parents[1]
    for name in (".env", ".env.local"):
        candidate = root / name
        if candidate.exists():
            return candidate
    return root / ".env"
