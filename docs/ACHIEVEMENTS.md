# What this sample demonstrates

Updated 21 October 2026. This is an independent, AI-assisted work sample built with public Sierra components and newly authored synthetic fixtures.

## The problem

A support agent can say the right thing while doing the wrong thing, perform the right update without permission, or receive a zero because the evaluation machinery stopped too early. A useful benchmark must make those cases distinguishable.

## The system, from input to evidence

1. **Define a synthetic world.** Two fictional customers, three products, and five orders supply inspectable initial state. Every trial gets a fresh environment.
2. **Author four tasks.** Cancellation, delivered-order refusal, variant exchange, and partial return each specify customer intent and separate evaluator targets.
3. **Run native tools.** Public retail implementations execute order reads and updates. The model proposes a tool call; the environment performs it.
4. **Evaluate the outcome.** Native evaluation compares predicted versus target database state and required communication. Its selected components remain unchanged.
5. **Inspect policy separately.** Controlled diagnostics and a separate model review inspect obligations that final-state reward may miss. They do not replace native reward.
6. **Validate the test machinery.** Explicit stop handling, participant-schema validation, saved termination reasons, source hashes, and regression tests make failures attributable.
7. **Retain receipts.** Public traces, call inputs/outputs, reward breakdowns, and failed attempts allow a reviewer to check each claim.

## What we learned from the controls

Four reference replays establish reachable intended outcomes. Seven negative controls test missing state changes, wrong variants, wrong refund destinations, unwanted extra returns, missing consent, missing identity lookup, and an invalid cancellation attempt.

Three designed policy violations still receive native outcome reward 1. This demonstrates the scope of the selected DB and communication reward components. It does not establish a defect rate for real agents or a claim about every task in the full benchmark.

## What we learned from real model runs

The original customer simulator sometimes approved an action and ended the conversation in the same turn. The native orchestrator therefore stopped before execution. We preserved those failed trials, clarified the customer instruction, and recorded a successful cancellation rerun.

The current engineering increment strengthens the narrow English confirmation guard to cover imperative requests, rejects model-authored native stop markers, avoids treating confirmation receipts as new requests, and distinguishes participant output errors from infrastructure failures. Regression tests reproduce each relevant failure before the fix.

Current model-run coverage and outcomes are recorded in [EXPERIMENT_STATUS.md](EXPERIMENT_STATUS.md). Follow the linked receipts rather than assuming every authored scenario has passed a live trial.

The completed guard-v2 suite has one real model trial for each of the four tasks. All four target database states matched; three received native reward 1. Exchange received 0 because our communication criterion required a literal phrase that the model paraphrased. The trace also needs a separate policy judgment about the omitted all-items reminder. Read the [analysis](../results/codex_20261020T185123068419Z/ANALYSIS.md) before describing this as complete task success or compliance.

## One real cancellation, explained

The guard-v2 [cancellation transcript](../results/codex_20261020T185123068419Z/sample_01_cancel_pending_trial_0.md) makes the mechanism concrete:

| Stage | Recorded event | What it establishes |
|---|---|---|
| Request | Customer asks to cancel order #W8100001 and use the original card | Desired operation and refund preference |
| Identity | Agent asks for email, then calls `find_user_id_by_email` | Connects customer-provided information to a synthetic account |
| Inspection | `get_order_details` returns the pending hoodie order and owner | Supplies actual order state and ownership information |
| Proposal | Agent explains the correct order, reason, 40.00 refund, and destination | Makes the proposed change explicit before consent |
| Confirmation | Customer approves and does not end the conversation | Allows the agent a turn to perform the operation |
| Execution | `cancel_pending_order` returns cancelled status and a 40.00 original-card refund record | Demonstrates the actual state change in the synthetic environment |
| Completion | Agent reports cancellation; customer then stops | Completes the conversation after execution |
| Evaluation | DB = 1 and COMMUNICATE = 1, so native reward = 1 | Meets this task's selected native scoring contract |

The tool result records a simulated refund; no real payment moved. A passing native score does not by itself establish every policy obligation or repeated-trial reliability.

## Why reviewer agreement is not enough

The separate Codex reviewer agreed with four selected control labels but missed the original premature customer stop when assessing customer fidelity. Its raw judgment is preserved. This is evidence that an LLM reviewer requires its own validation, not proof of comprehensive policy or simulator checking.

## What belongs to this sample versus upstream

Original work: synthetic state, scenarios, reference and negative-control traces, environment glue, Codex participants/transport, diagnostics, reporting, packaging, tests, and explanation.

Upstream: public task/data schemas, retail tool implementations, environment base, native text orchestrator, native evaluator, and an attributed policy. Details and the exact commit are in [PROVENANCE.md](../PROVENANCE.md).

The public τ³ generation includes voice and knowledge capabilities. This sample's scope is text retail. See the [pinned upstream overview](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/README.md).

## What a client can assess

The sample demonstrates task authoring, native tool/evaluator integration, model execution, controlled failure analysis, reproducibility, and careful interpretation of evidence. It is a basis for a technical discussion, not an official leaderboard result, a broad performance estimate, or proof of historical employer work.

For a live discussion, explain one cancellation trace from request through database mutation and reward. Then show the omitted-confirmation control and the premature-stop trace. Those three examples distinguish execution truth, authorization, and evaluation validity.
