# Domain docs

This repo uses a single-context layout:
- CONTEXT.md at the repo root defines domain vocabulary.
- docs/adr/ holds architectural decision records.

## Before exploring

Read CONTEXT.md and ADRs relevant to the area being explored.
If they do not exist, proceed silently. Domain modeling creates
them lazily when terms or decisions are resolved.

## Vocabulary

Use the terms defined in CONTEXT.md when naming domain concepts
in issues, proposals, hypotheses, and tests. Reconsider unfamiliar
terms or note real glossary gaps for domain modeling.

## ADR conflicts

Explicitly flag proposals that contradict an existing ADR,
identifying the decision and explaining why it should be revisited.
