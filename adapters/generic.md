# Adapter — Generic (single-process function-calling loop)

The minimal way to run the mesh anywhere with one model-calling loop.

## Mapping
- **Roles** -> a dispatcher that switches the active system prompt per role (load each
  `roles/*.agent.md` body).
- **Tool boundary** -> a tool allow-list keyed by role id. Deciders (alpha, router, taskmaster,
  loop-controller) and oversight (monitor, qc, security) get an **empty** allow-list. Only `execution-worker` gets
  effectful tools; `retrieval-worker` and `verifier` get read-only tools; `archivist` gets a
  doc-write tool scoped to `**/AGENTS.md` and `docs/**`.
- **Envelope** -> a plain object matching `contracts/envelope.schema.json`; validate on every hop.
- **Flow** -> a router function that, given a message, looks up the edge in `flow.graph.yaml`, runs
  the listed gates in order, and on FAIL follows `on_fail`.
- **State machine** -> a reducer over `contracts/state-machine.md`; default UNCERTAIN -> BLOCKED.
- **Gates** -> each gate is a model call with the guardian's prompt; it returns PASS/FAIL + rationale
  and emits a verdict to Security and a log entry to audit.
- **Credentials** -> the Taskmaster mints a short-lived token (`limits.credential_ttl_seconds`) listing
  exactly the tools an assignment may use; the worker's tool layer rejects anything not listed or expired.
- **Audit** -> append every envelope + verdict to a hash-chained file.

## Minimum viable enforcement (do not skip)
1. Tool allow-list is enforced by the tool layer, not by the prompt.
2. The constitution file is loaded read-only; no role has a write path to it.
3. Oversight model lineage differs from worker lineage (`models.yaml`).
4. Default-block on any uncertainty or unavailable gate.
