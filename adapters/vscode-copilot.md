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

## Minimum viable enforcement
1. Decider and oversight chat modes have no effectful tools enabled.
2. `constitution/core.md` is loaded read-only and referenced by every mode.
3. Oversight turns use a different model than execution turns where the platform allows model choice.
4. Consequential tools require a human approval turn (default-block otherwise).
