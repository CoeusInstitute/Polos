# AGENTS.md — adapters/

## Purpose
Stack-specific bootstrap notes. Adapters map the runtime-neutral specs onto a concrete host's
primitives. **Additive only** — an adapter may add wiring detail but may never contradict or weaken
the canonical specs.

## Ownership
- One note per supported host.

## Local Contracts
- Adapters add implementation detail; they do not change roles, capabilities, gates, or the flow graph.
- An adapter MUST be able to deny tools to deciders and oversight. If the host cannot enforce that, the
  invariant fails and the mesh must not be deployed there.

## Work Guidance
- New host -> add a note here following `generic.md`; reference it from `BUILD.md` step 1.
- Each adapter must state how the runtime populates `environment_profile` safely: host kind,
  provider-target detection, approval policy, and tool-boundary enforcement. Secrets are never stored.
- Each adapter must state how Nurse diagnostics stay read-only and threshold-triggered. Nurse repairs
  route through normal Monitor-reviewed Taskmaster assignments/doc assignments, never direct writes.

## Verification
- Confirm the adapter enforces the tool/no-tool boundary and wires every edge in `flow.graph.yaml`.
- Confirm the adapter can populate a redacted environment profile with unambiguous targets before
  shorthand playbooks such as "push to GitHub" or "deploy to Vercel" are used.
- Confirm the adapter can enforce Nurse cooldown/threshold triggers and keep Nurse tool access
  read-only.

## Child DOX Index
- `generic.md` — Default mapping for a single-process function-calling loop.
- `vscode-copilot.md` — Mapping for a VS Code + GitHub Copilot workflow with human-approved steps.
- `langgraph.md` — Mapping for LangGraph / graph-runner backends.
- `codex.md` — Mapping notes for a Codex-style local coding agent host.
- `claude-code.md` — Mapping notes for a Claude Code-style local agent host.
