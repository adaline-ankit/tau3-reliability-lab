# Provenance

## Public dependency

- Repository: [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench)
- Release selected for reproducibility: `v1.0.1`
- Commit: `fc0055dc4e0a316c3f83133267fbd6faaa770992`
- Dependency resolution: upstream committed `uv.lock`, installed with `uv sync --frozen --no-dev`
- License: upstream MIT text retained in [THIRD_PARTY_LICENSE.txt](THIRD_PARTY_LICENSE.txt)

The public checkout is downloaded into `.upstream/` by setup and excluded from the sharing archive. No private mirror, employer fork, or saved company checkout is used.

## Specific source contracts

| Contract used | Public source |
|---|---|
| Task, user-scenario, action and reward-basis schemas | [data_model/tasks.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/data_model/tasks.py) |
| Retail database schema | [domains/retail/data_model.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/domains/retail/data_model.py) |
| Native retail tool behavior | [domains/retail/tools.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/domains/retail/tools.py) |
| Database replay and state comparison | [evaluator/evaluator_env.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/evaluator/evaluator_env.py) |
| Reward-component aggregation | [evaluator/evaluator.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/evaluator/evaluator.py) |
| Communication substring matching | [evaluator/evaluator_communicate.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/evaluator/evaluator_communicate.py) |
| Live run configuration | [data_model/simulation.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/data_model/simulation.py) |
| Native runner and metrics | [runner/batch.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/runner/batch.py), [agent_metrics.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/metrics/agent_metrics.py) |
| Text agent input boundary | [agent/llm_agent.py](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/agent/llm_agent.py) |

## Original content

The task definitions, synthetic database, reference and negative-control conversation events, wrapper, bootstrap script, tests, packaging script, and explanatory reports were newly authored for this request with AI coding assistance. They were not copied, sanitized, translated, or reconstructed from Adaline materials. No Adaline code, data, prompts, logs, historical metrics, or credentials were accessed to construct them.

The retail policy is adapted from the [public upstream policy](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/data/tau2/domains/retail/policy.md). The only content change is replacing the product count of 50 with 3 to match the synthetic fixture. Upstream tools and evaluators are imported without changes.

All identities and addresses in the fixtures are fictional. Emails use the reserved `.test` namespace; payment IDs and card suffixes are synthetic references.

## Evidence boundaries

Supplied results come from executing authored tool sequences against the public implementation. They validate scenario targets and grader behavior. They do not show how an LLM would select those actions, establish past work, measure general reliability, or prove complete policy compliance. Native live configuration and orchestrator construction were checked without making model calls.

The explicit-allowlist archive excludes `.env` files, credentials, `.upstream`, virtual environments, caches, private local notes, and optional live-run directories. `SHA256SUMS.txt` records checksums of the included files other than itself.
