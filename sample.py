"""Original synthetic retail cases using pinned, public Sierra τ-bench components."""

import argparse
import json
import os
import socket
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
UPSTREAM_COMMIT = "fc0055dc4e0a316c3f83133267fbd6faaa770992"
DOMAIN = "portfolio_retail"
ACK = "Yes, proceed with that action."
WRITES = {
    "cancel_pending_order",
    "exchange_delivered_order_items",
    "return_delivered_order_items",
}


@contextmanager
def offline_network():
    """Make accidental outbound connections fail, including during library import."""
    with patch.object(
        socket.socket,
        "connect",
        side_effect=RuntimeError("Offline mode: network disabled"),
    ):
        yield


# Never search parent directories for .env files. Use public, fresh checkout only.
os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["TAU2_DATA_DIR"] = str(ROOT / ".upstream" / "data")

with offline_network():
    from loguru import logger

    logger.remove()
    logger.add(lambda message: print(message, end=""), level="ERROR")

    from tau2.data_model.message import (
        AssistantMessage,
        ToolCall,
        ToolMessage,
        UserMessage,
    )
    from tau2.data_model.simulation import (
        SimulationRun,
        TerminationReason,
        TextRunConfig,
    )
    from tau2.data_model.tasks import Task
    from tau2.domains.retail.data_model import RetailDB
    from tau2.domains.retail.tools import RetailTools
    from tau2.environment.environment import Environment
    from tau2.evaluator.evaluator import EvaluationType, evaluate_simulation
    from tau2.registry import registry


def read_json(relative_path):
    return json.loads((ROOT / relative_path).read_text())


def load_tasks(task_split_name="base"):
    if task_split_name not in ("base", None):
        raise ValueError("This authored demonstration has only a base split.")
    return [Task.model_validate(task) for task in read_json("data/tasks.json")]


def load_cases():
    return read_json("data/replay_cases.json")


def get_environment(solo_mode=False):
    if solo_mode:
        raise ValueError("Retail sample supports text conversations, not solo mode.")
    return Environment(
        domain_name=DOMAIN,
        policy=(ROOT / "data/policy.md").read_text(),
        tools=RetailTools(RetailDB.load(ROOT / "data/retail_db.json")),
    )


registry.register_domain(get_environment, DOMAIN)
registry.register_tasks(
    load_tasks, DOMAIN, lambda: {"base": [t.id for t in load_tasks()]}
)


def fixture_audit(messages):
    """Narrow, fixture-only protocol checks; NOT a free-form consent/intent judge.

    Auth lookup must succeed before private reads. Every sample write must follow
    an assistant proposal and the exact controlled ACK. Tool errors fail this
    diagnostic. This does not validate proposal correctness or ownership and is
    not included in the native benchmark reward.
    """
    violations = []
    authenticated = False
    for i, message in enumerate(messages):
        if isinstance(message, ToolMessage):
            if message.error:
                violations.append(f"tool_error:{message.id}")
            continue
        if not isinstance(message, AssistantMessage) or not message.tool_calls:
            continue
        if len(message.tool_calls) != 1 or (message.content or "").strip():
            violations.append(f"mixed_or_parallel_tool_message:{i}")
        for call in message.tool_calls:
            if call.name == "find_user_id_by_email":
                reply = messages[i + 1] if i + 1 < len(messages) else None
                authenticated = isinstance(reply, ToolMessage) and not reply.error
                continue
            if not authenticated:
                violations.append(f"missing_authentication:{call.id}")
            if call.name in WRITES:
                ack = messages[i - 1] if i >= 1 else None
                proposal = messages[i - 2] if i >= 2 else None
                if not (
                    isinstance(ack, UserMessage)
                    and ack.content == ACK
                    and isinstance(proposal, AssistantMessage)
                    and bool((proposal.content or "").strip())
                    and not proposal.tool_calls
                ):
                    violations.append(f"missing_controlled_confirmation:{call.id}")
    return {
        "scope": "controlled_replay_fixtures_only",
        "passed": not violations,
        "violations": violations,
    }


def replay_case(case):
    """Execute authored calls, then independently replay through official evaluators."""
    with offline_network():
        env = get_environment()
        initial_hash = env.get_db_hash()
        messages = []
        for event in case["events"]:
            if event["role"] == "tool":
                call = ToolCall(
                    id=f"call_{len(messages):03}",
                    name=event["name"],
                    arguments=event["arguments"],
                )
                messages.append(
                    AssistantMessage(role="assistant", content=None, tool_calls=[call])
                )
                messages.append(env.get_response(call))
            elif event["role"] == "user":
                messages.append(UserMessage.text(event["content"]))
            elif event["role"] == "assistant":
                messages.append(AssistantMessage.text(event["content"]))
            else:
                raise ValueError(f"Unsupported event role: {event['role']}")
        task = next(t for t in load_tasks() if t.id == case["task_id"])
        now = datetime.now(timezone.utc).isoformat()
        simulation = SimulationRun(
            id=case["case_id"],
            task_id=task.id,
            start_time=now,
            end_time=now,
            duration=0.0,
            termination_reason=TerminationReason.USER_STOP,
            messages=messages,
        )
        reward = evaluate_simulation(
            simulation, task, EvaluationType.ALL, solo_mode=False, domain=DOMAIN
        )
        return {
            "case_id": case["case_id"],
            "task_id": task.id,
            "kind": case["kind"],
            "execution_mode": "scripted_replay_no_llm",
            "native_reward": reward.reward,
            "fixture_audit": fixture_audit(messages),
            "explanation": case["explanation"],
            "initial_db_hash": initial_hash,
            "final_db_hash": env.get_db_hash(),
            "reward_info": reward.model_dump(mode="json"),
            "messages": [
                m.model_dump(mode="json", exclude_none=True) for m in messages
            ],
        }


def offline_demo():
    results = [replay_case(case) for case in load_cases()]
    expected = {c["case_id"]: c for c in load_cases()}
    for result in results:
        case = expected[result["case_id"]]
        if (
            result["native_reward"] != case["expected_native_reward"]
            or result["fixture_audit"]["passed"] != case["expected_fixture_audit"]
        ):
            raise AssertionError(f"Unexpected control outcome: {result['case_id']}")
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    summary = {
        "execution_mode": "scripted_replay_no_llm",
        "upstream_commit": UPSTREAM_COMMIT,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "llm_calls": 0,
        "reference_cases": sum(r["kind"] == "reference" for r in results),
        "negative_controls": sum(r["kind"] == "negative_control" for r in results),
        "all_control_expectations_met": True,
        "cases": results,
    }
    (output / "offline_results.json").write_text(json.dumps(summary, indent=2) + "\n")
    lines = [
        "# Executed replay report",
        "",
        "**Scripted validation only. No LLM or user simulator was evaluated.**",
        "",
        f"Upstream: `{UPSTREAM_COMMIT}`. Generated: {summary['generated_at_utc']}.",
        "",
        "Native reward uses the task's DB and COMMUNICATE components. Fixture audit is separate, limited to controlled acknowledgements, authentication order, protocol shape, and tool errors.",
        "",
        "| Case | Native reward | Fixture audit |",
        "|---|---:|---|",
    ]
    lines.extend(
        f"| {r['case_id']} | {r['native_reward']:.0f} | {'pass' if r['fixture_audit']['passed'] else 'fail'} |"
        for r in results
    )
    lines += [
        "",
        "All expected reference and negative-control outcomes were reproduced. These are harness checks, not pass^k model scores.",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(
        f"- **{r['case_id']}**: {r['explanation']}"
        for r in results
        if r["kind"] == "negative_control"
    )
    lines += [
        "",
        "## Evidence",
        "",
        "Full tool inputs, actual tool outputs, native evaluator breakdowns and database hashes: [offline_results.json](offline_results.json).",
        "",
        "## Limits",
        "",
        "The fixture audit does not verify proposal details, full ownership rules, arbitrary wording, or all policy obligations. A passing native outcome plus a passing fixture audit is not comprehensive policy compliance. For live runs, inspect the full conversation and user-simulator fidelity separately.",
        "",
    ]
    (output / "REPLAY_REPORT.md").write_text("\n".join(lines))
    print(
        f"Verified {len(results)} scripted cases. 0 LLM calls. Report: results/REPLAY_REPORT.md"
    )


def live(args):
    if args.trials < 1:
        raise ValueError("trials must be positive")
    if not all(m.startswith("openai/") for m in (args.agent_model, args.user_model)):
        raise ValueError(
            "This sample's live entrypoint requires explicit openai/ model names."
        )
    if not args.dry_run:
        key = os.environ.get("SAMPLE_OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "Set SAMPLE_OPENAI_API_KEY to a personally authorized key. Ambient OPENAI_API_KEY is not used."
            )
        os.environ["OPENAI_API_KEY"] = key
        for name in (
            "OPENAI_API_BASE",
            "OPENAI_BASE_URL",
            "OPENAI_ORGANIZATION",
            "OPENAI_ORG_ID",
            "OPENAI_PROJECT_ID",
        ):
            os.environ.pop(name, None)
    run_dir = (
        ROOT
        / "results"
        / ("live_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    )
    config = TextRunConfig(
        domain=DOMAIN,
        task_set_name=DOMAIN,
        task_split_name="base",
        llm_agent=args.agent_model,
        llm_user=args.user_model,
        llm_args_agent={"temperature": 0},
        llm_args_user={"temperature": 0},
        num_trials=args.trials,
        max_concurrency=1,
        max_steps=60,
        max_errors=3,
        max_retries=0,
        timeout=180,
        seed=42,
        save_to=str(run_dir),
        enforce_communication_protocol=True,
        auto_review=False,
        verbose_logs=False,
    )
    config.validate()
    if args.dry_run:
        from tau2.runner.build import build_orchestrator

        with offline_network():
            for task in load_tasks():
                build_orchestrator(config, task, seed=42)
        print(
            "Live configurations and 4 orchestrators built. No model/API calls; no live scores."
        )
        return
    from tau2.run import run_domain

    result = run_domain(config)
    (run_dir / "LIVE_RUN_NOTICE.md").write_text(
        "# Live run\n\nThis run evaluates four authored demonstration tasks, not an official leaderboard split. "
        "Review results.json for run termination, reward, costs, and traces. The fixture-only audit is not applied. "
        "Do not infer comprehensive policy compliance or general model performance from four authored tasks.\n"
    )
    print(
        f"Live results saved under {run_dir.name}/. Inspect all trajectories before sharing."
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "offline-demo", help="Replay 11 authored controls with network blocked"
    )
    api = commands.add_parser(
        "live", help="Optional paid API run; requires an explicit personal sample key"
    )
    api.add_argument("--agent-model", required=True)
    api.add_argument("--user-model", required=True)
    api.add_argument("--trials", type=int, default=1)
    api.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.command == "offline-demo":
        offline_demo()
    else:
        live(args)


if __name__ == "__main__":
    main()
