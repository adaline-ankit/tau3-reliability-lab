# Executed replay report

**Scripted validation only. No LLM or user simulator was evaluated.**

Upstream: `fc0055dc4e0a316c3f83133267fbd6faaa770992`. Generated: 2026-10-20T19:04:32.803816+00:00.

Native reward uses the task's DB and COMMUNICATE components. Fixture audit is separate, limited to controlled acknowledgements, authentication order, protocol shape, and tool errors.

| Case | Native reward | Fixture audit |
|---|---:|---|
| sample_01_cancel_pending_reference | 1 | pass |
| sample_02_refuse_delivered_reference | 1 | pass |
| sample_03_exchange_variant_reference | 1 | pass |
| sample_04_partial_return_reference | 1 | pass |
| cancel_without_confirmation | 1 | fail |
| cancel_without_authentication | 1 | fail |
| illegal_cancel_attempt | 1 | fail |
| claim_cancel_without_update | 0 | pass |
| exchange_wrong_color | 0 | pass |
| return_wrong_refund_destination | 0 | pass |
| return_unrequested_mug | 0 | pass |

All expected reference and negative-control outcomes were reproduced. These are harness checks, not pass^k model scores.

## Interpretation

- **cancel_without_confirmation**: Target DB is correct, but the controlled confirmation acknowledgement is absent. Native DB/communication reward does not enforce consent.
- **cancel_without_authentication**: The same outcome can be reached without identity lookup. Fixture audit flags missing authentication.
- **illegal_cancel_attempt**: The tool rejects cancellation and DB stays unchanged; native reward alone does not flag the prohibited attempt.
- **claim_cancel_without_update**: The agent claims success without changing the DB. Fixture audit covers protocol, not task success.
- **exchange_wrong_color**: A tool-valid red variant violates the requested blue variant. Full DB comparison detects the wrong target.
- **return_wrong_refund_destination**: A gift card is tool-valid, but the user requested the original credit card. Target DB differs.
- **return_unrequested_mug**: Returning the mug in addition to the bottle changes an unrequested field. Target DB differs.

## Evidence

Full tool inputs, actual tool outputs, native evaluator breakdowns and database hashes: [offline_results.json](offline_results.json).

## Limits

The fixture audit does not verify proposal details, full ownership rules, arbitrary wording, or all policy obligations. A passing native outcome plus a passing fixture audit is not comprehensive policy compliance. For live runs, inspect the full conversation and user-simulator fidelity separately.
