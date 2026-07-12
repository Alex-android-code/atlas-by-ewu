"""Project identity constants for ATLAS by EWU."""

PROJECT_NAME = "ATLAS by EWU"
ECOSYSTEM_OWNER = "EWU"
FOUNDER = "Oleksandr Didkivskyi / Aleksandr Didkowski"
SUCCESSORS = (
    "Dmitrii Didkovskii",
    "Mia Didkovska",
)

MISSION = (
    "ATLAS by EWU helps people in Europe build a stable work-life path through "
    "work, skills, documents, training, insurance, housing and trusted partners."
)

PUBLIC_PROJECT_METADATA = {
    "project_name": PROJECT_NAME,
}

ADMIN_PROJECT_METADATA = {
    "project_name": PROJECT_NAME,
    "ecosystem_owner": ECOSYSTEM_OWNER,
    "founder": FOUNDER,
    "successors": list(SUCCESSORS),
    "ownership_declaration": "See docs/FOUNDER_RIGHTS.md",
    "documentation": {
        "constitution": "docs/PROJECT_CONSTITUTION.md",
        "product_principles": "docs/PRODUCT_PRINCIPLES.md",
        "founder_rights": "docs/FOUNDER_RIGHTS.md",
        "roadmap": "docs/ROADMAP.md",
        "technical_decisions": "docs/TECHNICAL_DECISIONS.md",
    },
}
