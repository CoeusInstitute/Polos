# AGENTS.md — docs/

## Purpose
Human-facing documentation. **Derived** from the canonical specs by the Archivist — never
authoritative. If anything here contradicts a canonical source, the source wins.

## Ownership
- `ARCHITECTURE.md` — design rationale, the diagrams, the threat model, and prior art.
- `LOOPING.md` — the safe loop-engineering capability: budgets, external stop conditions, the ledger.
- `SELF-IMPROVEMENT.md` — the measured, governed Reflexion capability: propose → measure → ratify.
- `EXAMPLE-TRACE.md` — a worked end-to-end request trace with example envelopes.
- `PLAYBOOKS.md` — environment profiles and ratified repeatable task playbooks.
- `NURSE.md` — conditional harness triage, checkup triggers, repair manifests, and anti-overtrigger rules.
- `POLOS-RESEARCH-PAPER.md` — the published research paper (Coeus Institute Open-Source Research):
  architecture, formal invariants, threat model, looping, self-improvement, validation, and limitations.
  Derived from the canonical specs; states no rule the sources do not evidence.
- Other explainer material for human maintainers.

## Local Contracts
- Maintained only by the Archivist (write scope includes `docs/**`).
- Must not state any rule, contract, or capability the canonical specs do not evidence.

## Work Guidance
- When a contract or role changes, refresh the affected diagram or trace so docs match reality.

## Verification
- Archivist closeout confirms docs match their canonical sources.

## Child DOX Index
No child DOX docs are currently defined for this subtree.
