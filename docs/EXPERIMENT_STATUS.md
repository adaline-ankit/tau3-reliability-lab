# Experiment status

This file records executed evidence and pending work without treating transport availability as model capability.

## Scripted baseline

All four reference cases and seven designed negative controls reproduce their expected native rewards and fixture-audit outcomes. These are executable harness checks, not model performance trials.

## Codex transport probes

- The desktop alias `gpt-6.1-sol` was rejected by the CLI's ChatGPT backend before generation. No evaluation result was obtained from that request.
- A CLI-default probe returned valid structured output with a successful completion receipt.
- An explicit `gpt-5.6-sol` probe returned valid structured output using saved ChatGPT login. This slug appears in the installed CLI's bundled model catalog.
- These probes test connectivity and output contracts. They are not agent-task evaluations.

## First native-orchestrator batch

Evidence: [report](../results/codex_20261020T173011096826Z/REPORT.md), [full visible run records](../results/codex_20261020T173011096826Z/results.json).

Configuration: four authored tasks, one trial each, requested model `gpt-5.6-sol`, low effort, no separate API key. The first cancellation conversation produced three successful model turns: customer request, agent request for email authentication, and customer email response. The next call and the remaining task attempts exited with process errors. All four task attempts ended as infrastructure errors.

The initial transport version did not retain detailed failed-process diagnostics. A subsequent separate probe retained its diagnostics and returned `429 Too Many Requests`. That establishes a rate limit on the diagnostic request; it does not independently prove the precise cause of every earlier process failure.

The runner was then changed to preserve private failed-process diagnostics and stop a batch after an infrastructure failure. Private raw CLI logs remain outside the public-file inventory. All prior failed task attempts remain in the evidence; they are not silently replaced by a successful rerun.

## Interpretation

No completed Codex agent/customer conversation has yet been established by the first batch. Its zeros do not measure the agent's ability to solve these tasks. Semantic review and live task success require their own completed receipts. Later runs, if available, are recorded separately below.

## Paced Codex pilot

Evidence: [report](../results/codex_20261020T173827795034Z/REPORT.md), [transcript](../results/codex_20261020T173827795034Z/sample_01_cancel_pending_trial_0.md).

A separately declared cancellation pilot used CLI-supported `gpt-5.6-luna`, low effort, one task, one trial, and a 20-second minimum call-start interval. It completed seven model calls and terminated with native `user_stop`. Native reward was 0: the database was unchanged and cancellation completion was not communicated.

The decisive event is transcript message 9. The customer approved cancellation but also set its stop flag, which the adapter converted to `###STOP###`. The native orchestrator therefore ended before the agent could receive that approval and call the cancellation tool. This is direct evidence of premature customer-simulator termination. It does not establish that the agent would have chosen the correct next action if allowed to continue.

## Remaining baseline tasks

Evidence: [report](../results/codex_20261020T174145566328Z/REPORT.md), [raw records](../results/codex_20261020T174145566328Z/results.json).

The separately declared remaining three tasks completed 22 model calls with the same baseline customer protocol. Delivered-order refusal received native reward 1. Exchange and partial return each received native reward 0. Their final customer turns also granted consent and stopped before tool execution: message 11 in the exchange transcript and message 9 in the return transcript.

Combined with the earlier cancellation pilot, these are four authored baseline task attempts, not a representative benchmark suite. Three expose the same simulator termination defect. Neither their zero rewards nor the refusal success establishes general agent reliability.

## Protocol change under test

The customer instruction now explicitly distinguishes granting consent from completion: the agent must still execute the update and report its result. A narrow English guard rejects a customer stop when it simultaneously gives affirmative consent to a preceding confirmation question. It records a participant error rather than inventing a replacement response or silently continuing. Explicit refusal and a normal stop after completion remain allowed by tests.

This guard is not a full intent or simulator-fidelity validator. In particular, its question-mark and wording checks do not cover every imperative confirmation request. A later run uses the updated instruction and guard together, so any observed change cannot be attributed to either component alone. No seed control or repeated statistical comparison is claimed.

## Changed-protocol cancellation rerun

Evidence: [report](../results/codex_20261020T175014927690Z/REPORT.md), [transcript](../results/codex_20261020T175014927690Z/sample_01_cancel_pending_trial_0.md), [full records](../results/codex_20261020T175014927690Z/results.json).

One separately declared cancellation trial used the same `gpt-5.6-luna` model, low effort, and 20-second pacing with the changed customer instruction and guard. It made eleven model calls and received native reward 1, with both DB and communication checks passing.

The decisive events are messages 10–15: the agent proposed the exact cancellation and original-card refund; the customer approved without stopping; the native cancellation tool recorded the order as cancelled and a 40.00 original-card refund; the agent reported completion; the customer then stopped. The narrow question-mark guard did not fire on this imperative proposal. The customer followed the clarified instruction in this observed run.

This is an observed successful task after an explicit protocol change. It is not a causal estimate of improvement: there is one unseeded trial per protocol and other dialogue choices varied. Exchange and partial return were not rerun under this protocol. Do not imply four successful fixed-protocol tasks.

See [experiment comparison](../results/EXPERIMENT_COMPARISON.md) for all nine task attempts across four separately declared runs, including the initial four infrastructure failures. Results are not pooled across models and protocols.

## Executed separate review

Evidence: [review report](../results/review_20261020T175350498796Z/REPORT.md), [raw reviewer calls](../results/review_20261020T175350498796Z/results.json), [observed reviewer limitation](../results/review_20261020T175350498796Z/REVIEW_LIMITATIONS.md).

Six declared reviews completed using Codex `gpt-5.6-luna`: one reference, three policy controls, the original cancellation pilot, and the changed-protocol cancellation rerun. Control labels and native rewards were withheld from reviewer prompts. All four selected control verdicts agreed with their intended labels, with valid evidence indexes. The other seven replay controls were not model-reviewed in this run.

Both cancellation model traces received an agent-policy `pass`. The reviewer also called both customer traces `consistent`, missing the known premature-stop defect in the original pilot. Its raw judgment remains unchanged; the linked limitation annotation explains the conflicting trace evidence. This is why 4/4 designed-control agreement is not full judge validation or independent certification.
