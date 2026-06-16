# AGENTS.md — contracts/

## Purpose
The connection layer. Defines the single message shape, the complete edge graph, the request state
machine, and a payload schema for every message type. This subtree is **authoritative for all
inter-agent flow** and is what guarantees there are no gaps in the logic process or the connection
flow.

## Ownership
- `envelope.schema.json` — the one MeshEnvelope shape every message must satisfy.
- `flow.graph.yaml` — every legal edge, the gates on it, and the completeness invariants.
- `state-machine.md` — every request state and its PASS/FAIL/UNCERTAIN transitions.
- `schemas/` — one payload schema per graph message type (35 total) plus the `episode` runtime
    record schema, validated by `tools/validate_mesh.py`.

## Local Contracts
- No message may travel on any path not declared in `flow.graph.yaml`.
- Senders never select their own gates; the graph assigns them.
- Every message type used in `flow.graph.yaml` MUST have a `schemas/<type>.schema.json`.
- Every state and transition must be defined; the default on uncertainty is BLOCK (fail-closed).
- A role's `handoffs` (in its card) must exactly match the outbound edges declared here.

## Work Guidance
- Adding a message type: add its `schemas/<type>.schema.json`, add the edge(s) to `flow.graph.yaml`,
  update the sending/receiving cards' `inputs`/`outputs`, then run `tools/validate_mesh.py`.

## Verification
- `python tools/validate_mesh.py` — checks invariants I1–I14, exact edge/card coverage, schema
    coverage, envelope hardening, Security control coverage, and DOX reachability.

## Child DOX Index
- `schemas/` is covered by this parent (per-type payload schemas; no independent contract).
