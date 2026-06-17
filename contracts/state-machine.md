# State Machine — Request Lifecycle

Every request moves through these states. Each state defines transitions for **PASS**, **FAIL**, and
**UNCERTAIN**. There is no undefined state and no unhandled transition — this is the "no logic gaps"
guarantee. The default on UNCERTAIN or a gate being unavailable is **BLOCK** (fail-closed).

## States and transitions

| State | Entered when | PASS -> | FAIL -> | UNCERTAIN -> |
|---|---|---|---|---|
| RECEIVED | Alpha accepts a `user_request` | INTENT_RESOLVED | REFUSED | REFUSED |
| INTENT_RESOLVED | Alpha emits `request_manifest`, Monitor gates it | ROUTING | REFUSED | BLOCKED |
| ROUTING | Router builds retrieval + agent shortlist | GATHERING | REFUSED | BLOCKED |
| CHECKUP_ROUTING | Router emits `checkup_request`, Monitor gates it | CHECKING_HARNESS | REFUSED | BLOCKED |
| CHECKING_HARNESS | Nurse runs read-only diagnostics | CHECKUP_REVIEW | BLOCKED | BLOCKED |
| CHECKUP_REVIEW | Monitor reviews `checkup_report` and optional `repair_manifest` | REPAIR_PLANNING or RESPONDING | BLOCKED | BLOCKED |
| REPAIR_PLANNING | Taskmaster scopes a Monitor-passed `repair_manifest` into normal assignments/doc assignments | EXECUTING | REFUSED | BLOCKED |
| GATHERING | Retrieval Worker returns context, Monitor scrubs it | PLANNING | REFUSED | BLOCKED |
| PLANNING | Taskmaster plans, scopes assignments + JIT creds | EXECUTING | REFUSED | BLOCKED |
| EXECUTING | Worker runs an assignment | SAFETY_GATE | BLOCKED | BLOCKED |
| SAFETY_GATE | Monitor checks the `work_result` (two-axis) | QUALITY_GATE | BLOCKED | BLOCKED |
| QUALITY_GATE | QC checks the result vs definition-of-done | ACCEPTED | REWORK | REWORK |
| REWORK | QC failed the result (count < rework_max) | EXECUTING | BEST_EFFORT | BEST_EFFORT |
| ACCEPTED | A single assignment passed both gates | AGGREGATING | — | — |
| AGGREGATING | Taskmaster collects all accepted results | RESPONDING | REFUSED | BLOCKED |
| RESPONDING | Alpha emits `response` to Monitor; Monitor gates it before human delivery | RESPONDED | REFUSED | BLOCKED |
| RESPONDED | Response delivered to human | **TERMINAL** | — | — |
| BEST_EFFORT | rework_max exhausted | RESPONDING (with explicit caveat) | REFUSED | REFUSED |
| REWORK_EXCEEDED | alias of BEST_EFFORT handling | — | — | — |

## Terminal and exception states

| State | Meaning | Exit |
|---|---|---|
| RESPONDED | Normal completion | end |
| REFUSED | A safety/intent FAIL with no safe rework path | end, with reason logged |
| BLOCKED | A gate blocked (fail-closed) and could not be safely retried | end or ESCALATED |
| HALTED | Security issued HALT/quarantine across planes | end, frozen, ESCALATED |
| ESCALATED | Routed to the human for judgment | human decides: resume, refuse, or halt |

## Rules
- **Fail-closed is the default.** Any UNCERTAIN or gate-unavailable transition goes to BLOCKED, never
  forward.
- **Safety precedes quality.** SAFETY_GATE always runs before QUALITY_GATE; QC never sees content the
  Monitor blocked.
- **Rework is bounded.** REWORK loops back to EXECUTING up to `limits.rework_max`, then BEST_EFFORT
  returns the best result with an explicit caveat — it never loops forever and never silently passes.
- **HALT overrides everything.** Security may move the request to HALTED from any state.
- **Every transition is logged** to the audit store with the request `trace_id`.
- **The doc lifecycle mirrors this**: doc_change -> SAFETY_GATE -> QUALITY_GATE -> committed, with
  doc_rework as its bounded rework loop.
- **The Nurse lifecycle is conditional**: checkup_request/triage_signal -> Nurse read-only diagnostics
  -> Monitor review -> either human/audit report or a Monitor-passed repair_manifest routed through
  normal Taskmaster assignments/doc assignments. Nurse never repairs directly.
