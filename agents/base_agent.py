"""Base class for all personal ATLAS agents."""

from abc import ABC, abstractmethod
from typing import Any

from ai.ai_gateway import AIGateway, get_default_ai_gateway
from core.agent_context import AgentContext
from memory.memory_store import MemoryStore
from memory.user_memory import UserMemory


class BaseAgent(ABC):
    agent_type = "base"

    def __init__(self, memory_store: MemoryStore, ai_gateway: AIGateway | None = None) -> None:
        self.memory_store = memory_store
        self.ai_gateway = ai_gateway or get_default_ai_gateway()

    def build_context(
        self,
        user_id: str,
        profile: Any | None = None,
        country_config: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentContext:
        return AgentContext(
            user_id=user_id,
            agent_type=self.agent_type,
            memory=self.load_memory(user_id),
            profile=profile,
            country_config=country_config,
            metadata=metadata or {},
        )

    @abstractmethod
    def respond(self, message: str, context: AgentContext) -> dict[str, Any]:
        raise NotImplementedError

    def save_memory(self, memory: UserMemory) -> None:
        self.memory_store.save(memory)

    def load_memory(self, user_id: str) -> UserMemory:
        return self.memory_store.load(user_id)

    def ask_ai(self, message: str, context: AgentContext) -> dict[str, Any]:
        return self.ai_gateway.send_message_to_ai(
            user_id=context.user_id,
            agent_type=self.agent_type,
            context=self.serialize_context(context),
            message=message,
        )

    @staticmethod
    def serialize_context(context: AgentContext) -> dict[str, Any]:
        profile = context.profile
        if hasattr(profile, "to_dict"):
            profile = profile.to_dict()
        elif isinstance(profile, dict):
            profile = {
                key: value.to_dict() if hasattr(value, "to_dict") else value
                for key, value in profile.items()
            }

        return {
            "user_id": context.user_id,
            "agent_type": context.agent_type,
            "profile": profile,
            "country_config": context.country_config,
            "metadata": context.metadata,
            "memory": context.memory.to_dict(),
        }

    def handoff_to_human(self, context: AgentContext, reason: str) -> dict[str, Any]:
        context.memory.coordinator_notes.append(f"Human handoff requested: {reason}")
        self.save_memory(context.memory)
        return {
            "agent": self.agent_type,
            "handoff_required": True,
            "reason": reason,
            "user_id": context.user_id,
        }
