# Adapter — LangGraph / Graph Runners

How to realize the mesh on a graph-based agent runner (LangGraph or similar).

## Mapping
- **Roles** -> graph **nodes**; load each `roles/*.agent.md` body as the node's system prompt and
  bind only its declared tools.
- **Flow graph** -> `contracts/flow.graph.yaml` maps almost directly to graph **edges**. Gated edges
  become **conditional edges**: the gate node returns PASS/FAIL and the conditional routes PASS
  forward, FAIL to the `on_fail` target.
- **Envelope** -> the graph **state** object conforms to `contracts/envelope.schema.json`; validate
  on transitions. `trace_id` and `intent_ref` are carried in state, unchanged, the whole run.
- **State machine** -> `contracts/state-machine.md` is your reducer/checkpoint logic; set the default
  branch on any uncertain gate to the BLOCK path.
- **Gates** -> Monitor / QC / Security are nodes with no tools; they emit a verdict to a Security
  node and a log entry to an audit sink. Security can route any state to a HALTED terminal.
- **Credentials** -> the Taskmaster node attaches a scoped, expiring credential object to state; the
  Execution node's tool wrapper rejects tools/paths not granted or past expiry.
- **Audit** -> a side-effecting sink node (or callback) appends every state transition and verdict to
  an append-only, hash-chained store.

## Minimum viable enforcement
1. Tool binding is per-node; decider and oversight nodes bind zero effectful tools.
2. The constitution is read-only context shared by all nodes; no node writes to it.
3. Oversight nodes use a different model than worker nodes (`models.yaml`).
4. Conditional edges default to BLOCK when a gate is uncertain or unavailable.
5. Run `tools/validate_mesh.py` in CI so graph edits can't drift from the contracts.
