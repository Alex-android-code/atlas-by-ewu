"""Mock AI provider for local development and tests."""

from __future__ import annotations

from time import perf_counter
from typing import Any

from ai.ai_gateway import format_provider_prompt
from ai.models import AIRequest, AIResponse, ModelResult
from ai.usage_tracker import estimate_tokens


class MockAIProvider:
    name = "mock"
    model = "atlas-mock-1"

    def health(self) -> dict:
        return {"status": "ok", "mode": "deterministic", "model": self.model}

    async def close(self) -> None:
        return None

    async def call_model(
        self,
        *,
        system_prompt: str,
        user_message: str,
        context: dict[str, Any],
        role: str,
        estimated_tokens: int,
    ) -> ModelResult:
        started = perf_counter()
        prompt = format_provider_prompt(system_prompt=system_prompt, context=context, user_message=user_message)
        content = self._reply_for(role=role, message=user_message, context=context)
        return ModelResult(
            content=content,
            provider=self.name,
            model=self.model,
            input_tokens=estimate_tokens(prompt),
            output_tokens=estimate_tokens(content),
            estimated_cost=0.0,
            latency_ms=int((perf_counter() - started) * 1000),
            cached=False,
        )

    def send(self, request: AIRequest) -> AIResponse:
        reply = self._reply_for(role=request.agent_type, message=request.message, context=request.context)
        return AIResponse(
            reply=reply,
            action=self._action_for(request.agent_type),
            confidence=0.72,
            handoff_required=False,
            metadata={"provider": self.name, "agent_type": request.agent_type, "context_keys": sorted(request.context.keys())},
        )

    @staticmethod
    def _action_for(agent_type: str) -> str | None:
        actions = {
            "candidate": "update_candidate_memory",
            "employer": "update_employer_memory",
            "matching": "explain_match",
            "legal": "triage_legal_risk",
            "document": "check_documents",
            "coordinator": "summarize_dashboard",
        }
        return actions.get(agent_type)

    @staticmethod
    def _reply_for(*, role: str, message: str, context: dict[str, Any]) -> str:
        text = message.lower()
        translations = context.get("translations", {}) if isinstance(context, dict) else {}

        def t(key: str) -> str:
            return translations.get(key, key)

        if role == "employer":
            return f"{t('employer.response_ack')}\n\n{t('employer.response_next_question')}"
        if any(word in text for word in ("звар", "свар", "welder")):
            return f"{t('coordinator.ask_profession')}\n\n{t('coordinator.ask_country')}"
        if any(word in text for word in ("працівників", "работников", "employees", "workers", "людей")):
            return t("coordinator.ask_employer_need")
        if any(word in text for word in ("консульта", "consultation", "advice")):
            return t("coordinator.consultation_start")
        return t("coordinator.welcome")
