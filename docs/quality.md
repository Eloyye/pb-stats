# Quality checks

The Python tooling is implemented; the application, model pipeline, and application tests are not. The [V1 design](v1-design.md) defines the next implementation slices and their required validation.

## Reproducible environment

Use uv to manage the environment, development dependencies, and checked-in `uv.lock`. `.python-version` selects Python 3.12 and `pyproject.toml` restricts this initial environment to that minor version. This is the tooling baseline, not a claim that the eventual model stack has been validated on the Windows RTX 5080 machine. Revisit the runtime deliberately if model compatibility requires it, updating the pin, lock, type-check target, and CI together.

The current lock resolves Ruff 0.16.6, ty 0.0.78, and pytest 9.1.1. uv 0.12.10 is used locally and pinned in CI. FastAPI and GPU/model dependencies are added with the application and pilot; installing this tooling bootstrap does not install a working application.

```sh
uv sync --locked --dev
uv run --locked python scripts/check_quality.py
```

The same check script runs on Windows and Linux in `.github/workflows/quality.yml`. It executes:

```sh
uv lock --check
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked ty check
```

Once `src/` contains Python application code or `tests/` exists, it also runs `uv run --locked pytest`. At that point missing/empty test collection is a failure. Until then, it prints that application tests are absent; it does not claim an empty suite passed. Follow the planned `src/` layout, and update this gate explicitly if that layout changes.

`--locked` rejects a stale lock instead of silently updating it; the quality command does not reformat or fix source code. Use `uv run --locked ruff format .` to apply formatting intentionally. Update dependencies deliberately with uv and review the resulting lockfile. [uv lock and sync behavior](https://docs.astral.sh/uv/concepts/projects/sync/)

## Strict typing policy

Ruff enforces the presence of function argument and return annotations through `ANN`, including checks for explicit `Any` in function annotations. It also checks annotation idioms, imports, common bugs, modern syntax, and blanket/unused suppression comments. Fully untyped functions and constructor return types receive no automatic exemption. [Ruff annotation settings](https://docs.astral.sh/ruff/settings/#lint_flake8-annotations)

ty checks type correctness, unresolved imports, incomplete generic types, possibly unresolved references, dynamic decorator returns, and unsound assignments/returns/yields. Warnings fail the gate. Strict equality and generic narrowing are enabled. ty has no single `--strict` mode; this repository uses explicit documented rules rather than an invented flag or indiscriminately enabling every rule. [ty migration guidance](https://docs.astral.sh/ty/coming-from-mypy-or-pyright/), [ty configuration](https://docs.astral.sh/ty/reference/configuration/)

All application code, scripts, and tests must pass these checks. Keep domain interfaces typed and validate incoming model/API payloads into explicit records. Prefer `object` plus validation/narrowing for arbitrary inputs, precise unions for finite states, and typed interfaces for model integrations. Avoid broad dynamic dictionaries and casts used to disguise unchecked data.

Do not disable missing-import checks across the repository or replace imports globally with `Any`. Install typing stubs where appropriate or put an unavoidable dynamic dependency behind a small typed adapter. Any necessary suppression must name the rule and explain the precise limitation at that location; the annotation/data contract remains tested. [ty typing FAQ](https://docs.astral.sh/ty/reference/typing-faq/)

This policy does not prove that every possible dynamic type flow is rejected. Ruff's `ANN401` has alias limitations, and ty's soundness checks have documented scope limits. A review must still check that dynamic model output is actually validated before entering typed domain logic. [Ruff Any rule](https://docs.astral.sh/ruff/rules/any-type/), [ty rule reference](https://docs.astral.sh/ty/reference/rules/)

## Tests as implementation arrives

Write tests at module interfaces for domain behavior and durable integration scenarios, not for implementation details. The first application slice must introduce real tests; warnings, unknown markers, and invalid test configuration fail pytest. Do not add placeholder tests to satisfy collection.

The priority scenarios are scoring transitions and checkpoint conflicts, independent unknown attributes, exact numerator/denominator membership, source identity and timestamp mapping, human edits racing a worker result, structural reconciliation, job retry/resumption, and backup restoration. Ordinary CPU tests run in both CI environments. The actual Windows processing machine runs the model/resource/review-time benchmarks; a passing CPU check is not GPU validation.

When the frontend is scaffolded, add its lockfile, strict TypeScript compilation, lint/format checks, production build, and focused UI integration tests to the same quality workflow. Those frontend gates are requirements in the design, not implemented checks today.

## Bootstrap verification

Verified locally on macOS with Python 3.12.12 and the locked tool versions:

- Lock freshness, Ruff formatting, Ruff lint, and ty checks all passed.
- Temporary negative probes were rejected for missing annotations (`ANN001`/`ANN201`), explicit `Any` (`ANN401`), incompatible returns, unresolved imports, and unsound assignment.
- No application tests exist. Hosted CI and Windows/GPU validation have not run in this session.

The illustrative UI preview receives static markup/script validation only. Browser inspection of the local preview was blocked by the browser URL policy, so no interactive or responsive visual QA is claimed.

The CI action references and setup follow the [official uv GitHub Actions guide](https://docs.astral.sh/uv/guides/integration/github/); action revisions are pinned in the workflow.
