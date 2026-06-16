# AGENTS.md — oversight/

## Purpose
The three guardian policies. Each guardian holds **no tools** and can only reject, rework,
quarantine, or halt. Three distinct questions, three distinct axes — none of them can act.

## Ownership
- Monitor policy — **safety + intent**.
- QC policy — **correctness + quality** (canonical card: `roles/qc.agent.md`).
- Security policy — **global integrity + HALT** (the reference monitor).

## Monitor policy (safety + intent)
- Gates **every** mediated edge. Emits PASS/FAIL with rationale; FAIL blocks (fail-closed).
- **Two axes, either FAIL blocks:**
  - Axis A — intent fidelity: faithful to the *original* `intent_ref`?
  - Axis B — harm/policy: dangerous or disallowed regardless of intent?
- Also scrubs/normalizes retrieved content to blunt prompt injection, and reviews proposed backpack
  edits before ratification.
- Must run on a **different model lineage** than the worker it gates (anti-correlated-failure).

## QC policy (correctness + quality)
- Runs **after** the Monitor's safety gate, never before.
- Checks completeness, correctness, schema conformance, and faithfulness against the assignment's
  **definition of done**.
- May delegate execution-based checks to the read-only **Verifier**; QC itself runs nothing.
- FAIL -> bounded rework (`limits.rework_max`); never passes on uncertainty.

## Security policy (integrity + HALT)
- Observes the verdict stream and audit-derived runtime feed **independently** of the orchestration
  chain. This is passive input, not an active read tool.
- Sole holder of **HALT/quarantine**; ratifies non-safety backpack edits (humans ratify
  safety-adjacent ones).
- Reference-monitor properties: always invoked, tamper-proof, minimal/verifiable; subordinate to an
  external human kill switch.
- Detects cross-message patterns (scope creep, exfiltration signatures, drift) and freezes + escalates.

## Local Contracts
- No guardian may hold effectful or active read-only tools. Monitor and QC receive gate inputs;
  Security receives a passive verdict/audit feed; the Verifier is the separate read-only worker.
- A guardian may never weaken a constraint in `constitution/core.md`.

## Verification
- Confirm Monitor and worker resolve to different model lineages in `models.yaml`.
- Confirm SAFETY_GATE precedes QUALITY_GATE in `contracts/state-machine.md`.

## Child DOX Index
No child DOX docs are currently defined for this subtree.
