"""Gemini provider adapter for ATLAS MultiModelGateway."""

from __future__ import annotations

from time import perf_counter
from typing import Any

from ai.ai_gateway import format_provider_prompt
from ai.models import AIRequest, AIResponse, ModelResult
from ai.usage_tracker import estimate_tokens
from services.gemini_service import GeminiService, fallback_message


class GeminiProvider:
    name = "gemini"

    def __init__(self, service: GeminiService | None = None) -> None:
        self.service = service or GeminiService()
        self.model = self.service.model

    def health(self) -> dict[str, Any]:
        return self.service.health_check(ping=False)

    async def close(self) -> None:
        close = getattr(getattr(self.service, "_client", None), "close", None)
        if close:
            result = close()
            if hasattr(result, "__await__"):
                await result

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
        if not self.service.is_configured():
            raise RuntimeError("Gemini API key is not configured")
        prompt = format_provider_prompt(system_prompt=system_prompt, context=context, user_message=user_message)
        content = await self.service.generate_text_async(prompt, language=str(context.get("language") or "en"))
        return ModelResult(
            content=content,
            provider=self.name,
            model=self.service.model,
            input_tokens=estimate_tokens(prompt),
            output_tokens=estimate_tokens(content),
            estimated_cost=None,
            latency_ms=int((perf_counter() - started) * 1000),
            cached=False,
        )

    def send(self, request: AIRequest) -> AIResponse:
        if not self.service.is_configured():
            return AIResponse(
                reply=fallback_message(str(request.context.get("language") or "en")),
                action="gemini_fallback",
                confidence=0.0,
                handoff_required=False,
                metadata={"provider": self.name, "model": self.service.model, "fallback_used": True, "error_type": "not_configured"},
            )
        result = self.service.generate_json(
            format_provider_prompt(system_prompt="", context=request.context, user_message=request.message),
            language=str(request.context.get("language") or "en"),
        )
        return AIResponse(
            reply=result.message,
            action="gemini_structured_reply",
            confidence=result.confidence,
            handoff_required=False,
            metadata={"provider": self.name, "model": self.service.model, "next_field": result.next_field, "warnings": result.warnings},
        )
