"""Intent detection for the public ATLAS coordinator conversation."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class IntentResult:
    scenario: str
    agent_type: str
    confidence: float
    signals: list[str]
    profession: str | None = None


class IntentDetectorService:
    """Small deterministic detector before a real AI classifier is connected."""

    SCENARIOS = {"candidate", "employer", "legalization", "business", "consultation"}

    PROFESSION_SIGNALS = {
        "welder": ("зварюваль", "сварщик", "spawacz", "welder", "mig", "mag", "tig"),
        "construction worker": ("монтажник", "monter", "builder", "construction"),
        "production worker": ("production", "produkcji", "производств", "виробниц"),
        "warehouse worker": ("warehouse", "magazyn", "склад"),
        "driver": ("driver", "kierowca", "водитель", "водій"),
        "electrician": ("electrician", "elektryk", "електрик", "электрик"),
    }

    EMPLOYER_SIGNALS = (
        "потрібні", "потрібен", "треба", "найняти", "працівників", "робітників",
        "нужны", "нужен", "требуются", "нанять", "работников", "сотрудников",
        "pracowników", "pracownicy", "potrzebuję", "potrzebuje", "zatrudnię", "zatrudnic",
        "hire", "employees", "workers", "staff", "recruit",
    )
    CANDIDATE_SIGNALS = (
        "шукаю роботу", "потрібна робота", "хочу працювати", "працювати",
        "ищу работу", "нужна работа", "хочу работать", "работать",
        "szukam pracy", "chcę pracować", "chce pracowac",
        "find a job", "looking for job", "looking for work", "work in", "job",
    )
    LEGAL_SIGNALS = (
        "легаліза", "легализа", "legalizacja", "legalization", "віза", "виза", "visa",
        "карта побиту", "karta pobytu", "permit", "дозвіл", "разрешение",
    )
    BUSINESS_SIGNALS = (
        "business", "бізнес", "бизнес", "firma", "company registration", "spółka", "spolka",
        "działalność", "dzialalnosc", "відкрити компанію", "открыть компанию",
    )
    CONSULTATION_SIGNALS = (
        "консульта", "порада", "совет", "consultation", "advice", "dorad", "nie wiem", "не знаю",
    )

    def detect(self, message: str, requested_agent_type: str | None = None, previous_intent: str | None = None) -> IntentResult:
        text = (message or "").lower()
        scores = {
            "candidate": self._score(text, self.CANDIDATE_SIGNALS),
            "employer": self._score(text, self.EMPLOYER_SIGNALS),
            "legalization": self._score(text, self.LEGAL_SIGNALS),
            "business": self._score(text, self.BUSINESS_SIGNALS),
            "consultation": self._score(text, self.CONSULTATION_SIGNALS),
        }
        profession = self.detect_profession(text)

        if requested_agent_type == "employer":
            scores["employer"] += 2
        elif requested_agent_type == "candidate" and scores["employer"] == 0:
            scores["candidate"] += 1

        if profession and scores["employer"] == 0 and scores["candidate"] == 0:
            scores["candidate"] += 1
        if profession and scores["employer"] > 0:
            scores["employer"] += 1

        scenario = max(scores, key=scores.get)
        if scores[scenario] == 0 and previous_intent in self.SCENARIOS:
            scenario = previous_intent or "consultation"
        elif scores[scenario] == 0:
            scenario = "consultation"

        agent_type = "employer" if scenario == "employer" else "candidate"
        confidence = min(0.96, 0.52 + scores[scenario] * 0.11)
        signals = self._signals_for(text, scenario)
        return IntentResult(scenario=scenario, agent_type=agent_type, confidence=confidence, signals=signals, profession=profession)

    @staticmethod
    def _score(text: str, signals: tuple[str, ...]) -> int:
        return sum(1 for signal in signals if signal in text)

    def _signals_for(self, text: str, scenario: str) -> list[str]:
        mapping = {
            "candidate": self.CANDIDATE_SIGNALS,
            "employer": self.EMPLOYER_SIGNALS,
            "legalization": self.LEGAL_SIGNALS,
            "business": self.BUSINESS_SIGNALS,
            "consultation": self.CONSULTATION_SIGNALS,
        }
        return [signal for signal in mapping.get(scenario, ()) if signal in text][:5]

    def detect_profession(self, text: str) -> str | None:
        for profession, signals in self.PROFESSION_SIGNALS.items():
            if any(signal in text for signal in signals):
                return profession
        match = re.search(r"(?:potrzebuję|potrzebuje|потрібні|нужны|требуются|szukam|ищу|шукаю)\s+([\wąćęłńóśźżа-яіїєґ -]{3,40})", text)
        return match.group(1).strip() if match else None
