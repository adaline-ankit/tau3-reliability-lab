"""Attribute run outcomes without pooling incompatible experiments."""

import unittest

from analyze_runs import classify_simulation


class AnalysisTests(unittest.TestCase):
    def test_flags_imperative_confirmation_without_question_mark(self):
        row = classify_simulation(
            {
                "termination_reason": "user_stop",
                "messages": [
                    {
                        "role": "assistant",
                        "content": "Please confirm by replying yes to proceed.",
                    },
                    {"role": "user", "content": "Yes, please proceed. ###STOP###"},
                ],
                "reward_info": {"reward": 0.0},
            }
        )
        self.assertTrue(row["possible_premature_customer_stop"])

    def test_flags_consent_followed_by_customer_stop(self):
        simulation = {
            "termination_reason": "user_stop",
            "messages": [
                {"role": "assistant", "content": "Do you confirm cancellation?"},
                {"role": "user", "content": "Yes, please. ###STOP###"},
            ],
            "reward_info": {"reward": 0.0, "db_check": {"db_match": False}},
        }
        self.assertTrue(
            classify_simulation(simulation)["possible_premature_customer_stop"]
        )

    def test_infrastructure_failure_has_no_capability_score(self):
        row = classify_simulation(
            {"termination_reason": "infrastructure_error", "messages": []}
        )
        self.assertIsNone(row["native_reward"])
        self.assertEqual(row["category"], "infrastructure_failure")

    def test_normal_success_does_not_trigger_stop_warning(self):
        row = classify_simulation(
            {
                "termination_reason": "user_stop",
                "messages": [
                    {"role": "assistant", "content": "Order cancelled."},
                    {"role": "user", "content": "Thanks. ###STOP###"},
                ],
                "reward_info": {"reward": 1.0, "db_check": {"db_match": True}},
            }
        )
        self.assertFalse(row["possible_premature_customer_stop"])
        self.assertEqual(row["category"], "native_outcome_success")


if __name__ == "__main__":
    unittest.main()
