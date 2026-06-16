# AGENTS.md — experience/

## Purpose
Runtime-written store of `episode` records derived from the audit log: past task trajectories tagged
with what happened and whether they succeeded. This is the **held-out evaluation data** the Evaluator
uses to shadow-test proposed improvements before they can reach ratification. It is what makes
self-improvement *measured* rather than superstitious.

## Ownership
- Append-only `episode` records derived from the audit log by the runtime.

## Local Contracts
- Read-only to the Evaluator (`read_experience`) and Learning; written only by the runtime's
  episode-derivation from audit. No agent edits it directly.
- Evaluation must use **held-out** episodes (not the traces that generated a proposal) plus a control
  set, so both benefit and regressions can be measured.

## Verification
- Confirm the Evaluator measures benefit AND regressions on disjoint held-out and control sets.

## Child DOX Index
No child DOX docs are currently defined for this subtree.
