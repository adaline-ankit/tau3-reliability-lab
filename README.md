# τ-bench work sample: four original retail tasks

An independent, AI-assisted demonstration of task authoring, tool execution, state-based evaluation, and failure analysis using public Sierra τ-bench components. All customer records, orders, task instructions, and scripted conversations were created for this sample.

**Executed evidence: 11 scripted replay cases; zero LLM calls.** The four reference trajectories pass. Seven negative controls demonstrate task failures and gaps in outcome-only scoring. No live agent performance or leaderboard score is claimed.

Start with [SAMPLE_REPORT.md](SAMPLE_REPORT.md), then inspect the [executed replay report](results/REPLAY_REPORT.md) and [raw traces](results/offline_results.json).

## Four authored tasks

| ID | Scenario | Required outcome | Main failure to detect |
|---|---|---|---|
| sample_01_cancel_pending | Cancel a pending hoodie order | Cancel for `no longer needed`; refund original card | Success claim without a database update; omitted confirmation |
| sample_02_refuse_delivered | Customer insists on cancelling a delivered order | Explain restriction and preserve database | Invalid cancellation attempt hidden by unchanged end state |
| sample_03_exchange_variant | Exchange blue M hoodie for blue L | Request correct same-product exchange; record 5.00 difference | Tool-valid red variant instead of requested blue variant |
| sample_04_partial_return | Return bottle, keep mug | Request bottle-only return to original credit card | Wrong refund destination or returning an unrequested item |

Four is the sample count. Compatibility is pinned to Sierra's public `v1.0.1` release, commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`. This release includes the τ³-bench update in the `tau2-bench` repository. These custom tasks are a demonstration set, not an official leaderboard split. Confirm the client's requested version and schema before adapting them to a project.

## Run locally

Requires Git and [uv](https://docs.astral.sh/uv/getting-started/installation/). Setup downloads public dependencies and uses their committed lockfile; the offline replay makes no API calls. Execute commands from the extracted sample directory:

```bash
python3 bootstrap.py
python3 bootstrap.py --check
.upstream/.venv/bin/python -m unittest discover -s tests -v
.upstream/.venv/bin/python sample.py offline-demo
```

The dependency requires Python `>=3.12,<3.14`; uv selects an interpreter. Setup creates `.upstream/` and its virtual environment locally. They are excluded from the sharing archive.

`offline-demo` executes the hand-authored calls against real upstream tools, captures their actual outputs, and independently replays them through the native evaluator. Outbound socket connections are blocked during imports and replay. No former-employer repository, `.env`, account, service, code, data, or credentials are needed.

## Optional live evaluation

Live execution was **not performed** for the supplied results. An agent and a user simulator both incur provider usage. Use a personally authorized API key, keep it outside this folder, and choose currently available models that support tool calling and `temperature=0`.

Check configuration and construction without a key or model calls:

```bash
.upstream/.venv/bin/python sample.py live \
  --agent-model openai/YOUR_AGENT_MODEL \
  --user-model openai/YOUR_USER_SIMULATOR_MODEL \
  --trials 4 --dry-run
```

For a paid run, set `SAMPLE_OPENAI_API_KEY` in your process environment and run the same command without `--dry-run`. The entrypoint uses that explicit key; it does not fall back to an existing `OPENAI_API_KEY`. Provider `.env` discovery is disabled. The sample supports OpenAI model names in this entrypoint; this is a scope choice, not a limitation of τ-bench.

Execution uses upstream `llm_agent` and `user_simulator`, concurrency 1, seed 42, 60-step maximum, 180-second per-simulation timeout, no whole-simulation retries, and protocol enforcement. Provider-library request retries may still occur. These limits do not constitute a dollar spending cap. Four tasks × four trials produces 16 planned conversations, with multiple model requests inside each conversation.

Native output goes into a new `results/live_<UTC timestamp>/` directory. Review task reward, termination reason, actual messages, simulator behavior, and recorded usage before sharing. The fixture-only acknowledgement audit is not a free-form dialogue grader and is not applied to live runs. Model availability, credentials, and successful end-to-end live execution remain unverified.

## Files and execution boundaries

| File | Purpose |
|---|---|
| `data/tasks.json` | Four new tasks validated by upstream `Task` schema; user instructions and evaluator targets are separate fields |
| `data/retail_db.json` | Three products, five orders, two fictional accounts; reserved `.test` email addresses |
| `data/replay_cases.json` | Four reference traces and seven intentional negative controls |
| `data/policy.md` | Public upstream retail policy, with product count changed from 50 to 3 |
| `sample.py` | Native environment adapter, replay, limited fixture diagnostics, report generation, optional live entrypoint |
| `bootstrap.py` | Fetch public source; verify remote, commit, clean tracked files; install frozen core dependencies |
| `tests/test_sample.py` | Behavioral regressions against real upstream tools and evaluator |
| `package_sample.py` | Create an explicit-allowlist sharing archive and SHA-256 manifest |
| `THIRD_PARTY_LICENSE.txt` | Sierra's MIT license for upstream components and adapted policy |

The adapter registers `portfolio_retail` as a separate domain. It loads a fresh copy of the synthetic database for every environment and uses upstream `RetailTools` unchanged. The live agent receives policy, tools, and conversation; `llm_agent` does not receive the evaluator's reference actions. Replay fixtures intentionally know the desired actions because they validate the harness rather than measure an agent.

## Provenance and reuse

See [PROVENANCE.md](PROVENANCE.md) for exact sources and boundaries. All newly authored task/data/wrapper files were created for this request with AI coding assistance. The sample demonstrates the supplied implementation and executed checks; it does not establish any historical contribution or employment project result.

The archive contains only explicitly listed source, synthetic fixtures, reports, license, and checksums. It excludes `.upstream`, environments, secrets, caches, and optional live runs. Build it with:

```bash
python3 package_sample.py
```
