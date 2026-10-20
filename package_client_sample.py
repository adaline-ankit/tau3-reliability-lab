"""Extract three review samples from preserved evidence and build a small ZIP."""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from package_sample import validate_inventory

ROOT = Path(__file__).resolve().parent
RUN = "results/codex_20261020T185123068419Z/results.json"
REPLAYS = "results/offline_results.json"
REPO = "https://github.com/adaline-ankit/tau3-reliability-lab"
TASK_IDS = (
    "sample_01_cancel_pending",
    "sample_02_refuse_delivered",
    "sample_03_exchange_variant",
)
CONTROL_IDS = ("cancel_without_confirmation", "exchange_wrong_color")


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def source_reference(path):
    return {
        "path": path,
        "sha256": digest(path),
        "url": f"{REPO}/blob/main/{path}",
    }


def generated_files():
    run = json.loads((ROOT / RUN).read_text())
    manifest = run["manifest"]
    for key, path in (
        ("task_sha256", "data/tasks.json"),
        ("database_sha256", "data/retail_db.json"),
        ("policy_sha256", "data/policy.md"),
    ):
        if digest(path) != manifest[key]:
            raise ValueError(f"Recorded run does not match current {path}")
    if not run["complete"] or manifest["trials_per_task"] != 1:
        raise ValueError("Expected a complete one-trial-per-task source run")
    tasks = json.loads((ROOT / "data/tasks.json").read_text())
    replays = json.loads((ROOT / REPLAYS).read_text())
    simulations = [s for s in run["simulations"] if s["task_id"] in TASK_IDS]
    selected_tasks = [t for t in tasks if t["id"] in TASK_IDS]
    controls = [c for c in replays["cases"] if c["case_id"] in CONTROL_IDS]
    if (
        [s["task_id"] for s in simulations] != list(TASK_IDS)
        or [t["id"] for t in selected_tasks] != list(TASK_IDS)
        or [c["case_id"] for c in controls] != list(CONTROL_IDS)
    ):
        raise ValueError("Missing, duplicate, or reordered selected evidence")
    return {
        "client_sample/tasks.json": selected_tasks,
        "client_sample/model_results.json": {
            "evidence_type": "selected_original_simulations_not_a_new_run",
            "source": source_reference(RUN),
            "original_simulation_count": len(run["simulations"]),
            "original_call_count": len(run["calls"]),
            "selection_reason": "Three distinct behaviors: mutation, refusal, exchange",
            "omitted_task_ids": [
                s["task_id"] for s in run["simulations"] if s["task_id"] not in TASK_IDS
            ],
            "original_manifest": manifest,
            "task_source": source_reference("data/tasks.json"),
            "simulations": simulations,
        },
        "client_sample/replay_controls.json": {
            "evidence_type": "scripted_controls_not_model_decisions",
            "source": source_reference(REPLAYS),
            "definition_source": source_reference("data/replay_cases.json"),
            "original_case_count": len(replays["cases"]),
            "llm_calls": replays["llm_calls"],
            "cases": controls,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without writing")
    args = parser.parse_args()
    public_names = json.loads((ROOT / "PUBLIC_FILES.json").read_text())
    validate_inventory(ROOT, [RUN, REPLAYS, "data/tasks.json"])
    for name, value in generated_files().items():
        content = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
        if args.check:
            if not (ROOT / name).is_file() or (ROOT / name).read_bytes() != content:
                raise ValueError(f"Stale generated file: {name}")
        else:
            if name not in public_names:
                raise ValueError(f"Generated path outside public inventory: {name}")
            (ROOT / name).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / name).write_bytes(content)
    names = json.loads((ROOT / "CLIENT_FILES.json").read_text())
    if not set(names).issubset(public_names):
        raise ValueError("Client inventory must be a subset of the public inventory")
    validate_inventory(ROOT, names)
    if args.check:
        print(f"Verified {len(names)} client files and exact source-derived evidence.")
        return
    checksums = "".join(f"{digest(name)}  {name}\n" for name in sorted(names))
    archive = ROOT.parent / "tau-bench-client-samples.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
        for name in sorted(names):
            bundle.write(ROOT / name, arcname="tau-bench-client-samples/" + name)
        bundle.writestr("tau-bench-client-samples/SHA256SUMS.txt", checksums)
    print(f"Created {archive.name}: {archive.stat().st_size:,} bytes.")


if __name__ == "__main__":
    main()
