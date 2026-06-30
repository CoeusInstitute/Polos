# AGENTS.md — tools/

## Purpose
Developer and CI tooling for the mesh. Currently the structural validator that proves the "no gaps"
property mechanically.

## Ownership
- `validate_mesh.py` — checks JSON/YAML well-formedness (canonical spec files only — runtime stores
  and the `.agent`/`.venv`/`.git` trees are skipped so spec validity never couples to runtime data), exact
  edge-by-edge card handoff coverage, card-vs-flow-graph input/output consistency (both directions),
  schema coverage for every graph message type, envelope hardening sentinels, model-registry sanity
  (including independent oversight/evaluator bindings), capability ceilings, final-response gating,
  Security control and verdict-audit coverage, invariants I12–I15 (including the Evaluator-gated
  `measured_improvement` hand-off, the required loop `fresh_context`/`verified_evidence`/`ledger_ref`
  fields, the lesson/playbook-only `kind` restriction, structured playbook fields, environment-profile
  hardening including the `available_tools` inventory shape, workflow-learning episode/signal fields,
  Nurse read-only ceilings, trigger/cooldown requirements, and Monitor-reviewed repair routing), the
  constitution-is-never-written rule, and DOX index reachability.
- Robustness: tolerates CRLF and missing-trailing-newline in role-card front-matter, and reports a
  missing or malformed canonical spec (`flow.graph.yaml`, `models.yaml`, `mesh.config.yaml`, role
  cards) as a clean `FAIL` rather than a Python traceback.
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
