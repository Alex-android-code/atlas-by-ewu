"""Worker friend-agent mode routing for ATLAS conversations."""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class AgentMode(StrEnum):
    FRIEND = "FRIEND"
    MENTOR = "MENTOR"
    EXECUTOR = "EXECUTOR"


FRIEND_HINTS = {
    "hard",
    "scared",
    "afraid",
    "tired",
    "worried",
    "stress",
    "nothing works",
    "i do not know what to do",
    "важко",
    "страшно",
    "втомився",
    "втомилась",
    "переживаю",
    "боюся",
    "нічого не виходить",
    "не знаю що робити",
    "тяжело",
    "страшно",
    "устал",
    "устала",
    "переживаю",
    "боюсь",
    "ничего не получается",
}

EXECUTOR_HINTS = {
    "do",
    "write",
    "create",
    "prepare",
    "find",
    "resume",
    "cv",
    "letter",
    "translate",
    "fill",
    "зроби",
    "напиши",
    "створи",
    "підготуй",
    "знайди",
    "резюме",
    "лист",
    "переклади",
    "заповни",
    "сделай",
    "напиши",
    "создай",
    "подготовь",
    "найди",
    "письмо",
    "переведи",
    "заполни",
}

WORKER_AGENT_RULES = [
    "Speak warmly, calmly and practically.",
    "Be supportive, but do not pretend to be human.",
    "Ask only one main question at a time.",
    "React to the user's message before moving forward.",
    "Do not judge education, experience, documents, language level or employment gaps.",
    "Do not make empty promises or pressure the user.",
    "Do not ask the user to repeat known information.",
    "Offer one to three concrete next steps.",
    "If the task is clear, help execute instead of over-explaining.",
    "Answer in the user's language when possible.",
]


MODE_BEHAVIOR = {
    AgentMode.FRIEND: {
        "relationship": "supportive friend and calm helper",
        "goal": "help the user feel heard, then propose one simple next step",
    },
    AgentMode.MENTOR: {
        "relationship": "career mentor",
        "goal": "analyze the situation and suggest practical professional next steps",
    },
    AgentMode.EXECUTOR: {
        "relationship": "practical executor",
        "goal": "produce or prepare the requested artifact or action",
    },
}


def detect_agent_mode(message: str) -> AgentMode:
    text = (message or "").lower()
    if any(hint in text for hint in EXECUTOR_HINTS):
        return AgentMode.EXECUTOR
    if any(hint in text for hint in FRIEND_HINTS):
        return AgentMode.FRIEND
    return AgentMode.MENTOR


def worker_agent_context(message: str, language: str = "en", profile: dict[str, Any] | None = None) -> dict[str, Any]:
    mode = detect_agent_mode(message)
    return {
        "mode": mode.value,
        "language": language,
        "behavior": MODE_BEHAVIOR[mode],
        "rules": WORKER_AGENT_RULES,
        "memoryPolicy": {
            "recentMessagesLimit": 40,
            "doNotStoreSecrets": True,
            "doNotInferMissingFacts": True,
        },
        "knownProfileKeys": sorted((profile or {}).keys()),
    }


def worker_agent_system_prompt() -> str:
    rules = "\n".join(f"{index + 1}. {rule}" for index, rule in enumerate(WORKER_AGENT_RULES))
    modes = "\n".join(f"{mode.value}: {data['goal']}" for mode, data in MODE_BEHAVIOR.items())
    return (
        "You are the worker's personal AI agent inside ATLAS.\n"
        "You are warm, natural, calm and practical, while clearly remaining an AI assistant.\n\n"
        f"Rules:\n{rules}\n\n"
        f"Modes:\n{modes}\n"
    )
