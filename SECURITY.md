# Security Policy

## Scope
This repository is a **safety architecture specification**, not a running service. "Security issues"
here usually mean one of:
- a way the specified mesh could be made to **violate its core invariant** (a decider or oversight
  agent gaining effectful capability, an unsupervised action path, a bypass of a gate);
- a **gap in the flow graph or state machine** that the validator does not catch;
- a documented contract that could be read to **weaken a safety constraint**.

## Reporting
Please report suspected weaknesses privately to the maintainers (open a minimal issue asking for a
private channel, or use the repository's security advisory feature) rather than as a public issue
with full exploit detail. Include the file(s), the path through the mesh, and why it breaks the
invariant.

## What we will do
- Acknowledge the report.
- Reproduce it against `tools/validate_mesh.py` and, if the validator missed it, add a check.
- Patch the spec and note it in `CHANGELOG.md`.

## Hardening reminders for implementers
A spec cannot enforce itself. When you build the mesh:
- Enforce the tool / no-tool boundary in your **tool layer**, not in prompts.
- Load `constitution/core.md` read-only; ensure no role has a write path to it.
- Use a **different model lineage** for oversight than for workers.
- Default to **block** on any uncertain or unavailable gate.
- Keep the audit log append-only and tamper-evident, and keep an external human kill switch above
  the Security agent.
