"""Codex agent and customer participants inside the native τ³ text orchestrator."""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone

from codex_backend import AGENT_SCHEMA, USER_SCHEMA, CodexClient, participant_prompt
from sample import DOMAIN, ROOT, UPSTREAM_COMMIT, get_environment, load_tasks
from tau2.agent.base_agent import HalfDuplexAgent
from tau2.data_model.message import (
    AssistantMessage,
    MultiToolMessage,
    ToolCall,
    UserMessage,
)
from tau2.data_model.simulation import SimulationRun, TerminationReason
from tau2.orchestrator.orchestrator import Orchestrator
from tau2.runner.simulation import run_simulation
from tau2.user.user_simulator_base import STOP, HalfDuplexUser


class CustomerProtocolError(ValueError):
    pass


class AgentProtocolError(ValueError):
    pass


def validate_customer_stop(previous_agent_text, answer):
    """Narrow English confirmation guard; rejects a stop, never fabricates consent."""
    if STOP in answer["text"]:
        raise CustomerProtocolError("Customer text contains a reserved stop marker")
    asks_confirmation = re.search(
        r"\b(?:please|kindly)\s+(?:confirm|approve|authorize)\b"
        r"|\b(?:do|can|could|will|would)\s+you\s+(?:please\s+)?(?:confirm|approve|authorize)\b"
        r"|\breply\b[^\n]*\byes\b"
        r"|\b(?:do|would)\s+you\b[^\n?]*\bproceed\b",
        previous_agent_text,
        re.IGNORECASE,
    )
    grants_consent = re.match(
        r"\s*(yes\b|yep\b|yeah\b|i (confirm|approve)\b|confirmed\b|go ahead\b|please proceed\b)",
        answer["text"],
        re.IGNORECASE,
    )
    if answer["done"] and asks_confirmation and grants_consent:
        raise CustomerProtocolError(
            "Customer cannot stop while answering an action confirmation request"
        )


def compact_message(message):
    result = {"role": message.role}
    if message.content is not None:
        result["content"] = message.content
    if getattr(message, "tool_calls", None):
        result["tool_calls"] = [
            {"name": call.name, "arguments": call.arguments, "id": call.id}
            for call in message.tool_calls
        ]
    if message.role == "tool":
        result.update(id=message.id, error=message.error)
    return result


class CodexAgent(HalfDuplexAgent):
    def __init__(self, client, tools, domain_policy):
        super().__init__(tools=tools, domain_policy=domain_policy)
        self.client = client
        self.schemas = [tool.openai_schema for tool in tools]
        self.names = {tool.name for tool in tools}

    def get_init_state(self, message_history=None):
        return list(message_history or [])

    def set_seed(self, seed):
        # CLI does not expose a sampling seed. Do not imply native seed controls it.
        pass

    def generate_next_message(self, message, state):
        state.extend(
            message.tool_messages
            if isinstance(message, MultiToolMessage)
            else [message]
        )
        prompt = participant_prompt(
            "agent",
            self.domain_policy,
            self.schemas,
            [compact_message(m) for m in state],
        )
        answer = self.client.complete(prompt, AGENT_SCHEMA, "agent")
        try:
            arguments = json.loads(answer["arguments_json"])
        except (json.JSONDecodeError, TypeError) as exc:
            raise AgentProtocolError("Decision arguments are not valid JSON") from exc
        if answer["kind"] == "tool":
            if answer["text"] or answer["tool_name"] not in self.names:
                raise AgentProtocolError(
                    "Invalid tool decision: mixed content or unknown tool"
                )
            if not isinstance(arguments, dict):
                raise AgentProtocolError("Tool arguments must be an object")
            result = AssistantMessage(
                role="assistant",
                content=None,
                tool_calls=[
                    ToolCall(
                        id=f"call_{len(state):03}",
                        name=answer["tool_name"],
                        arguments=arguments,
                    )
                ],
            )
        else:
            if not answer["text"].strip() or answer["tool_name"] or arguments != {}:
                raise AgentProtocolError("Invalid customer-facing message")
            result = AssistantMessage.text(answer["text"])
        state.append(result)
        return result, state


class CodexCustomer(HalfDuplexUser):
    def __init__(self, client, instructions):
        super().__init__(instructions=instructions, tools=[])
        self.client = client

    def get_init_state(self, message_history=None):
        return list(message_history or [])

    def set_seed(self, seed):
        pass

    @classmethod
    def is_stop(cls, message):
        return STOP in (message.content or "")

    def generate_next_message(self, message, state):
        if not isinstance(message, AssistantMessage) or message.tool_calls:
            raise CustomerProtocolError(
                "Customer must receive only customer-visible assistant text"
            )
        state.append(message)
        answer = self.client.complete(
            participant_prompt(
                "customer", self.instructions, [], [compact_message(m) for m in state]
            ),
            USER_SCHEMA,
            "customer",
        )
        if not any(isinstance(m, UserMessage) for m in state) and answer["done"]:
            raise CustomerProtocolError("Customer tried to end before making a request")
        if not answer["text"].strip() and not answer["done"]:
            raise CustomerProtocolError("Empty customer turn")
        validate_customer_stop(message.content or "", answer)
        result = UserMessage.text(
            answer["text"] + (" " + STOP if answer["done"] else "")
        )
        state.append(result)
        return result, state


def run_episode(task, client, trial=0):
    environment = get_environment()
    orchestrator = Orchestrator(
        domain=DOMAIN,
        agent=CodexAgent(client, environment.get_tools(), environment.get_policy()),
        user=CodexCustomer(client, str(task.user_scenario)),
        environment=environment,
        task=task,
        max_steps=40,
        max_errors=3,
        timeout=900,
        simulation_id=f"{task.id}_trial_{trial}",
        validate_communication=True,
    )
    try:
        simulation = run_simulation(orchestrator)
    except Exception as exc:
        now = datetime.now(timezone.utc).isoformat()
        reason = (
            TerminationReason.USER_ERROR
            if isinstance(exc, CustomerProtocolError)
            else TerminationReason.AGENT_ERROR
            if isinstance(exc, AgentProtocolError)
            else TerminationReason.INFRASTRUCTURE_ERROR
        )
        simulation = SimulationRun(
            id=f"{task.id}_trial_{trial}",
            task_id=task.id,
            start_time=now,
            end_time=now,
            duration=0.0,
            messages=orchestrator.get_messages(),
            termination_reason=reason,
            info={
                "error_type": type(exc).__name__,
                "error": str(exc),
                "failure_kind": getattr(exc, "kind", "participant_error"),
                "duration_unavailable": True,
            },
        )
    simulation.trial = trial
    # Codex subscription usage has no trustworthy per-call dollar amount here.
    simulation.agent_cost = None
    simulation.user_cost = None
    return simulation


def write_results(output, simulations, client, manifest):
    output.mkdir(parents=True, exist_ok=True)
    payload = {
        "manifest": manifest,
        "complete": len(simulations)
        == len(manifest["task_ids"]) * manifest["trials_per_task"],
        "simulations": [
            s.model_dump(mode="json", exclude_none=True) for s in simulations
        ],
        "calls": client.calls,
    }
    (output / "results.json").write_text(json.dumps(payload, indent=2) + "\n")
    lines = [
        "# Codex model-run report",
        "",
        "Actual model-generated conversations using saved ChatGPT login. Custom Codex transport; four authored text-retail tasks. These are not official leaderboard results.",
        "",
        f"Requested model: `{client.model or 'CLI default (not independently resolved)'}`. CLI: `{client.version}`. Effort: `{client.effort}`.",
        "",
        "| Task | Trial | Native reward | DB match | Communication | Termination | Seconds |",
        "|---|---:|---:|---|---:|---|---:|",
    ]
    for simulation in simulations:
        info = (
            simulation.reward_info.model_dump(mode="json")
            if simulation.reward_info
            else {}
        )
        reward = info.get("reward", "n/a")
        db_match = (info.get("db_check") or {}).get("db_match", "n/a")
        communication = info.get("reward_breakdown", {}).get("COMMUNICATE", "n/a")
        duration = (
            "n/a"
            if (simulation.info or {}).get("duration_unavailable")
            else f"{simulation.duration:.2f}"
        )
        lines.append(
            f"| {simulation.task_id} | {simulation.trial} | {reward} | {db_match} | {communication} | {simulation.termination_reason.value} | {duration} |"
        )
        trace = [
            f"# {simulation.id}",
            "",
            "Model-generated transcript. Tool responses come from the real public implementation and synthetic database.",
            "",
        ]
        for index, message in enumerate(simulation.messages or []):
            trace += [
                f"## {index}: {message.role}",
                "",
                "```json",
                json.dumps(compact_message(message), indent=2),
                "```",
                "",
            ]
        (output / f"{simulation.id}.md").write_text("\n".join(trace))
    successful = sum(
        s.reward_info is not None and s.reward_info.reward == 1.0 for s in simulations
    )
    tokens = {}
    for call in client.calls:
        for key, value in call.get("usage", {}).items():
            if isinstance(value, (int, float)):
                tokens[key] = tokens.get(key, 0) + value
    lines += [
        "",
        f"Attempted {len(simulations)} of {len(manifest['task_ids']) * manifest['trials_per_task']} planned task trials. Run complete: {payload['complete']}.",
        "",
        f"Observed native outcome successes: {successful}/{len(simulations)}. Includes all attempted trials; infrastructure failures count as failures.",
        "",
        f"Codex process calls: {len(client.calls)}. Returned token counters: `{json.dumps(tokens, sort_keys=True)}`.",
        "",
        "Dollar cost is unavailable. Calls consume the user's Codex allowance. Sampling seed and temperature are not exposed by this adapter. One trial per authored task does not estimate consistency across repeated trials or general model performance. Native reward does not certify policy compliance. Agent/customer prompts, visible outputs, tool traces, prompt hashes and token counters are retained in results.json. No reasoning traces or authentication data are exported.",
        "",
    ]
    (output / "REPORT.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", required=True, help="Exact Codex CLI-supported model slug"
    )
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--task", action="append", default=[])
    parser.add_argument("--max-calls", type=int, default=80)
    parser.add_argument(
        "--interval",
        type=float,
        default=20,
        help="Minimum seconds between Codex call starts",
    )
    args = parser.parse_args()
    if args.trials < 1 or args.max_calls < 1 or args.interval < 0:
        parser.error("trials/max-calls must be positive; interval must be nonnegative")
    tasks = load_tasks()
    if args.task:
        unknown = set(args.task) - {task.id for task in tasks}
        if unknown:
            parser.error("Unknown task IDs: " + ", ".join(sorted(unknown)))
        tasks = [task for task in tasks if task.id in args.task]
    client = CodexClient(
        model=args.model, max_calls=args.max_calls, interval=args.interval
    )
    manifest = {
        "mode": "codex_chatgpt_native_orchestrator",
        "upstream_commit": UPSTREAM_COMMIT,
        "requested_model": args.model,
        "cli_version": client.version,
        "effort": client.effort,
        "customer_protocol": "confirmation_guard_v2",
        "backend_source_sha256": hashlib.sha256(
            (ROOT / "codex_backend.py").read_bytes()
        ).hexdigest(),
        "runner_source_sha256": hashlib.sha256(
            (ROOT / "codex_runner.py").read_bytes()
        ).hexdigest(),
        "task_ids": [t.id for t in tasks],
        "trials_per_task": args.trials,
        "max_calls": args.max_calls,
        "call_start_interval_seconds": args.interval,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "task_sha256": hashlib.sha256(
            (ROOT / "data/tasks.json").read_bytes()
        ).hexdigest(),
        "database_sha256": hashlib.sha256(
            (ROOT / "data/retail_db.json").read_bytes()
        ).hexdigest(),
        "policy_sha256": hashlib.sha256(
            (ROOT / "data/policy.md").read_bytes()
        ).hexdigest(),
        "separate_api_keys": False,
        "dollar_cost": None,
    }
    output = (
        ROOT
        / "results"
        / ("codex_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    )
    simulations = []
    stopped = False
    for trial in range(args.trials):
        for task in tasks:
            print(
                f"Running {task.id}, trial {trial}; Codex allowance only",
                file=sys.stderr,
                flush=True,
            )
            simulations.append(run_episode(task, client, trial))
            write_results(output, simulations, client, manifest)
            result = simulations[-1]
            print(
                f"Finished {task.id}: reward={result.reward_info.reward if result.reward_info else 'unscored'}, termination={result.termination_reason.value}",
                file=sys.stderr,
                flush=True,
            )
            if result.termination_reason == TerminationReason.INFRASTRUCTURE_ERROR:
                print(
                    "Batch stopped after infrastructure failure; no automatic trial retries.",
                    file=sys.stderr,
                    flush=True,
                )
                stopped = True
                break
        if stopped:
            break
    print(f"Saved model-run evidence: {output.relative_to(ROOT)}/REPORT.md")


if __name__ == "__main__":
    main()
