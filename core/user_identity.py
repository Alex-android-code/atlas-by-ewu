"""Unified user profile and roles for public ATLAS flows."""

from dataclasses import asdict, dataclass, field
from typing import Any


SUPPORTED_USER_ROLES = {
    "candidate",
    "employer",
    "coordinator",
    "consultant",
    "trainer",
    "admin",
}


@dataclass
class UserProfile:
    user_id: str
    roles: list[str] = field(default_factory=list)
    preferred_language: str = "uk"
    profile_data: dict[str, Any] = field(default_factory=dict)

    def add_role(self, role: str) -> None:
        if role not in SUPPORTED_USER_ROLES:
            raise ValueError(f"Unsupported user role: {role}")
        if role not in self.roles:
            self.roles.append(role)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

