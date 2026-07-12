"""Provider-neutral AI Gateway for ATLAS/EWU.

The gateway is the only layer agents should use for model-like responses.
Concrete providers are adapters registered by name, not hardcoded branches.
"""

from dataclasses import asdict, dataclass, field
import os
from time import perf_counter
from typing import Any, Protocol
from uuid import uuid4


@dataclass
class AIRequest:
    user_id: str
    agent_type: str
    context: dict[str, Any]
    message: str
    request_id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class AIResponse:
    reply: str
    action: str | None = None
    confidence: float = 0.0
    handoff_required: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AIProvider(Protocol):
    name: str

    def send(self, request: AIRequest) -> AIResponse:
        ...

    def health(self) -> dict[str, Any]:
        ...


class AIProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}

    def register(self, provider: AIProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, provider_name: str) -> AIProvider:
        provider = self._providers.get(provider_name)
        if provider is None:
            available = ", ".join(sorted(self._providers)) or "none"
            raise ValueError(f"AI provider '{provider_name}' is not registered. Available: {available}")
        return provider

    def available(self) -> list[str]:
        return sorted(self._providers)


class AIGateway:
    def __init__(
        self,
        registry: AIProviderRegistry,
        default_provider: str = "mock",
        fallback_provider: str = "mock",
    ) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.fallback_provider = fallback_provider

    def send_message_to_ai(
        self,
        user_id: str,
        agent_type: str,
        context: dict[str, Any],
        message: str,
        provider_name: str | None = None,
    ) -> dict[str, Any]:
        provider_name = provider_name or self.default_provider
        request = self._build_request(
            user_id=user_id,
            agent_type=agent_type,
            context=context,
            message=message,
        )
        started = perf_counter()
        try:
            provider = self.registry.get(provider_name)
            response = provider.send(request)
            normalized = self._normalize_response(response, request, provider.name)
        except Exception as error:
            normalized = self._fallback_response(request, provider_name, error)

        normalized.metadata.update(
            {
                "request_id": request.request_id,
                "latency_ms": int((perf_counter() - started) * 1000),
                "gateway": "atlas_ai_gateway",
            }
        )
        return normalized.to_dict()

    def health(self) -> dict[str, Any]:
        providers = {}
        for provider_name in self.registry.available():
            try:
                provider = self.registry.get(provider_name)
                health_fn = getattr(provider, "health", None)
                providers[provider_name] = health_fn() if callable(health_fn) else {"status": "unknown"}
            except Exception as error:
                providers[provider_name] = {"status": "error", "error": str(error)}
        return {
            "status": "ok" if self.default_provider in self.registry.available() else "degraded",
            "default_provider": self.default_provider,
            "fallback_provider": self.fallback_provider,
            "available_providers": self.registry.available(),
            "providers": providers,
        }

    @staticmethod
    def _build_request(user_id: str, agent_type: str, context: dict[str, Any], message: str) -> AIRequest:
        return AIRequest(
            user_id=str(user_id or "anonymous"),
            agent_type=str(agent_type or "candidate").strip().lower(),
            context=context if isinstance(context, dict) else {},
            message=str(message or "").strip(),
        )

    def _normalize_response(self, response: AIResponse | dict[str, Any], request: AIRequest, provider_name: str) -> AIResponse:
        if isinstance(response, dict):
            response = AIResponse(
                reply=response.get("reply", ""),
                action=response.get("action"),
                confidence=response.get("confidence", 0.0),
                handoff_required=response.get("handoff_required", False),
                metadata=response.get("metadata", {}),
            )
        if not isinstance(response, AIResponse):
            raise TypeError(f"Provider '{provider_name}' returned unsupported response type: {type(response).__name__}")

        reply = str(response.reply or "").strip()
        if not reply:
            reply = self._safe_reply_for(request.agent_type)

        metadata = dict(response.metadata or {})
        metadata["provider"] = provider_name
        metadata["normalized"] = True
        metadata["fallback_used"] = bool(metadata.get("fallback_used", False))
        return AIResponse(
            reply=reply[:4000],
            action=str(response.action).strip() if response.action else None,
            confidence=max(0.0, min(float(response.confidence or 0.0), 1.0)),
            handoff_required=bool(response.handoff_required),
            metadata=metadata,
        )

    def _fallback_response(self, request: AIRequest, failed_provider: str, error: Exception) -> AIResponse:
        try:
            fallback = self.registry.get(self.fallback_provider)
            response = self._normalize_response(fallback.send(request), request, fallback.name)
            response.metadata.update(
                {
                    "fallback_used": True,
                    "failed_provider": failed_provider,
                    "provider_error": str(error),
                }
            )
            return response
        except Exception as fallback_error:
            return AIResponse(
                reply=self._safe_reply_for(request.agent_type),
                action=None,
                confidence=0.0,
                handoff_required=True,
                metadata={
                    "provider": "gateway",
                    "fallback_used": True,
                    "failed_provider": failed_provider,
                    "provider_error": str(error),
                    "fallback_error": str(fallback_error),
                },
            )

    @staticmethod
    def _safe_reply_for(agent_type: str) -> str:
        replies = {
            "employer": "Understood. I will structure this as a clear recruitment request and ask one key question.",
            "candidate": "I understand. I will help you sort this out step by step and ask one simple question.",
            "matching": "Understood. I will check the match and prepare a coordinator summary.",
            "legal": "Understood. I will flag this for careful review by a coordinator.",
            "document": "Understood. I will check which documents are still needed.",
            "coordinator": "Understood. I will prepare a short operational summary.",
        }
        return replies.get(agent_type, "Understood. I will continue carefully.")


def send_message_to_ai(
    user_id: str,
    agent_type: str,
    context: dict[str, Any],
    message: str,
) -> dict[str, Any]:
    return get_default_ai_gateway().send_message_to_ai(
        user_id=user_id,
        agent_type=agent_type,
        context=context,
        message=message,
    )


def get_default_ai_gateway() -> AIGateway:
    global _DEFAULT_GATEWAY
    if _DEFAULT_GATEWAY is not None:
        return _DEFAULT_GATEWAY

    registry = AIProviderRegistry()
    from ai.mock_provider import MockAIProvider
    from ai.gemini_provider import GeminiProvider

    registry.register(MockAIProvider())
    registry.register(GeminiProvider())
    default_provider = os.getenv("ATLAS_AI_PROVIDER", "mock").strip().lower() or "mock"
    if default_provider not in registry.available():
        default_provider = "mock"
    _DEFAULT_GATEWAY = AIGateway(
        registry=registry,
        default_provider=default_provider,
        fallback_provider="mock",
    )
    return _DEFAULT_GATEWAY


_DEFAULT_GATEWAY: AIGateway | None = None
