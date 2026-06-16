# AGENTS.md — Polos (DOX Root)

> **If you are an agent:** this repository (Polos) is a buildable specification, not a library to import.
> To instantiate the mesh in your host environment, read this file, then execute `BUILD.md`.
> The specs in `constitution/`, `roles/`, `contracts/`, and `models.yaml` are runtime-neutral.
> Map them onto your stack's primitives using `adapters/`. Do not weaken any constraint while
> building. Run the completeness check in `contracts/flow.graph.yaml` before going live.

## Purpose
Provide a portable, self-documenting safety harness that decomposes one logical agent into a
mesh of specialized agents so that no single component can both decide to cause harm and carry
it out. Safety is a property of the **topology**, enforced structurally, not a property assumed
of any single model.

## Repository Ownership
- This root owns the **global invariant**, the **plane model**, the **build protocol**, and the
  top-level index.
- `constitution/` owns immutable rules and capability ceilings. **Authoritative.**
- `roles/` owns canonical agent definitions and the agent-card template. **Authoritative.**
- `contracts/` owns the message envelope, the complete connection graph, and the state machine.
  **Authoritative for all inter-agent flow.**
- `oversight/` owns the three guardian policies (Monitor, QC, Security).
- `models.yaml` owns model binding for every role.
- `backpacks/`, `audit/` own runtime-written lessons and the append-only log.
- `loops/` owns runtime loop ledgers; `experience/` owns the runtime episode store for measured self-improvement.
- `adapters/` owns stack-specific bootstrap notes (additive only).
- `docs/` owns human-facing material. **Derived** — never authoritative.

## Global Contracts
- **The invariant.** Deciders (Alpha, Router, Taskmaster, Loop Controller) hold no effectful tools.
  Only Execution Workers act, and only on scoped, monitored, credentialed assignments. Oversight
  agents (Monitor, QC, Security) hold no tools and can only reject / rework / quarantine / halt.
- **One envelope.** Every inter-agent message is a valid `MeshEnvelope`
  (`contracts/envelope.schema.json`). No exceptions; this is what makes the flow gapless.
- **Gates are total.** Every edge that delivers a worker result or a doc change is mediated by
  the Monitor (safety) then QC (quality). Gates are assigned by `contracts/flow.graph.yaml`,
  never chosen by the sender.
- **Docs describe, they do not define.** `AGENTS.md` files are derived views of the canonical
  specs. If a doc ever contradicts a canonical source, the source wins and the Archivist repairs
  the doc. No `AGENTS.md` may weaken DOX, the constitution, or a parent's safety constraints.
- **Fail-closed.** Any unavailable or uncertain gate blocks. Ambiguity resolves toward safety.
- **Corrigible.** The mesh accepts halt and correction without resisting or self-preserving.
- **Loops are bounded.** A looped goal declares budgets and an externally verifiable stop condition checked by the Verifier; the Loop Controller holds no tools; Security can HALT a runaway loop.
- **Self-improvement is measured.** Proposed lessons/playbooks must pass the Evaluator (benefit, no regressions) before ratification, are append-only and versioned, and can never grant capability or weaken a constraint.

## Work Guidance
- Treat `constitution/core.md` as read-only at runtime. Changes happen out-of-band by a human,
  then a redeploy.
- Every agent observes **Read-Before-Editing** and **Update-After-Editing** (DOX). The Archivist
  owns installation, repair, and closeout of the `AGENTS.md` tree.
- Bind models only in `models.yaml`. Never hardcode a model inside an agent card.
- Add stack support by adding a file under `adapters/`, never by editing the canonical specs.

## Verification
- Structure/flow: run `python tools/validate_mesh.py` (also wired into CI). It checks the
  completeness invariants in `contracts/flow.graph.yaml` — card-vs-graph consistency in both
  directions, a payload schema for every message type, model-registry sanity, capability ceilings,
  and DOX index reachability. All must pass before going live.
- Documentation: the Archivist's closeout must report a fully reachable `AGENTS.md` tree with no
  stale indexes and no doc/source contradictions.
- Behavior: run a dry-run request through the state machine (`contracts/state-machine.md`) and
  confirm it terminates at a response, a refusal, or a human escalation — never an undefined state.

## DOX Workflow
This repo is itself a DOX tree. Every durable directory carries an `AGENTS.md`. The Archivist
keeps them current, schema-conformant (DOX Child Doc Shape), and reachable from this root index.

## User Preferences
- Prompts are **pure markdown**. Contracts and config are **YAML/JSON**. Do not mix.
- Model IDs are **explicit `provider/model` strings** — no hidden tiers or opaque abstractions.

## Child DOX Index
- `constitution/AGENTS.md` — Owns immutable rules, the invariant, capability ceilings, tiering, refusal boundaries.
- `roles/AGENTS.md` — Owns the canonical agent roster, capability matrix, and the agent-card template.
- `contracts/AGENTS.md` — Owns the message envelope, the complete flow graph, and the state machine.
- `oversight/AGENTS.md` — Owns the Monitor, QC, and Security guardian policies.
- `backpacks/AGENTS.md` — Owns append-only per-role lesson stores (runtime-written).
- `audit/AGENTS.md` — Owns the append-only, hash-chained event log (runtime-written).
- `adapters/AGENTS.md` — Owns stack-specific bootstrap notes (additive).
- `docs/AGENTS.md` — Owns human-facing, derived documentation.
- `tools/AGENTS.md` — Owns the structural validator and CI tooling.
- `loops/AGENTS.md` — Owns the runtime loop ledgers that drive safe, fresh-context loop iteration.
- `experience/AGENTS.md` — Owns the runtime episode store the Evaluator measures improvements against.

`.github/` intentionally has no child DOX doc; it holds standard GitHub metadata (CI workflow,
issue and PR templates), not mesh contracts.
