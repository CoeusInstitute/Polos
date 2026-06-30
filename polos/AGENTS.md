# AGENTS.md — polos/

## Purpose
Installable Python runtime package for Polos Core Runtime. It turns the canonical mesh specification
into a local CLI, task contract store, policy engine, JIT grant layer, governed tool gateway,
verification subsystem, loop controller, model-provider abstraction, and host adapter interfaces.

## Ownership
- `cli.py` owns the `polos` command surface.
- `contracts/` owns runtime-local contract models such as durable task records. Canonical inter-agent
  message contracts remain in top-level `contracts/`.
- `runtime/` owns task storage helpers, role capability boundaries, approvals, grants, redacted
  environment detection, sandbox interfaces, and loop control.
- `policy/` owns fail-closed tool policy and default policy data.
- `tools/` owns the governed tool gateway and wrapper around the canonical mesh validator.
- `audit/` owns runtime audit logging helpers.
- `verification/` owns evidence-producing checks and verification reports.
- `evaluation/` owns deterministic scaffolding for measured improvement proposals.
- `models/` owns provider-neutral model routing based on top-level `models.yaml`.
- `adapters/` owns Python adapter interfaces for host environments.

## Local Contracts
- Runtime code may consume or wrap canonical specs, but it must not redefine or weaken the
  constitution, role cards, flow graph, envelope schema, or structural validator.
- Decider and oversight roles remain tool-less in code. Execution Worker is the only role that may
  use write or shell tools through the runtime gateway, and only with an active scoped grant.
- Policy is fail-closed. Unknown tools, uncertain policy decisions, missing grants, missing sandbox
  requirements, and missing approvals block.
- Network and external-service actions are denied by default.
- Runtime artifacts are local generated state under `.agent/`; never store secrets in task records,
  audit events, evidence, or logs.
- Environment profiles may store host, workspace, git remote, provider-target, and script names, but
  must record secret names only when needed and never secret values.

## Work Guidance
- Keep provider integrations behind `models/` and keep dry-run operation working without API keys.
- Prefer small typed interfaces over provider- or host-specific assumptions in core runtime code.
- Tool execution must flow through task contract, role authorization, grant, policy, optional
  approval/sandbox, execution, and audit.
- Verifier gathers evidence; QC-style judgment remains separate. Execution Worker self-report is not
  completion evidence.
- Evaluation code may measure proposals but must never grant authority, relax policy, or commit
  lessons/playbooks directly.

## Verification
- `python tools/validate_mesh.py`
- `python -m pytest`

## Child DOX Index
No child DOX docs are currently defined for this subtree.
