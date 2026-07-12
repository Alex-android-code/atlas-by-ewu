"""Safety validation for public ATLAS replies."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .public_tone import FORBIDDEN_PUBLIC_TERMS, safe_fallback_for


@dataclass(frozen=True)
class OneQuestionValidationResult:
    valid: bool
    warnings: list[str]
    safe_fallback: str | None = None


MULTIPLE_QUESTION_PATTERNS = (
    r"\b(and|or)\b[^?.!]{0,40}\?",
    r"\b oraz \b[^?.!]{0,40}\?",
    r"\b i \b[^?.!]{0,40}\?",
    r"\b oraz jakie \b",
    r"\b i jakie \b",
    r"\bгде\b[^?.!]{0,60}\bесть ли\b",
    r"\bгде\b[^?.!]{0,60}\bкакая\b",
    r"\bесть ли\b[^?.!]{0,60}\bкакая\b",
    r"\bде\b[^?.!]{0,60}\bчи є\b",
)


def validate_one_question_rule(text: str, language: str | None = None) -> OneQuestionValidationResult:
    value = (text or "").strip()
    warnings: list[str] = []

    if value.count("?") > 1:
        warnings.append("more_than_one_question_mark")

    lower = value.lower()
    for term in FORBIDDEN_PUBLIC_TERMS:
        if term in lower:
            warnings.append(f"forbidden_public_term:{term}")

    if re.search(r"(?m)^\s*(?:\d+[\.)]|[-*])\s+.+\?", value):
        warnings.append("stacked_question_list")

    for pattern in MULTIPLE_QUESTION_PATTERNS:
        if re.search(pattern, lower, flags=re.IGNORECASE):
            warnings.append("multiple_question_pattern")
            break

    return OneQuestionValidationResult(
        valid=not warnings,
        warnings=warnings,
        safe_fallback=None if not warnings else safe_fallback_for(language),
    )
