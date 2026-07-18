"""Entitlement-based subscription access control."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.models import CustomerSubscription, PlanFeature, SubscriptionFeature, SubscriptionPlan
from database.repositories import (
    CustomerSubscriptionRepository,
    PlanFeatureRepository,
    SubscriptionFeatureRepository,
    SubscriptionPlanRepository,
)


PLAN_ORDER = ["start", "medium", "pro", "enterprise"]


@dataclass
class EntitlementRepositories:
    plans: SubscriptionPlanRepository
    features: SubscriptionFeatureRepository
    plan_features: PlanFeatureRepository
    customer_subscriptions: CustomerSubscriptionRepository


class EntitlementService:
    def __init__(
        self,
        repositories: EntitlementRepositories,
        config_path: Path | None = None,
    ) -> None:
        self.repositories = repositories
        self.config_path = config_path or Path(__file__).resolve().parents[1] / "configs" / "subscriptions.json"

    def catalog(self) -> dict[str, Any]:
        data = self._load_config()
        return {
            "plans": [
                {
                    "code": code,
                    "label": plan.get("label", code.title()),
                    "features": dict(plan.get("features", {})),
                }
                for code, plan in data["plans"].items()
            ]
        }

    def sync_catalog(self) -> dict[str, int]:
        data = self._load_config()
        plan_count = 0
        feature_codes: set[str] = set()
        plan_feature_count = 0
        for code, plan in data["plans"].items():
            self._upsert_plan(code, plan.get("label", code.title()))
            plan_count += 1
            for feature_code, enabled in plan.get("features", {}).items():
                self._upsert_feature(feature_code)
                self._upsert_plan_feature(code, feature_code, bool(enabled))
                feature_codes.add(feature_code)
                plan_feature_count += 1
        return {"plans": plan_count, "features": len(feature_codes), "plan_features": plan_feature_count}

    def set_customer_subscription(self, customer_id: str, customer_type: str, plan_code: str) -> CustomerSubscription:
        normalized_plan = self._normalize_plan(plan_code)
        for subscription in self.repositories.customer_subscriptions.list():
            if subscription.customer_id == customer_id and subscription.customer_type == customer_type:
                subscription.plan_code = normalized_plan
                subscription.status = "active"
                return self.repositories.customer_subscriptions.update(subscription)
        return self.repositories.customer_subscriptions.add(
            CustomerSubscription(customer_id=customer_id, customer_type=customer_type, plan_code=normalized_plan)
        )

    def effective_plan(self, customer_id: str, customer_type: str = "user") -> str:
        for subscription in self.repositories.customer_subscriptions.list():
            if (
                subscription.customer_id == customer_id
                and subscription.customer_type == customer_type
                and subscription.status == "active"
            ):
                return self._normalize_plan(subscription.plan_code)
        return "start"

    def has_entitlement(self, customer_id: str, feature_code: str, customer_type: str = "user") -> bool:
        plan_code = self.effective_plan(customer_id, customer_type=customer_type)
        return self.plan_has_feature(plan_code, feature_code)

    def plan_has_feature(self, plan_code: str, feature_code: str) -> bool:
        data = self._load_config()
        plan = data["plans"].get(self._normalize_plan(plan_code), data["plans"]["start"])
        return bool(plan.get("features", {}).get(feature_code, False))

    def require_entitlement(self, customer_id: str, feature_code: str, customer_type: str = "user") -> None:
        if not self.has_entitlement(customer_id, feature_code, customer_type=customer_type):
            raise PermissionError(f"Feature '{feature_code}' is not enabled for this subscription")

    def _upsert_plan(self, code: str, label: str) -> None:
        existing = _find_by_attr(self.repositories.plans.list(), "code", code)
        if existing:
            existing.label = label
            self.repositories.plans.update(existing)
            return
        self.repositories.plans.add(SubscriptionPlan(code=code, label=label))

    def _upsert_feature(self, code: str) -> None:
        existing = _find_by_attr(self.repositories.features.list(), "code", code)
        if existing:
            return
        self.repositories.features.add(SubscriptionFeature(code=code, label=code.replace("_", " ").title()))

    def _upsert_plan_feature(self, plan_code: str, feature_code: str, enabled: bool) -> None:
        for item in self.repositories.plan_features.list():
            if item.plan_code == plan_code and item.feature_code == feature_code:
                item.enabled = enabled
                self.repositories.plan_features.update(item)
                return
        self.repositories.plan_features.add(PlanFeature(plan_code=plan_code, feature_code=feature_code, enabled=enabled))

    def _normalize_plan(self, plan_code: str) -> str:
        normalized = plan_code.strip().lower()
        if normalized not in self._load_config()["plans"]:
            raise ValueError(f"Unknown subscription plan: {plan_code}")
        return normalized

    def _load_config(self) -> dict[str, Any]:
        return json.loads(self.config_path.read_text(encoding="utf-8"))


def _find_by_attr(items: list[Any], attr: str, value: str) -> Any | None:
    for item in items:
        if getattr(item, attr) == value:
            return item
    return None
