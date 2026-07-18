"""External provider adapters for ATLAS MultiModelGateway."""

from __future__ import annotations

import asyncio
import os
from time import perf_counter
from typing import Any

import requests

from ai.ai_gateway import format_provider_prompt
from ai.models import AIRequest, AIResponse, ModelResult
from ai.usage_tracker import estimate_tokens


class _HTTPProviderBase:
    name = "base"
    api_key_env = ""
    model_env = ""
    default_model = ""

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout_seconds: int | None = None) -> None:
        self.api_key = api_key if api_key is not None else os.getenv(self.api_key_env)
        self.model = model or os.getenv(self.model_env, self.default_model)
        self.timeout_seconds = timeout_seconds or int(os.getenv("AI_DEFAULT_TIMEOUT_SECONDS", "30"))

    def health(self) -> dict[str, Any]:
        if not self.api_key:
            return {"status": "degraded", "provider": self.name, "model": self.model, "error_type": "not_configured"}
        return {"status": "ok", "provider": self.name, "model": self.model, "configured": True}

    async def close(self) -> None:
        return None

    def send(self, request: AIRequest) -> AIResponse:
        return AIResponse(reply="", action=None, confidence=0.0, handoff_required=False, metadata={"provider": self.name, "model": self.model})


class OpenAIProvider(_HTTPProviderBase):
    name = "openai"
    api_key_env = "OPENAI_API_KEY"
    model_env = "OPENAI_MODEL"
    default_model = "gpt-4.1-mini"

    async def call_model(
        self,
        *,
        system_prompt: str,
        user_message: str,
        context: dict[str, Any],
        role: str,
        estimated_tokens: int,
    ) -> ModelResult:
        if not self.api_key:
            raise RuntimeError("OpenAI API key is not configured")
        prompt = format_provider_prompt(system_prompt=system_prompt, context=context, user_message=user_message)
        started = perf_counter()
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"<atlas_context>\n{context}\n</atlas_context>\n\n<user_message>\n{user_message}\n</user_message>"},
            ],
            "temperature": 0.4,
            "max_tokens": int(os.getenv("AI_MAX_OUTPUT_TOKENS", "900")),
        }
        response = await asyncio.to_thread(self._post_json, "https://api.openai.com/v1/chat/completions", payload)
        content = response["choices"][0]["message"]["content"]
        usage = response.get("usage", {})
        return ModelResult(
            content=str(content),
            provider=self.name,
            model=self.model,
            input_tokens=usage.get("prompt_tokens") or estimate_tokens(prompt),
            output_tokens=usage.get("completion_tokens") or estimate_tokens(str(content)),
            estimated_cost=None,
            latency_ms=int((perf_counter() - started) * 1000),
            cached=False,
        )

    def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()


class AnthropicProvider(_HTTPProviderBase):
    name = "anthropic"
    api_key_env = "ANTHROPIC_API_KEY"
    model_env = "ANTHROPIC_MODEL"
    default_model = "claude-3-5-haiku-latest"

    async def call_model(
        self,
        *,
        system_prompt: str,
        user_message: str,
        context: dict[str, Any],
        role: str,
        estimated_tokens: int,
    ) -> ModelResult:
        if not self.api_key:
            raise RuntimeError("Anthropic API key is not configured")
        prompt = format_provider_prompt(system_prompt=system_prompt, context=context, user_message=user_message)
        started = perf_counter()
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": f"<atlas_context>\n{context}\n</atlas_context>\n\n<user_message>\n{user_message}\n</user_message>"}],
            "max_tokens": int(os.getenv("AI_MAX_OUTPUT_TOKENS", "900")),
            "temperature": 0.1,
        }
        response = await asyncio.to_thread(self._post_json, "https://api.anthropic.com/v1/messages", payload)
        parts = response.get("content") or []
        content = "\n".join(str(part.get("text", "")) for part in parts if isinstance(part, dict)).strip()
        usage = response.get("usage", {})
        return ModelResult(
            content=content,
            provider=self.name,
            model=self.model,
            input_tokens=usage.get("input_tokens") or estimate_tokens(prompt),
            output_tokens=usage.get("output_tokens") or estimate_tokens(content),
            estimated_cost=None,
            latency_ms=int((perf_counter() - started) * 1000),
            cached=False,
        )

    def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            url,
            json=payload,
            headers={
                "x-api-key": str(self.api_key),
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()


ClaudeProvider = AnthropicProvider


class LocalAIProvider(_HTTPProviderBase):
    name = "local"
    api_key_env = "LOCAL_AI_API_KEY"
    model_env = "LOCAL_AI_MODEL"
    default_model = "local-default"

    async def call_model(self, *, system_prompt: str, user_message: str, context: dict[str, Any], role: str, estimated_tokens: int) -> ModelResult:
        raise RuntimeError("Local AI provider endpoint is not configured")
