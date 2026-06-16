# AGENTS.md — loops/

## Purpose
Runtime-written ledgers for safe loop engineering. One append-only ledger per active loop holds the
spec, `definition_of_done`, the external `stop_condition`, the `budgets`, and the iteration log (what
each iteration tried, what failed, and the Verifier's result). The Loop Controller reconstructs each
iteration's **fresh context** from here — the ledger is the source of truth, not an accumulating chat
session.

## Ownership
- One ledger per loop (e.g. `loops/<loop_id>.jsonl`), written via `loop_state_update`.

## Local Contracts
- **Append-only.** The iteration log is never rewritten, so dead ends are remembered and not repeated.
- Written only by the Loop Controller; read to rebuild fresh context each iteration.
- A loop may never run without `budgets` and an externally verifiable `stop_condition` recorded here.

## Work Guidance
- The stop check is sourced from the Verifier (through QC), never self-reported by the worker.

## Verification
- Confirm every active loop's ledger records `budgets` + `stop_condition` before iteration 1.

## Child DOX Index
No child DOX docs are currently defined for this subtree.
