"""Ownership metadata for admin-only use."""

from core.project_identity import ADMIN_PROJECT_METADATA, FOUNDER, SUCCESSORS

FOUNDER_RIGHTS_DECLARATION = (
    "ATLAS by EWU is a founder-led project. Ownership rights, strategic control, "
    "intellectual property control, brand control, product direction and final "
    "decision-making authority belong to the founder during his lifetime and then "
    "pass to the listed successors."
)

ADMIN_OWNERSHIP_METADATA = {
    **ADMIN_PROJECT_METADATA,
    "founder_rights_declaration": FOUNDER_RIGHTS_DECLARATION,
    "founder": FOUNDER,
    "successors": list(SUCCESSORS),
}
