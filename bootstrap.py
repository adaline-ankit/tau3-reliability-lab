"""Fetch verified public τ-bench source and install its frozen core dependencies."""

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPOSITORY = "https://github.com/sierra-research/tau2-bench.git"
COMMIT = "fc0055dc4e0a316c3f83133267fbd6faaa770992"
RELEASE = "v1.0.1"


def run(*args, capture=False):
    return subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=capture)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check installed source identity without installing",
    )
    args = parser.parse_args()
    upstream = ROOT / ".upstream"
    if not shutil.which("git") or not shutil.which("uv"):
        raise SystemExit("Install Git and uv first. See README.md.")
    if not upstream.exists():
        if args.check:
            raise SystemExit(
                "Public dependency is missing. Run python3 bootstrap.py first."
            )
        run(
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            RELEASE,
            REPOSITORY,
            str(upstream),
        )
    remote = run(
        "git", "-C", str(upstream), "remote", "get-url", "origin", capture=True
    ).stdout.strip()
    actual = run(
        "git", "-C", str(upstream), "rev-parse", "HEAD", capture=True
    ).stdout.strip()
    if remote != REPOSITORY or actual != COMMIT:
        raise SystemExit(
            "Dependency does not match the expected public repository and commit; left untouched."
        )
    if run(
        "git",
        "-C",
        str(upstream),
        "status",
        "--porcelain",
        "--untracked-files=no",
        capture=True,
    ).stdout.strip():
        raise SystemExit(
            "Tracked public dependency files have changed; left untouched."
        )
    if not args.check:
        run("uv", "sync", "--project", str(upstream), "--frozen", "--no-dev")
    print(f"Verified public source: {RELEASE} / {COMMIT}")
    print("Run: .upstream/.venv/bin/python sample.py offline-demo")


if __name__ == "__main__":
    main()
