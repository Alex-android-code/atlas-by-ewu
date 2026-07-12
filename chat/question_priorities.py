"""Deterministic next-question priorities for public ATLAS chat."""

from __future__ import annotations

from typing import Any

from .intents import ChatIntent


CANDIDATE_PRIORITY = [
    "skills",
    "currentLocation",
    "experience",
    "documentsLegalStatus",
    "preferredContactMethod",
    "phoneOrContact",
    "drivingLicense",
    "certificates",
    "relocationReadiness",
    "preferredDestination",
    "learningReadiness",
    "desiredSalary",
    "startAvailability",
    "accommodationNeed",
    "photoUpload",
    "documentUpload",
]

EMPLOYER_PRIORITY = [
    "workLocation",
    "workersCount",
    "requiredSkills",
    "salaryOrRate",
    "contractType",
    "workingHours",
    "accommodationProvided",
    "startDate",
    "trainingPossibility",
    "companyName",
    "contactPerson",
    "phoneOrEmail",
    "nipOrRegon",
]

LEGALIZATION_PRIORITY = [
    "currentCountry",
    "nationality",
    "currentDocument",
    "documentExpiryDate",
    "applicationSubmitted",
    "hasConfirmation",
    "hasWorkContract",
    "urgency",
    "contact",
]

COURSE_PRIORITY = [
    "currentCity",
    "desiredProfessionOrSkill",
    "experienceLevel",
    "trainingBudget",
    "onlineOfflinePreference",
    "readinessDate",
    "contact",
]

INSURANCE_PRIORITY = [
    "country",
    "userOrFamily",
    "insurancePurpose",
    "duration",
    "startDate",
    "budget",
    "contact",
]

HOUSING_PRIORITY = [
    "onePersonFamilyOrGroup",
    "housingType",
    "budget",
    "moveInDate",
    "duration",
    "contact",
]

QUESTION_PRIORITIES = {
    ChatIntent.CANDIDATE_JOB_SEARCH: CANDIDATE_PRIORITY,
    ChatIntent.EMPLOYER_HIRING: EMPLOYER_PRIORITY,
    ChatIntent.LEGALIZATION_HELP: LEGALIZATION_PRIORITY,
    ChatIntent.COURSE_INTEREST: COURSE_PRIORITY,
    ChatIntent.INSURANCE_HELP: INSURANCE_PRIORITY,
    ChatIntent.HOUSING_HELP: HOUSING_PRIORITY,
}

QUESTIONS = {
    "ru": {
        "candidate_job_search.skills": "\u0420\u0430\u0441\u0441\u043a\u0430\u0436\u0438\u0442\u0435, \u043a\u0430\u043a\u0443\u044e \u0440\u0430\u0431\u043e\u0442\u0443 \u0432\u044b \u0438\u0449\u0435\u0442\u0435 \u0438 \u0447\u0442\u043e \u0443\u043c\u0435\u0435\u0442\u0435 \u0434\u0435\u043b\u0430\u0442\u044c.",
        "candidate_job_search.currentLocation": "\u0413\u0434\u0435 \u0432\u044b \u0441\u0435\u0439\u0447\u0430\u0441 \u043d\u0430\u0445\u043e\u0434\u0438\u0442\u0435\u0441\u044c?",
        "candidate_job_search.experience": "\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u043f\u0440\u0438\u043c\u0435\u0440\u043d\u043e \u043b\u0435\u0442 \u0443 \u0432\u0430\u0441 \u0442\u0430\u043a\u043e\u0433\u043e \u043e\u043f\u044b\u0442\u0430?",
        "candidate_job_search.documentsLegalStatus": "\u041a\u0430\u043a\u0438\u0435 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b \u0443 \u0432\u0430\u0441 \u0441\u0435\u0439\u0447\u0430\u0441 \u0435\u0441\u0442\u044c?",
        "candidate_job_search.preferredContactMethod": "\u041a\u0430\u043a \u0432\u0430\u043c \u0443\u0434\u043e\u0431\u043d\u0435\u0435 \u0441\u0432\u044f\u0437\u0430\u0442\u044c\u0441\u044f?",
        "candidate_job_search.phoneOrContact": "\u041a\u0430\u043a\u043e\u0439 \u043d\u043e\u043c\u0435\u0440 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430 \u0438\u043b\u0438 \u043a\u043e\u043d\u0442\u0430\u043a\u0442 \u043c\u043e\u0436\u043d\u043e \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c?",
        "candidate_job_search.drivingLicense": "\u0415\u0441\u0442\u044c \u043b\u0438 \u0443 \u0432\u0430\u0441 \u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0435 \u043f\u0440\u0430\u0432\u0430?",
        "candidate_job_search.certificates": "\u0415\u0441\u0442\u044c \u043b\u0438 \u0443 \u0432\u0430\u0441 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u044b \u043f\u043e \u044d\u0442\u043e\u0439 \u0440\u0430\u0431\u043e\u0442\u0435?",
        "candidate_job_search.relocationReadiness": "\u0413\u043e\u0442\u043e\u0432\u044b \u043b\u0438 \u0432\u044b \u043a \u043f\u0435\u0440\u0435\u0435\u0437\u0434\u0443?",
        "candidate_job_search.preferredDestination": "\u0412 \u043a\u0430\u043a\u043e\u0439 \u0441\u0442\u0440\u0430\u043d\u0435 \u0432\u044b \u0445\u043e\u0442\u0435\u043b\u0438 \u0431\u044b \u0440\u0430\u0431\u043e\u0442\u0430\u0442\u044c?",
        "candidate_job_search.learningReadiness": "\u0413\u043e\u0442\u043e\u0432\u044b \u043b\u0438 \u0432\u044b \u043f\u0440\u0438 \u043d\u0443\u0436\u0434\u0435 \u043f\u0440\u043e\u0439\u0442\u0438 \u043a\u043e\u0440\u043e\u0442\u043a\u043e\u0435 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u0435?",
        "candidate_job_search.desiredSalary": "\u041a\u0430\u043a\u0430\u044f \u0441\u0442\u0430\u0432\u043a\u0430 \u0438\u043b\u0438 \u0437\u0430\u0440\u043f\u043b\u0430\u0442\u0430 \u0432\u0430\u043c \u043f\u043e\u0434\u0445\u043e\u0434\u0438\u0442?",
        "candidate_job_search.startAvailability": "\u041a\u043e\u0433\u0434\u0430 \u0432\u044b \u0433\u043e\u0442\u043e\u0432\u044b \u043d\u0430\u0447\u0430\u0442\u044c?",
        "candidate_job_search.accommodationNeed": "\u041d\u0443\u0436\u043d\u043e \u043b\u0438 \u0432\u0430\u043c \u0436\u0438\u043b\u044c\u0435?",
        "candidate_job_search.photoUpload": "\u041c\u043e\u0436\u043d\u043e \u043b\u0438 \u0431\u0443\u0434\u0435\u0442 \u043f\u043e\u0437\u0436\u0435 \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0444\u043e\u0442\u043e \u0434\u043b\u044f \u043f\u0440\u043e\u0444\u0438\u043b\u044f?",
        "candidate_job_search.documentUpload": "\u0413\u043e\u0442\u043e\u0432\u044b \u043b\u0438 \u0432\u044b \u043f\u043e\u0437\u0436\u0435 \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0444\u0430\u0439\u043b\u044b \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u043e\u0432?",
        "employer_hiring.workLocation": "\u0413\u0434\u0435 \u0431\u0443\u0434\u0435\u0442 \u0440\u0430\u0431\u043e\u0442\u0430?",
        "employer_hiring.workersCount": "\u0421\u043a\u043e\u043b\u044c\u043a\u043e \u043b\u044e\u0434\u0435\u0439 \u043d\u0443\u0436\u043d\u043e?",
        "employer_hiring.requiredSkills": "\u041a\u0430\u043a\u0438\u0435 \u043d\u0430\u0432\u044b\u043a\u0438 \u0432\u0430\u0436\u043d\u044b \u0434\u043b\u044f \u044d\u0442\u043e\u0439 \u0440\u0430\u0431\u043e\u0442\u044b?",
        "employer_hiring.salaryOrRate": "\u041a\u0430\u043a\u0443\u044e \u0441\u0442\u0430\u0432\u043a\u0443 \u0438\u043b\u0438 \u0437\u0430\u0440\u043f\u043b\u0430\u0442\u0443 \u0432\u044b \u043f\u0440\u0435\u0434\u043b\u0430\u0433\u0430\u0435\u0442\u0435?",
        "employer_hiring.contractType": "\u041a\u0430\u043a\u043e\u0439 \u0442\u0438\u043f \u0434\u043e\u0433\u043e\u0432\u043e\u0440\u0430 \u043f\u043b\u0430\u043d\u0438\u0440\u0443\u0435\u0442\u0441\u044f?",
        "employer_hiring.workingHours": "\u041a\u0430\u043a\u043e\u0439 \u0433\u0440\u0430\u0444\u0438\u043a \u0440\u0430\u0431\u043e\u0442\u044b?",
        "employer_hiring.accommodationProvided": "\u0412\u044b \u043f\u0440\u0435\u0434\u043e\u0441\u0442\u0430\u0432\u043b\u044f\u0435\u0442\u0435 \u0436\u0438\u043b\u044c\u0435?",
        "employer_hiring.startDate": "\u041a\u043e\u0433\u0434\u0430 \u043b\u044e\u0434\u0438 \u0434\u043e\u043b\u0436\u043d\u044b \u0432\u044b\u0439\u0442\u0438 \u043d\u0430 \u0440\u0430\u0431\u043e\u0442\u0443?",
        "employer_hiring.trainingPossibility": "\u0413\u043e\u0442\u043e\u0432\u044b \u043b\u0438 \u0432\u044b \u043e\u0431\u0443\u0447\u0438\u0442\u044c \u043d\u043e\u0432\u044b\u0445 \u043b\u044e\u0434\u0435\u0439 \u043d\u0430 \u043c\u0435\u0441\u0442\u0435?",
        "employer_hiring.companyName": "\u041a\u0430\u043a \u043d\u0430\u0437\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u0432\u0430\u0448\u0430 \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u044f?",
        "employer_hiring.contactPerson": "\u041a \u043a\u043e\u043c\u0443 \u043c\u043e\u0436\u0435\u0442 \u043e\u0431\u0440\u0430\u0442\u0438\u0442\u044c\u0441\u044f \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u043e\u0440?",
        "employer_hiring.phoneOrEmail": "\u041a\u0430\u043a\u043e\u0439 \u0442\u0435\u043b\u0435\u0444\u043e\u043d \u0438\u043b\u0438 email \u0443\u0434\u043e\u0431\u043d\u043e \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c?",
        "employer_hiring.nipOrRegon": "\u041c\u043e\u0436\u0435\u0442\u0435 \u0443\u043a\u0430\u0437\u0430\u0442\u044c NIP, REGON \u0438\u043b\u0438 \u043d\u043e\u043c\u0435\u0440 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438?",
        "legalization_help.currentCountry": "\u041e\u043f\u0438\u0448\u0438\u0442\u0435 \u043a\u043e\u0440\u043e\u0442\u043a\u043e, \u043a\u0430\u043a\u0430\u044f \u0443 \u0432\u0430\u0441 \u0441\u0438\u0442\u0443\u0430\u0446\u0438\u044f \u0441 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430\u043c\u0438.",
        "course_interest.currentCity": "\u0420\u0430\u0441\u0441\u043a\u0430\u0436\u0438\u0442\u0435, \u0447\u0435\u043c\u0443 \u0432\u044b \u0445\u043e\u0442\u0438\u0442\u0435 \u043d\u0430\u0443\u0447\u0438\u0442\u044c\u0441\u044f \u0438\u043b\u0438 \u043a\u0430\u043a\u0443\u044e \u0440\u0430\u0431\u043e\u0442\u0443 \u0445\u043e\u0442\u0438\u0442\u0435 \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c \u043f\u043e\u0441\u043b\u0435 \u043a\u0443\u0440\u0441\u0430.",
        "insurance_help.country": "\u0414\u043b\u044f \u0447\u0435\u0433\u043e \u0432\u0430\u043c \u043d\u0443\u0436\u043d\u0430 \u0441\u0442\u0440\u0430\u0445\u043e\u0432\u043a\u0430?",
        "housing_help.onePersonFamilyOrGroup": "\u0412 \u043a\u0430\u043a\u043e\u043c \u0433\u043e\u0440\u043e\u0434\u0435 \u0432\u0430\u043c \u043d\u0443\u0436\u043d\u043e \u0436\u0438\u043b\u044c\u0435?",
    },
    "pl": {
        "candidate_job_search.skills": "Opowiedz, jakiej pracy szukasz i co potrafisz robic.",
        "candidate_job_search.currentLocation": "Gdzie teraz jestes?",
        "candidate_job_search.experience": "Ile mniej wiecej masz lat takiego doswiadczenia?",
        "candidate_job_search.documentsLegalStatus": "Jakie dokumenty masz teraz przy sobie?",
        "employer_hiring.workLocation": "Gdzie bedzie praca?",
        "employer_hiring.workersCount": "Ilu pracownikow potrzebujesz?",
        "employer_hiring.requiredSkills": "Jakie umiejetnosci sa najwazniejsze?",
        "employer_hiring.salaryOrRate": "Jaka stawke lub wynagrodzenie oferujesz?",
        "employer_hiring.accommodationProvided": "Czy zapewniasz zakwaterowanie?",
        "legalization_help.currentCountry": "Opisz krotko, jaka jest sytuacja z dokumentami.",
        "course_interest.currentCity": "Opowiedz, czego chcesz sie nauczyc albo jaka prace chcesz pozniej dostac.",
        "insurance_help.country": "Do czego potrzebujesz ubezpieczenia?",
        "housing_help.onePersonFamilyOrGroup": "W jakim miescie potrzebujesz mieszkania?",
    },
    "en": {
        "candidate_job_search.skills": "Tell me what work you are looking for and what you can do.",
        "candidate_job_search.currentLocation": "Where are you now?",
        "candidate_job_search.experience": "How many years of this experience do you have?",
        "candidate_job_search.documentsLegalStatus": "Which documents do you already have?",
        "candidate_job_search.preferredContactMethod": "How is it best to contact you?",
        "candidate_job_search.phoneOrContact": "Which phone number or contact should I save?",
        "candidate_job_search.drivingLicense": "Do you have a driving license?",
        "candidate_job_search.certificates": "Do you have certificates for this work?",
        "candidate_job_search.relocationReadiness": "Are you ready to relocate?",
        "candidate_job_search.preferredDestination": "Which country would you like to work in?",
        "candidate_job_search.learningReadiness": "Would you be ready for short training if needed?",
        "candidate_job_search.desiredSalary": "What salary or rate would work for you?",
        "candidate_job_search.startAvailability": "When are you ready to start?",
        "candidate_job_search.accommodationNeed": "Do you need accommodation?",
        "candidate_job_search.photoUpload": "Could you add a profile photo later?",
        "candidate_job_search.documentUpload": "Could you add document files later?",
        "employer_hiring.workLocation": "Where is the work located?",
        "employer_hiring.workersCount": "How many people do you need?",
        "employer_hiring.requiredSkills": "Which skills are most important for this work?",
        "employer_hiring.salaryOrRate": "What salary or hourly rate do you offer?",
        "employer_hiring.contractType": "What type of contract is planned?",
        "employer_hiring.workingHours": "What are the working hours?",
        "employer_hiring.accommodationProvided": "Do you provide accommodation?",
        "employer_hiring.startDate": "When should people start work?",
        "employer_hiring.trainingPossibility": "Can you train new people on site?",
        "employer_hiring.companyName": "What is your company name?",
        "employer_hiring.contactPerson": "Who should the coordinator contact?",
        "employer_hiring.phoneOrEmail": "Which phone or email should I save?",
        "employer_hiring.nipOrRegon": "Can you provide NIP, REGON or company registration number?",
        "legalization_help.currentCountry": "Briefly describe your document situation.",
        "course_interest.currentCity": "Tell me what you want to learn or what work you want after the course.",
        "insurance_help.country": "What do you need insurance for?",
        "housing_help.onePersonFamilyOrGroup": "In which city do you need housing?",
    },
}


FIELD_ALIASES = {
    "skills": ("skills", "skill", "profession", "role", "requiredSkills"),
    "currentLocation": ("currentLocation", "country", "city", "location"),
    "experience": ("experience", "experience_years", "yearsOfExperience"),
    "documentsLegalStatus": ("documentsLegalStatus", "documents", "legalStatus"),
    "phoneOrContact": ("phoneOrContact", "phone", "phone_number", "contact"),
    "workLocation": ("workLocation", "country", "city", "location"),
    "workersCount": ("workersCount", "quantity", "people_needed"),
    "requiredSkills": ("requiredSkills", "requirements", "skills", "profession"),
    "salaryOrRate": ("salaryOrRate", "salary", "rate"),
    "accommodationProvided": ("accommodationProvided", "housing", "accommodation"),
}


def get_next_question(intent: str | ChatIntent, known_fields: dict[str, Any] | None = None, language: str = "en") -> str | None:
    chat_intent = _normalize_intent(intent)
    priority = QUESTION_PRIORITIES.get(chat_intent)
    if not priority:
        return None
    fields = known_fields or {}
    for field in priority:
        if not _has_field(fields, field):
            return _question_for(chat_intent, field, language)
    return None


def _normalize_intent(intent: str | ChatIntent) -> ChatIntent:
    if isinstance(intent, ChatIntent):
        return intent
    aliases = {
        "candidate": ChatIntent.CANDIDATE_JOB_SEARCH,
        "employer": ChatIntent.EMPLOYER_HIRING,
        "legalization": ChatIntent.LEGALIZATION_HELP,
        "legal": ChatIntent.LEGALIZATION_HELP,
        "course": ChatIntent.COURSE_INTEREST,
        "courses": ChatIntent.COURSE_INTEREST,
        "insurance": ChatIntent.INSURANCE_HELP,
        "housing": ChatIntent.HOUSING_HELP,
    }
    return aliases.get(str(intent), ChatIntent(str(intent)) if str(intent) in ChatIntent._value2member_map_ else ChatIntent.UNKNOWN)


def _has_field(fields: dict[str, Any], field: str) -> bool:
    keys = FIELD_ALIASES.get(field, (field,))
    return any(_truthy(fields.get(key)) for key in keys)


def _truthy(value: Any) -> bool:
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return value is not None and value is not False and value != ""


def _question_for(intent: ChatIntent, field: str, language: str) -> str:
    key = f"{intent.value}.{field}"
    language_questions = QUESTIONS.get(language, {})
    return language_questions.get(key) or QUESTIONS["en"].get(key) or QUESTIONS["en"].get(f"{intent.value}.{QUESTION_PRIORITIES[intent][0]}")
