"""Constitutional safety guard for ATLAS user messages."""

from __future__ import annotations

import re
from typing import Any

from ai.models import GuardDecision, RiskLevel


_OLD_EVENT_PATTERNS = (
    re.compile(r"\b(ten|10|десять|десять\s+років|years?\s+ago|років\s+тому|лет\s+назад)\b", re.IGNORECASE),
)

_CATEGORY_RULES: list[tuple[str, RiskLevel, tuple[str, ...], tuple[re.Pattern[str], ...]]] = [
    ("passport_retention", RiskLevel.URGENT, ("паспорт забрали", "забрав паспорт", "документи забрали", "kept my passport", "took my passport"), (re.compile(r"(паспорт|документ\w*)\s+(забрал\w*|забрав\w*|утрим\w*|держ\w*)", re.IGNORECASE),)),
    ("unpaid_wages", RiskLevel.HIGH, ("не платять", "не выплатили", "unpaid wages", "no salary"), (re.compile(r"(зарплат\w*|wages?|salary).{0,30}(не\s+плат|unpaid|затрим)", re.IGNORECASE),)),
    ("illegal_employment", RiskLevel.HIGH, ("без договору", "без контракта", "illegal work"), (re.compile(r"(без\s+(договор|контракт)|illegal\s+work)", re.IGNORECASE),)),
    ("deportation_risk", RiskLevel.URGENT, ("депортац", "deportation"), (re.compile(r"(депортац|deportation|видворенн)", re.IGNORECASE),)),
    ("police_or_court", RiskLevel.HIGH, ("поліція", "полиция", "court", "суд"), (re.compile(r"(поліці|полици|police|court|суд)", re.IGNORECASE),)),
    ("discrimination", RiskLevel.SENSITIVE, ("дискримінац", "discrimination", "расизм"), (re.compile(r"(дискримінац|дискриминац|discriminat|racis)", re.IGNORECASE),)),
    ("workplace_injury", RiskLevel.HIGH, ("травма на роботі", "injury at work", "несчастный случай"), (re.compile(r"(травм\w*|injur\w*).{0,30}(робот|work|prac)", re.IGNORECASE),)),
    ("violence_or_threat", RiskLevel.URGENT, ("погрож", "угрож", "violence", "threat"), (re.compile(r"(погрож|угрож|threat|violence|насиль)", re.IGNORECASE),)),
    ("document_fraud", RiskLevel.HIGH, ("підроб", "поддел", "fake document"), (re.compile(r"(підроб|поддел|fake).{0,30}(документ|passport|certificate)", re.IGNORECASE),)),
    ("legal_dispute", RiskLevel.SENSITIVE, ("юрист", "адвокат", "lawsuit", "legal dispute"), (re.compile(r"(адвокат|юрист|lawsuit|legal\s+dispute)", re.IGNORECASE),)),
    ("human_trafficking_risk", RiskLevel.EMERGENCY, ("не дозволяє піти", "не выпускают", "locked", "forced work"), (re.compile(r"(не\s+дозволя\w*\s+піти|не\s+выпуска\w*|locked|forced\s+work|змушу\w*)", re.IGNORECASE),)),
]


class ConstitutionalGuard:
    def evaluate(self, message: str, context: dict[str, Any] | None = None) -> GuardDecision:
        text = str(message or "").strip()
        lowered = text.lower()
        old_history = any(pattern.search(lowered) for pattern in _OLD_EVENT_PATTERNS)
        best: GuardDecision | None = None
        for category, level, keywords, patterns in _CATEGORY_RULES:
            keyword_hit = any(keyword in lowered for keyword in keywords)
            regex_hit = any(pattern.search(text) for pattern in patterns)
            if not keyword_hit and not regex_hit:
                continue
            if old_history and category == "workplace_injury" and not self._has_current_urgency(lowered):
                continue
            decision = GuardDecision(
                level=level,
                category=category,
                reason="constitutional_guard_rule_match",
                requires_human=level in {RiskLevel.HIGH, RiskLevel.URGENT, RiskLevel.EMERGENCY},
                allow_ai_response=level in {RiskLevel.NORMAL, RiskLevel.SENSITIVE, RiskLevel.URGENT},
            )
            if best is None or self._rank(decision.level) > self._rank(best.level):
                best = decision
        if best:
            return best
        return GuardDecision(RiskLevel.NORMAL, "none", "no_sensitive_signal", False, True)

    @staticmethod
    def _has_current_urgency(text: str) -> bool:
        return any(token in text for token in ("зараз", "сьогодні", "now", "today", "urgent", "терміново", "срочно"))

    @staticmethod
    def _rank(level: RiskLevel) -> int:
        return {
            RiskLevel.NORMAL: 0,
            RiskLevel.SENSITIVE: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.URGENT: 3,
            RiskLevel.EMERGENCY: 4,
        }[level]
