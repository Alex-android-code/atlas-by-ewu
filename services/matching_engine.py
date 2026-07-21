"""Explainable AI Matching Engine v1 for ATLAS.

The engine is deterministic by default: AI may enrich recommendations later,
but it never changes profiles, rejects candidates, hires candidates, or sends
offers. Every score is component-based and explainable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models import ActivityEvent, Candidate, Match, ProfessionalDNA, Vacancy, new_id, utc_now_iso
from database.repositories import ActivityRepository, CandidateRepository, MatchRepository, ProfessionalDNARepository, VacancyRepository


PROTECTED_FIELDS = {
    "age",
    "birth_date",
    "birthDate",
    "gender",
    "sex",
    "photo",
    "profile_photo",
    "nationality",
    "religion",
    "marital_status",
    "maritalStatus",
    "political_views",
    "politicalViews",
    "pregnancy",
    "disability",
}
RECOMMENDATION_LEVELS = [
    (95, "strong_match", "Strong Match"),
    (85, "recommended", "Recommended"),
    (70, "worth_review", "Worth Review"),
    (50, "weak_match", "Weak Match"),
    (0, "not_recommended", "Not Recommended"),
]
COMPONENT_WEIGHTS = {
    "profession": 14,
    "skills": 15,
    "experience": 10,
    "education": 6,
    "credentials": 8,
    "languages": 10,
    "work_authorization": 7,
    "location": 8,
    "salary": 8,
    "availability": 5,
    "schedule": 4,
    "contract": 3,
    "professional_dna": 2,
}


@dataclass
class NormalizedProfile:
    candidate_id: str
    user_id: str
    profession_keys: set[str]
    profession_label: str
    skills: set[str]
    years_experience: int
    education: set[str]
    credentials: set[str]
    languages: dict[str, str]
    work_authorization: set[str]
    countries: set[str]
    salary_expectation: float | None
    salary_currency: str
    availability: str
    relocation: set[str]
    schedule: set[str]
    contract_types: set[str]
    dna: dict[str, Any]
    ignored_protected_fields: list[str]


@dataclass
class NormalizedVacancy:
    vacancy_id: str
    company_id: str
    title: str
    profession_key: str
    profession_label: str
    skills_required: set[str]
    skills_preferred: set[str]
    experience_minimum_years: int
    education_required: set[str]
    credentials_required: set[str]
    languages_required: dict[str, str]
    work_authorization: set[str]
    location_countries: set[str]
    remote: bool
    salary_minimum: float | None
    salary_maximum: float | None
    salary_currency: str
    target_start_date: str
    schedule: set[str]
    contract_types: set[str]
    dna_requirements: dict[str, Any]


class ProfileNormalizer:
    def normalize(self, candidate: Candidate, profile: ProfessionalDNA | None = None) -> NormalizedProfile:
        metadata = candidate.metadata or {}
        dna = profile.to_dict() if profile else {}
        ignored = [field for field in PROTECTED_FIELDS if field in metadata or field in dna]
        profession_values = _text_set(
            [
                candidate.profession_code,
                metadata.get("profession"),
                *(dna.get("preferred_roles") or []),
                dna.get("professional_summary"),
            ]
        )
        skills = _text_set(candidate.metadata.get("skills")) | _text_set(dna.get("skills"))
        credentials = _text_set(candidate.documents) | _text_set(dna.get("certificates")) | _text_set(dna.get("licenses"))
        languages = _languages(candidate.languages, dna.get("languages"))
        countries = _text_set([candidate.country_code, metadata.get("desired_country_code"), *(dna.get("preferred_countries") or [])])
        salary = metadata.get("desired_salary") or (dna.get("salary_expectations") or {}).get("expected")
        return NormalizedProfile(
            candidate_id=candidate.id,
            user_id=candidate.user_id or candidate.id,
            profession_keys=profession_values,
            profession_label=metadata.get("profession") or candidate.profession_code,
            skills=skills,
            years_experience=max(candidate.years_of_experience, len(dna.get("work_experience") or [])),
            education=_text_set(dna.get("education")),
            credentials=credentials,
            languages=languages,
            work_authorization=_text_set(metadata.get("work_authorization") or metadata.get("workAuthorization")),
            countries=countries,
            salary_expectation=_safe_float(salary),
            salary_currency=str(metadata.get("salary_currency") or (dna.get("salary_expectations") or {}).get("currency") or "").upper(),
            availability=str(metadata.get("availability") or metadata.get("ready_from") or ""),
            relocation=_text_set(metadata.get("relocation") or (dna.get("relocation_preferences") or {}).get("countries")),
            schedule=_text_set(metadata.get("schedule") or dna.get("employment_format")),
            contract_types=_text_set(metadata.get("contract_types") or dna.get("employment_format")),
            dna=dna,
            ignored_protected_fields=ignored,
        )


class VacancyNormalizer:
    def normalize(self, vacancy: Vacancy) -> NormalizedVacancy:
        data = vacancy.metadata.get("recruitment") if isinstance(vacancy.metadata.get("recruitment"), dict) else {}
        requirements = data.get("requirements") or []
        preferred = data.get("preferredQualifications") or []
        return NormalizedVacancy(
            vacancy_id=vacancy.id,
            company_id=data.get("companyId") or vacancy.employer_id,
            title=data.get("title") or vacancy.title,
            profession_key=_norm(data.get("normalizedProfessionKey") or vacancy.profession_code or vacancy.title),
            profession_label=data.get("professionLabel") or vacancy.title,
            skills_required=_requirement_set(requirements, {"skill", "other"}) | _text_set(data.get("skillRequirements")),
            skills_preferred=_requirement_set(preferred, {"skill", "other"}),
            experience_minimum_years=int(data.get("experienceMinimumYears") or _max_requirement_years(requirements)),
            education_required=_requirement_set(requirements, {"education"}),
            credentials_required=_requirement_set(requirements, {"certificate", "license", "work_authorization"}) | _text_set(data.get("credentialRequirements")),
            languages_required=_languages([], data.get("languageRequirements")),
            work_authorization=_text_set(data.get("workAuthorizationRequirements")),
            location_countries=_text_set(data.get("remoteCountries") or data.get("locationCountries") or [vacancy.country_code]),
            remote="remote" in _text_set(data.get("workModes")),
            salary_minimum=_safe_float((data.get("salary") or {}).get("minimum") or vacancy.salary_min),
            salary_maximum=_safe_float((data.get("salary") or {}).get("maximum") or vacancy.salary_max),
            salary_currency=str((data.get("salary") or {}).get("currency") or vacancy.currency or "").upper(),
            target_start_date=str(data.get("targetStartDate") or ""),
            schedule=_text_set((data.get("schedule") or {}).values() if isinstance(data.get("schedule"), dict) else data.get("schedule")),
            contract_types=_text_set(data.get("employmentTypes")),
            dna_requirements=data.get("professionalDnaRequirements") if isinstance(data.get("professionalDnaRequirements"), dict) else {},
        )


class ComponentMatcher:
    name = "component"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        raise NotImplementedError

    def result(self, score: int, positives: list[str] | None = None, risks: list[str] | None = None, recommendations: list[str] | None = None) -> dict[str, Any]:
        return {
            "component": self.name,
            "score": max(0, min(100, round(score))),
            "positives": positives or [],
            "risks": risks or [],
            "recommendations": recommendations or [],
        }


class ProfessionMatcher(ComponentMatcher):
    name = "profession"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if vacancy.profession_key in profile.profession_keys:
            return self.result(100, [f"Profession matches {vacancy.profession_label}"])
        if any(vacancy.profession_key in item or item in vacancy.profession_key for item in profile.profession_keys):
            return self.result(75, [f"Profession is related to {vacancy.profession_label}"])
        return self.result(20, risks=[f"Profile profession does not clearly match {vacancy.profession_label}"], recommendations=["Add target profession to profile if relevant"])


class SkillsMatcher(ComponentMatcher):
    name = "skills"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        required = vacancy.skills_required
        if not required:
            return self.result(80, ["No strict skill list in vacancy"])
        matched = required & profile.skills
        score = int((len(matched) / len(required)) * 100)
        missing = sorted(required - matched)
        positives = [f"{len(matched)} required skill(s) matched"] if matched else []
        risks = [f"Missing skill: {item}" for item in missing[:4]]
        return self.result(score, positives, risks, ["Confirm missing skills with evidence"] if missing else [])


class ExperienceMatcher(ComponentMatcher):
    name = "experience"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        minimum = vacancy.experience_minimum_years
        if minimum <= 0:
            return self.result(85, ["No minimum experience required"])
        if profile.years_experience >= minimum:
            return self.result(100, [f"{profile.years_experience} years experience meets minimum {minimum}"])
        ratio = profile.years_experience / minimum
        return self.result(int(ratio * 80), risks=[f"{profile.years_experience} years vs required {minimum}"], recommendations=["Add verified experience evidence"])


class EducationMatcher(ComponentMatcher):
    name = "education"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if not vacancy.education_required:
            return self.result(85, ["No strict education requirement"])
        matched = profile.education & vacancy.education_required
        return self.result(100 if matched else 45, [f"Education matched: {', '.join(sorted(matched))}"] if matched else [], [f"Education requirement not confirmed: {', '.join(sorted(vacancy.education_required))}"] if not matched else [])


class CredentialsMatcher(ComponentMatcher):
    name = "credentials"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if not vacancy.credentials_required:
            return self.result(85, ["No required credentials listed"])
        matched = profile.credentials & vacancy.credentials_required
        missing = vacancy.credentials_required - matched
        return self.result(int((len(matched) / len(vacancy.credentials_required)) * 100), [f"Credential confirmed: {item}" for item in sorted(matched)], [f"Missing credential: {item}" for item in sorted(missing)], ["Upload or verify missing credential"] if missing else [])


class LanguageMatcher(ComponentMatcher):
    name = "languages"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if not vacancy.languages_required:
            return self.result(85, ["No strict language requirement"])
        matched = [lang for lang in vacancy.languages_required if lang in profile.languages]
        score = int((len(matched) / len(vacancy.languages_required)) * 100)
        missing = sorted(set(vacancy.languages_required) - set(matched))
        return self.result(score, [f"Language matched: {lang.upper()}" for lang in matched], [f"Missing language: {lang.upper()}" for lang in missing], ["Confirm language level"] if missing else [])


class WorkAuthorizationMatcher(ComponentMatcher):
    name = "work_authorization"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if not vacancy.work_authorization:
            return self.result(80, ["No explicit work authorization requirement"])
        matched = profile.work_authorization & vacancy.work_authorization
        return self.result(100 if matched else 30, ["Work authorization confirmed"] if matched else [], ["Work authorization not confirmed"] if not matched else [], ["Add work authorization document"] if not matched else [])


class LocationMatcher(ComponentMatcher):
    name = "location"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if vacancy.remote:
            return self.result(95, ["Remote work mode available"])
        if profile.countries & vacancy.location_countries:
            return self.result(100, ["Candidate country matches vacancy location"])
        if profile.relocation & vacancy.location_countries:
            return self.result(75, ["Relocation preference matches vacancy country"], risks=["Relocation required"])
        return self.result(45, risks=["Location does not match current or preferred countries"], recommendations=["Add relocation countries if open to move"])


class SalaryMatcher(ComponentMatcher):
    name = "salary"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if profile.salary_expectation is None or not vacancy.salary_maximum:
            return self.result(75, ["Salary comparison needs confirmation"])
        if profile.salary_currency and vacancy.salary_currency and profile.salary_currency != vacancy.salary_currency:
            return self.result(60, risks=["Salary currencies differ; no FX conversion applied"])
        if profile.salary_expectation <= vacancy.salary_maximum:
            return self.result(100, ["Salary expectation fits vacancy range"])
        gap = profile.salary_expectation - vacancy.salary_maximum
        score = max(25, 100 - int((gap / max(vacancy.salary_maximum, 1)) * 100))
        return self.result(score, risks=[f"Salary expectation is {gap:g} above vacancy maximum"], recommendations=["Adjust salary expectation or negotiate range"])


class AvailabilityMatcher(ComponentMatcher):
    name = "availability"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if not profile.availability or not vacancy.target_start_date:
            return self.result(75, ["Availability needs confirmation"])
        return self.result(85, ["Availability provided for recruiter review"])


class ScheduleMatcher(ComponentMatcher):
    name = "schedule"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if not vacancy.schedule or not profile.schedule:
            return self.result(75, ["Schedule compatibility needs confirmation"])
        matched = profile.schedule & vacancy.schedule
        return self.result(100 if matched else 55, ["Schedule preference matches"] if matched else [], ["Schedule preference may differ"] if not matched else [])


class ContractMatcher(ComponentMatcher):
    name = "contract"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        if not vacancy.contract_types or not profile.contract_types:
            return self.result(75, ["Contract type needs confirmation"])
        matched = profile.contract_types & vacancy.contract_types
        return self.result(100 if matched else 55, ["Contract type matches"] if matched else [], ["Contract type preference differs"] if not matched else [])


class ProfessionalDNAMatcher(ComponentMatcher):
    name = "professional_dna"

    def score(self, profile: NormalizedProfile, vacancy: NormalizedVacancy) -> dict[str, Any]:
        completeness = int(profile.dna.get("profile_completeness") or 0)
        if not profile.dna:
            return self.result(60, risks=["Professional DNA is not completed"], recommendations=["Complete Professional DNA to improve match confidence"])
        return self.result(min(100, 55 + completeness // 2), [f"Professional DNA completeness {completeness}%"])


class ExplainabilityEngine:
    def explain(self, components: dict[str, dict[str, Any]], overall: int) -> dict[str, Any]:
        positives: list[str] = []
        risks: list[str] = []
        recommendations: list[str] = []
        for result in components.values():
            positives.extend(result.get("positives", []))
            risks.extend(result.get("risks", []))
            recommendations.extend(result.get("recommendations", []))
        return {
            "summary": f"Overall Match: {overall}%",
            "componentScores": {key: value["score"] for key, value in components.items()},
            "positiveReasons": positives[:10],
            "risks": risks[:10],
            "recommendations": _dedupe(recommendations)[:8],
            "humanDecisionRequired": True,
            "humanReview": {"status": "pending", "allowedActions": ["review", "shortlist", "invite", "reject_with_reason"], "aiFinalDecision": False},
        }


class RecommendationEngine:
    def level(self, score: int) -> dict[str, str]:
        for threshold, code, label in RECOMMENDATION_LEVELS:
            if score >= threshold:
                return {"code": code, "label": label}
        return {"code": "not_recommended", "label": "Not Recommended"}


@dataclass
class MatchingEngineService:
    candidates: CandidateRepository
    vacancies: VacancyRepository
    profiles: ProfessionalDNARepository
    matches: MatchRepository
    activity: ActivityRepository
    profile_normalizer: ProfileNormalizer | None = None
    vacancy_normalizer: VacancyNormalizer | None = None
    explainability: ExplainabilityEngine | None = None
    recommendations: RecommendationEngine | None = None

    def __post_init__(self) -> None:
        self.profile_normalizer = self.profile_normalizer or ProfileNormalizer()
        self.vacancy_normalizer = self.vacancy_normalizer or VacancyNormalizer()
        self.explainability = self.explainability or ExplainabilityEngine()
        self.recommendations = self.recommendations or RecommendationEngine()
        self.component_matchers: list[ComponentMatcher] = [
            ProfessionMatcher(),
            SkillsMatcher(),
            ExperienceMatcher(),
            EducationMatcher(),
            CredentialsMatcher(),
            LanguageMatcher(),
            WorkAuthorizationMatcher(),
            LocationMatcher(),
            SalaryMatcher(),
            AvailabilityMatcher(),
            ScheduleMatcher(),
            ContractMatcher(),
            ProfessionalDNAMatcher(),
        ]

    def run(self, candidate_id: str | None = None, vacancy_id: str | None = None, limit: int = 100, actor_id: str = "system") -> dict[str, Any]:
        candidates = [self._candidate(candidate_id)] if candidate_id else self.candidates.list()
        vacancies = [self._vacancy(vacancy_id)] if vacancy_id else self._published_vacancies()
        results: list[dict[str, Any]] = []
        for vacancy in vacancies[:limit]:
            for candidate in candidates[:limit]:
                results.append(self._match(candidate, vacancy, actor_id))
        analytics = self._analytics(results)
        self._audit(actor_id, "matching_run_completed", {"candidate_id": candidate_id, "vacancy_id": vacancy_id, "count": len(results), "average_score": analytics["averageMatch"]})
        return {"runId": new_id("MRUN"), "status": "completed", "count": len(results), "matches": results, "analytics": analytics, "scaling": {"mode": "sync_v1", "supportsAsyncRecalculate": True, "cacheKeyStrategy": "candidate:v:profile_updated_at|vacancy:v:updatedAt", "indexKeys": ["candidate_id", "vacancy_id", "score", "recommendation", "updated_at"]}}

    def get(self, match_id: str) -> dict[str, Any]:
        match = self.matches.get(match_id)
        if not match:
            raise ValueError("Match not found")
        return self._match_response(match)

    def explanation(self, match_id: str) -> dict[str, Any]:
        match = self.get(match_id)
        return match["explanation"]

    def recalculate(self, match_id: str, actor_id: str = "system") -> dict[str, Any]:
        existing = self.matches.get(match_id)
        if not existing:
            raise ValueError("Match not found")
        recalculated = self._match(self._candidate(existing.candidate_id), self._vacancy(existing.vacancy_id), actor_id, existing_match=existing)
        self._audit(actor_id, "matching_recalculated", {"match_id": match_id, "candidate_id": existing.candidate_id, "vacancy_id": existing.vacancy_id})
        return recalculated

    def _match(self, candidate: Candidate, vacancy: Vacancy, actor_id: str, existing_match: Match | None = None) -> dict[str, Any]:
        profile = next((item for item in self.profiles.list() if item.user_id == candidate.user_id), None)
        normalized_profile = self.profile_normalizer.normalize(candidate, profile) if self.profile_normalizer else ProfileNormalizer().normalize(candidate, profile)
        normalized_vacancy = self.vacancy_normalizer.normalize(vacancy) if self.vacancy_normalizer else VacancyNormalizer().normalize(vacancy)
        components = {matcher.name: matcher.score(normalized_profile, normalized_vacancy) for matcher in self.component_matchers}
        overall = _weighted_score(components)
        explanation = self.explainability.explain(components, overall) if self.explainability else ExplainabilityEngine().explain(components, overall)
        recommendation = self.recommendations.level(overall) if self.recommendations else RecommendationEngine().level(overall)
        metadata = {
            "engine": "matching_engine_v1",
            "component_scores": components,
            "explanation": explanation,
            "recommendation": recommendation,
            "biasProtection": {"protectedFieldsIgnored": normalized_profile.ignored_protected_fields, "protectedFieldsUsed": []},
            "humanReview": explanation["humanReview"],
            "candidateRecommendations": _candidate_recommendations(explanation),
            "employerView": {"score": overall, "strengths": explanation["positiveReasons"], "risks": explanation["risks"], "recommendations": explanation["recommendations"]},
            "candidateView": {"whyThisFits": explanation["positiveReasons"][:5], "whatToImprove": explanation["recommendations"][:5], "biggestBoost": (explanation["recommendations"] or ["Keep profile updated"])[0]},
            "updated_at": utc_now_iso(),
        }
        reasons = explanation["positiveReasons"] + explanation["risks"]
        if existing_match:
            existing_match.score = overall
            existing_match.reasons = reasons
            existing_match.metadata = {**existing_match.metadata, **metadata, "recalculated_at": utc_now_iso()}
            saved = self.matches.update(existing_match)
        else:
            duplicate = self._existing(candidate.id, vacancy.id)
            if duplicate:
                duplicate.score = overall
                duplicate.reasons = reasons
                duplicate.metadata = {**duplicate.metadata, **metadata, "recalculated_at": utc_now_iso()}
                saved = self.matches.update(duplicate)
            else:
                saved = self.matches.add(Match(candidate_id=candidate.id, vacancy_id=vacancy.id, score=overall, reasons=reasons, metadata=metadata))
        return self._match_response(saved)

    def _match_response(self, match: Match) -> dict[str, Any]:
        return {
            "id": match.id,
            "candidateId": match.candidate_id,
            "vacancyId": match.vacancy_id,
            "score": match.score,
            "recommendation": match.metadata.get("recommendation", {}),
            "explanation": match.metadata.get("explanation", {}),
            "componentScores": match.metadata.get("component_scores", {}),
            "biasProtection": match.metadata.get("biasProtection", {}),
            "humanReview": match.metadata.get("humanReview", {}),
            "employerView": match.metadata.get("employerView", {}),
            "candidateView": match.metadata.get("candidateView", {}),
            "metadata": {"engine": match.metadata.get("engine"), "updated_at": match.metadata.get("updated_at")},
        }

    def _published_vacancies(self) -> list[Vacancy]:
        return [vacancy for vacancy in self.vacancies.list() if vacancy.status in {"published", "open"} or (vacancy.metadata.get("recruitment") or {}).get("status") == "published"]

    def _candidate(self, candidate_id: str | None) -> Candidate:
        if not candidate_id:
            raise ValueError("candidate_id is required")
        candidate = self.candidates.get(candidate_id)
        if not candidate:
            for item in self.candidates.list():
                if item.user_id == candidate_id:
                    return item
            raise ValueError("Candidate not found")
        return candidate

    def _vacancy(self, vacancy_id: str | None) -> Vacancy:
        if not vacancy_id:
            raise ValueError("vacancy_id is required")
        vacancy = self.vacancies.get(vacancy_id)
        if not vacancy:
            raise ValueError("Vacancy not found")
        return vacancy

    def _existing(self, candidate_id: str, vacancy_id: str) -> Match | None:
        return next((item for item in self.matches.list() if item.candidate_id == candidate_id and item.vacancy_id == vacancy_id and item.metadata.get("engine") == "matching_engine_v1"), None)

    def _analytics(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        if not results:
            return {"averageMatch": 0, "recommendationCounts": {}, "successfulHires": 0, "algorithmPrecision": None, "timeToHireDays": None}
        counts: dict[str, int] = {}
        for item in results:
            code = item.get("recommendation", {}).get("code", "unknown")
            counts[code] = counts.get(code, 0) + 1
        return {"averageMatch": round(sum(item["score"] for item in results) / len(results), 2), "recommendationCounts": counts, "successfulHires": 0, "recommendationOverrides": 0, "algorithmPrecision": None, "timeToHireDays": None}

    def _audit(self, actor_id: str, action: str, metadata: dict[str, Any]) -> None:
        self.activity.add(ActivityEvent(entity_type="matching", entity_id=metadata.get("match_id") or metadata.get("vacancy_id") or metadata.get("candidate_id") or "matching", action=action, old_value=None, new_value="matching_engine_v1", actor_id=actor_id, metadata=metadata))


def _weighted_score(components: dict[str, dict[str, Any]]) -> int:
    total_weight = sum(COMPONENT_WEIGHTS.values())
    total = sum(components[key]["score"] * COMPONENT_WEIGHTS.get(key, 1) for key in components)
    return round(total / total_weight) if total_weight else 0


def _candidate_recommendations(explanation: dict[str, Any]) -> list[str]:
    return explanation.get("recommendations", [])[:5]


def _requirement_set(requirements: list[dict[str, Any]], categories: set[str]) -> set[str]:
    return {_norm(item.get("normalizedKey") or item.get("label")) for item in requirements if item.get("category") in categories and item.get("required", True) and _norm(item.get("normalizedKey") or item.get("label"))}


def _max_requirement_years(requirements: list[dict[str, Any]]) -> int:
    values = [int(item.get("minimumYears") or 0) for item in requirements if item.get("category") == "experience"]
    return max(values) if values else 0


def _languages(candidate_languages: list[Any], dna_languages: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in candidate_languages or []:
        result[_norm(item)] = "unknown"
    if isinstance(dna_languages, list):
        for item in dna_languages:
            if isinstance(item, dict):
                name = _norm(item.get("name") or item.get("language") or item.get("label"))
                if name:
                    result[name] = str(item.get("level") or "unknown").lower()
            elif _norm(item):
                result[_norm(item)] = "unknown"
    return result


def _text_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, dict):
        return {_norm(item) for item in value.values() if _norm(item)}
    if isinstance(value, (list, tuple, set)):
        result: set[str] = set()
        for item in value:
            if isinstance(item, dict):
                result |= _text_set(item)
            elif _norm(item):
                result.add(_norm(item))
        return result
    if isinstance(value, str):
        separators = [",", ";", "|", "/"]
        parts = [value]
        for separator in separators:
            if separator in value:
                parts = value.split(separator)
                break
        return {_norm(item) for item in parts if _norm(item)}
    return {_norm(value)} if _norm(value) else set()


def _norm(value: Any) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in str(value or "").strip()).strip("_")


def _safe_float(value: Any) -> float | None:
    try:
        if value in {None, ""}:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result
