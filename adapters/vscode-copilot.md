# Adapter — VS Code / GitHub Copilot

How to realize the mesh inside a VS Code + GitHub Copilot workflow, where "agents" are scoped
instruction files and a human approves consequential steps.

## Mapping
- **Roles** -> one instruction file per role. Put the canonical bodies from `roles/*.agent.md` into
  `.github/instructions/` (or reference this repo's `roles/` directly). The repo's own `AGENTS.md`
  tree is the in-editor contract surface Copilot reads as it works.
- **Tool boundary** -> Copilot's tool/extension permissions are the enforcement point. Configure the
  "decider" and "oversight" chat modes with **no tools / read-only** and the "execution" mode with
  the specific tools a task needs. If a mode can't be tool-restricted, do not use it for a decider.
- **Envelope** -> a JSON object per `contracts/envelope.schema.json`, passed between steps (or kept
  in a scratch file the modes read/write under `docs/` or a working dir).
- **Flow + gates** -> run roles as an ordered chat sequence: Alpha -> Monitor check -> Router ->
  (Retrieval) -> Taskmaster -> Execution -> Monitor -> QC. Implement gates as separate review turns
  using the Monitor/QC bodies; a FAIL stops the sequence and follows `on_fail`.
- **Tiering / approval** -> for `external-write`, `financial`, and `code-exec`, require an explicit
  human approval turn before the Execution mode runs the tool (maps to the constitution's Human
  approval tier). This is the natural fit for Copilot's human-in-the-loop model.
- **Credentials** -> the Taskmaster turn writes the assignment's allowed scope into the envelope; the
  human granting tool access for that turn is the credential.
- **Audit** -> append each envelope + verdict to an append-only file (e.g. `audit/run.jsonl`,
  git-ignored).
- **Environment profile** -> record `host_kind: vscode-copilot`, OS/shell, workspace roots, git
  remotes, `.github/workflows`, package scripts, `.vercel/` or `vercel.json`, and
  `supabase/config.toml` if present. Store only target identifiers and variable names. When multiple
  remotes or provider configs exist, mark the target ambiguous and ask the human before running a
  shorthand playbook.
- **Tool inventory** -> populate the profile's `available_tools` from what the host exposes: enabled
  chat-mode tools, installed VS Code extensions (e.g. `github.copilot-chat`, the Stripe extension),
  connected MCP servers (`mcp:supabase`, `mcp:github`), and CLIs on PATH (`git`, `gh`, `vercel`,
  `supabase`, `az`, `docker`, `stripe`). Record each tool's `kind`, highest `consequence_class`, the
  enforcement point (the Copilot chat-mode tool toggle / human approval turn), and required secret
  variable **names** only. The Taskmaster grants from this list; the Nurse audits it.
- **Playbooks** -> expose ratified backpack playbooks as shorthand-safe procedures: e.g. "push to
  GitHub" first confirms the active remote and branch from the environment profile, then runs preflight,
  commit/push, remote verification, and audit logging through the normal gated workflow.
- **Nurse** -> implement as a read-only checkup mode. It can inspect repo files, diagnostics, validator
  output, audit summaries, and experience episodes, but it cannot edit. Any `repair_manifest` becomes
  normal Copilot work through Taskmaster/Execution Worker or an Archivist doc pass with Monitor/QC
  review.

## Minimum viable enforcement
1. Decider and oversight chat modes have no effectful tools enabled.
2. `constitution/core.md` is loaded read-only and referenced by every mode.
3. Oversight turns use a different model than execution turns where the platform allows model choice.
  Copilot is effectively single-provider, so apply the single-provider guidance in `models.yaml`:
  keep oversight on a different model *family* than the workers, and if only one family is available,
  flag the relaxed anti-correlation guarantee in the environment profile for human acknowledgment.
4. Consequential tools require a human approval turn (default-block otherwise).
5. A redacted environment profile exists and is fresh enough for any shorthand task alias being used.
6. Nurse checkups run only on explicit user request or thresholded Security/audit evidence; do not run
  them automatically in every chat turn.
