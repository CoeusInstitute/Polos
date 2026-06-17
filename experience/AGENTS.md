# AGENTS.md — experience/

## Purpose
Runtime-written store of `episode` records derived from the audit log: past task, playbook, Nurse
checkup, and repair trajectories tagged with what happened, which environment profile and provider
targets were used, which preflights ran, which errors occurred, how they were resolved, and whether
verification passed. This is the **held-out evaluation data** the Evaluator uses to shadow-test
proposed improvements before they can reach ratification. It is what makes self-improvement and repair
learning *measured* rather than superstitious.

## Ownership
- Append-only `episode` records derived from the audit log by the runtime.

## Local Contracts
- Read-only to the Evaluator (`read_experience`) and Learning; written only by the runtime's
  episode-derivation from audit. No agent edits it directly.
- Evaluation must use **held-out** episodes (not the traces that generated a proposal) plus a control
  set, so both benefit and regressions can be measured.
- Repeatable task playbooks must be evaluated against episodes from matching task families and host
  profiles, plus control episodes that should not change.
- Nurse checkups and repairs must record `checkup_id`, `repair_manifest_id`, trigger source, outcome,
  cooldown suppression/override, and whether a repair was completed, blocked, or a false positive.

## Verification
- Confirm the Evaluator measures benefit AND regressions on disjoint held-out and control sets.
- Confirm workflow episodes record `task_family`, `playbook_id`, `environment_profile_ref`, preflight
  results, error signatures, known issue refs, and verification results when those fields apply.
- Confirm Nurse-related episodes record checkup/repair ids and trigger outcomes when those fields apply.

## Child DOX Index
No child DOX docs are currently defined for this subtree.
