"""Config-neutral matching helpers."""

from core.models import Candidate, Match, Vacancy


def score_candidate_for_vacancy(candidate: Candidate, vacancy: Vacancy) -> Match:
    score = 0.0
    reasons: list[str] = []

    if candidate.profession_code == vacancy.profession_code:
        score += 0.5
        reasons.append("profession_match")

    shared_languages = set(candidate.languages) & set(vacancy.required_languages)
    if shared_languages:
        score += 0.3
        reasons.append("language_match")

    if candidate.country_code == vacancy.country_code:
        score += 0.2
        reasons.append("same_target_country")

    return Match(
        candidate_id=candidate.id,
        vacancy_id=vacancy.id,
        score=round(score, 2),
        reasons=reasons,
    )

