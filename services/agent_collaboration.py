"""Consent-aware bridge between personal and corporate AI agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models import (
    AgentCollaborationAuditEvent,
    AgentCollaborationProposal,
    AgentConsentGrant,
    UpskillingOpportunity,
    utc_now_iso,
)
from database.repositories import (
    AgentCollaborationAuditEventRepository,
    AgentCollaborationProposalRepository,
    AgentConsentGrantRepository,
    ConsentRepository,
    UpskillingOpportunityRepository,
)


COLLABORATION_SCOPE = "corporate_agent_collaboration"
ALLOWED_DATA_CATEGORIES = {
    "competency_summary",
    "skill_gap_summary",
    "development_preferences",
    "availability_window",
}


@dataclass
class AgentCollaborationRepositories:
    proposals: AgentCollaborationProposalRepository
    grants: AgentConsentGrantRepository
    audit_events: AgentCollaborationAuditEventRepository
    consents: ConsentRepository
    upskilling_opportunities: UpskillingOpportunityRepository


class ConsentAwareMatchingService:
    def __init__(self, repositories: AgentCollaborationRepositories) -> None:
        self.repositories = repositories

    def can_share(self, user_id: str, employer_id: str, scope: str = COLLABORATION_SCOPE) -> bool:
        for grant in self.repositories.grants.list():
            if (
                grant.user_id == user_id
                and grant.employer_id == employer_id
                and grant.scope == scope
                and grant.status == "active"
            ):
                return True
        return False


class UpskillingOpportunityService:
    def __init__(self, repositories: AgentCollaborationRepositories) -> None:
        self.repositories = repositories

    def create_from_proposal(self, proposal: AgentCollaborationProposal) -> UpskillingOpportunity:
        competency_id = str(proposal.metadata.get("competency_id", "unknown"))
        opportunity = UpskillingOpportunity(
            competency_id=competency_id,
            title=proposal.title,
            provider=f"employer:{proposal.employer_id}",
            metadata={
                "proposal_id": proposal.id,
                "user_id": proposal.user_id,
                "proposal_type": proposal.proposal_type,
                "requires_user_consent": True,
            },
        )
        return self.repositories.upskilling_opportunities.add(opportunity)


class EmployerFundedTrainingService:
    def prepare_offer(self, proposal: AgentCollaborationProposal, grant: AgentConsentGrant | None) -> dict[str, Any]:
        return {
            "proposal_id": proposal.id,
            "employer_id": proposal.employer_id,
            "user_id": proposal.user_id,
            "funding_status": "available_after_user_consent" if grant is None else "consented",
            "can_share_personal_data": grant is not None and grant.status == "active",
            "legal_basis": proposal.legal_basis,
            "consent_scope": proposal.consent_scope,
        }


class AgentCollaborationService:
    def __init__(
        self,
        repositories: AgentCollaborationRepositories,
        matching: ConsentAwareMatchingService | None = None,
        opportunities: UpskillingOpportunityService | None = None,
        employer_funded_training: EmployerFundedTrainingService | None = None,
    ) -> None:
        self.repositories = repositories
        self.matching = matching or ConsentAwareMatchingService(repositories)
        self.opportunities = opportunities or UpskillingOpportunityService(repositories)
        self.employer_funded_training = employer_funded_training or EmployerFundedTrainingService()

    def create_proposal(
        self,
        employer_id: str,
        user_id: str,
        proposal_type: str,
        title: str,
        data_categories: list[str],
        actor_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> AgentCollaborationProposal:
        normalized_categories = _validate_data_categories(data_categories)
        proposal = AgentCollaborationProposal(
            employer_id=employer_id,
            user_id=user_id,
            proposal_type=proposal_type,
            title=title,
            data_categories=normalized_categories,
            metadata=metadata or {},
        )
        saved = self.repositories.proposals.add(proposal)
        self._audit(saved.id, "proposal_created", actor_id, {"data_categories": normalized_categories})
        return saved

    def grant_consent(self, proposal_id: str, user_id: str, actor_id: str) -> AgentConsentGrant:
        proposal = self._require_proposal(proposal_id)
        if proposal.user_id != user_id:
            raise ValueError("Proposal does not belong to this user")
        grant = AgentConsentGrant(
            proposal_id=proposal.id,
            user_id=proposal.user_id,
            employer_id=proposal.employer_id,
            scope=proposal.consent_scope,
            metadata={"legal_basis": proposal.legal_basis, "data_categories": proposal.data_categories},
        )
        saved = self.repositories.grants.add(grant)
        proposal.status = "consented"
        self.repositories.proposals.update(proposal)
        self.opportunities.create_from_proposal(proposal)
        self._audit(proposal.id, "consent_granted", actor_id, {"grant_id": saved.id})
        return saved

    def revoke_consent(self, grant_id: str, actor_id: str) -> AgentConsentGrant:
        grant = self.repositories.grants.get(grant_id)
        if grant is None:
            raise ValueError(f"Consent grant not found: {grant_id}")
        grant.status = "revoked"
        grant.revoked_at = utc_now_iso()
        saved = self.repositories.grants.update(grant)
        proposal = self.repositories.proposals.get(grant.proposal_id)
        if proposal:
            proposal.status = "consent_revoked"
            self.repositories.proposals.update(proposal)
        self._audit(grant.proposal_id, "consent_revoked", actor_id, {"grant_id": grant_id})
        return saved

    def collaboration_status(self, proposal_id: str) -> dict[str, Any]:
        proposal = self._require_proposal(proposal_id)
        grant = self._active_grant_for(proposal)
        return {
            "proposal": proposal.to_dict(),
            "can_share_personal_data": grant is not None,
            "grant": grant.to_dict() if grant else None,
            "employer_funded_training": self.employer_funded_training.prepare_offer(proposal, grant),
            "audit_events": [
                item.to_dict() for item in self.repositories.audit_events.list() if item.proposal_id == proposal.id
            ],
        }

    def _active_grant_for(self, proposal: AgentCollaborationProposal) -> AgentConsentGrant | None:
        for grant in self.repositories.grants.list():
            if grant.proposal_id == proposal.id and grant.status == "active":
                return grant
        return None

    def _require_proposal(self, proposal_id: str) -> AgentCollaborationProposal:
        proposal = self.repositories.proposals.get(proposal_id)
        if proposal is None:
            raise ValueError(f"Collaboration proposal not found: {proposal_id}")
        return proposal

    def _audit(self, proposal_id: str, event_type: str, actor_id: str, metadata: dict[str, Any]) -> None:
        self.repositories.audit_events.add(
            AgentCollaborationAuditEvent(
                proposal_id=proposal_id,
                event_type=event_type,
                actor_id=actor_id,
                metadata=metadata,
            )
        )


def _validate_data_categories(categories: list[str]) -> list[str]:
    normalized = []
    for category in categories:
        value = category.strip().lower()
        if value not in ALLOWED_DATA_CATEGORIES:
            raise ValueError(f"Unsupported collaboration data category: {category}")
        normalized.append(value)
    return list(dict.fromkeys(normalized))
