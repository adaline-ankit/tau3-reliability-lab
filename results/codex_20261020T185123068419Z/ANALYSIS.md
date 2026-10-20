# Interpret the four-task guard-v2 run

Declared scope: four authored tasks, one trial each, Codex `gpt-5.6-luna`, low effort, 64-call limit, and 20-second minimum call-start interval. All four attempted trials terminated with `user_stop`; 41 model calls completed. The exact manifest, prompts, tool traces, and native rewards are in [results.json](results.json).

| Task | Native DB match | Native communication | Native reward |
|---|---|---:|---:|
| Pending cancellation | True | 1 | 1 |
| Delivered-order refusal | True | 1 | 1 |
| Variant exchange | True | 0 | 0 |
| Partial return | True | 1 | 1 |

These are per-task observations, not a population accuracy estimate. Refusal succeeds by preserving the required state; the other three tasks require mutations.

## The exchange exposes an authored scoring issue

In the [exchange transcript](sample_03_exchange_variant_trial_0.md), the agent authenticated the customer, inspected the account/order/product, proposed the blue-L variant and 5.00 original-card charge, obtained approval, and called the exact target exchange action. The native database comparison and action check both passed.

Message 16 begins: “Your exchange request is confirmed.” The native communication requirement in our authored task is the literal substring `exchange requested`. That substring is absent, so COMMUNICATE is 0 and the selected native reward is 0.

Trace inspection indicates the request status was communicated in different wording. This is evidence that our authored communication requirement is too literal for a meaning-based completion requirement. It is not evidence that the database update failed. The native result remains 0; neither the task criterion nor actor prompt was changed to make this observed run pass.

The lesson for task authoring is to agree the communication acceptance rubric before measuring models, validate plausible paraphrases as well as wrong statements, and distinguish native contract results from separate semantic judgments. Do not tune a scorer on one observed miss and report the same trace as held-out validation.

## State correctness does not establish all policy obligations

The exchange proposal mentions the one-exchange allowance but does not explicitly remind the customer to confirm that all desired exchange items have been provided. The policy requires that reminder. This is a separate policy-review concern even though the target database state is correct. A semantically understandable completion statement does not resolve it.

The authored exchange reference and wrong-color control were subsequently clarified together to include the explicit all-items/one-time reminder. Their intended native outcomes remain unchanged. Those are scripted fixtures; their clarification did not change this model run's task, policy, database, actor prompt, or recorded trace.

The [separate model review](../review_20261020T190556705814Z/REPORT.md) returned policy `pass` for all four traces and did not flag that omitted reminder. Its [limitation annotation](../review_20261020T190556705814Z/REVIEW_LIMITATIONS.md) explains why the raw reviewer verdict is not complete policy verification.

## Limits

One unseeded trial per task does not establish consistency, pass^k, full policy compliance, or performance on official tasks. The custom Codex transport differs from an official leaderboard setup. Run time includes intentional pacing, CLI startup, network and generation; it is not raw model-inference latency. Model review is another fallible evidence layer, with its own retained outputs.
