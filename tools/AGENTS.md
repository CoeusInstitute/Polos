# AGENTS.md — tools/

## Purpose
Developer and CI tooling for the mesh. Currently the structural validator that proves the "no gaps"
property mechanically.

## Ownership
- `validate_mesh.py` — checks JSON/YAML well-formedness, exact edge-by-edge card handoff coverage,
  card-vs-flow-graph input/output consistency (both directions), schema coverage for every graph
  message type, envelope hardening sentinels, model-registry sanity (including independent
  oversight/evaluator bindings), capability ceilings, final-response gating, Security control and
  verdict-audit coverage, invariants I12–I14 (including the Evaluator-gated `measured_improvement`
  hand-off, the required loop `fresh_context`/`verified_evidence`/`ledger_ref` fields, and the
  lesson/playbook-only `kind` restriction), the constitution-is-never-written rule, and DOX index
  reachability.
- `requirements.txt` — the only dependency, `pyyaml`.

## Local Contracts
- The validator is read-only; it never modifies repo files.
- It must exit non-zero on any violation so CI fails the build.
- It is the canonical executable implementation of the invariants in `contracts/flow.graph.yaml`;
  keep the two in sync when invariants change.

## Work Guidance
- Run before every release and in CI: `pip install -r tools/requirements.txt && python tools/validate_mesh.py`.

## Verification
- `python tools/validate_mesh.py` exits 0 on a healthy repo.

## Child DOX Index
No child DOX docs are currently defined for this subtree.
