# Repository instructions

- Keep all scenarios synthetic. Do not add employer code, prompts, data, credentials, or private customer records.
- Public Sierra source is pinned by `bootstrap.py`; do not modify `.upstream` or manually change its lockfile.
- Model calls use the Codex CLI's saved ChatGPT login. Do not introduce API-key billing or reuse credentials from another project.
- Preserve native reward separately from fixture diagnostics and semantic review. Preserve failed attempts; do not silently retry or delete them.
- Agent/customer prompts must exclude evaluator criteria. Customers must not see private tool messages.
- Public artifacts are explicitly listed in `PUBLIC_FILES.json`. Private outreach drafts, logs, environments, and `.runs` must remain excluded.
- Save explanatory deliverables as Markdown. Do not add a website or HTML report.

Verification:

```bash
python3 bootstrap.py --check
.upstream/.venv/bin/python -m unittest discover -s tests -v
.upstream/.venv/bin/python sample.py offline-demo
ruff check .
ruff format --check .
python3 package_sample.py --check
```

These checks require no model calls. A Codex transport probe, orchestrator construction, scripted replay, and completed model task are distinct receipts.
