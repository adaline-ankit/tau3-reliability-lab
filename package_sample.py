"""Package only named, reviewed sample files; never archive a whole workspace."""

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
FILES = [
    ".gitignore",
    "README.md",
    "SAMPLE_REPORT.md",
    "PROVENANCE.md",
    "VERIFICATION.md",
    "THIRD_PARTY_LICENSE.txt",
    "sample.py",
    "bootstrap.py",
    "package_sample.py",
    "tests/test_sample.py",
    "data/tasks.json",
    "data/retail_db.json",
    "data/replay_cases.json",
    "data/policy.md",
    "results/offline_results.json",
    "results/REPLAY_REPORT.md",
]


def main():
    for name in FILES:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"Missing or unexpected file: {name}")
    manifest = "".join(
        f"{hashlib.sha256((ROOT / name).read_bytes()).hexdigest()}  {name}\n"
        for name in sorted(FILES)
    )
    (ROOT / "SHA256SUMS.txt").write_text(manifest)
    archive = ROOT.parent / "tau-bench-independent-sample.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
        for name in FILES + ["SHA256SUMS.txt"]:
            bundle.write(ROOT / name, arcname="tau-bench-sample/" + name)
    print(
        f"Created {archive.name}: {archive.stat().st_size:,} bytes, {len(FILES) + 1} files."
    )


if __name__ == "__main__":
    main()
