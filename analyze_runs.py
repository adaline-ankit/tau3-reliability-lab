"""Compare explicitly selected run receipts; no model calls and no pooled score."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def classify_simulation(simulation):
    messages = simulation.get("messages", [])
    reward = (simulation.get("reward_info") or {}).get("reward")
    termination = simulation["termination_reason"]
    last = messages[-1] if messages else {}
    previous = messages[-2] if len(messages) >= 2 else {}
    suspected = bool(
        termination == "user_stop"
        and last.get("role") == "user"
        and "###STOP###" in (last.get("content") or "")
        and previous.get("role") == "assistant"
        and re.search(
            r"\b(confirm|confirmation|approve|proceed)\b",
            previous.get("content") or "",
            re.IGNORECASE,
        )
    )
    category = (
        "infrastructure_failure"
        if termination == "infrastructure_error"
        else "participant_protocol_error"
        if termination in {"user_error", "agent_error"}
        else "native_outcome_success"
        if reward == 1.0
        else "native_outcome_not_met"
    )
    info = simulation.get("reward_info") or {}
    return {
        "task_id": simulation.get("task_id"),
        "trial": simulation.get("trial"),
        "termination": termination,
        "native_reward": reward,
        "db_match": (info.get("db_check") or {}).get("db_match"),
        "reward_breakdown": info.get("reward_breakdown", {}),
        "category": category,
        "possible_premature_customer_stop": suspected,
        "tool_errors": sum(
            m.get("role") == "tool" and m.get("error", False) for m in messages
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "runs", nargs="+", type=Path, help="Explicit codex_runner results.json files"
    )
    args = parser.parse_args()
    records = []
    for path in args.runs:
        payload = json.loads(path.read_text())
        manifest = payload["manifest"]
        records.append(
            {
                "directory": path.parent.name,
                "requested_model": manifest["requested_model"],
                "customer_protocol": manifest.get(
                    "customer_protocol", "baseline_before_confirmation_guard"
                ),
                "planned_trials": len(manifest["task_ids"])
                * manifest["trials_per_task"],
                "attempted_trials": len(payload["simulations"]),
                "model_calls": len(payload["calls"]),
                "rows": [classify_simulation(s) for s in payload["simulations"]],
            }
        )
    output = ROOT / "results"
    (output / "experiment_summary.json").write_text(
        json.dumps(records, indent=2) + "\n"
    )
    lines = [
        "# Experiment comparison",
        "",
        "Each row belongs to its own declared run. Different models, customer protocols, and trial scopes are not pooled into one performance score. All listed attempts, including failures, remain visible.",
        "",
        "| Run | Model | Customer protocol | Planned / attempted | Calls |",
        "|---|---|---|---|---:|",
    ]
    for run in records:
        lines.append(
            f"| [{run['directory']}]({run['directory']}/REPORT.md) | {run['requested_model']} | {run['customer_protocol']} | {run['planned_trials']} / {run['attempted_trials']} | {run['model_calls']} |"
        )
    for run in records:
        lines += [
            "",
            f"## {run['directory']}",
            "",
            "| Task | Native reward | DB match | Communication | Termination | Possible early customer stop |",
            "|---|---:|---|---:|---|---|",
        ]
        for row in run["rows"]:
            lines.append(
                f"| {row['task_id']} | {row['native_reward']} | {row['db_match']} | {row['reward_breakdown'].get('COMMUNICATE', 'n/a')} | {row['termination']} | {row['possible_premature_customer_stop']} |"
            )
    lines += [
        "",
        "The early-stop flag is a narrow diagnostic: the customer stopped immediately after an assistant message containing confirmation/proceed wording. This includes imperative requests without a question mark. Inspect the actual customer text and provider response before attributing cause. It is not a general simulator-fidelity classifier.",
        "",
        "DB and communication are shown separately: a zero native reward can arise from either selected component. A missing required substring is not by itself proof that a semantically correct completion statement was false. Inspect the actual statement before attributing an agent reasoning failure.",
        "",
        "Missing native reward is shown as null/None for unscored infrastructure failures. Benchmark counting conventions may assign failed trials zero, but that convention does not turn infrastructure outages into evidence of reasoning failure. Elapsed run time includes CLI startup, network, model time and intentional pacing; it is not raw model-inference latency.",
        "",
    ]
    (output / "EXPERIMENT_COMPARISON.md").write_text("\n".join(lines))
    print("Wrote results/EXPERIMENT_COMPARISON.md and results/experiment_summary.json")


if __name__ == "__main__":
    main()
