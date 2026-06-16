# Contributing to Polos

Thanks for helping make agentic systems safer. This repo is a **specification**, so contributions
are mostly spec edits — new roles, new adapters, tighter contracts, clearer docs. A few rules keep
the architecture sound.

## The one rule that cannot be broken
Every change must preserve the **core invariant**:

> Anything that can decide cannot act, and anything that can act cannot act unsupervised.

Concretely, a PR may **never**:
- give a decider (Alpha, Router, Taskmaster, Loop Controller) or an oversight agent (Monitor, QC,
  Security) an effectful tool;
- give any role a standing write scope except the Archivist (`**/AGENTS.md`, `docs/**`);
- create a write path to `constitution/**`;
- let documentation define behavior (docs are derived; canonical specs win).

If your idea needs one of these, it's a different architecture — open a proposal issue first.

## Before you open a PR
1. Run the validator and make sure it passes:
   ```bash
   pip install -r tools/requirements.txt
   python tools/validate_mesh.py
   ```
2. Keep the layers consistent:
   - **New/changed message type** -> add or update its schema in `contracts/schemas/`, and the
     edge(s) in `contracts/flow.graph.yaml`.
   - **New/changed role** -> copy `roles/_TEMPLATE.agent.md`, fill the front-matter contract, add a
     binding in `models.yaml`, and make sure the card's `inputs`/`outputs`/`handoffs` exactly match
     the flow graph (the validator checks this in both directions).
   - **New adapter** -> add a note under `adapters/` following `generic.md`; it must explain how the
     host denies tools to deciders and oversight.
3. Follow **DOX** for docs: update the nearest owning `AGENTS.md`, refresh any affected
   `Child DOX Index`, and never invent rules the specs don't prove. The validator checks that every
   `AGENTS.md` is reachable from the root index.

## Prompt style
Agent prompt bodies are **pure markdown** in the house structure (Priority Stack -> Identity ->
Prime Directive gate -> Procedure -> Self-Check -> Output Contract -> Anti-Patterns). Contracts and
config are YAML/JSON. Don't mix the two.

## Commit / PR hygiene
- Small, focused PRs.
- Use the PR template's invariant checklist.
- CI must be green (it runs `tools/validate_mesh.py`).

## Renaming a fork
"Polos" is this project's name. If you fork to publish under a different name, update `README.md`,
`NOTICE`, and `CONTRIBUTING.md`. The AGPL requires you to keep prominent notice of your modifications
and to preserve the license and notices; see `LICENSE`.
