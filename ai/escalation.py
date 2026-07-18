"""Escalation service interfaces and local durable implementation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
from typing import Any, Protocol
from uuid import uuid4

from ai.models import EscalationCase


class EscalationService(Protocol):
    async def create_case(
        self,
        *,
        tenant_id: str,
        user_id: str,
        message: str,
        reason: str,
        category: str,
        priority: str,
        context_snapshot: dict[str, Any],
    ) -> EscalationCase:
        ...


class JsonEscalationService:
    def __init__(self, path: str | Path | None = None) -> None:
        data_dir = Path(os.getenv("ATLAS_DATA_DIR", "data"))
        self.path = Path(path) if path else data_dir / "ai_escalations.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def create_case(
        self,
        *,
        tenant_id: str,
        user_id: str,
        message: str,
        reason: str,
        category: str,
        priority: str,
        context_snapshot: dict[str, Any],
    ) -> EscalationCase:
        now = datetime.now(timezone.utc)
        case = EscalationCase(
            case_id=f"ATLAS-{now.strftime('%Y%m%d')}-{uuid4().hex[:8]}",
            status="open",
            priority=priority,
            created_at=now,
            assigned_to=None,
        )
        record = {
            "case_id": case.case_id,
            "status": case.status,
            "priority": case.priority,
            "created_at": case.created_at.isoformat(),
            "assigned_to": case.assigned_to,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "message": str(message or "")[:2000],
            "reason": reason,
            "category": category,
            "context_snapshot": context_snapshot,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return case
