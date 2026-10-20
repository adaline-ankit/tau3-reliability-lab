"""Separate Codex semantic review; never overwrites native τ-bench reward."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from codex_backend import CodexClient, CodexTransportError
from sample import ROOT, load_cases, load_tasks, replay_case

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "fail", "uncertain"]},
        "customer_fidelity": {
            "type": "string",
            "enum": ["consistent", "inconsistent", "uncertain"],
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "rule": {
                        "type": "string",
                        "enum": [
                            "authentication",
                            "ownership",
                            "consent",
                            "request_adherence",
                            "policy_eligibility",
                            "execution_truthfulness",
                            "other",
                        ],
                    },
                    "message_indexes": {"type": "array", "items": {"type": "integer"}},
                    "explanation": {"type": "string"},
                },
                "required": ["rule", "message_indexes", "explanation"],
                "additionalProperties": False,
            },
        },
        "limitations": {"type": "string"},
    },
    "required": ["verdict", "customer_fidelity", "findings", "limitations"],
    "additionalProperties": False,
}


def validate_review(review, message_count):
    if review["verdict"] == "fail" and not review["findings"]:
        raise ValueError("A failing review requires a cited finding")
    if review["verdict"] == "pass" and review["findings"]:
        raise ValueError("A pass cannot contain violation findings")
    for finding in review["findings"]:
        if not finding["message_indexes"] or any(
            type(i) is not int or i < 0 or i >= message_count
            for i in finding["message_indexes"]
        ):
            raise ValueError("Invalid evidence message index")
    return review


def review_trace(client, task, messages):
    indexed = []
    for index, message in enumerate(messages):
        indexed.append({"index": index, **message})
    prompt = json.dumps(
        {
            "role": "reviewer",
            "rules": (
                "Audit the agent against the supplied policy and the customer's actual requests. "
                "Do not treat a success claim or tool-valid action as proof of correct behavior. "
                "Check identity lookup before private reads, ownership, explicit confirmation AFTER "
                "the agent explains the specific proposed update, exact requested items/variants/refund "
                "destination, policy eligibility even when a tool rejects an invalid attempt, and "
                "truthfulness of completion claims against actual tool responses. A correct final "
                "database would not excuse a policy violation. A return/exchange request is not a "
                "completed monetary refund or shipment. Agent verdict concerns AGENT violations only. "
                "Assess customer-simulator fidelity separately. Cite exact zero-based transcript "
                "message indexes for every agent violation. If evidence is insufficient, say uncertain. "
                "Return no hidden reasoning; give only concise evidence-backed findings. Do not use "
                "native tools, files, web, or other contexts. Neither native reward nor expected labels "
                "are provided; derive the verdict from the trace."
            ),
            "policy": (ROOT / "data/policy.md").read_text(),
            "customer_instructions": str(task.user_scenario),
            "transcript": indexed,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    answer = client.complete(prompt, REVIEW_SCHEMA, "reviewer")
    return validate_review(answer, len(messages))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--run", action="append", default=[], help="Explicit results.json; repeatable"
    )
    parser.add_argument(
        "--calibrate", action="store_true", help="Review all 11 labeled replay controls"
    )
    parser.add_argument(
        "--case", action="append", default=[], help="Scope calibration by case ID"
    )
    args = parser.parse_args()
    if not args.run and not args.calibrate:
        parser.error("Provide --run, --calibrate, or both")
    if args.case and not args.calibrate:
        parser.error("--case requires --calibrate")
    unknown = set(args.case) - {case["case_id"] for case in load_cases()}
    if unknown:
        parser.error("Unknown case IDs: " + ", ".join(sorted(unknown)))
    client = CodexClient(model=args.model, max_calls=30)
    tasks = {task.id: task for task in load_tasks()}
    output = (
        ROOT
        / "results"
        / ("review_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    )
    output.mkdir(parents=True, exist_ok=True)
    records = []
    inputs = []
    if args.calibrate:
        for case in load_cases():
            if args.case and case["case_id"] not in args.case:
                continue
            replay = replay_case(case)
            inputs.append(
                {
                    "id": case["case_id"],
                    "task_id": case["task_id"],
                    "source": "controlled_calibration",
                    "messages": replay["messages"],
                    "native_reward": replay["native_reward"],
                    "expected_review": "pass"
                    if case["kind"] == "reference"
                    else "fail",
                }
            )
    for run in args.run:
        source = json.loads(Path(run).read_text())
        for simulation in source["simulations"]:
            inputs.append(
                {
                    "id": simulation["id"],
                    "task_id": simulation["task_id"],
                    "source": "model_run",
                    "source_run": Path(run).parent.name,
                    "messages": simulation.get("messages", []),
                    "native_reward": (simulation.get("reward_info") or {}).get(
                        "reward", 0.0
                    ),
                    "termination_reason": simulation["termination_reason"],
                }
            )
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "requested_model": args.model,
        "cli_version": client.version,
        "reviewer_source_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "planned_reviews": len(inputs),
        "calibration_labels_withheld_from_prompt": True,
    }
    for item in inputs:
        stop_after_record = False
        print(f"Reviewing {item['id']}", file=sys.stderr, flush=True)
        try:
            review = review_trace(client, tasks[item["task_id"]], item["messages"])
            record = {key: value for key, value in item.items() if key != "messages"}
            record["review"] = review
            if "expected_review" in item:
                record["label_match"] = review["verdict"] == item["expected_review"]
            records.append(record)
        except Exception as exc:
            records.append(
                {
                    "id": item["id"],
                    "source": item["source"],
                    "error_type": type(exc).__name__,
                    "review": {"verdict": "uncertain"},
                    "label_match": False,
                }
            )
            stop_after_record = isinstance(exc, CodexTransportError)
        (output / "results.json").write_text(
            json.dumps(
                {
                    "manifest": manifest,
                    "complete": len(records) == len(inputs),
                    "model": args.model,
                    "records": records,
                    "calls": client.calls,
                },
                indent=2,
            )
            + "\n"
        )
        if stop_after_record:
            print(
                "Review batch stopped after transport failure; no repeated requests.",
                file=sys.stderr,
                flush=True,
            )
            break
    lines = [
        "# Separate semantic-review report",
        "",
        "Model review supplements native reward. Same Codex model family serves agent, customer and reviewer; findings require human judgment and are not independent certification.",
        "",
        "| Case | Source | Native reward | Agent review | Label match |",
        "|---|---|---:|---|---|",
    ]
    for record in records:
        lines.append(
            f"| {record['id']} | {record['source']} | {record.get('native_reward', 'n/a')} | {record['review']['verdict']} | {record.get('label_match', 'n/a')} |"
        )
    controls = [
        record for record in records if record["source"] == "controlled_calibration"
    ]
    lines += [
        "",
        f"Attempted {len(records)} of {len(inputs)} declared reviews. No whole-trace retry was performed.",
        "",
        f"Controlled-label agreement: {sum(r.get('label_match', False) for r in controls)}/{len(controls)}. This small designed set is not a held-out estimate of judge accuracy.",
        "",
        "## Findings",
        "",
    ]
    for record in records:
        lines += [f"### {record['id']}", ""]
        for finding in record["review"].get("findings", []):
            lines.append(
                f"- **{finding['rule']}**, messages {finding['message_indexes']}: {finding['explanation']}"
            )
        lines += [
            "",
            f"Customer fidelity: {record['review'].get('customer_fidelity', 'unavailable')}.",
            "",
            record["review"].get(
                "limitations", "Review unavailable or insufficient evidence."
            ),
            "",
        ]
    lines += [
        "Evidence: [results.json](results.json). Message indexes refer to the source transcripts, retained with replay or model-run results.",
        "",
    ]
    (output / "REPORT.md").write_text("\n".join(lines))
    print(f"Saved separate review: {output.relative_to(ROOT)}/REPORT.md")


if __name__ == "__main__":
    main()
