"""Helpers for separating demo seed data from real ATLAS operations."""

from __future__ import annotations

from typing import Any


def is_demo_record(item: Any) -> bool:
    metadata = getattr(item, "metadata", None)
    if not isinstance(metadata, dict):
        metadata = item.get("metadata", {}) if isinstance(item, dict) else {}
    return bool(metadata.get("is_demo") or metadata.get("data_classification") in {"demo", "test"})
