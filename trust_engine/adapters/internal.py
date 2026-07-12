"""Local trust adapters used until external registries are connected."""

from __future__ import annotations

from typing import Any


class ProfileCompletenessAdapter:
    name = "profile_completeness"

    def check(self, employer: dict[str, Any], vacancy: dict[str, Any]) -> dict[str, Any]:
        missing = [
            key for key in ("company_name", "country", "contact_email", "contact_phone")
            if not employer.get(key)
        ]
        return {
            "adapter": self.name,
            "key": "trust.company_profile_complete" if not missing else "trust.company_profile_incomplete",
            "status": "ok" if not missing else "warning",
            "penalty": 0 if not missing else 14,
            "metadata": {"missing": missing},
        }


class InternalHistoryAdapter:
    name = "internal_history"

    def check(self, employer: dict[str, Any], vacancy: dict[str, Any]) -> dict[str, Any]:
        complaints = int(employer.get("complaints", 0) or 0)
        completed = int(employer.get("completed_recruitments", 0) or 0)
        if complaints >= 3:
            return {
                "adapter": self.name,
                "key": "trust.complaints_history",
                "status": "critical",
                "penalty": 42,
                "metadata": {"complaints": complaints, "completed_recruitments": completed},
            }
        return {
            "adapter": self.name,
            "key": "trust.internal_history_ok",
            "status": "ok" if completed or not complaints else "warning",
            "penalty": 0 if not complaints else 8,
            "metadata": {"complaints": complaints, "completed_recruitments": completed},
        }
