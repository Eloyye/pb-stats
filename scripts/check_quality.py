"""Run the same locked Python quality gates locally and in CI."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Stop at the first failed gate without mutating source files or the lockfile."""
    commands = [
        ("uv", "lock", "--check"),
        ("uv", "run", "--locked", "ruff", "format", "--check", "."),
        ("uv", "run", "--locked", "ruff", "check", "."),
        ("uv", "run", "--locked", "ty", "check"),
    ]
    for command in commands:
        print(f"Running: {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            return result.returncode

    # Both runners fail empty collection; application tests are mandatory now.
    for command in [
        ("uv", "run", "--locked", "pytest"),
        ("npm.cmd" if os.name == "nt" else "npm", "run", "check", "--prefix", "frontend"),
    ]:
        print(f"Running: {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
