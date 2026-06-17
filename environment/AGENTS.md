# AGENTS.md — environment/

## Purpose
Runtime-derived, redacted environment profiles for the workspace where Polos is instantiated. A
profile records the host surface (VS Code/Copilot, Codex, Claude Code, LangGraph, generic, etc.),
workspace roots, detected provider targets, available scripts, approval policy, and the tool-boundary
facts needed to run repeatable task playbooks safely.

## Ownership
- One profile per workspace or deployment (for example `environment/<profile_id>.json`), shaped by
  `contracts/schemas/environment_profile.schema.json`.

## Local Contracts
- **No secrets.** Store provider names, target identifiers, and secret variable names only; never store
  tokens, keys, passwords, cookies, or connection strings.
- Written by the runtime's read-only environment detection and refreshed when the workspace target
  changes. No agent edits the profile directly.
- Read by the Router, Taskmaster, Learning, and Evaluator as context for playbook matching,
  verification, and measured improvement.
- **Tool inventory.** The profile's `available_tools` array is the canonical record of which tools
  the host actually exposes (CLIs, IDE extensions, MCP servers, scripts), each with its `kind`,
  highest `consequence_class`, enforcement note, and required secret variable **names**. It is
  detection-derived like the rest of the profile — the runtime writes it; **no agent maintains it by
  hand, so it cannot rot through neglect.** The **Taskmaster** grants JIT credentials only from tools
  listed here; the **Nurse** audits it for staleness and missing/over-broad entries during a checkup.
- Stale, ambiguous, or conflicting targets fail closed. A playbook may not run from a guessed target,
  and an assignment may not request a tool absent from `available_tools`.

## Work Guidance
- Capture evidence for every observed binding: git remotes, package scripts, CI files, provider config
  files, and adapter/tool-boundary facts.
- If multiple remotes or provider targets are present, mark the binding ambiguous and require a human
  decision before a shorthand task can use it.
- The user-authored `PROJECT_CONTEXT.md` at the repo root is the hand-edited companion to this
  auto-detected profile: the profile says what the harness detected; PROJECT_CONTEXT says what the
  user wants the harness to know. The Router reads both.

## Verification
- Confirm `secret_names_only` is true and no secret-looking values are present.
- Confirm the active adapter can enforce the tool/no-tool boundary recorded in the profile.
- Confirm each provider target used by a playbook has direct evidence in the profile.
- Confirm `available_tools` lists only tools the host actually exposes, each with a `consequence_class`,
  and that no entry carries a secret value (names only).

## Child DOX Index
No child DOX docs are currently defined for this subtree.