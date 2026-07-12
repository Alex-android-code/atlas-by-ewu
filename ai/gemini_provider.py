"""Gemini provider adapter for ATLAS AI Gateway."""

from __future__ import annotations

from typing import Any

from ai.ai_gateway import AIRequest, AIResponse
from services.gemini_service import (
    GeminiService,
    build_structured_prompt,
    fallback_message,
    minimal_context,
)


class GeminiProvider:
    name = "gemini"

    def __init__(self, service: GeminiService | None = None) -> None:
        self.service = service or GeminiService()

    def health(self) -> dict[str, Any]:
        return self.service.health_check(ping=False)

    def send(self, request: AIRequest) -> AIResponse:
        language = request.context.get("language") or request.context.get("conversation_language") or "en"
        profile = request.context.get("profile") if isinstance(request.context.get("profile"), dict) else {}
        recent_messages = profile.get("messages", []) if isinstance(profile, dict) else []
        prompt = build_structured_prompt(
            language=language,
            user_role=request.agent_type,
            current_step=request.context.get("current_step") or "conversation",
            profile_data=profile,
            recent_messages=recent_messages,
            task="public_chat_reply",
        )
        prompt = f"{prompt}\n\nUser message:\n{request.message}"
        try:
            result = self.service.generate_json(prompt, language=language)
            return AIResponse(
                reply=result.message,
                action="gemini_structured_reply",
                confidence=result.confidence,
                handoff_required=False,
                metadata={
                    "provider": self.name,
                    "model": self.service.model,
                    "next_field": result.next_field,
                    "warnings": result.warnings,
                    "context": minimal_context(
                        language=language,
                        user_role=request.agent_type,
                        current_step="conversation",
                        profile_data=profile,
                        recent_messages=recent_messages,
                        task="public_chat_reply",
                    ),
                },
            )
        except Exception as error:
            return AIResponse(
                reply=fallback_message(str(language)),
                action="gemini_fallback",
                confidence=0.0,
                handoff_required=False,
                metadata={
                    "provider": self.name,
                    "model": self.service.model,
                    "fallback_used": True,
                    "error_type": getattr(error, "error_type", "unknown"),
                },
            )
