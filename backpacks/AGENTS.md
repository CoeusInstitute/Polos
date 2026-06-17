# AGENTS.md — backpacks/

## Purpose
Per-role, append-only stores of durable lessons and playbooks learned from runtime evidence. Lessons
are cautionary heuristics; playbooks are reusable task strategies such as "push to GitHub" or
"deploy to Vercel." Neither may be a rule, a permission, or a new capability.

## Ownership
- `<role>/` — one append-only store per role, written only via the ratified path.

## Local Contracts
- **Append-only**, provenance-tagged, size-capped. No deletions.
- Written only by `backpack_commit` from Security (non-safety edits) or a Human (safety-adjacent).
- The Learning agent may only **propose**; it has no write path here.
- A backpack entry may never grant capability or weaken a constraint; such proposals are auto-rejected.
- Playbooks are strategy templates only. They still require environment-profile target resolution,
  preflight checks, consequence-tier approval, JIT credentials, Monitor/QC gates, and verification.

## Work Guidance
- Lessons are caution/heuristics for a role; playbooks are reusable task strategies with aliases,
  preflight checks, steps, verification, recovery notes, and known issue references. Both are consumed
  read-only at runtime.

## Verification
- Confirm every commit traces to a ratified `backpack_commit` in the audit log.

## Child DOX Index
Per-role subfolders are created at runtime and covered by this parent.
