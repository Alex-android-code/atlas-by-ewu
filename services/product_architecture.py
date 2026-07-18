"""Product architecture registry for ATLAS rebuild."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from crm.crm_service import CrmService


class ProductArchitectureService:
    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or Path(__file__).resolve().parents[1] / "configs"

    def product_architecture(self) -> dict[str, Any]:
        return self._read_json("product_architecture.json")

    def pipelines(self) -> dict[str, Any]:
        return self._read_json("pipelines.json")

    def navigation_for_role(self, role: str) -> list[dict[str, Any]]:
        architecture = self.product_architecture()
        normalized = str(role or "candidate").strip().lower()
        role_navigation = architecture.get("role_navigation", {})
        module_codes = role_navigation.get(normalized) or role_navigation.get("candidate", [])
        modules = architecture.get("modules", {})
        return [
            {"code": code, **modules.get(code, {"label": code.replace("_", " ").title(), "contour": "control_center"})}
            for code in module_codes
        ]

    def crm_workspace(self, crm: CrmService, role: str = "admin") -> dict[str, Any]:
        dashboard = crm.coordinator_dashboard()
        candidates = crm.candidates.list()
        employers = crm.employers.list()
        vacancies = crm.vacancies.list()
        matches = crm.matches.list()
        pipelines = self.pipelines()["pipelines"]
        overdue_candidates = [
            candidate.to_dict()
            for candidate in candidates
            if candidate.status in {"documents_pending", "profile_incomplete", "verification"}
        ]
        intelligence_groups = [
            {
                "code": "requires_contact",
                "label": "Requires contact",
                "count": len(dashboard.get("manual_contact", [])),
                "priority": "high" if dashboard.get("manual_contact") else "normal",
                "source": "CRM candidate status",
            },
            {
                "code": "vacancy_without_progress",
                "label": "Vacancies without progress",
                "count": len(dashboard.get("pending_vacancies", [])),
                "priority": "medium" if dashboard.get("pending_vacancies") else "normal",
                "source": "Vacancy pipeline",
            },
            {
                "code": "risk_cases",
                "label": "Risk cases",
                "count": len(dashboard.get("risky_cases", [])),
                "priority": "high" if dashboard.get("risky_cases") else "normal",
                "source": "Matching risk metadata",
            },
            {
                "code": "records_without_owner",
                "label": "Records without owner",
                "count": sum(1 for item in candidates if not item.metadata.get("owner_id")),
                "priority": "medium",
                "source": "CRM metadata",
            },
        ]
        daily_brief = self._daily_brief(dashboard, intelligence_groups)
        return {
            "role": role,
            "navigation": self.navigation_for_role(role),
            "pipelines": pipelines,
            "daily_brief": daily_brief,
            "quick_actions": self._quick_actions(role),
            "table_view": {
                "candidates": [item.to_dict() for item in candidates[-50:]],
                "employers": [item.to_dict() for item in employers[-50:]],
                "vacancies": [item.to_dict() for item in vacancies[-50:]],
                "matches": [item.to_dict() for item in matches[-50:]],
            },
            "kanban_view": {
                "candidate": self._kanban_counts(candidates, pipelines["candidate"]),
                "vacancy": self._kanban_counts(vacancies, pipelines["vacancy"]),
                "employer": self._kanban_counts(employers, pipelines["employer"]),
            },
            "intelligence_view": {
                "groups": intelligence_groups,
                "overdue_candidates": overdue_candidates[:20],
            },
            "source": {
                "dashboard": dashboard,
                "generated_from": "json_crm_repositories",
            },
        }

    def _read_json(self, name: str) -> dict[str, Any]:
        path = self.config_dir / name
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _kanban_counts(items: list[Any], stages: list[str]) -> list[dict[str, Any]]:
        counts = {stage: 0 for stage in stages}
        for item in items:
            status = str(getattr(item, "status", "new") or "new")
            normalized = _legacy_status_to_pipeline(status)
            counts[normalized if normalized in counts else stages[0]] += 1
        return [{"status": status, "count": count} for status, count in counts.items()]

    @staticmethod
    def _daily_brief(dashboard: dict[str, Any], intelligence_groups: list[dict[str, Any]]) -> dict[str, Any]:
        important = [
            group
            for group in intelligence_groups
            if group["count"] and group["priority"] in {"high", "medium"}
        ]
        return {
            "greeting": "ATLAS analyzed the current operations queue.",
            "summary": f"{len(important)} areas require attention.",
            "events_analyzed": len(dashboard.get("activity", [])) + len(dashboard.get("event_feed", [])),
            "recommendations": [
                {
                    "title": group["label"],
                    "priority": group["priority"],
                    "reason": f"{group['count']} records detected.",
                    "source": group["source"],
                    "expected_result": "Coordinator decision or status update.",
                    "action": "open_crm_workspace",
                }
                for group in important
            ],
        }

    @staticmethod
    def _quick_actions(role: str) -> list[dict[str, str]]:
        normalized = str(role or "admin").lower()
        if normalized in {"candidate", "worker"}:
            return [
                {"code": "find_opportunities", "label": "Find opportunities"},
                {"code": "update_profile", "label": "Update profile"},
                {"code": "check_documents", "label": "Check documents"},
                {"code": "find_learning", "label": "Find learning"},
            ]
        if normalized.startswith("employer"):
            return [
                {"code": "create_vacancy", "label": "Create vacancy"},
                {"code": "find_people", "label": "Find people"},
                {"code": "analyze_workforce", "label": "Analyze workforce"},
                {"code": "request_report", "label": "Request report"},
            ]
        return [
            {"code": "open_crm", "label": "Open CRM"},
            {"code": "review_risks", "label": "Review risks"},
            {"code": "run_matching", "label": "Run matching"},
            {"code": "open_ai_control", "label": "Open AI Control"},
        ]


def _legacy_status_to_pipeline(status: str) -> str:
    mapping = {
        "new": "new",
        "registered": "verification",
        "documents_pending": "verification",
        "ready_for_matching": "ready",
        "matched": "matching",
        "interview": "interview",
        "hired": "hired",
        "open": "active",
        "published": "active",
        "pending_review": "awaiting_approval",
        "verified": "active",
        "archived": "closed",
    }
    return mapping.get(status, status)
