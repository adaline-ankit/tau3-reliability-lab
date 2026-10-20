"""Reviewer evidence validation; no model calls."""

import unittest

from trace_review import validate_review


class TraceReviewTests(unittest.TestCase):
    def test_rejects_out_of_range_evidence(self):
        review = {
            "verdict": "fail",
            "findings": [
                {
                    "rule": "consent",
                    "message_indexes": [99],
                    "explanation": "Missing consent",
                }
            ],
            "limitations": "",
        }
        with self.assertRaisesRegex(ValueError, "message index"):
            validate_review(review, 3)

    def test_failure_requires_cited_finding(self):
        with self.assertRaisesRegex(ValueError, "finding"):
            validate_review({"verdict": "fail", "findings": [], "limitations": ""}, 3)

    def test_pass_cannot_contain_violation_findings(self):
        review = {
            "verdict": "pass",
            "findings": [
                {
                    "rule": "consent",
                    "message_indexes": [1],
                    "explanation": "Missing consent",
                }
            ],
            "limitations": "",
        }
        with self.assertRaisesRegex(ValueError, "pass"):
            validate_review(review, 3)


if __name__ == "__main__":
    unittest.main()
