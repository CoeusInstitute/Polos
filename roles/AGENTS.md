# AGENTS.md — roles/

## Purpose
Canonical, authoritative definitions of every agent in the mesh, plus the rigid card template all
roles share. These cards are the **source of truth** for capabilities and handoffs; derived docs
must match them.

## Ownership
- `_TEMPLATE.agent.md` — the mandatory agent-card shape (YAML contract + markdown prompt body).
- `*.agent.md` — one canonical card per role. Front-matter = machine contract; body = system prompt.

## Local Contracts
- Every card MUST use the template's front-matter keys and prompt-section order.
- A card's `capabilities` may never exceed the ceilings in `constitution/core.md`.
- A card's `handoffs` MUST be a subset of edges declared in `contracts/flow.graph.yaml` (no orphans).
- Model binding lives in `models.yaml`. Cards reference it via `model_ref`; never hardcode a model.
- Prompt bodies are **pure markdown**. No JSON, no tool schemas in the body.

## The Roster (capability matrix)
| Role | Plane | Effectful tools | Read-only tools | Write scope | Issue creds | Backpacks | Veto | Model class |
|---|---|---|---|---|---|---|---|---|
| alpha | intent | no | no | none | no | none | none | worker |
| router | orchestration | no | no | none | no | none | none | worker |
| taskmaster | orchestration | no | no | none | **yes (JIT)** | none | none | worker |
| loop-controller | orchestration | no | no | none | no | none | none | worker |
| retrieval-worker | execution | no | **yes (read-only)** | none | no | none | none | worker |
| execution-worker | execution | **yes (scoped)** | per grant | JIT-granted | no | none | none | worker |
| archivist | execution | no | read repo | **`**/AGENTS.md`, `docs/**`** | no | none | none | worker |
| verifier | execution | no | **yes (read-only)** | none | no | none | none | worker |
| monitor | oversight | no | no | none | no | review | **reject** | **trusted-diverse** |
| qc | oversight | no | no | none | no | none | **rework** | **trusted-diverse** |
| security | oversight | no | passive verdict/audit feed only | none | no | ratify | **HALT** | **trusted-diverse** |
| learning | adaptation | no | read audit/experience | none | no | **propose** | none | worker |
| evaluator | adaptation | no | **read-only (sandbox)** | none | no | none | none | **trusted-diverse** |
| nurse | adaptation | no | read repo/audit/experience + validator | none | no | none | none | worker |

Two structural guarantees: exactly one column (effectful tools) can affect the world, held only by
the Execution Worker; the veto/HALT column is held only by tool-less guardians and the human.
Security's verdict/audit feed is passive runtime input, not an active read tool.

## Work Guidance
- New role -> copy `_TEMPLATE.agent.md`, fill the contract, add its edges to `flow.graph.yaml`, add
  a binding to `models.yaml`, then have the Archivist refresh this roster.
- All fourteen roles are fully specified as cards in this directory. Each card's `inputs`, `outputs`,
  and `handoffs` are derived directly from `contracts/flow.graph.yaml`; keep the two in sync when
  either changes.
- After editing YAML front matter in a role card, run `python tools/validate_mesh.py`; nested
  `handoffs` indentation is significant and malformed YAML blocks validation.

## Verification
- Lint every card: front-matter keys present, capabilities within ceilings, handoffs ⊆ flow graph.
- Confirm `model_ref` for each card resolves in `models.yaml`.

## Child DOX Index
No child DOX docs are currently defined for this subtree.
