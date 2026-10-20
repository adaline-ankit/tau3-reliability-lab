# Experiment comparison

Each row belongs to its own declared run. Different models, customer protocols, and trial scopes are not pooled into one performance score. All listed attempts, including failures, remain visible.

| Run | Model | Customer protocol | Planned / attempted | Calls |
|---|---|---|---|---:|
| [codex_20261020T173011096826Z](codex_20261020T173011096826Z/REPORT.md) | gpt-5.6-sol | baseline_before_confirmation_guard | 4 / 4 | 7 |
| [codex_20261020T173827795034Z](codex_20261020T173827795034Z/REPORT.md) | gpt-5.6-luna | baseline_before_confirmation_guard | 1 / 1 | 7 |
| [codex_20261020T174145566328Z](codex_20261020T174145566328Z/REPORT.md) | gpt-5.6-luna | baseline_before_confirmation_guard | 3 / 3 | 22 |
| [codex_20261020T175014927690Z](codex_20261020T175014927690Z/REPORT.md) | gpt-5.6-luna | confirmation_guard_v1 | 1 / 1 | 11 |
| [codex_20261020T185123068419Z](codex_20261020T185123068419Z/REPORT.md) | gpt-5.6-luna | confirmation_guard_v2 | 4 / 4 | 41 |

## codex_20261020T173011096826Z

| Task | Native reward | DB match | Communication | Termination | Possible early customer stop |
|---|---:|---|---:|---|---|
| sample_01_cancel_pending | None | None | n/a | infrastructure_error | False |
| sample_02_refuse_delivered | None | None | n/a | infrastructure_error | False |
| sample_03_exchange_variant | None | None | n/a | infrastructure_error | False |
| sample_04_partial_return | None | None | n/a | infrastructure_error | False |

## codex_20261020T173827795034Z

| Task | Native reward | DB match | Communication | Termination | Possible early customer stop |
|---|---:|---|---:|---|---|
| sample_01_cancel_pending | 0.0 | False | 0.0 | user_stop | True |

## codex_20261020T174145566328Z

| Task | Native reward | DB match | Communication | Termination | Possible early customer stop |
|---|---:|---|---:|---|---|
| sample_02_refuse_delivered | 1.0 | True | 1.0 | user_stop | False |
| sample_03_exchange_variant | 0.0 | False | 0.0 | user_stop | True |
| sample_04_partial_return | 0.0 | False | 0.0 | user_stop | True |

## codex_20261020T175014927690Z

| Task | Native reward | DB match | Communication | Termination | Possible early customer stop |
|---|---:|---|---:|---|---|
| sample_01_cancel_pending | 1.0 | True | 1.0 | user_stop | False |

## codex_20261020T185123068419Z

| Task | Native reward | DB match | Communication | Termination | Possible early customer stop |
|---|---:|---|---:|---|---|
| sample_01_cancel_pending | 1.0 | True | 1.0 | user_stop | False |
| sample_02_refuse_delivered | 1.0 | True | 1.0 | user_stop | False |
| sample_03_exchange_variant | 0.0 | True | 0.0 | user_stop | False |
| sample_04_partial_return | 1.0 | True | 1.0 | user_stop | False |

The early-stop flag is a narrow diagnostic: the customer stopped immediately after an assistant message containing confirmation/proceed wording. This includes imperative requests without a question mark. Inspect the actual customer text and provider response before attributing cause. It is not a general simulator-fidelity classifier.

DB and communication are shown separately: a zero native reward can arise from either selected component. A missing required substring is not by itself proof that a semantically correct completion statement was false. Inspect the actual statement before attributing an agent reasoning failure.

Missing native reward is shown as null/None for unscored infrastructure failures. Benchmark counting conventions may assign failed trials zero, but that convention does not turn infrastructure outages into evidence of reasoning failure. Elapsed run time includes CLI startup, network, model time and intentional pacing; it is not raw model-inference latency.
