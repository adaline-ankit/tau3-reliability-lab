"""Native orchestrator and input-boundary tests using deterministic stubs."""

import json
import unittest

from jsonschema import ValidationError

from codex_runner import validate_customer_stop, run_episode
from sample import load_cases, load_tasks


class ScriptedClient:
    def __init__(self):
        case = load_cases()[0]
        self.agent = iter(e for e in case["events"] if e["role"] != "user")
        self.user = iter([e["content"] for e in case["events"] if e["role"] == "user"])
        self.calls = []

    def complete(self, prompt, schema, role):
        payload = json.loads(prompt)
        self.calls.append(
            {"role": role, "prompt": payload, "status": "completed", "usage": {}}
        )
        if role == "agent":
            event = next(self.agent)
            if event["role"] == "tool":
                return {
                    "kind": "tool",
                    "text": "",
                    "tool_name": event["name"],
                    "arguments_json": json.dumps(event["arguments"]),
                }
            return {
                "kind": "message",
                "text": event["content"],
                "tool_name": "",
                "arguments_json": "{}",
            }
        try:
            return {"text": next(self.user), "done": False}
        except StopIteration:
            return {"text": "Thank you.", "done": True}


class CodexRunnerTests(unittest.TestCase):
    def test_customer_cannot_stop_on_imperative_confirmation(self):
        with self.assertRaisesRegex(ValueError, "confirmation"):
            validate_customer_stop(
                "Please confirm by replying yes to proceed.",
                {"text": "Yes, please proceed.", "done": True},
            )

    def test_customer_cannot_embed_reserved_stop_marker(self):
        with self.assertRaisesRegex(ValueError, "reserved"):
            validate_customer_stop(
                "Do you confirm cancellation?",
                {"text": "Yes, please. ###STOP###", "done": False},
            )

    def test_customer_can_end_after_confirmation_receipt(self):
        validate_customer_stop(
            "Order cancelled. Your confirmation number is ABC. Anything else?",
            {"text": "Yes, that is all. Thanks.", "done": True},
        )

    def test_customer_cannot_end_while_answering_a_confirmation_request(self):
        with self.assertRaisesRegex(ValueError, "confirmation"):
            validate_customer_stop(
                "Do you confirm cancellation?",
                {"text": "Yes, please cancel it.", "done": True},
            )

    def test_customer_can_end_after_a_completed_action(self):
        validate_customer_stop(
            "Your order is cancelled.", {"text": "Thank you.", "done": True}
        )

    def test_customer_can_decline_and_end(self):
        validate_customer_stop(
            "Do you confirm cancellation?",
            {"text": "No, please make no changes. Goodbye.", "done": True},
        )

    def test_malformed_agent_arguments_are_not_infrastructure_failure(self):
        class MalformedAgentClient(ScriptedClient):
            bad_value = "{"

            def complete(self, prompt, schema, role):
                answer = super().complete(prompt, schema, role)
                if role == "agent" and answer["kind"] == "tool":
                    answer["arguments_json"] = self.bad_value
                return answer

        for bad_value in ["{", None]:
            with self.subTest(bad_value=bad_value):
                client = MalformedAgentClient()
                client.bad_value = bad_value
                simulation = run_episode(load_tasks()[0], client)
                self.assertEqual(simulation.termination_reason.value, "agent_error")
                self.assertIsNone(simulation.reward_info)

    def test_schema_invalid_output_is_attributed_to_its_participant(self):
        class InvalidShapeClient(ScriptedClient):
            invalid_role = "agent"

            def complete(self, prompt, schema, role):
                if role == self.invalid_role:
                    raise ValidationError("Output does not match participant schema")
                return super().complete(prompt, schema, role)

        for role in ["agent", "customer"]:
            with self.subTest(role=role):
                client = InvalidShapeClient()
                client.invalid_role = role
                simulation = run_episode(load_tasks()[0], client)
                expected = "agent_error" if role == "agent" else "user_error"
                self.assertEqual(simulation.termination_reason.value, expected)
                self.assertIsNone(simulation.reward_info)

    def test_native_orchestrator_reaches_target_state(self):
        client = ScriptedClient()
        simulation = run_episode(load_tasks()[0], client, trial=0)
        self.assertEqual(simulation.reward_info.reward, 1.0)
        self.assertEqual(simulation.termination_reason.value, "user_stop")

    def test_customer_never_sees_private_tool_outputs(self):
        client = ScriptedClient()
        run_episode(load_tasks()[0], client, trial=0)
        for call in client.calls:
            if call["role"] == "customer":
                self.assertTrue(
                    all(
                        m["role"] in {"assistant", "user"}
                        for m in call["prompt"]["conversation"]
                    )
                )
                self.assertEqual(call["prompt"]["available_tools"], [])
            self.assertNotIn("evaluation_criteria", json.dumps(call["prompt"]))


if __name__ == "__main__":
    unittest.main()
