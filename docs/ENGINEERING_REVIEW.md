# Engineering review and regression evidence

Reviewed 21 October 2026. Changes are limited to the independent transport and participant adapters. Public retail tools, task targets, policy, and native evaluator remain unchanged.

## Bugs reproduced before their fixes

| Case | Before | After |
|---|---|---|
| Customer grants consent after “Please confirm…” and sets done | Imperative request without a question mark could evade the stop guard | Recorded as a customer protocol error; no fabricated continuation |
| Customer embeds the native stop marker in its text | Could terminate even with done false | Model-authored reserved marker rejected; only the adapter owns that marker |
| Agent supplies a confirmation receipt and asks whether anything else is needed | Broad keyword matching could reject a legitimate final customer stop | Receipt wording alone does not count as a request for action authorization |
| Agent returns malformed nested argument JSON | Could be recorded as infrastructure failure | Classified as an agent protocol error |
| Participant output fails its JSON schema | Could be recorded as infrastructure failure | Classified as agent or customer error at the corresponding participant boundary |
| CLI emits a rate-limit diagnostic only on stderr | Could be classified as a generic process failure | stdout and stderr both contribute to the classification; raw diagnostics stay private |

The regression tests were run before the relevant fix and failed, then passed after implementation. The full suite contains 33 tests, including integration through the real native orchestrator with deterministic participant stubs. Tests do not call a model.

A policy inspection also clarified the scripted exchange reference and its wrong-color counterpart to explicitly remind the customer to confirm all items before the one-time exchange. Both fixtures changed together; all eleven expected native outcomes remained unchanged. This is a reference-quality correction, distinct from the real model run and its unchanged grading criteria.

## Codex static-review receipts

Three Codex static reviews raised the nested-JSON type classification, schema-error attribution, and stderr-classification issues. All three were addressed and regression-tested. The review requests and responses are retained, including their original `request_changes` verdicts:

- [First review](../results/code_review_20261020T184711703988Z/results.json)
- [Second review](../results/code_review_20261020T184828648498Z/results.json)
- [Third review](../results/code_review_20261020T185007125171Z/results.json)

The reviewers performed static inspection; they did not execute tests. The initial non-string argument example is additionally constrained by transport schema validation in normal operation; fault injection checks defensive classification at the participant boundary as well. A resolved finding does not retroactively turn the reviewer's original verdict into approval.

## Final source inspection

**Correctness:** the stop guard distinguishes explicit requests from receipt wording, while output errors preserve role attribution. Separate DB and communication columns expose the selected native reward components. Missing scores and unknown durations are displayed as unavailable.

**Readability:** changes stay in existing participant and transport boundaries. There is no new framework or duplicate evaluator.

**Architecture:** agent inputs remain policy/tools/conversation; customer inputs remain scenario/customer-visible dialogue. Evaluator actions remain outside their supplied prompts. Native state changes and reward still belong to upstream code.

**Security and provenance:** API-key environment variables remain excluded. Native Codex tools remain disabled and emitted tool events are rejected. Raw process diagnostics and outreach drafts remain outside the public inventory. The reserved stop marker is controlled by the adapter.

**Runtime bounds:** explicit call budgets, pacing, per-call timeouts, and native step/time limits remain in force. Failed episodes retain partial traces when handled normally. An abrupt process kill before a result write is not covered by a durable per-turn journal.

No additional blocking defect was found in this source inspection. This is an engineering review, not a security or compliance certification.

## Remaining limits

The English confirmation guard is a lexical protocol check, not a complete consent or intent classifier. Managed Codex runtime context is not fully controlled. A same-family model reviewer can miss defects. One trial per task does not estimate repeated-trial consistency, `pass^k`, or population performance. Source hashes identify the exact code/data used by each declared run; later code changes do not relabel earlier attempts.
