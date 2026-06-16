# Worked Example — A Request Through the Mesh

A concrete trace of one request, showing the envelopes that move between agents and where the gates
sit. Payloads and repeated envelope metadata are abbreviated; every message is a `MeshEnvelope`
(`contracts/envelope.schema.json`) sharing one `trace_id`, an unchanged `intent_ref`, explicit
`gates_required`, `consequence_class`, and `credentials` (`null` except on assignments).

**User asks:** *"Add a `/health` endpoint to our API service and update the docs."*

### 1. Human -> Alpha
```json
{ "type": "user_request", "from": "human", "to": "alpha",
  "intent_ref": "Add a /health endpoint to our API service and update the docs.",
  "payload": { "text": "Add a /health endpoint to our API service and update the docs." } }
```

### 2. Alpha -> Monitor -> Router  (request_manifest, Monitor PASS)
```json
{ "type": "request_manifest", "from": "alpha", "to": "router",
  "payload": { "objective": "Expose a /health endpoint and document it",
               "success_criteria": ["endpoint returns 200 + status JSON", "docs mention /health"],
               "constraints": ["no change to auth"] } }
```
Monitor — Axis A (faithful to intent): PASS. Axis B (harmful?): PASS. -> verdict to Security + audit.

### 3. Router -> Retrieval Worker (retrieval_manifest)  then result is scrubbed
```json
{ "type": "retrieval_manifest", "from": "router", "to": "retrieval-worker",
  "payload": { "queries": ["api service router file", "existing endpoint conventions"],
               "scope": "repo:src/api" } }
```
Retrieval Worker (read-only) returns `retrieval_result` with provenance; Monitor scrubs it for
injected instructions before the Router plans on it.

### 4. Router -> Taskmaster (task_manifest)
```json
{ "type": "task_manifest", "from": "router", "to": "taskmaster",
  "payload": { "objective": "Add /health + docs",
               "sub_goals": ["implement endpoint", "update docs"],
               "agent_shortlist": ["execution-worker", "archivist"] } }
```

### 5. Taskmaster -> Execution Worker (assignment + JIT credentials)
```json
{ "type": "assignment", "from": "taskmaster", "to": "execution-worker",
  "credentials": { "scope": "write:src/api/health.*", "tools": ["fs.write","run.tests"],
                   "expires_at": "2026-06-14T20:10:00Z" },
  "payload": { "assignment_id": "asg-health-endpoint",
               "goal": "Add GET /health returning {status:'ok'}",
               "definition_of_done": ["route registered", "unit test passes"],
               "consequence_class": "code-exec" } }
```
Least privilege: the grant allows writing only the health files and running tests, for ten minutes.
Because `consequence_class` is `code-exec`, the tiering table requires **human approval** before the
tool runs.

### 6. Execution Worker -> Monitor -> QC (work_result, double-gated)
```json
{ "type": "work_result", "from": "execution-worker", "to": "monitor",
  "payload": { "assignment_ref": "asg-health-endpoint",
               "status": "success",
               "outputs": { "files": ["src/api/health.ts"] },
               "evidence": "test run: 1 passed",
               "what_was_done": "registered GET /health; added test" } }
```
- **Monitor (safety):** action stayed inside the grant, no auth change -> PASS.
- **QC (quality):** checks against `definition_of_done`. To confirm the test actually passes, QC
  sends a `verify_spec` to the **Verifier**, which runs the suite in a sandbox and returns
  `verify_result {passed:true}`. QC -> `accepted_result`.

### 7. Docs path — Taskmaster -> Archivist (doc_assignment)
The Archivist updates the relevant `AGENTS.md` / docs to mention `/health`, derived from the actual
change. Its `doc_change` passes **Monitor** (does it weaken a constraint? no) then **QC** (DOX shape
+ matches the source + indexes still reachable) -> `doc_committed`.

### 8. Taskmaster -> Monitor -> Alpha -> Monitor -> Human (response)
```json
{ "type": "response", "from": "alpha", "to": "monitor",
  "payload": { "answer": "Added GET /health (returns {status:'ok'}) and updated the docs.",
               "caveats": [] } }
```
Monitor performs the final safety/intent check, emits its verdict to Security + audit, and only then
delivers the same `response` to the human.

### If something had gone wrong
- **QC FAIL** (e.g. test didn't pass): `rework_request` back to the Taskmaster with the exact
  shortfall; re-assigned up to `rework_max`, then a best-effort response with a caveat.
- **Monitor FAIL** (e.g. the worker also tried to change auth): blocked; never reaches QC; verdict to
  Security.
- **Security HALT** (e.g. a pattern of scope-creep across messages): `quarantine` to the Execution
  Worker, `halt` to the deciders, `escalation` to the human with the correlated evidence.

Every step above is appended to the hash-chained audit log under the same `trace_id`.
