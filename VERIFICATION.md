# Verification receipt

Date: 20 October 2026. Local platform: macOS, Python 3.12.9, Ruff 0.15.17.

## Local checks

| Check | Executed result |
|---|---|
| `python3 bootstrap.py --check` | Exact public origin, pinned commit, and clean tracked dependency files verified |
| `.upstream/.venv/bin/python -m unittest discover -s tests -v` | 27 tests passed, including eleven replay-control subcases |
| `.upstream/.venv/bin/python sample.py offline-demo` | Four references and seven negative controls reproduced expected outcomes; no model calls |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed |

The native integration test executes the real upstream orchestrator with deterministic participant stubs, real tools, and native evaluation. It reaches the expected cancellation state with reward 1. Other tests check participant input separation, completion receipts, rejection of native Codex tools, customer-stop semantics, reviewer evidence indexes, run attribution, fresh state, and unsafe packaging paths.

These tests validate implementation contracts. Actual model performance is separate evidence in [experiment status](docs/EXPERIMENT_STATUS.md). Tests and CI do not make Codex calls or need model credentials.

## Reproduction and sharing

The upgraded 55-file archive was extracted into a new temporary directory. It cloned the exact public dependency and installed 75 core packages without copying the authoring checkout or virtual environment. All 27 tests, eleven replay controls, and inventory validation passed from that extraction. Local package caches were available; this was a fresh installation, not an uncached-download test. ZIP integrity, all 54 file checksums, and Markdown relative links were also verified. The repository includes an Ubuntu CI workflow for the same offline checks.

The sharing archive uses an explicit public-file inventory. `python3 package_sample.py --check` validates file existence, containment, symlinks, excluded paths, and obvious credential patterns. `python3 package_sample.py` writes a ZIP and a SHA-256 manifest. Private raw CLI diagnostics, private outreach notes, caches, and the dependency checkout are excluded. Content review is still required; a path filter is not a comprehensive secret detector.

## Model evidence boundaries

Codex CLI 0.145.0 uses saved ChatGPT login. Failed attempts, paced baseline runs, and changed-protocol reruns have separate evidence directories. Native reward is retained independently of policy review. Reported token counters come from completion events; per-call dollar cost, model seed, and temperature are unavailable. Managed Codex instructions are not fully controlled by this adapter.

All real-run results, including failures and simulator defects, are linked from [EXPERIMENT_STATUS.md](docs/EXPERIMENT_STATUS.md). A successful infrastructure check is not a completed task, and a completed task is not a general reliability estimate.
