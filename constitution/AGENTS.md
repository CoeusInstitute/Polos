# AGENTS.md — constitution/

## Purpose
Holds the immutable rules that bind the whole mesh: the invariant, capability ceilings, the
two-axis and quality gates, tiering, documentation authority, and reference-monitor properties.

## Ownership
- `core.md` — the authoritative, runtime-immutable rule set.

## Local Contracts
- This directory is **read-only at runtime**. No agent may write here.
- Changes are made by a human out-of-band and applied by redeploy.
- Child specs elsewhere may specialize behavior but may never weaken anything here.

## Work Guidance
- When a rule changes, the Archivist must refresh every `AGENTS.md` whose description references it
  and confirm no derived doc now contradicts `core.md`.

## Verification
- Confirm no role's card grants a capability that `core.md` reserves or forbids.
- Confirm no edge in `contracts/flow.graph.yaml` writes to `constitution/**`.

## Child DOX Index
No child DOX docs are currently defined for this subtree.
