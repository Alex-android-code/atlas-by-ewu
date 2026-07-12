"""Build short public replies for the ATLAS coordinator."""

from __future__ import annotations

import re

from .public_tone import acknowledgement_for, safe_fallback_for
from .validators import validate_one_question_rule


def build_public_reply(
    *,
    acknowledgement: str | None = None,
    understood_summary: str | None = None,
    next_question: str | None = None,
    language: str | None = None,
    audience: str | None = None,
) -> str:
    parts = [
        (acknowledgement or acknowledgement_for(language, audience)).strip(),
        (understood_summary or "").strip(),
        (next_question or "").strip(),
    ]
    reply = " ".join(part for part in parts if part)
    reply = re.sub(r"\s+", " ", reply).strip()
    validation = validate_one_question_rule(reply, language=language)
    if validation.valid:
        return reply
    if next_question:
        fallback = f"{acknowledgement_for(language, audience)} {next_question}".strip()
        if validate_one_question_rule(fallback, language=language).valid:
            return fallback
    return validation.safe_fallback or safe_fallback_for(language, audience)
