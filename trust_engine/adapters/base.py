"""Base adapter contract for employer trust checks."""

from __future__ import annotations

from typing import Any, Protocol


class TrustCheckAdapter(Protocol):
    name: str

    def check(self, employer: dict[str, Any], vacancy: dict[str, Any]) -> dict[str, Any]:
        """Return a trust check result without blocking the employer."""
