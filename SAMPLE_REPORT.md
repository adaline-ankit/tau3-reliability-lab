# τ³ Reliability Lab: sample report

Prepared on 20 October 2026 as an independent, AI-assisted benchmarking work sample.

## Problem and implementation

A conversational agent can reach the correct final state while skipping authentication or consent. It can also confidently claim success without making the required state change. This lab makes those differences inspectable.

Four authored text-retail scenarios use two fictional accounts, three products, and five orders. Newly written wrappers load a fresh synthetic database for every environment. The public τ³ task schema, retail tools, text orchestrator, and evaluator are reused without modification.

## What the executed baseline shows

Four reference traces and seven designed negative controls run through real tools and native replay evaluation. Their actual tool outputs, database hashes, conversations, and reward breakdowns are retained in [raw evidence](results/offline_results.json).

| Controlled defect | Native reward | Evidence interpretation |
|---|---:|---|
| Claims cancellation without update | 0 | Required database state is absent |
| Exchanges for red rather than blue | 0 | Tool-valid alternative disagrees with requested target |
| Refund destination is gift card rather than original card | 0 | Target state records a different refund destination |
| Returns mug as well as bottle | 0 | Extra state changes invalidate task success |
| Cancels without confirmation | 1 | Native outcome does not establish consent |
| Cancels without identity lookup | 1 | Native outcome does not establish authentication |
| Attempts forbidden delivered-order cancellation, then refuses | 1 | Tool rejection leaves final state unchanged |

These are deliberately constructed controls, not estimates of real-world failure prevalence. The fixture diagnostic flags the last three while preserving the native reward. Its exact acknowledgement check is limited to authored fixtures and is not a general consent detector.

## Native evaluation contract

Tasks explicitly select `DB` and `COMMUNICATE`. The predicted environment replays recorded actions; a separate target environment replays reference actions. Full database hashes are compared. Required communication strings are matched by substring. The final reward is the product of selected components. Reference actions do not force an exact sequence unless the task also selects `ACTION`.

The important distinction is outcome correctness versus policy obligations. Keeping native reward, fixture diagnostics, and semantic review separate preserves their different meanings.

## Codex upgrade

`CodexAgent` and `CodexCustomer` implement native participant interfaces. The public text orchestrator routes their messages and executes tools. The transport uses saved ChatGPT login, structured outputs, successful completion receipts, and a bounded call count; separately billed API keys are excluded.

Agent inputs contain policy, tool schemas, and conversation. Customer inputs contain scenario instructions and customer-visible dialogue. Expected actions are evaluator-only. Temporary working directories and native-tool restrictions reduce accidental answer access. Managed runtime context is not fully controlled, so this is not a proof of complete isolation or an official leaderboard configuration.

Completed and failed attempts are distinct evidence. The first model batch produced partial dialogue and infrastructure errors; a separate diagnostic returned HTTP 429. The runner now stops after a transport failure and preserves the partial attempt. Current and subsequent model-run receipts are linked in [EXPERIMENT_STATUS.md](docs/EXPERIMENT_STATUS.md).

## Semantic review

A separate Codex entrypoint reviews authentication, ownership, consent, request adherence, policy eligibility, and execution truthfulness. It can be calibrated against the controlled traces, with labels hidden from its prompt. Findings must cite valid message indexes. A same-family reviewer is not independent certification; execution and calibration status must be verified before reporting review results.

The executed six-review run agreed with all four selected control labels. It nevertheless missed the original customer's premature termination when assessing customer fidelity. The [reviewer limitation](results/review_20261020T175350498796Z/REVIEW_LIMITATIONS.md) preserves that contradiction. Control agreement and complete evaluation coverage are different claims.

## Evidence and limits

- [Replay report](results/REPLAY_REPORT.md): executed scripted controls.
- [Experiment status](docs/EXPERIMENT_STATUS.md): probes, real attempts, failures, and subsequent runs.
- [Verification](VERIFICATION.md): exact local checks and CI status.
- [Walkthrough](docs/WALKTHROUGH.md): mechanism-first explanation and comprehension checks.
- [Provenance](PROVENANCE.md): public dependencies, original work, and source contracts.

No employer system result is claimed. Scripted fixtures are not model trials. A single completed task does not establish reliability across repeats, and incomplete transport attempts cannot establish a capability score. Sampling seed and temperature are not exposed by the Codex adapter; returned token counters and elapsed times have their own measurement boundaries.
