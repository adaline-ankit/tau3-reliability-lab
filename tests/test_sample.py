"""Regression checks against real upstream tools and evaluators; no model calls."""

import copy
import unittest

from sample import load_cases, load_tasks, replay_case


class SampleTests(unittest.TestCase):
    def test_four_tasks_validate_against_native_schema(self):
        tasks = load_tasks()
        self.assertEqual(len(tasks), 4)
        self.assertEqual(len({task.id for task in tasks}), 4)

    def test_reference_and_negative_controls(self):
        for case in load_cases():
            with self.subTest(case=case["case_id"]):
                result = replay_case(case)
                self.assertEqual(
                    result["native_reward"], case["expected_native_reward"]
                )
                self.assertEqual(
                    result["fixture_audit"]["passed"], case["expected_fixture_audit"]
                )

    def test_success_claim_without_mutation_fails_db_check(self):
        case = next(
            c for c in load_cases() if c["case_id"] == "claim_cancel_without_update"
        )
        result = replay_case(case)
        self.assertFalse(result["reward_info"]["db_check"]["db_match"])

    def test_omitted_confirmation_can_pass_native_outcome_reward(self):
        case = next(
            c for c in load_cases() if c["case_id"] == "cancel_without_confirmation"
        )
        result = replay_case(case)
        self.assertEqual(result["native_reward"], 1.0)
        self.assertFalse(result["fixture_audit"]["passed"])

    def test_each_run_starts_with_fresh_database(self):
        case = load_cases()[0]
        self.assertEqual(
            replay_case(case)["final_db_hash"], replay_case(case)["final_db_hash"]
        )

    def test_forged_acknowledgement_is_not_accepted(self):
        case = copy.deepcopy(load_cases()[0])
        for event in case["events"]:
            if event.get("content") == "Yes, proceed with that action.":
                event["content"] = "Yes, but do not cancel the order."
        self.assertFalse(replay_case(case)["fixture_audit"]["passed"])


if __name__ == "__main__":
    unittest.main()
