# Three τ-bench work samples

**Ankit Prasad · Independent, AI-assisted sample · 21 October 2026**

Three original text-retail tasks demonstrate task authoring, real tool execution, and evaluation analysis using Sierra's public τ³-bench code. Everything runs against a fictional store. No Adaline code, data, prompts, or internal artifacts were used.

Each sample includes a task definition, a model-generated conversation with actual tool responses, and the original native score. The two added negative controls are explicitly scripted. They test the evaluator; they are not model-performance results.

## Review in three minutes

| Sample | What the agent must do | Native DB match | Native communication | Native reward |
|---|---|---|---:|---:|
| 1. Cancel a pending order | Authenticate, get consent, cancel the correct order | Yes | 1 | 1 |
| 2. Refuse an ineligible cancellation | Inspect a delivered order and refuse, even after insistence | Yes, state preserved | 1 | 1 |
| 3. Exchange the correct variant | Blue M → blue L, with a 5.00 price difference | Yes | 0 | 0 |

One model trial per task, selected from a declared four-task run. These observations do not establish general accuracy or repeated-trial reliability. The fourth task, a partial return, also matched its target state and received native reward 1. [Full run, including all four tasks and original call receipts](https://github.com/adaline-ankit/tau3-reliability-lab/blob/main/results/codex_20261020T185123068419Z/results.json).

## 1. Cancellation: prove the update happened

**Request:** Cancel pending order `#W8100001`, reason `no longer needed`, with its 40.00 refund to the original card.

The agent finds the synthetic account by email, inspects the order and owner, explains the proposed cancellation and refund, and obtains explicit approval. It then calls:

```json
{"name":"cancel_pending_order","arguments":{"order_id":"#W8100001","reason":"no longer needed"}}
```

The environment returns `status: cancelled` and a 40.00 original-card refund record. The final message reports cancellation. Native database and communication checks both pass. This is a simulated refund record; no money moved.

**Inspect:** [full transcript](results/codex_20261020T185123068419Z/sample_01_cancel_pending_trial_0.md), messages 8–12. Message 9 grants consent, message 10 calls the tool, and message 11 records the changed state.

**Why this sample matters:** A success claim alone is insufficient. The tool response and native database comparison provide execution evidence.

## 2. Refusal: success can mean preserving state

**Request:** Cancel delivered order `#W8100002`. The customer insists once and does not authorize a return or exchange.

After identity lookup and order inspection, the agent explains that delivered orders cannot be cancelled. It maintains that boundary when challenged and performs no mutation. The native database target is unchanged state, and the required delivered-order explanation is present.

**Inspect:** [full transcript](results/codex_20261020T185123068419Z/sample_02_refuse_delivered_trial_0.md), messages 6–11.

**Why this sample matters:** Benchmark targets must represent correct refusal as well as successful actions. No mutation is the expected outcome here.

## 3. Exchange: explain a zero without hiding it

**Request:** Exchange the delivered blue M hoodie in order `#W8100003` for blue L, with the 5.00 difference assigned to the original card.

The agent inspects the customer, order, and available product variants. After consent, it requests the correct exchange:

```json
{"name":"exchange_delivered_order_items","arguments":{"order_id":"#W8100003","item_ids":["8100000001"],"new_item_ids":["8100000002"],"payment_method_id":"credit_card_demo_1001"}}
```

The tool records `exchange requested`, the correct new item, and `exchange_price_difference: 5.0`. Native DB match is true. The authored communication criterion requires the literal phrase `exchange requested`; the final reply says “Your exchange request is confirmed.” The communication check fails, so native reward remains **0**. The criterion and recorded result were not changed to turn this run into a pass.

There is also a separate policy issue: the proposal mentions the one-exchange allowance but omits the explicit reminder to confirm all desired exchange items. A separate model reviewer passed the trace and missed that omission. State correctness, wording sensitivity, and policy completeness therefore require separate interpretation.

**Inspect:** [full transcript](results/codex_20261020T185123068419Z/sample_03_exchange_variant_trial_0.md), messages 12–16; [policy](data/policy.md), “Exchange delivered order.” [Original analysis and reviewer limitation](https://github.com/adaline-ankit/tau3-reliability-lab/blob/main/results/codex_20261020T185123068419Z/ANALYSIS.md).

**Why this sample matters:** A useful evaluation report explains which component failed and preserves its result. A matching database does not establish complete policy compliance.

## Two controls that test the test

| Authored replay | Native result | Separate diagnostic | What it tests |
|---|---:|---|---|
| Cancel without confirmation | 1 | Fixture audit fails | Final-state and wording reward can miss authorization |
| Exchange for red L instead of blue L | 0 | Native DB comparison fails | A valid tool call can still violate the requested target |

The actions in these controls were supplied by us. The public tools and evaluator executed them. They validate grader behavior, not the model's ability to choose actions. Raw messages, tool responses, hashes, native reward, and fixture diagnostics are in [replay_controls.json](client_sample/replay_controls.json). The fixture audit is narrow and is not a general policy grader.

## Files and provenance

- [tasks.json](client_sample/tasks.json): the three task definitions, including separate customer instructions and evaluator targets.
- [retail_db.json](data/retail_db.json) and [policy.md](data/policy.md): complete synthetic starting state and attributed policy.
- [model_results.json](client_sample/model_results.json): three original simulation records, unchanged messages and native reward breakdowns, full-run manifest, and source SHA-256 values. This is an extract, not a new run. The original manifest describes all four tasks.
- The three linked Markdown transcripts provide the same conversations in readable form.
- `SHA256SUMS.txt` in the ZIP verifies the included files.

The public source is Sierra's `tau2-bench` repository, release `v1.0.1`, commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`, whose overview identifies the τ³ generation. This sample covers text retail. Native retail tools, text orchestration, and evaluation are imported unchanged; the policy adapts the public product count to three. Original contributions are the synthetic tasks/data, controls, Codex adapter, diagnostics, tests, and analysis. [Upstream license](THIRD_PARTY_LICENSE.txt); [original-work license](LICENSE).

Agent and customer decisions used Codex CLI `0.145.0`, saved ChatGPT login, requested model `gpt-5.6-luna`, low effort, and a 20-second call-start interval. The complete four-task run made 41 model calls. Task evaluator criteria were excluded from the participant prompts. The custom transport and managed runtime differ from an official leaderboard setup.

The ZIP is an inspection packet. [Full source, offline reproduction steps, all attempts, and tests](https://github.com/adaline-ankit/tau3-reliability-lab) remain available for deeper review. From that repository, `python3 package_client_sample.py` regenerates this extract and archive; `--check` checks freshness without writing files. Extraction makes no model calls and does not rerun or improve any score.
