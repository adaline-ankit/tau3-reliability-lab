# Independent τ-bench sample

Prepared for a freelance benchmarking discussion. Date: 20 October 2026.

## Purpose

Demonstrate a complete, inspectable path from an authored customer scenario to actual tool execution, independently replayed state evaluation, and a concise explanation of failures. The sample uses public τ-bench components and newly created synthetic records. It was prepared with AI coding assistance and contains no Adaline implementation, data, prompts, logs, or historical results.

## What was built

Four retail tasks cover cancellation, policy refusal, variant selection, and a partial return with a specific refund destination. Each task includes user-simulator instructions, relevant policy context, reference actions, communication requirements, and an explicit reward basis. The scenario specifications are in [tasks.json](data/tasks.json).

The environment is small enough to inspect: two fictional accounts, three products, five orders, and synthetic payment references. Upstream `RetailTools` executes against that database without modification. A separate `portfolio_retail` registry entry keeps the sample dataset separate from the bundled retail benchmark.

## Evaluation mechanism

1. Create a fresh environment from the synthetic fixture.
2. Execute a scripted trajectory and record actual tool outputs.
3. Ask upstream `evaluate_simulation(..., EvaluationType.ALL)` to replay the trajectory independently.
4. Replay the task's reference actions on another fresh environment to derive the target state.
5. Compare database hashes and evaluate required communication strings.
6. Report native reward separately from limited fixture-protocol diagnostics.

These tasks explicitly use `DB` and `COMMUNICATE` as their reward basis. Native reward is their product. Reference actions define the target database state; they do not require an exact tool sequence because `ACTION` is not in the basis. Communication is substring matching in this pinned version. Neither check is a complete policy or truthfulness evaluation.

## Executed evidence

| Check | Observed result |
|---|---|
| Native schema validation | All four tasks accepted |
| Four scripted reference cases | All receive native reward 1 and pass the limited fixture audit |
| Seven intentional negative controls | All reproduce the specified native reward and audit outcome |
| Regression tests | See `VERIFICATION.md` for the executed command and final test count |
| Live configuration smoke check | All four native orchestrators construct with outbound connections blocked |
| Live model evaluation | Not run; zero LLM calls in supplied results |

The [executed report](results/REPLAY_REPORT.md) records each case. [Raw evidence](results/offline_results.json) includes actual tool arguments, tool outputs, full conversations, reward breakdowns, and database hashes. The generated `SimulationRun` objects describe scripted fixtures; their zero duration is a placeholder, not a measured latency.

## Failure analysis

| Control | Native reward | Interpretation |
|---|---:|---|
| Claim cancellation without calling its tool | 0 | Conversation text does not substitute for the required database update |
| Exchange for red instead of blue | 0 | Tool accepts a valid alternative, but target state encodes the user's requested variant |
| Refund to gift card instead of original card | 0 | Tool-valid choice can still violate the task |
| Return mug as well as bottle | 0 | Unrequested state changes invalidate success |
| Cancel without explicit confirmation | 1 | Final state and required wording can pass while consent is missing |
| Cancel without identity lookup | 1 | Outcome reward does not establish authentication was performed |
| Attempt prohibited delivered-order cancellation, then correctly refuse | 1 | Tool rejects the update; unchanged end state and required wording can still pass |

The last three controls are intentional demonstrations of evaluator scope. The separate fixture audit flags them, while preserving the native reward in the report. It checks controlled acknowledgement order, successful email lookup before private calls, tool errors, and basic one-tool-per-message shape. It does not interpret arbitrary consent wording, validate proposal details, enforce every ownership rule, or certify overall compliance.

## What a live experiment would add

Run an LLM agent against an independently prompted LLM user simulator, preserve model identifiers and parameters, repeat each task, and inspect all failures. Report task success, policy review, simulator errors, termination, latency, and cost separately. The native live entrypoint is wired and construction-tested; API execution is still pending.

For repeated runs, τ-bench's `pass^k` concerns consistency across all k attempts. It differs from `pass@k`, which concerns at least one success. With n trials and c successes for one task, the usual finite-sample estimator is `C(c, k) / C(n, k)` for `n >= k`, averaged across tasks. The supplied scripted cases are not independent model trials, so no model `pass^k` is reported. Four authored scenarios also do not support a general performance claim or comparison to an official leaderboard.

## Reproduction and scope

Public dependency: [Sierra τ-bench, pinned commit](https://github.com/sierra-research/tau2-bench/tree/fc0055dc4e0a316c3f83133267fbd6faaa770992). Installation and commands: [README.md](README.md). Source attribution: [PROVENANCE.md](PROVENANCE.md).

This sample demonstrates task authoring, native integration, reference validation, negative-control design, and evidence-led failure analysis. It contains no live model performance result and makes no claim about an employer's system.
