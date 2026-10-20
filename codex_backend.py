"""Structured Codex CLI transport; uses saved ChatGPT login, never an API key."""

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import jsonschema

BASE_INSTRUCTIONS = """You are a participant in a synthetic customer-support simulation.
Follow the role and input supplied in the user message. Return only the requested
JSON object. Never use native Codex tools, shell, files, web, connectors, skills,
or other agents. The supplied conversation and tool schemas are your entire
information source. A tool decision is JSON for the caller to execute; it is not
a native Codex tool invocation. Do not discuss the experiment with the customer.
"""

AGENT_SCHEMA = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": ["message", "tool"]},
        "text": {"type": "string"},
        "tool_name": {"type": "string"},
        "arguments_json": {"type": "string"},
    },
    "required": ["kind", "text", "tool_name", "arguments_json"],
    "additionalProperties": False,
}
USER_SCHEMA = {
    "type": "object",
    "properties": {"text": {"type": "string"}, "done": {"type": "boolean"}},
    "required": ["text", "done"],
    "additionalProperties": False,
}


class CodexTransportError(ValueError):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(f"Codex transport {kind}; private diagnostic retained")


def failure_kind(stdout):
    return (
        "rate_limited"
        if "429" in stdout or "Too Many Requests" in stdout
        else "process_failed"
    )


def participant_prompt(role, instructions, tools, conversation):
    if role not in {"agent", "customer"}:
        raise ValueError("Unknown participant role")
    rules = (
        "Act as the retail support agent. Follow policy. Choose exactly one tool call "
        "or one customer-facing message. For tools set text empty and arguments_json "
        "to a JSON object string. For messages set tool_name empty and arguments_json "
        "to '{}'. Do not invent tool results. Authenticate and inspect order ownership "
        "before private actions. Obtain explicit consent after explaining action details."
        if role == "agent"
        else "Act as the customer, following your scenario. You do not see private tool "
        "calls or database state. Do not invent unknown IDs, tool results, or facts. "
        "Answer naturally; only confirm the exact action you want after its details "
        "are explained. Set done true only after completion, accepted refusal, or "
        "transfer. Never set done true while granting consent or answering an action "
        "confirmation request: the agent still needs a turn to execute it and report "
        "the result. Your first turn must state your request rather than end the call."
    )
    return json.dumps(
        {
            "role": role,
            "rules": rules,
            "instructions": instructions,
            "available_tools": tools,
            "conversation": conversation,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


def parse_codex_output(stdout, answer_text):
    events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    if any(e.get("type") in {"turn.failed", "error"} for e in events):
        raise ValueError("Codex turn failed; inspect private transport log")
    for event in events:
        item = event.get("item", {})
        if item and item.get("type") not in {"agent_message", "reasoning"}:
            raise ValueError("Codex attempted a native tool or unexpected item")
    completed = [e for e in events if e.get("type") == "turn.completed"]
    if len(completed) != 1:
        raise ValueError("Missing unique successful completion receipt")
    answer = json.loads(answer_text)
    if not isinstance(answer, dict):
        raise ValueError("Codex answer must be a JSON object")
    return answer, completed[0].get("usage", {})


class CodexClient:
    def __init__(
        self, model=None, effort="low", timeout=120, max_calls=80, interval=20
    ):
        self.binary = shutil.which("codex")
        if not self.binary:
            raise ValueError("Install Codex CLI and run codex login first")
        self.model = model
        self.effort = effort
        self.timeout = timeout
        self.max_calls = max_calls
        self.interval = interval
        self._last_started = 0.0
        self.calls = []
        self._attempts = 0
        self.version = subprocess.run(
            [self.binary, "--version"], check=True, capture_output=True, text=True
        ).stdout.strip()
        login = subprocess.run(
            [self.binary, "login", "status"], capture_output=True, text=True
        )
        if login.returncode or "ChatGPT" not in login.stdout + login.stderr:
            raise ValueError(
                "This runner requires a saved ChatGPT login; API-key authentication is excluded"
            )

    def complete(self, prompt, schema, role):
        if self._attempts >= self.max_calls:
            raise ValueError("Declared Codex call limit reached")
        delay = self.interval - (time.monotonic() - self._last_started)
        if delay > 0:
            time.sleep(delay)
        self._last_started = time.monotonic()
        self._attempts += 1
        started = time.monotonic()
        record = {
            "call": self._attempts,
            "role": role,
            "requested_model": self.model,
            "effort": self.effort,
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "prompt": json.loads(prompt),
            "status": "started",
        }
        self.calls.append(record)
        # Only auth-related HOME/CODEX_HOME locations are inherited, never API keys.
        env = {
            key: value
            for key, value in os.environ.items()
            if key
            in {
                "PATH",
                "HOME",
                "USER",
                "LOGNAME",
                "TMPDIR",
                "LANG",
                "LC_ALL",
                "CODEX_HOME",
                "SSL_CERT_FILE",
                "SSL_CERT_DIR",
                "HTTPS_PROXY",
                "HTTP_PROXY",
                "NO_PROXY",
            }
        }
        with tempfile.TemporaryDirectory(prefix="tau3-codex-turn-") as tmp:
            work = Path(tmp)
            schema_path, answer_path = work / "schema.json", work / "answer.json"
            instructions_path = work / "instructions.md"
            schema_path.write_text(json.dumps(schema))
            instructions_path.write_text(BASE_INSTRUCTIONS)
            command = [
                self.binary,
                "exec",
                "--ignore-user-config",
                "--ignore-rules",
                "--ephemeral",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--json",
                "--color",
                "never",
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(answer_path),
                "--cd",
                str(work),
            ]
            if self.model:
                command += ["--model", self.model]
            config = {
                "approval_policy": '"never"',
                "project_doc_max_bytes": "0",
                "web_search": '"disabled"',
                "skills.max_context_tokens": "1",
                "tools.view_image": "false",
                "model_reasoning_effort": json.dumps(self.effort),
                "model_instructions_file": json.dumps(str(instructions_path)),
            }
            for feature in (
                "shell_tool",
                "shell_snapshot",
                "apps",
                "plugins",
                "remote_plugin",
                "multi_agent",
                "memories",
                "hooks",
                "browser_use",
                "computer_use",
                "image_generation",
                "workspace_dependencies",
                "skill_search",
            ):
                config[f"features.{feature}"] = "false"
            for key, value in config.items():
                command += ["-c", f"{key}={value}"]
            command += ["-"]
            try:
                result = subprocess.run(
                    command,
                    input=prompt,
                    text=True,
                    capture_output=True,
                    timeout=self.timeout,
                    env=env,
                )
                if result.returncode:
                    private = Path(__file__).resolve().parent / ".runs" / "transport"
                    private.mkdir(parents=True, exist_ok=True)
                    stem = f"call_{self._attempts}_{time.time_ns()}"
                    (private / (stem + ".jsonl")).write_text(result.stdout)
                    (private / (stem + ".stderr.txt")).write_text(result.stderr)
                    record["private_diagnostic"] = ".runs/transport/" + stem
                    record["failure_kind"] = failure_kind(result.stdout)
                    raise CodexTransportError(record["failure_kind"])
                answer, usage = parse_codex_output(
                    result.stdout, answer_path.read_text()
                )
                jsonschema.validate(answer, schema)
                record.update(status="completed", response=answer, usage=usage)
                return answer
            except Exception as exc:
                record.update(status="failed", error_type=type(exc).__name__)
                raise
            finally:
                record["elapsed_seconds"] = round(time.monotonic() - started, 3)
