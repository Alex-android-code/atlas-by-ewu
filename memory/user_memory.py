"""Per-user memory model for personal ATLAS agents."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class UserMemory:
    user_id: str
    profile_data: dict[str, Any] = field(default_factory=dict)
    conversation_summary: str = ""
    preferences: dict[str, Any] = field(default_factory=dict)
    last_offers: list[dict[str, Any]] = field(default_factory=list)
    risks: list[dict[str, Any]] = field(default_factory=list)
    coordinator_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserMemory":
        return cls(
            user_id=data["user_id"],
            profile_data=data.get("profile_data", {}),
            conversation_summary=data.get("conversation_summary", ""),
            preferences=data.get("preferences", {}),
            last_offers=data.get("last_offers", []),
            risks=data.get("risks", []),
            coordinator_notes=data.get("coordinator_notes", []),
        )

