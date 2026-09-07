# Quality checks

The local FastAPI/React shell, SQLite migration skeleton, and backend/frontend integration tests are implemented. Match analysis and the model pipeline are not. The [V1 design](v1-design.md) defines the next implementation slices and their required validation.

## Reproducible environment

Use uv to manage the environment, development dependencies, and checked-in `uv.lock`. `.python-version` selects Python 3.12 and `pyproject.toml` restricts this initial environment to that minor version. This is the tooling baseline, not a claim that the eventual model stack has been validated on the Windows RTX 5080 machine. Revisit the runtime deliberately if model compatibility requires it, updating the pin, lock, type-check target, and CI together.

The current lock resolves Ruff 0.16.6, ty 0.0.78, and pytest 9.1.1. uv 0.12.10 is used locally and pinned in CI. FastAPI and Uvicorn power the shell. AnyIO is temporarily constrained below 4.15 because current Starlette references the deprecated BlockingPortal alias; warnings remain errors. GPU/model dependencies are deferred.

```sh
uv sync --locked --dev
npm ci --prefix frontend
uv run --locked python scripts/check_quality.py
```

The same check script runs on Windows and Linux in `.github/workflows/quality.yml`. It executes:

```sh
uv lock --check
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked ty check
```

It then runs `uv run --locked pytest` unconditionally: zero collected tests fail. Finally `npm run check --prefix frontend` runs strict TypeScript compilation, ESLint, Prettier verification, Vitest UI integration tests, and a Vite production build. Vitest also fails empty collection. Both Windows and Linux jobs install the checked-in npm lock with Node.js 24 before running this same script.

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

Frontend gates are part of the shared workflow. API conflict tests and UI mocked-network tests verify save behavior and retention of unsaved proposals; production serving and the real loopback launcher are checked separately.

## Application foundation verification

Backend integration tests cover validated edits, stale revisions, persistence after reopening, rejected host/origin/session credentials, API misses, migrations, foreign keys, backup-before-migration, concurrent editors, and committed reads during writes. The initial schema has workspace, processing-run, fact, and append-only-intended human-decision records; full domain editing and reconciliation APIs remain later slices.

The local validation uses Python 3.12 and Node.js 24. Hosted CI and Windows/GPU validation have not run in this session. Frontend tests use a DOM environment and mocked requests; they do not prove visual layout or video playback. The shell exposes only a workspace-name edit, and does not claim implemented footage import, inference, or statistics.

Dependency updates must preserve warnings-as-errors and both empty-suite failures. The CI action revisions are pinned, and the Python tooling baseline remains intact.

Real-browser smoke verification on 2026-09-06 used the built UI served by the loopback launcher: saving a name, competing edits in two tabs, preserving the stale proposal, retrying against the current revision, and reloading the saved state all passed. The full quality command passed 18 backend tests and 5 frontend tests, typing, lint, formatting, lock validation, and the production build.
