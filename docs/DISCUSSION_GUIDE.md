# Discuss the sample with a client

## Thirty-second opening

“I created an independent text-retail sample using the public τ³-bench release. It has four authored scenarios, a synthetic database, native tools and evaluation, and negative controls that show where final-state success can miss authentication or consent. I also added a Codex-only agent/customer adapter and a separate semantic-review entrypoint. The repository separates the scripted checks from actual model-run receipts, including infrastructure failures.”

Read [experiment status](EXPERIMENT_STATUS.md) immediately before the call. If a later model run completed, describe its exact sample size and outcome. If it did not, say so. Never convert transport probes into task-success claims.

## One example to explain well

“Take a pending cancellation. If the agent cancels the correct order with the expected refund record, the native database check passes. If it also says the required cancellation wording, native reward is 1. But if it skipped confirmation, the interaction still violated policy. I preserve that native reward and report the policy issue separately.”

Show `cancel_without_confirmation` in [replay report](../results/REPLAY_REPORT.md). Then show `claim_cancel_without_update`: the agent says it cancelled, but the native database comparison fails. Together, the cases distinguish outcome correctness from conversational authorization.

## Likely questions

| Question | Evidence-bounded answer |
|---|---|
| Which τ-bench version? | Public τ³ generation in `tau2-bench`, software release `v1.0.1`, pinned by full commit hash. Text retail portion. |
| What did you write? | Synthetic tasks/data, scenario and negative-control traces, environment glue, replay/reporting, Codex participants/transport, separate review entrypoint, tests and docs. |
| What came from upstream? | Task schemas, retail tools, environment base, text orchestrator, native evaluator and an attributed policy. |
| Did you build voice or banking retrieval? | This sample covers text retail. Those τ³ capabilities were not implemented or tested here. |
| Are the original traces model-generated? | They are authored replay fixtures. Actual Codex attempts are stored separately with call receipts and terminations. |
| Did you measure model accuracy? | Refer to current run receipts. A transport probe or an incomplete four-task batch cannot establish task accuracy. |
| Why not require the exact tool sequence? | Equivalent paths can reach the correct target state. The task's `reward_basis` determines whether action matching gates reward. |
| How do you stop answer leakage? | Separate participant inputs; evaluator criteria are excluded from agent/customer prompts; temporary working directories and native-tool restrictions; no claim of complete control over managed runtime context. |
| Why add negative controls? | They test grader sensitivity and reveal missing evaluation coverage before relying on success rates. |
| Is the policy audit complete? | The fixture audit is deliberately narrow. The separate model reviewer needs calibration and human review. Neither is a compliance certification. |
| What about pass^k? | It measures consistency across k attempts, unlike pass@k's at-least-one success. Repeated completed model trials are needed. |
| How would you improve it next? | Confirm their task schema and domain, add reviewed scenarios, establish a completed baseline, inspect failure causes, change one component, then rerun a fixed suite. |

## Questions for the client

1. Is the work task authoring, tool/environment implementation, evaluation infrastructure, or analyzing runs?
2. Which τ³ domain and modality: text retail/airline, banking knowledge retrieval, or voice?
3. Do they have a task-authoring schema, acceptance rubric, and examples of accepted/rejected work?
4. What volume, review process, deliverables, and compensation do they expect?
5. Which materials are public versus under their NDA, and how are model-usage costs handled?

## Phrases to avoid

- “I built τ³-bench.” You built an independent lab using public components.
- “Four tasks passed, so the model has 100% reliability.” A tiny authored set cannot establish general reliability.
- “The agent was compliant because reward was 1.” The negative controls demonstrate why that inference fails.
- “This shows Adaline's system.” The sample is separate and contains none of that system's materials.
- “Codex calls cost zero.” They consume subscription allowance; per-call dollar cost is unavailable here.
- “The judge verified everything.” Review outputs need calibration, valid evidence, and human judgment.

## Explain the actual model run

“The first paced cancellation run stopped too early: the simulated customer approved the action and ended the conversation in the same turn. I preserved the failed trace, clarified the stop instruction, added a narrow guard and regression tests, then recorded a fresh run. That run obtained consent, called the real cancellation tool, recorded the original-card refund, and received native reward 1.”

One unseeded rerun is an example, not proof of a statistically significant improvement. The baseline delivered-order refusal also passed; baseline exchange and partial return stopped prematurely. The later four-task guard-v2 suite below includes fresh attempts for all four scenarios. See [all attempts](../results/EXPERIMENT_COMPARISON.md).

## A two-minute demonstration

1. Run `.upstream/.venv/bin/python sample.py offline-demo`.
2. Show the three reward-1 policy controls in the replay report. Explain why the selected reward components cannot see those obligations.
3. Show the original premature-stop transcript beside the changed-protocol cancellation transcript.
4. Point to the tool response recording `cancelled` and the 40.00 refund. That is the execution receipt behind the completion claim.
5. State the limits: four authored tasks, one trial per task in the current declared suite, text retail only, custom Codex transport, no general reliability estimate.

## Current four-task suite

The later guard-v2 run completed all four tasks under one declared configuration, with 41 Codex calls. All four target database comparisons passed; native rewards were 1, 1, 0, 1. Exchange missed the literal phrase `exchange requested` while reporting that the exchange request was confirmed. Its state update and action match passed, but its proposal also omitted the explicit all-items reminder required by policy.

The separate model reviewer passed all four traces without flagging that omission. Explain these as separate measurements and limitations, not as four fully compliant successes. See the [current analysis](../results/codex_20261020T185123068419Z/ANALYSIS.md). The earlier one-task rerun remains a separate experiment.
