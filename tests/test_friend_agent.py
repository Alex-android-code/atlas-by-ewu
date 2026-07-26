import unittest

from services.friend_agent import AgentMode, detect_agent_mode, worker_agent_context, worker_agent_system_prompt


class FriendAgentTests(unittest.TestCase):
    def test_detects_friend_mentor_and_executor_modes(self) -> None:
        self.assertEqual(detect_agent_mode("Мне страшно и ничего не получается"), AgentMode.FRIEND)
        self.assertEqual(detect_agent_mode("Напиши мне CV для сварщика"), AgentMode.EXECUTOR)
        self.assertEqual(detect_agent_mode("Какая работа мне подходит?"), AgentMode.MENTOR)

    def test_context_contains_safety_rules_and_memory_policy(self) -> None:
        context = worker_agent_context("зроби резюме", language="uk", profile={"profession": "welder"})

        self.assertEqual(context["mode"], "EXECUTOR")
        self.assertTrue(context["rules"])
        self.assertEqual(context["memoryPolicy"]["recentMessagesLimit"], 40)
        self.assertIn("profession", context["knownProfileKeys"])

    def test_system_prompt_keeps_ai_identity_boundary(self) -> None:
        prompt = worker_agent_system_prompt()

        self.assertIn("clearly remaining an AI assistant", prompt)
        self.assertIn("FRIEND", prompt)
        self.assertIn("EXECUTOR", prompt)


if __name__ == "__main__":
    unittest.main()
