"""Run the same locked Python quality gates locally and in CI."""

from __future__ import annotations

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

    has_application = any((ROOT / "src").rglob("*.py"))
    has_tests = (ROOT / "tests").exists()
    if has_application or has_tests:
        print("Running: uv run --locked pytest", flush=True)
        return subprocess.run(("uv", "run", "--locked", "pytest"), cwd=ROOT, check=False).returncode

    print("Application tests: not present yet; no application code has been added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
