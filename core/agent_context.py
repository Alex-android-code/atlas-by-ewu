"""Runtime context passed into ATLAS agents."""

from dataclasses import dataclass, field
from typing import Any

from memory.user_memory import UserMemory


@dataclass
class AgentContext:
    user_id: str
    agent_type: str
    memory: UserMemory
    profile: Any | None = None
    country_config: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

