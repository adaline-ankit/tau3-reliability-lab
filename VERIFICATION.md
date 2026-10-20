# Verification receipt

Date: 20 October 2026. Platform: macOS, Python 3.12.9.

## Executed checks

| Command | Result |
|---|---|
| `python3 bootstrap.py --check` | Public origin, exact pinned commit, and clean tracked dependency files verified |
| `.upstream/.venv/bin/python -m unittest discover -s tests -v` | Six tests passed, including all eleven reference/negative-control subcases |
| `.upstream/.venv/bin/python sample.py offline-demo` | Four reference cases and seven negative controls match expected native rewards and fixture-audit outcomes; zero LLM calls |
| `.upstream/.venv/bin/python sample.py live --agent-model openai/example-agent --user-model openai/example-user --trials 4 --dry-run` | Native configuration accepted and all four orchestrators constructed; no model/API calls |
| `ruff check sample.py bootstrap.py package_sample.py tests` | Passed |
| `ruff format --check sample.py bootstrap.py package_sample.py tests` | Passed |

The model names in the dry run are deliberately placeholders. Construction success does not establish model availability, valid credentials, provider compatibility, or successful live evaluation.

## Scope

Tests use the real pinned upstream `Task`, `RetailTools`, environment, and evaluators. They verify the sample's integration and expected control behavior. They are not a performance test of an LLM. The protocol diagnostic is intentionally limited to controlled replay fixtures; it does not validate full policy compliance.

## Fresh archive reproduction

The sharing ZIP was extracted into a newly created temporary directory. No dependency checkout or virtual environment was copied from the authoring directory. The following commands then completed successfully from the extracted package:

```bash
python3 bootstrap.py
.upstream/.venv/bin/python -m unittest discover -s tests -v
.upstream/.venv/bin/python sample.py offline-demo
.upstream/.venv/bin/python sample.py live \
  --agent-model openai/example-agent \
  --user-model openai/example-user \
  --trials 4 --dry-run
```

Setup fetched the exact public commit and installed 75 core packages from the upstream lockfile. All six tests passed, all eleven scripted outcomes matched, and all four live orchestrators constructed without API calls. This reproduction uses local package caches where available; installation was fresh, not an uncached download test.

ZIP integrity and all 16 manifest file checksums were verified. Archive entries were checked for path traversal, dependency checkouts, virtual environments, `.env` files, caches, and optional live-run directories. The shared raw replay payload was also checked for local absolute paths and credential fields; none were present. All relative links in the supplied Markdown files resolve.
