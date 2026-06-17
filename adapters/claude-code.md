# Adapter — Claude Code-Style Local Agent

How to realize the mesh in a Claude Code-style local coding environment while preserving Polos's
decide/act split.

## Mapping
- **Roles** -> use the canonical role cards as mode-specific instructions or as a dispatcher that swaps
  the active role prompt.
- **Tool boundary** -> configure tool access so Alpha, Router, Taskmaster, Loop Controller, Monitor,
  QC, and Security have no effectful tools. Execution Worker receives only assignment-scoped tools.
- **Envelope** -> persist or pass a JSON object matching `contracts/envelope.schema.json` between role
  turns.
- **Flow + gates** -> follow `contracts/flow.graph.yaml`; Monitor and QC turns are separate gates and
  their verdicts are appended to audit.
- **Environment profile** -> set `host_kind: claude-code`. Record workspace roots, OS/shell, git
  remotes, package scripts, CI, and provider config evidence using read-only probes. Store secret names
  only, never values.
- **Tool inventory** -> populate `available_tools` from the host's allowed tools and provider CLIs,
  each with `kind`, highest `consequence_class`, enforcement note, and required secret variable names
  only. The Taskmaster grants JIT credentials only from this list; the Nurse audits it.
- **Playbooks** -> ratified backpack playbooks may provide aliases and step templates, but they do not
  grant authority. Consequential actions still require the configured approval tier and JIT credentials.
- **Nurse** -> use a read-only diagnostic mode for checkups. It may inspect repo structure, validator
  output, audit summaries, and experience episodes, then emit `checkup_report` or `repair_manifest` to
  Monitor. It must not hold file-write or shell privileges.

## Minimum viable enforcement
1. If the host cannot deny effectful tools to deciders and oversight, do not deploy the mesh there.
2. A shorthand playbook may not run without a fresh, unambiguous environment profile.
3. All playbook failures and recoveries are logged so Learning can propose measured playbook patches.
4. Nurse checkups are explicit or threshold-triggered; do not run them as a default background step.