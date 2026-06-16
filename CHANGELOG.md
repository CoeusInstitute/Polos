# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]
### Changed
- **Renamed the project to "Polos"** (was "Agent Mesh"). Internal `mesh` / `MeshEnvelope` terms are
  retained as descriptive vocabulary for the agent topology Polos builds.
- **Relicensed from Apache-2.0 to AGPL-3.0** to keep Polos open source while preventing proprietary
  capture; added a README "License & commercial use" section and updated `NOTICE`. Commercial
  arrangements beyond the AGPL: Coeus Institute (https://coeus.institute).
- **Self-improvement measurement is now structural.** The Evaluator->Monitor hand-off carries a new
  `measured_improvement` message type (its own schema with `measured_benefit`, `regressions`, and
  `evaluation_evidence` required), so an unmeasured `proposed_improvement` cannot reach safety review.
  Invariant I13 in `tools/validate_mesh.py` now enforces the exact propose->measure->review routing.
- **Loop guarantees are enforced in the schemas**, not just prose: `iteration_assignment` requires a
  `fresh_context: true` const, `iteration_result` requires `verified_evidence`, and `loop_complete`
  requires `ledger_ref`.
- **I14 is partly mechanical.** The validator now asserts the improvement/backpack `kind` is
  restricted to `lesson` | `playbook`, so a commit cannot express a capability or constraint change.
- Clarified that the **Loop Controller is a tool-less decider** (root `AGENTS.md`, constitution,
  generic adapter), that **Security has no self-halt edge** and is governed by the external human kill
  switch (I8, constitution §Control Signals), and that **tiered approvals are a credential/tool
  activation precondition**, not a separate graph edge (constitution §Tiering).

### Fixed
- Aligned derived docs and counts with the canonical specs: the mesh is now **thirteen agents,
  55 edges, 35 graph message types, 36 schemas** (342 structural checks).

## [0.2.0] — 2026-06-16
### Added
- **Safe looping (loop engineering).** A new tool-less **Loop Controller** role runs a task as a
  bounded, self-correcting loop: mandatory budgets (max iterations / wall-clock / cost / no-progress
  patience), an **externally verifiable** stop condition checked by the Verifier through QC, and
  fresh-context-per-iteration rebuilt from a new append-only `loops/` ledger (the Ralph pattern).
  Documented in `docs/LOOPING.md`.
- **Measured self-improvement (governed Reflexion).** A new read-only **Evaluator** role shadow-tests
  every proposed lesson against held-out episodes in a new `experience/` store and forwards it only on
  measured benefit with zero regressions — on a different model lineage than the proposer, mitigating
  *degeneration of thought*. Learning now proposes falsifiable hypotheses (`proposed_improvement`,
  `lesson_retirement`) routed through the Evaluator first. Documented in `docs/SELF-IMPROVEMENT.md`.
- New message types and payload schemas for both subsystems (`loop_request`, `iteration_assignment`,
  `iteration_result`, `loop_state_update`, `loop_complete`, `proposed_improvement`,
  `rejected_improvement`, `lesson_retirement`) plus the `episode` runtime record schema.
- Constitution sections **§Looping** and **§Self-Improvement**, and completeness invariants
  **I12–I14** enforcing bounded/externally-verified loops, evaluator-before-ratification, and
  append-only/capability-safe improvement.
- `mesh.config.yaml` gained `limits.loop` and `limits.improvement` budgets, and the two new roles in
  `roles_enabled`.
- Validator (`tools/validate_mesh.py`) extended with structural checks for I12–I14.

### Changed
- Reframed the project's thesis from prompt-injection defense to **structural safety + verified
  correctness + governed autonomy**; README, architecture doc, threat model (now T1–T10), and prior
  art updated accordingly.
- The mesh is now **thirteen agents, 55 edges, 34 graph message types, 35 schemas** (333 structural
  checks).

### Fixed
- Closed response, documentation, verdict-audit, and Security control-flow gaps: final responses now
  pass Alpha -> Monitor -> Human, `doc_committed` returns to Taskmaster and audit, every guardian
  verdict is audited, and Security reaches all roles through halt/quarantine control edges.
- Hardened `MeshEnvelope` and result/documentation payload schemas so assignments, evidence,
  credential metadata, gate requirements, and traceable result references are required where needed.
- Strengthened `tools/validate_mesh.py` so it enforces exact graph/card handoff coverage, schema
  hardening sentinels, response gating, doc completion, Security control coverage, and invariants
  I12–I14 instead of only broad type-level consistency.

## [0.1.0] — 2026-06-14
### Added
- Initial public release of the Agent Mesh universal safety harness.
- Core invariant, plane model, and immutable constitution (`constitution/core.md`).
- Eleven canonical agent cards plus the rigid agent-card template (`roles/`).
- The connection layer: uniform `MeshEnvelope`, the complete flow graph with completeness
  invariants, and the request state machine (`contracts/`).
- Per-message-type payload schemas for all 27 message types (`contracts/schemas/`).
- Three guardian policies — Monitor (safety + intent), Quality Control (correctness + quality),
  Security (integrity + HALT) (`oversight/`).
- Archivist agent and the DOX `AGENTS.md` documentation tree across every durable directory.
- OpenRouter-style single-file model binding with a diverse-oversight default (`models.yaml`).
- Stack-agnostic bootstrap protocol (`BUILD.md`) and adapters for generic loops, VS Code / Copilot,
  and LangGraph (`adapters/`).
- Structural validator (`tools/validate_mesh.py`) and a CI workflow that runs it on every PR.
- Architecture deep-dive and a worked end-to-end request trace (`docs/`).
