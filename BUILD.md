# BUILD.md — Polos Bootstrap Protocol

This is the procedure an agent follows to construct **Polos** — the governed agent mesh — inside its
host environment. It is runtime-neutral: it tells you *what* to wire, not *which framework* to use.
Stack specifics live in `adapters/`. Follow the steps in order; each one names the exact file to read
and what to wire next, so smaller models can build it reliably too.

## Preconditions
- You can spawn or simulate multiple independent model calls with distinct system prompts.
- You can mediate messages between those calls (a queue, function calls, a graph runner, or even
  a single loop that switches roles — any of these works).
- You can enforce that some calls have tools and some do not. **This is mandatory.** If your host
  cannot deny tools to a role, the invariant fails and you must not deploy.

## Steps

### 1. Detect environment
Identify your host (VS Code/Copilot, custom harness, function-calling loop, LangGraph, other).
Load the matching note from `adapters/`. If none matches, use `adapters/generic.md`.

### 2. Load the constitution (immutable)
Read `constitution/core.md`. Hold it read-only for the session. Every gate and the Security
agent are bound by it. No role you build may obtain a write path to it.

### 3. Resolve models
Read `models.yaml`. For each role, resolve `role.model` if pinned, else
`profiles[active_profile][role.class]`. The active profile comes from `MESH_PROFILE` or the
`profile:` field. **Oversight roles must resolve to a different model lineage than workers** —
verify this before continuing; if they collapse to the same family, change the profile.

### 4. Instantiate roles
For each card in `roles/*.agent.md`: parse the YAML front-matter (the contract) and load the
markdown body as that role's system prompt. Bind only the `capabilities` the card declares —
no more. Workers receive **no standing credentials**; they get JIT scoped credentials per
assignment from the Taskmaster.

### 5. Wire the flow (the gapless part)
Read `contracts/flow.graph.yaml`. For every edge, create the channel and attach the gates the
edge declares, in order. Every message on every channel must validate against
`contracts/envelope.schema.json`. Senders never choose their own gates — the graph does.

### 6. Wire the state machine
Implement `contracts/state-machine.md`. Every state must have defined transitions for PASS,
FAIL, and UNCERTAIN. The default on UNCERTAIN or gate-unavailable is **BLOCK** (fail-closed).

### 7. Stand up oversight
Attach the verdict stream from Monitor and QC to the Security agent, and the audit sink to all
three. Wire the Security HALT/quarantine signal to every plane, and the escalation path to the
human. Security observes verdicts and the audit log **independently** of the orchestration
chain so a compromised Taskmaster cannot blind it.

### 8. Install documentation (DOX)
Run the Archivist in install/retrofit mode. It builds or repairs the `AGENTS.md` tree from the
canonical specs, verifies reachability and schema conformance, and produces a closeout report.

### 9. Self-test
Send one benign dry-run request through the mesh. Confirm it terminates at a response. Send one
deliberately out-of-scope request and confirm a gate blocks it. Confirm the audit log captured
every hop.

### 10. Verify and report
Run `python tools/validate_mesh.py` (it checks the completeness invariants from
`contracts/flow.graph.yaml`, schema coverage, model-registry sanity, and DOX reachability). Report:
roles built, models bound (with explicit IDs), edges wired, gates attached, DOX closeout, and any
invariant that did not pass. **Do not go live with a failing invariant.**

## Adapter patterns (summary; full notes in `adapters/`)
- **Generic / function-calling loop** — One process, a role dispatcher, and a tool allow-list
  keyed by role. Deny the tool registry to deciders and oversight by construction.
- **VS Code / GitHub Copilot** — Encode roles as scoped instruction files; use the DOX
  `AGENTS.md` tree as the in-repo contract surface; gate effectful actions behind explicit
  human-approved steps for `external-write`, `financial`, `code-exec`.
- **LangGraph / graph runners** — Roles are nodes; `flow.graph.yaml` maps directly to edges;
  gates are conditional edges with the FAIL branch wired to rework/block/escalate.
- **Custom harness** — Implement the envelope as your message type and the state machine as your
  reducer; everything else follows.
