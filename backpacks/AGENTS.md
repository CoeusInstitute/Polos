# AGENTS.md — backpacks/

## Purpose
Per-role, append-only stores of durable lessons learned (recurring errors to watch for, environment
notes). Lessons only — never rules, never new permissions.

## Ownership
- `<role>/` — one append-only store per role, written only via the ratified path.

## Local Contracts
- **Append-only**, provenance-tagged, size-capped. No deletions.
- Written only by `backpack_commit` from Security (non-safety edits) or a Human (safety-adjacent).
- The Learning agent may only **propose**; it has no write path here.
- A backpack entry may never grant capability or weaken a constraint; such proposals are auto-rejected.

## Work Guidance
- Entries are caution/heuristics for a role, consumed read-only at runtime.

## Verification
- Confirm every commit traces to a ratified `backpack_commit` in the audit log.

## Child DOX Index
Per-role subfolders are created at runtime and covered by this parent.
