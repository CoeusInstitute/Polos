# Adapter — Codex-Style Local Coding Agent

How to realize the mesh in a Codex-style local coding agent that runs inside a repository with a
terminal, file tools, and optional provider CLIs.

## Mapping
- **Roles** -> load the canonical `roles/*.agent.md` bodies as separate role prompts or as a role
  dispatcher in the local agent loop.
- **Tool boundary** -> deciders and oversight receive no effectful tools. Only the Execution Worker
  receives shell/file/provider tools, and only for the current assignment's credential grant.
- **Envelope** -> validate the message object against `contracts/envelope.schema.json` at each hop.
- **Flow + gates** -> use `contracts/flow.graph.yaml` as the router table; Monitor and QC are separate
  review calls before any result is accepted.
- **Environment profile** -> set `host_kind: codex`. Populate workspace roots, OS/shell, git remotes,
  package scripts, CI, and provider config evidence using read-only probes. Store provider target IDs
  and secret variable names only. Mark any ambiguous GitHub/Vercel/Supabase target as ambiguous.
- **Tool inventory** -> populate `available_tools` from the shell/file tools and provider CLIs the
  agent can invoke (`git`, `gh`, `vercel`, `supabase`, `docker`, scripts), each with `kind`, highest
  `consequence_class`, enforcement note, and required secret variable names only. The Taskmaster
  grants from this list; the Nurse audits it for staleness.
- **Playbooks** -> load ratified backpack playbooks read-only. A shorthand task such as "push to
  GitHub" may run only when the environment profile has one unambiguous target and the playbook's
  preflight succeeds.
- **Nurse** -> run as a read-only checkup prompt/tool mode. It may inspect files, validator output,
  audit summaries, and experience episodes. It emits reports/manifests only; repairs are ordinary
  assignment work under JIT credentials or Archivist doc work.

## Minimum viable enforcement
1. The tool allow-list is enforced outside the model prompt.
2. Provider CLIs are invoked only by the Execution Worker under JIT credentials.
3. Environment profile detection never prints or stores secret values.
4. Ambiguous targets default-block until a human picks the target.
5. Automatic Nurse wakeups require repeated evidence and cooldown; one failed command is not enough.