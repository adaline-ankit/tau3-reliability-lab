# τ³ Reliability Lab

Audit agent outcomes, policy obligations, and execution evidence separately.

An independent, AI-assisted work sample built on Sierra's public τ³-bench code. Four original retail tasks use a synthetic database. Native tools, orchestration, and evaluation remain upstream. Codex-only participants provide a model transport through saved ChatGPT login; no separately billed API key is needed.

**Start here:** [walkthrough](docs/WALKTHROUGH.md) · [sample report](SAMPLE_REPORT.md) · [executed status](docs/EXPERIMENT_STATUS.md) · [discussion guide](docs/DISCUSSION_GUIDE.md)

## The useful result

Three crafted policy violations can receive native outcome reward 1: cancellation without confirmation, cancellation without identity lookup, and an invalid cancellation attempt that leaves the database unchanged. We reproduce those cases and keep policy evidence separate from native reward.

This is a finding about these constructed tasks and this reward configuration. It is not a claim that the complete benchmark is broken or that real agents fail at that frequency.

Actual Codex runs also exposed a customer-simulator defect: it ended the conversation while granting consent. A separately recorded cancellation rerun with a clarified stop instruction completed the real tool action and received native reward 1. Earlier failures remain visible. [Read all attempts and their limits](docs/EXPERIMENT_STATUS.md).

| Evidence layer | What it establishes | Supplied artifact |
|---|---|---|
| Scripted native replay | Task targets and grader behavior are executable | [11 cases and raw traces](results/REPLAY_REPORT.md) |
| Codex agent/customer run | Model-generated decisions and actual tool execution, when a full trial completes | [Current experiment status](docs/EXPERIMENT_STATUS.md) |
| Separate semantic review | Evidence-backed model judgments; requires calibration and human judgment | `trace_review.py` |
| Offline regression tests | Integration, prompt boundaries, transport receipts, packaging safety | [Verification](VERIFICATION.md) |

## Four authored scenarios

| Task | Desired behavior | Failure under test |
|---|---|---|
| Pending cancellation | Correct order, valid reason, original-card refund record | False success claim or missing consent |
| Delivered-order refusal | Explain restriction, preserve state | Prohibited cancellation attempt |
| Variant exchange | Blue M hoodie → blue L; record 5.00 difference | Tool-valid wrong color |
| Partial return | Bottle only, keep mug, original card | Wrong refund destination or extra returned item |

All identities, payment references, addresses, and records are synthetic. Files: [tasks](data/tasks.json), [database](data/retail_db.json), [policy](data/policy.md).

## Reproduce without model calls

Requires Git and [uv](https://docs.astral.sh/uv/getting-started/installation/). Setup downloads the public pinned dependency and installs its core lockfile. Replay runs with outbound socket connections blocked.

```bash
python3 bootstrap.py
python3 bootstrap.py --check
.upstream/.venv/bin/python -m unittest discover -s tests -v
.upstream/.venv/bin/python sample.py offline-demo
python3 package_sample.py --check
```

The public dependency requires Python `>=3.12,<3.14`; uv selects an interpreter. The repository's CI uses these offline checks and no model credentials.

## Run Codex participants

Install Codex CLI and authenticate using your ChatGPT account. This adapter was exercised with `codex-cli 0.145.0`. Its flags must be supported by your installed version. Choose a CLI-supported model slug; desktop aliases and CLI model names can differ.

```bash
codex login status
.upstream/.venv/bin/python codex_runner.py \
  --model gpt-5.6-sol --trials 1 --max-calls 80 --interval 20
```

The model name is the experiment's selected slug, not a guarantee of future availability. You may scope a pilot with `--task sample_01_cancel_pending`. The interval is the minimum time between call starts. Codex allowance is consumed; a trustworthy per-call dollar cost is unavailable here. API-key environment variables are excluded from the child process and saved ChatGPT login is required.

The native text orchestrator manages a `CodexAgent`, a separate `CodexCustomer`, and the real retail environment. The agent receives policy, tool schemas, and its visible conversation. The customer receives scenario instructions and customer-visible dialogue. Neither receives evaluator criteria or reference actions in its supplied prompt. Managed Codex runtime instructions can still be injected; these controls do not prove complete system-context isolation.

The adapter uses JSON-schema-constrained final responses. The harness executes the returned tool decisions. Native Codex tool execution is disabled in configuration and emitted native-tool events are rejected. Temporary working directories contain no task files. The adapter does not expose sampling temperature or seed; it is a custom transport, so runs are not directly comparable to an official leaderboard configuration.

Every attempted trial is saved. A transport failure stops the batch; it does not trigger an automatic whole-trial retry. A later rerun produces a separate evidence directory. Infrastructure failures must not be presented as evidence of a model's reasoning failure.

## Review traces separately

```bash
.upstream/.venv/bin/python trace_review.py \
  --model gpt-5.6-sol --calibrate \
  --run results/YOUR_CODEX_RUN/results.json
```

Calibration reviews the eleven authored controls with their labels withheld. Findings must cite valid transcript indexes. Reviewer results never overwrite native reward. Agent, customer, and reviewer may use the same model family, so correlated mistakes remain possible. Check [experiment status](docs/EXPERIMENT_STATUS.md) before claiming a review was executed.

## Native reward and limits

The authored tasks use `DB` and `COMMUNICATE` in `reward_basis`. Reference actions derive the target database state; exact action matching is not required. Communication uses upstream substring checks in this pinned version. A separate fixture audit checks controlled acknowledgement order, authentication order, message shape, and tool errors. It is deliberately unsuitable for grading arbitrary live consent wording.

A high native reward is not comprehensive policy compliance. One completed trial is not a consistency estimate. `pass^k` concerns success across all k attempts; it differs from `pass@k`, which concerns at least one success.

## Version, provenance, and sharing

Public upstream: [Sierra τ-bench](https://github.com/sierra-research/tau2-bench/tree/fc0055dc4e0a316c3f83133267fbd6faaa770992), release `v1.0.1`, commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`. This is the τ³ generation in the repository still named `tau2-bench`. The sample covers text retail. Voice and banking knowledge retrieval remain outside its tested scope.

Original work and imported contracts are listed in [PROVENANCE.md](PROVENANCE.md). The adapted policy retains Sierra's [license](THIRD_PARTY_LICENSE.txt). New files are offered under [MIT](LICENSE). The sample contains no employer implementation, records, prompts, or historical metrics.

`PUBLIC_FILES.json` lists the reviewed sharing files. Packaging rejects traversal, symlinks, environment files, dependency checkouts, private logs, and obvious credential patterns. It is an inventory boundary, not a substitute for content review. Private outreach notes remain local.

```bash
python3 package_sample.py
```

The ZIP includes a SHA-256 manifest. Code, fixtures, reports, and documentation are intended to be inspectable before a client discussion.
