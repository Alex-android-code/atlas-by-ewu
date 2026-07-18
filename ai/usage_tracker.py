"""AI usage accounting and budget checks."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import os

from ai.models import UsageRecord


class UsageTracker:
    def __init__(self) -> None:
        self.records: list[UsageRecord] = []
        self.daily_budget_eur = _float_env("AI_DAILY_BUDGET_EUR")
        self.monthly_budget_eur = _float_env("AI_MONTHLY_BUDGET_EUR")
        self.user_daily_limit = _float_env("AI_USER_DAILY_LIMIT")
        self.tenant_monthly_limit = _float_env("AI_TENANT_MONTHLY_LIMIT")

    async def can_spend(self, *, tenant_id: str, user_id: str, estimated_cost: float | None, critical: bool = False) -> bool:
        if critical:
            return True
        estimate = float(estimated_cost or 0.0)
        now = datetime.now(timezone.utc)
        day_total = sum(float(r.estimated_cost or 0.0) for r in self.records if r.created_at.date() == now.date())
        month_total = sum(float(r.estimated_cost or 0.0) for r in self.records if r.created_at.year == now.year and r.created_at.month == now.month)
        user_day_total = sum(float(r.estimated_cost or 0.0) for r in self.records if r.user_id == user_id and r.created_at.date() == now.date())
        tenant_month_total = sum(float(r.estimated_cost or 0.0) for r in self.records if r.tenant_id == tenant_id and r.created_at.year == now.year and r.created_at.month == now.month)
        if self.daily_budget_eur is not None and day_total + estimate > self.daily_budget_eur:
            return False
        if self.monthly_budget_eur is not None and month_total + estimate > self.monthly_budget_eur:
            return False
        if self.user_daily_limit is not None and user_day_total + estimate > self.user_daily_limit:
            return False
        if self.tenant_monthly_limit is not None and tenant_month_total + estimate > self.tenant_monthly_limit:
            return False
        return True

    async def record(self, usage: UsageRecord) -> None:
        self.records.append(usage)

    def snapshot(self) -> list[dict]:
        return [asdict(record) for record in self.records]


def estimate_tokens(text: str) -> int:
    return max(1, len(str(text or "")) // 4)


def _float_env(name: str) -> float | None:
    value = os.getenv(name)
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except ValueError:
        return None
