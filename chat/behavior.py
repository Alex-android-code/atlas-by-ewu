"""Configuration for public ATLAS coordinator conversation behavior."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatBehaviorConfig:
    max_questions_per_message: int = 1
    max_public_reply_length: str = "short"
    tone: str = "calm_coordinator"
    allow_technical_labels_in_public_chat: bool = False
    allow_internal_scores_in_public_chat: bool = False
    ask_only_missing_fields: bool = True
    confirm_extracted_info_briefly: bool = True


CHAT_BEHAVIOR = ChatBehaviorConfig()
