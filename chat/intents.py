"""Prepared public chat intent constants.

These constants are deterministic foundations for future AI classification.
They do not perform full extraction or matching.
"""

from enum import StrEnum


class ChatIntent(StrEnum):
    CANDIDATE_JOB_SEARCH = "candidate_job_search"
    EMPLOYER_HIRING = "employer_hiring"
    COURSE_INTEREST = "course_interest"
    LEGALIZATION_HELP = "legalization_help"
    INSURANCE_HELP = "insurance_help"
    HOUSING_HELP = "housing_help"
    RELOCATION_HELP = "relocation_help"
    PARTNER_COOPERATION = "partner_cooperation"
    GENERAL_CONSULTATION = "general_consultation"
    UNKNOWN = "unknown"


SCENARIO_TO_INTENT = {
    "candidate": ChatIntent.CANDIDATE_JOB_SEARCH,
    "employer": ChatIntent.EMPLOYER_HIRING,
    "legalization": ChatIntent.LEGALIZATION_HELP,
    "business": ChatIntent.PARTNER_COOPERATION,
    "consultation": ChatIntent.GENERAL_CONSULTATION,
}
