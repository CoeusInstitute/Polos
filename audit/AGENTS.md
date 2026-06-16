# AGENTS.md — audit/

## Purpose
The append-only, hash-chained event log. Every manifest, assignment, message, verdict, doc commit,
and backpack edit is recorded here with the request `trace_id`. The forensic backbone and a deterrent.

## Ownership
- The single append-only log sink (one file/stream per deployment).

## Local Contracts
- **Append-only and tamper-evident** (hash-chained). No edits, no deletions.
- Every gate (Monitor, QC, Security) writes a decision entry here (invariant I10).
- Read-only to the Learning and Security agents; writable by no agent except as log emission.

## Verification
- Confirm the hash chain is unbroken across a sample range.
- Confirm every state transition in a dry-run appears in the log.

## Child DOX Index
No child DOX docs are currently defined for this subtree.
