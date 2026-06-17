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
- **Environment profile** -> on startup and whenever provider config changes, run read-only probes
  for workspace roots, git remotes, package scripts, CI files, and provider config files. Write a
  redacted `environment_profile` runtime record with `host_kind: generic`. If more than one GitHub,
  Vercel, or Supabase target is plausible, mark that target `ambiguous: true` and require a human
  choice before a playbook can use it.
- **Tool inventory** -> populate `available_tools` from the host's registered tools/CLIs/scripts,
  each with `kind`, highest `consequence_class`, enforcement note (the allow-list keyed by role), and
  required secret variable names only. The Taskmaster may grant JIT credentials only from this list;
  an assignment requesting a tool not present fails closed.
- **Playbooks** -> load ratified `kind: playbook` backpack entries as read-only strategy templates.
  The Router may match aliases, but the Taskmaster still turns every step into normal assignments with
  preflight checks, consequence tiers, JIT credentials, gates, and verification.
- **Nurse** -> expose read-only repo/audit/experience/validator inspection only. Router can dispatch
  explicit `checkup_request`; audit/Security can dispatch `triage_signal` only after threshold and
  cooldown checks. Nurse outputs go to Monitor, and repairs execute only as normal Taskmaster
  assignments or Archivist doc assignments.

## Minimum viable enforcement (do not skip)
1. Tool allow-list is enforced by the tool layer, not by the prompt.
2. The constitution file is loaded read-only; no role has a write path to it.
3. Oversight model lineage differs from worker lineage (`models.yaml`).
4. Default-block on any uncertainty or unavailable gate.
5. Environment profiles store provider identifiers and secret names only; never secret values.
6. Nurse triage is not per-request; enforce `limits.nurse` threshold and cooldown before automatic
  checkups.
