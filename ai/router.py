"""Task classification and provider routing for MultiModelGateway."""

from __future__ import annotations

import os
from typing import Any

from ai.models import RoutingDecision, TaskType
from ai.usage_tracker import estimate_tokens


class TaskClassifier:
    def classify(self, *, role: str, message: str, context: dict[str, Any]) -> TaskType:
        explicit = context.get("task_type") or context.get("task")
        if explicit:
            try:
                return TaskType(str(explicit))
            except ValueError:
                pass
        lowered = str(message or "").lower()
        if role in {"legal"} or any(term in lowered for term in ("паспорт", "депортац", "police", "court", "адвокат")):
            return TaskType.LEGAL_SENSITIVE
        if role in {"matching"} and any(term in lowered for term in ("final", "compare", "matching", "match")):
            return TaskType.MATCHING_FINAL
        if role in {"employer", "corporate"} or "b2b" in lowered:
            return TaskType.EMPLOYER_ANALYSIS
        if len(message) > int(os.getenv("AI_LONG_CONTEXT_THRESHOLD", "12000")):
            return TaskType.DOCUMENT_ANALYSIS
        if any(term in lowered for term in ("pdf", "document", "cv", "резюме", "документ")):
            return TaskType.DOCUMENT_ANALYSIS
        if any(term in lowered for term in ("translate", "переклади", "переведи", "tłumacz")):
            return TaskType.TRANSLATION
        if any(term in lowered for term in ("summary", "summarize", "підсум", "резюмуй")):
            return TaskType.SUMMARIZATION
        return TaskType.CHAT


class ModelRouter:
    def __init__(self) -> None:
        self.openai_model = os.getenv("OPENAI_MODEL", "openai-default")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "anthropic-default")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.max_output_tokens = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "900"))

    def route(self, *, task_type: TaskType, role: str, message: str, context: dict[str, Any]) -> RoutingDecision:
        tokens = estimate_tokens(message) + estimate_tokens(str(context)[:4000])
        long_context = tokens >= int(os.getenv("AI_LONG_CONTEXT_THRESHOLD", "12000"))
        openai_ready = bool(os.getenv("OPENAI_API_KEY"))
        anthropic_ready = bool(os.getenv("ANTHROPIC_API_KEY"))
        gemini_ready = bool(os.getenv("GEMINI_API_KEY"))

        def choose(preferred: str, order: list[str]) -> tuple[str, str, list[str]]:
            if preferred == "openai" and openai_ready:
                return "openai", self.openai_model, order
            if preferred == "anthropic" and anthropic_ready:
                return "anthropic", self.anthropic_model, order
            if preferred == "gemini" and gemini_ready:
                return "gemini", self.gemini_model, order
            if gemini_ready:
                return "gemini", self.gemini_model, ["gemini", *[item for item in order if item != "gemini"]]
            return preferred, {"openai": self.openai_model, "anthropic": self.anthropic_model, "gemini": self.gemini_model}.get(preferred, self.gemini_model), order

        if task_type in {TaskType.DOCUMENT_ANALYSIS, TaskType.SUMMARIZATION} or long_context:
            provider, model, order = choose("gemini", ["gemini", "anthropic", "openai", "mock"])
            return RoutingDecision(provider, model, "large_context_or_document", self.max_output_tokens, 0.2, order)
        if task_type in {TaskType.MATCHING_FINAL, TaskType.EMPLOYER_ANALYSIS}:
            provider, model, order = choose("anthropic", ["anthropic", "openai", "gemini", "mock"])
            return RoutingDecision(provider, model, "complex_b2b_or_final_matching", self.max_output_tokens, 0.1, order)
        if task_type == TaskType.LEGAL_SENSITIVE:
            provider, model, order = choose("openai", ["openai", "gemini", "mock"])
            return RoutingDecision(provider, model, "sensitive_chat_with_human_guard", 450, 0.0, order)
        provider, model, order = choose("openai", ["openai", "anthropic", "gemini", "mock"])
        return RoutingDecision(provider, model, "general_dialogue", 600, 0.4, order)
