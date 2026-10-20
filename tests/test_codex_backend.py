"""Transport and information-boundary checks, with no model calls."""

import json
import unittest

from codex_backend import failure_kind, parse_codex_output, participant_prompt


def event_stream(*items):
    return "\n".join(json.dumps(item) for item in items)


class CodexBackendTests(unittest.TestCase):
    def test_rate_limit_on_stderr_is_classified(self):
        self.assertEqual(failure_kind("", "HTTP 429 Too Many Requests"), "rate_limited")

    def test_rate_limit_is_classified_without_leaking_provider_details(self):
        stream = event_stream(
            {
                "type": "error",
                "message": "exceeded retry limit, last status: 429 Too Many Requests",
            }
        )
        self.assertEqual(failure_kind(stream), "rate_limited")

    def test_requires_successful_completion_receipt(self):
        with self.assertRaisesRegex(ValueError, "completion"):
            parse_codex_output(
                event_stream({"type": "turn.started"}), '{"text":"hello"}'
            )

    def test_rejects_native_tool_execution(self):
        stream = event_stream(
            {
                "type": "item.completed",
                "item": {"type": "command_execution", "command": "cat secret"},
            },
            {"type": "turn.completed", "usage": {}},
        )
        with self.assertRaisesRegex(ValueError, "native tool"):
            parse_codex_output(stream, '{"text":"hello"}')

    def test_rejects_failed_turn_even_if_answer_file_exists(self):
        stream = event_stream(
            {"type": "turn.failed", "error": {"message": "transport unavailable"}}
        )
        with self.assertRaisesRegex(ValueError, "failed"):
            parse_codex_output(stream, '{"text":"hello"}')

    def test_preserves_structured_answer_and_usage(self):
        stream = event_stream(
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 12, "output_tokens": 4},
            }
        )
        answer, usage = parse_codex_output(stream, '{"text":"hello"}')
        self.assertEqual(answer, {"text": "hello"})
        self.assertEqual(usage["input_tokens"], 12)

    def test_agent_prompt_has_no_customer_or_evaluator_fields(self):
        prompt = participant_prompt(
            "agent",
            "POLICY",
            [{"name": "lookup"}],
            [{"role": "user", "content": "hello"}],
        )
        self.assertIn("POLICY", prompt)
        self.assertNotIn("evaluation_criteria", prompt)
        self.assertNotIn("user_scenario", prompt)
        self.assertNotIn("expected_actions", prompt)


if __name__ == "__main__":
    unittest.main()
