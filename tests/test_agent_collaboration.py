import tempfile
import unittest
from pathlib import Path

from database.json_database import JsonDatabase
from database.repositories import (
    AgentCollaborationAuditEventRepository,
    AgentCollaborationProposalRepository,
    AgentConsentGrantRepository,
    ConsentRepository,
    UpskillingOpportunityRepository,
)
from services.agent_collaboration import (
    COLLABORATION_SCOPE,
    AgentCollaborationRepositories,
    AgentCollaborationService,
    ConsentAwareMatchingService,
)


class AgentCollaborationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.repositories = AgentCollaborationRepositories(
            proposals=AgentCollaborationProposalRepository(database),
            grants=AgentConsentGrantRepository(database),
            audit_events=AgentCollaborationAuditEventRepository(database),
            consents=ConsentRepository(database),
            upskilling_opportunities=UpskillingOpportunityRepository(database),
        )
        self.service = AgentCollaborationService(self.repositories)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_proposal_does_not_allow_sharing_without_grant(self):
        proposal = self.service.create_proposal(
            employer_id="emp-1",
            user_id="user-1",
            proposal_type="employer_funded_training",
            title="Safety leadership development",
            data_categories=["competency_summary", "skill_gap_summary"],
            actor_id="admin",
        )

        status = self.service.collaboration_status(proposal.id)

        self.assertFalse(status["can_share_personal_data"])
        self.assertEqual(status["employer_funded_training"]["funding_status"], "available_after_user_consent")

    def test_grant_and_revoke_control_matching_permission(self):
        proposal = self.service.create_proposal(
            employer_id="emp-1",
            user_id="user-1",
            proposal_type="upskilling",
            title="Inventory control mentoring",
            data_categories=["competency_summary"],
            actor_id="admin",
            metadata={"competency_id": "COMP-1"},
        )
        matching = ConsentAwareMatchingService(self.repositories)

        self.assertFalse(matching.can_share("user-1", "emp-1"))
        grant = self.service.grant_consent(proposal.id, "user-1", actor_id="user-1")
        self.assertTrue(matching.can_share("user-1", "emp-1", COLLABORATION_SCOPE))
        self.service.revoke_consent(grant.id, actor_id="user-1")
        self.assertFalse(matching.can_share("user-1", "emp-1", COLLABORATION_SCOPE))

    def test_grant_creates_audit_events_and_upskilling_opportunity(self):
        proposal = self.service.create_proposal(
            employer_id="emp-1",
            user_id="user-1",
            proposal_type="upskilling",
            title="Technical drawing practice",
            data_categories=["development_preferences"],
            actor_id="admin",
            metadata={"competency_id": "COMP-2"},
        )

        self.service.grant_consent(proposal.id, "user-1", actor_id="user-1")
        status = self.service.collaboration_status(proposal.id)

        self.assertEqual([event["event_type"] for event in status["audit_events"]], ["proposal_created", "consent_granted"])
        self.assertEqual(len(self.repositories.upskilling_opportunities.list()), 1)

    def test_unsupported_data_category_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.create_proposal(
                employer_id="emp-1",
                user_id="user-1",
                proposal_type="upskilling",
                title="Bad proposal",
                data_categories=["full_private_profile"],
                actor_id="admin",
            )

    def test_wrong_user_cannot_grant_proposal(self):
        proposal = self.service.create_proposal(
            employer_id="emp-1",
            user_id="user-1",
            proposal_type="upskilling",
            title="Mentoring",
            data_categories=["competency_summary"],
            actor_id="admin",
        )

        with self.assertRaises(ValueError):
            self.service.grant_consent(proposal.id, "user-2", actor_id="user-2")


if __name__ == "__main__":
    unittest.main()
