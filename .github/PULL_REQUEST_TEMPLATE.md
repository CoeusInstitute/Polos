## What this changes

<!-- One or two sentences. -->

## Type of change
- [ ] New adapter (a stack mapping under `adapters/`)
- [ ] New role or role edit (`roles/`, with matching `contracts/flow.graph.yaml` + `models.yaml`)
- [ ] Contract change (`contracts/`)
- [ ] Docs only (`docs/`, `README.md`, `**/AGENTS.md`)
- [ ] Other

## Invariant checklist
- [ ] `python tools/validate_mesh.py` passes locally.
- [ ] No change weakens the core invariant (deciders hold no tools; only workers act; oversight holds no tools).
- [ ] No new write path to `constitution/**`.
- [ ] If I added/changed a message type, I added/updated its schema in `contracts/schemas/`.
- [ ] If I added/changed a role, its card `inputs`/`outputs`/`handoffs` match `contracts/flow.graph.yaml`.
- [ ] Affected `AGENTS.md` docs and their `Child DOX Index` entries are updated.

## Notes for reviewers
