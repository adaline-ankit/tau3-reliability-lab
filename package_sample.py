"""Build a shareable ZIP from a reviewed public-file inventory."""

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
EXCLUDED = {
    ".git",
    ".upstream",
    ".runs",
    ".venv",
    "__pycache__",
    ".ruff_cache",
    "node_modules",
}


def validate_inventory(root, names):
    if len(names) != len(set(names)):
        raise ValueError("Duplicate inventory path")
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or not path.parts:
            raise ValueError("Unsafe inventory path")
        if any(part in EXCLUDED or part.startswith(".env") for part in path.parts):
            raise ValueError("Inventory includes an excluded path")
        current = root
        for part in path.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError("Inventory contains a symlink")
        if not current.is_file() or not current.resolve().is_relative_to(
            root.resolve()
        ):
            raise ValueError("Missing or invalid inventory path")
        content = current.read_text()
        if re.search(r"(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,})", content):
            raise ValueError("Potential credential pattern in a public file")
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Validate inventory without writing a ZIP"
    )
    args = parser.parse_args()
    names = json.loads((ROOT / "PUBLIC_FILES.json").read_text())
    validate_inventory(ROOT, names)
    if args.check:
        print(f"Verified {len(names)} public files; no archive written.")
        return
    manifest = "".join(
        f"{hashlib.sha256((ROOT / name).read_bytes()).hexdigest()}  {name}\n"
        for name in sorted(names)
    )
    (ROOT / "SHA256SUMS.txt").write_text(manifest)
    archive = ROOT.parent / "tau3-reliability-lab.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
        for name in names + ["SHA256SUMS.txt"]:
            bundle.write(ROOT / name, arcname="tau3-reliability-lab/" + name)
    print(
        f"Created {archive.name}: {archive.stat().st_size:,} bytes, {len(names) + 1} files."
    )


if __name__ == "__main__":
    main()
