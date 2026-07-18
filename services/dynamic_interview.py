"""Dynamic AI-interview foundation for ATLAS.

The service keeps the core interview rules deterministic and testable:
one question at a time, skip known fields, preserve unfinished sessions, and
separate inferred competencies from verified facts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from core.models import DynamicInterviewSession, utc_now_iso
from database.repositories import DynamicInterviewSessionRepository
from services.competency_intelligence import CompetencyIntelligenceService


INTERVIEW_FIELDS = [
    "professional_goal",
    "experience_summary",
    "competencies",
    "competency_evidence",
    "career_goals",
    "market_requirements",
    "documents",
    "constraints",
]

QUESTIONS = {
    "en": {
        "professional_goal": "What work or professional direction do you want to move toward now?",
        "experience_summary": "What relevant experience have you already had?",
        "competencies": "Which skills or competencies do you already have for that direction?",
        "competency_evidence": "What evidence can confirm one of those competencies?",
        "career_goals": "What result do you want to reach in your career next?",
        "market_requirements": "Which employer or market requirements do you want to prepare for?",
        "documents": "Which documents, certificates, or licenses do you already have?",
        "constraints": "What limits or conditions should your agent remember?",
    },
    "uk": {
        "professional_goal": "У якому професійному напрямку ви хочете рухатися зараз?",
        "experience_summary": "Який релевантний досвід у вас уже є?",
        "competencies": "Які навички або компетенції у вас уже є для цього напрямку?",
        "competency_evidence": "Який доказ може підтвердити одну з цих компетенцій?",
        "career_goals": "Якого результату ви хочете досягти в кар'єрі далі?",
        "market_requirements": "До яких вимог роботодавця або ринку ви хочете підготуватися?",
        "documents": "Які документи, сертифікати або ліцензії у вас уже є?",
        "constraints": "Які обмеження або умови ваш агент має пам'ятати?",
    },
    "pl": {
        "professional_goal": "W jakim kierunku zawodowym chcesz teraz isc?",
        "experience_summary": "Jakie masz juz odpowiednie doswiadczenie?",
        "competencies": "Jakie umiejetnosci lub kompetencje juz masz w tym kierunku?",
        "competency_evidence": "Jaki dowod moze potwierdzic jedna z tych kompetencji?",
        "career_goals": "Jaki wynik chcesz osiagnac dalej w karierze?",
        "market_requirements": "Do jakich wymagan pracodawcy lub rynku chcesz sie przygotowac?",
        "documents": "Jakie dokumenty, certyfikaty albo licencje juz masz?",
        "constraints": "Jakie ograniczenia albo warunki agent powinien pamietac?",
    },
}

COMPLETE_MESSAGE = {
    "en": "The interview foundation is complete. Your agent can now build a professional map.",
    "uk": "Базове інтерв'ю завершено. Ваш агент може формувати професійну карту.",
    "pl": "Podstawowy wywiad jest gotowy. Agent moze budowac mape zawodowa.",
}


@dataclass(frozen=True)
class AnswerAnalysis:
    field: str
    value: Any
    extracted_competencies: list[str]
    contradictions: list[dict[str, Any]]
    warnings: list[str]


class QuestionGenerationService:
    def next_field(self, session: DynamicInterviewSession) -> str | None:
        completed = set(session.completed_fields)
        for field in INTERVIEW_FIELDS:
            if field not in completed and not _has_value(session.profile_data.get(field)):
                return field
        return None

    def question_for(self, field: str | None, language: str) -> str:
        if field is None:
            return COMPLETE_MESSAGE.get(language, COMPLETE_MESSAGE["en"])
        return QUESTIONS.get(language, QUESTIONS["en"]).get(field) or QUESTIONS["en"][field]


class ContradictionDetectionService:
    def detect(self, profile_data: dict[str, Any], field: str, value: Any) -> list[dict[str, Any]]:
        previous = profile_data.get(field)
        if not _has_value(previous) or previous == value:
            return []
        return [
            {
                "field": field,
                "previous_value": previous,
                "new_value": value,
                "status": "needs_clarification",
                "detected_at": utc_now_iso(),
            }
        ]


class CompetencyExtractionService:
    def extract(self, field: str, answer: str) -> list[str]:
        if field != "competencies":
            return []
        parts = re.split(r"[,;/\n]|\band\b|\boraz\b|\bi\b", answer, flags=re.IGNORECASE)
        competencies = []
        for part in parts:
            value = re.sub(r"\s+", " ", part.strip().lower())
            if len(value) >= 3:
                competencies.append(value)
        return list(dict.fromkeys(competencies))


class AnswerAnalysisService:
    def __init__(
        self,
        contradictions: ContradictionDetectionService | None = None,
        competencies: CompetencyExtractionService | None = None,
    ) -> None:
        self.contradictions = contradictions or ContradictionDetectionService()
        self.competencies = competencies or CompetencyExtractionService()

    def analyze(self, session: DynamicInterviewSession, answer: str) -> AnswerAnalysis:
        field = session.current_field or "professional_goal"
        value = _clean_answer(answer)
        if not value:
            return AnswerAnalysis(field=field, value="", extracted_competencies=[], contradictions=[], warnings=["empty_answer"])
        contradictions = self.contradictions.detect(session.profile_data, field, value)
        extracted = self.competencies.extract(field, value)
        return AnswerAnalysis(
            field=field,
            value=value,
            extracted_competencies=extracted,
            contradictions=contradictions,
            warnings=[],
        )


class ProfessionalProfileBuilder:
    def apply(self, session: DynamicInterviewSession, analysis: AnswerAnalysis) -> DynamicInterviewSession:
        if analysis.value:
            session.profile_data[analysis.field] = analysis.value
        if analysis.field not in session.completed_fields and analysis.value and not analysis.contradictions:
            session.completed_fields.append(analysis.field)
        if analysis.extracted_competencies:
            session.profile_data["competency_names"] = analysis.extracted_competencies
        session.contradictions.extend(analysis.contradictions)
        session.updated_at = utc_now_iso()
        return session


class DynamicInterviewService:
    def __init__(
        self,
        sessions: DynamicInterviewSessionRepository,
        competency_service: CompetencyIntelligenceService | None = None,
        questions: QuestionGenerationService | None = None,
        answers: AnswerAnalysisService | None = None,
        profile_builder: ProfessionalProfileBuilder | None = None,
    ) -> None:
        self.sessions = sessions
        self.competency_service = competency_service
        self.questions = questions or QuestionGenerationService()
        self.answers = answers or AnswerAnalysisService()
        self.profile_builder = profile_builder or ProfessionalProfileBuilder()

    def start_or_resume(self, user_id: str, role: str = "candidate", language: str = "en") -> dict[str, Any]:
        session = self._get_or_create_active_session(user_id, role, language)
        next_field = self.questions.next_field(session)
        session.current_field = next_field
        if next_field is None:
            session.status = "complete"
        self.sessions.update(session)
        return self._response(session, self.questions.question_for(next_field, session.language), None, [])

    def answer_step(self, session_id: str, answer: str) -> dict[str, Any]:
        session = self.sessions.get(session_id)
        if session is None:
            raise ValueError(f"Dynamic interview session not found: {session_id}")
        if session.status == "complete":
            return self._response(session, self.questions.question_for(None, session.language), None, [])

        analysis = self.answers.analyze(session, answer)
        session.history.append(
            {
                "role": "user",
                "field": analysis.field,
                "content": answer,
                "timestamp": utc_now_iso(),
            }
        )
        if analysis.warnings:
            question = self.questions.question_for(session.current_field, session.language)
            self.sessions.update(session)
            return self._response(session, question, analysis, analysis.warnings)
        if analysis.contradictions:
            session.contradictions.extend(analysis.contradictions)
            session.updated_at = utc_now_iso()
            question = self.questions.question_for(session.current_field, session.language)
            self.sessions.update(session)
            return self._response(session, question, analysis, ["contradiction_needs_clarification"])

        self.profile_builder.apply(session, analysis)
        self._persist_extracted_competencies(session, analysis)
        next_field = self.questions.next_field(session)
        session.current_field = next_field
        session.status = "complete" if next_field is None else "active"
        question = self.questions.question_for(next_field, session.language)
        session.history.append(
            {
                "role": "assistant",
                "field": next_field,
                "content": question,
                "timestamp": utc_now_iso(),
            }
        )
        self.sessions.update(session)
        return self._response(session, question, analysis, [])

    def _get_or_create_active_session(self, user_id: str, role: str, language: str) -> DynamicInterviewSession:
        for session in self.sessions.list():
            if session.user_id == user_id and session.status == "active":
                return session
        session = DynamicInterviewSession(user_id=user_id, role=role, language=_normalize_language(language))
        return self.sessions.add(session)

    def _persist_extracted_competencies(self, session: DynamicInterviewSession, analysis: AnswerAnalysis) -> None:
        if self.competency_service is None:
            return
        for competency_name in analysis.extracted_competencies:
            self.competency_service.add_user_competency(
                user_id=session.user_id,
                competency_name=competency_name,
                source="self_declared",
                confidence_score=0.45,
                evidence_reference=f"dynamic_interview:{session.id}:{analysis.field}",
            )

    @staticmethod
    def _response(
        session: DynamicInterviewSession,
        question: str,
        analysis: AnswerAnalysis | None,
        warnings: list[str],
    ) -> dict[str, Any]:
        return {
            "session": session.to_dict(),
            "question": question,
            "one_question_per_step": question.count("?") <= 1,
            "analysis": None
            if analysis is None
            else {
                "field": analysis.field,
                "extracted_competencies": analysis.extracted_competencies,
                "contradictions": analysis.contradictions,
                "warnings": analysis.warnings,
            },
            "warnings": warnings,
        }


def _clean_answer(answer: str) -> str:
    return re.sub(r"\s+", " ", (answer or "").strip())


def _has_value(value: Any) -> bool:
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return value not in (None, "", False)


def _normalize_language(language: str) -> str:
    return language if language in QUESTIONS else "en"
