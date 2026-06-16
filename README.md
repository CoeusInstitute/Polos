# Polos

**Polos is a self-improving, safe-looping, prompt-injection-proof agentic harness — developed through the R&D efforts of [Coeus Institute](https://coeus.institute).** It turns one AI agent into a governed *mesh* of specialized agents in which no single component can both decide and act, so autonomous agentic work becomes safe enough to leave running: structurally contained, continuously verified, able to loop without running away, and able to improve itself without ever rewriting its own rules.

*An open-source project by [Coeus Institute](https://coeus.institute) — free and open under AGPL-3.0.*

![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)
![Status](https://img.shields.io/badge/status-reference%20architecture-success)
![Checks](https://img.shields.io/badge/structural%20checks-342%20passing-success)
![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Built for agents](https://img.shields.io/badge/built%20for-agents-8A2BE2)

<!-- After pushing, enable the CI badge (replace with your repo path, e.g. CoeusInstitute/polos):
![validate](https://github.com/CoeusInstitute/polos/actions/workflows/validate.yml/badge.svg)
-->

> **The core invariant**
> Anything that can **decide** cannot **act**. Anything that can **act** cannot act **unsupervised**.

## What this is

Most agent frameworks try to make a single model trustworthy enough to be handed power, then bolt on a content filter. Polos starts somewhere else: assume no single component is fully trustworthy, and make the system's properties hold **structurally** — as a consequence of how the agents are wired, not of any one model behaving. Resisting prompt injection falls out of that wiring, but it is the **floor, not the pitch.**

The mesh is built around three capabilities that have to hold *at the same time* for autonomy to be safe:

| | Capability | How |
|---|---|---|
| 🛡️ | **Structural safety** | Deciders hold no tools; one role acts, only on scoped, time-boxed, monitored grants; tool-less guardians can reject / rework / quarantine / **halt** but never act. Safety is a property of the topology. |
| 🔁 | **Safe looping** | Run a task as a bounded, **externally verified** loop (the loop-engineering / Ralph pattern) — with budgets, a Verifier-checked stop condition, and fresh-context-from-ledger — so it can't infinite-loop, drift, or explode in cost. → [`docs/LOOPING.md`](docs/LOOPING.md) |
| 📈 | **Measured self-improvement** | Get better over time by accumulating **evidence-tested, reversible** lessons — proposed by one agent, *measured by a different one*, ratified before commit — so the mesh never expands its own authority. → [`docs/SELF-IMPROVEMENT.md`](docs/SELF-IMPROVEMENT.md) |

The same discipline that contains an untrusted model is exactly what makes looping and self-improvement safe to switch on. That combination — not prompt-injection defense alone — is the point.

---

## This is a spec your agent builds — not a runtime you install

There is nothing to `pip install` as a server. This repository is a **portable specification an agent reads and then constructs around itself**, mapped onto whatever stack you already use — VS Code / GitHub Copilot, a custom harness, a plain function-calling loop, LangGraph, and so on.

### Point your agent at it (copy-paste)

Open this repo in your AI coding tool and give your agent this one instruction:

> Read `AGENTS.md`, then follow `BUILD.md` step by step, and build the Polos harness in this
> workspace, adapted to my stack. Use the matching note in `adapters/` (or `adapters/generic.md`
> if none fits). When you finish, run `python tools/validate_mesh.py` and show me the result.

That is enough for a capable agent. The instructions are written to be followed **literally, in order**, so smaller models can build it too: every step names the exact file to read and what to wire next, and the validator mechanically proves the result is complete.

### Build it yourself (human)

1. Clone the repo and open it in your editor.
2. `pip install -r tools/requirements.txt && python tools/validate_mesh.py` — confirm it prints `PASS`.
3. Bind your models in [`models.yaml`](models.yaml) (one line per role; keep oversight on a different model lineage than workers).
4. Pick an adapter in [`adapters/`](adapters/) for your stack.
5. Have your agent follow [`BUILD.md`](BUILD.md).

---

## Architecture

Three planes do the work — **intent**, **orchestration**, **execution**. One plane guards it — **oversight**. One plane improves it — **adaptation**.

```mermaid
flowchart TB
    H([Human Principal])

    subgraph INTENT["Intent · no tools"]
        A[Alpha]
    end
    subgraph ORCH["Orchestration · deciders, no tools"]
        R[Router]
        T[Taskmaster<br/>mints JIT credentials]
        LC[Loop Controller<br/>bounded loops]
    end
    subgraph EXEC["Execution · the only actors"]
        RW[Retrieval Worker<br/>read-only]
        EW[Execution Worker<br/>scoped tools]
        AR[Archivist<br/>docs only]
        V[Verifier<br/>read-only]
    end
    subgraph OVER["Oversight · guardians, no tools"]
        M[Monitor<br/>safety + intent]
        Q[QC<br/>correctness + quality]
        S[Security<br/>integrity + HALT]
    end
    subgraph ADAPT["Adaptation"]
        L[Learning<br/>propose only]
        E[Evaluator<br/>measure, read-only]
    end

    H --> A --> R --> T
    A -. loop_request .-> LC
    LC -. iteration .-> T
    LC -. loop_complete .-> A
    T --> EW
    T --> AR
    R -. retrieval .-> RW
    Q -. verify .-> V
    EW --> M
    AR --> M
    M --> Q
    M --> S
    Q --> S
    Q -. iteration_result .-> LC
    S -. halt / quarantine .-> EXEC
    L --> E --> M
    S --> H
```

The only column that can affect the world is a single role (Execution Worker). The only roles that can veto or halt are tool-less guardians and the human. The **Loop Controller** drives bounded loops but holds no tools; the **Evaluator** gates self-improvement but only measures.

## Dataflow — the path a single request takes

```mermaid
flowchart TD
    U([user_request]) --> A[Alpha<br/>resolve intent, set intent_ref]
    A -->|request_manifest| M1{{Monitor}}
    M1 -->|FAIL| XR[refuse]
    M1 -->|PASS| RT[Router<br/>plan + what to retrieve]
    RT -->|retrieval_manifest| RW[Retrieval Worker<br/>read-only]
    RW -->|retrieval_result| M2{{Monitor<br/>scrub injection}}
    M2 -->|PASS| TM[Taskmaster<br/>assignments + JIT creds]
    TM -->|assignment| EW[Execution Worker<br/>only granted tools]
    EW -->|work_result| MS{{Monitor<br/>safety · two-axis}}
    MS -->|FAIL| BL[block]
    MS -->|PASS| QG{{QC<br/>vs definition-of-done}}
    QG -. verify_spec .-> VF[Verifier] -. verify_result .-> QG
    QG -->|FAIL · n < max| TM
    QG -->|PASS| AGG[Taskmaster<br/>aggregate]
    AGG -->|aggregate_result| M3{{Monitor}}
    M3 -->|PASS| AC[Alpha<br/>compose]
    AC -->|response| M4{{Monitor<br/>final safety gate}}
    M4 -->|PASS| RESP([response])
    M4 -->|verdict| SE
    MS -->|verdict| SE[[Security]]
    QG -->|verdict| SE
    SE -. HALT / quarantine .-> EW
    SE -. escalation .-> HU([human])
```

Deciders emit manifests but never touch tools. Retrieval is delegated, then scrubbed. The Taskmaster mints least-privilege credentials per assignment. Every worker result is **double-gated** — safety first, then quality. Even the final response is Monitor-gated before human delivery. Security sees every verdict on a side channel, so it can HALT independently.

## 🔁 Looping — autonomy that can't run away

Driven by the tool-less **Loop Controller**, a task can run as a self-correcting loop instead of a single pass — but only under guardrails that answer the three ways loops fail in production (infinite loops, goal drift, cost explosion):

```mermaid
flowchart LR
    A[Alpha] -->|loop_request| LC[Loop Controller]
    LC -->|iteration_assignment| TM[Taskmaster → Worker]
    TM --> GATES{{Monitor → QC → Verifier}}
    GATES -->|iteration_result<br/>+ verified evidence| LC
    LC -->|loop_state_update| LG[(loops/ ledger)]
    LC -->|stop?| D{verified done?<br/>or budget hit?}
    D -->|not yet| TM
    D -->|done / budget_exhausted / no_progress| A
```

- **Budgets are mandatory** — max iterations, wall-clock, cost, no-progress patience. A budget hit stops and reports; it is never extended to "just finish."
- **The stop condition is externally verified** by the Verifier through QC — never a self-reported "done." A loop with no checkable done-test is rejected.
- **Each iteration starts from a fresh context** rebuilt from the [`loops/`](loops) ledger, including the log of prior failed attempts, so dead ends aren't repeated (the Ralph pattern).
- `intent_ref` rides through unchanged, so the Monitor catches drift on every pass, and **Security can HALT** a runaway from any state.

Every iteration is a full pass through the normal safety mesh — looping repeats the gated cycle, it doesn't bypass it. Full detail in [`docs/LOOPING.md`](docs/LOOPING.md).

## 📈 Self-improvement — better over time, without more authority

The mesh improves the way a careful engineering org does: it accumulates **measured, reversible lessons**, not new permissions. The design is governed Reflexion, with the proposer and the evaluator kept deliberately separate:

```mermaid
flowchart LR
    AU[(audit log)] -->|signals| L[Learning<br/>reflect + propose]
    L -->|proposed_improvement| E[Evaluator<br/>shadow-test on held-out experience]
    E -->|measured_improvement| M{{Monitor<br/>safety review}}
    E -->|unmeasured / regressing| RJ[rejected → audit]
    M -->|non-safety| S[[Security ratify]]
    M -->|safety-adjacent| HU([Human ratify])
    S & HU -->|backpack_commit| BP[(backpacks/<br/>append-only, versioned)]
```

- **Measured before adoption.** Learning can only *propose* a falsifiable lesson; the **Evaluator** shadow-tests it against held-out episodes in [`experience/`](experience) and forwards it only if it shows real benefit with **zero** regressions.
- **Independent evaluation.** The Evaluator runs on a **different model lineage** than Learning — the documented mitigation for *degeneration of thought* (a model reinforcing its own flawed reasoning).
- **Append-only and reversible.** Commits are versioned and ratified (Security for non-safety, a human for safety-adjacent); retiring a lesson writes a tombstone, never a deletion.
- **Bounded.** Lessons and playbooks may tune *how* the mesh works; they may **never** grant capability, alter the constitution, or weaken a gate.

A mesh that improves gets **better at its job** but can never **expand its own authority.** Full detail in [`docs/SELF-IMPROVEMENT.md`](docs/SELF-IMPROVEMENT.md).

---

## The thirteen agents

| Agent | Plane | Holds tools? | Can it act? | Veto / control |
|---|---|---|---|---|
| **Alpha** | intent | no | no | — |
| **Router** | orchestration | no | no | — |
| **Taskmaster** | orchestration | no (mints credentials) | no | — |
| **Loop Controller** | orchestration | no | no | drives bounded loops |
| **Retrieval Worker** | execution | read-only | reads only | — |
| **Execution Worker** | execution | **yes, per JIT grant** | **yes (scoped)** | — |
| **Archivist** | execution | docs write only | docs only | — |
| **Verifier** | execution | read-only (sandboxed) | reads only | — |
| **Monitor** | oversight | no | no | reject |
| **Quality Control** | oversight | no | no | rework |
| **Security** | oversight | no | no | **HALT** |
| **Learning** | adaptation | read audit | no | propose only |
| **Evaluator** | adaptation | read-only (sandboxed) | measures only | gate self-improvement |

The three guardians ask three independent questions: **Monitor** — *is this safe and faithful to the original intent?* **QC** — *is this correct and complete?* **Security** — *is the whole system behaving?* None can act.

---

## Directory structure

```
polos/
├── AGENTS.md                  ← DOX root + AGENT ENTRY POINT (an agent starts here)
├── BUILD.md                   ← bootstrap: how an agent builds the mesh in any stack
├── README.md                  ← you are here
├── models.yaml                ← model binding (OpenRouter-style); swap a model in one line
├── mesh.config.yaml           ← enabled roles, tiering, loop + improvement budgets, fail-closed limits
├── LICENSE  ·  NOTICE         ← AGPL-3.0
├── CONTRIBUTING.md  ·  CODE_OF_CONDUCT.md  ·  SECURITY.md  ·  CHANGELOG.md
│
├── constitution/              ← IMMUTABLE rules (authoritative)
│   ├── core.md                   invariant, ceilings, tiering, §Looping, §Self-Improvement, control signals
│   └── AGENTS.md
├── roles/                     ← canonical agent definitions (source of truth)
│   ├── _TEMPLATE.agent.md        the rigid card shape every role fills
│   ├── alpha · router · taskmaster · loop-controller        .agent.md   (intent / orchestration)
│   ├── retrieval-worker · execution-worker · archivist · verifier  .agent.md   (execution)
│   ├── monitor · qc · security                              .agent.md   (oversight)
│   ├── learning · evaluator                                 .agent.md   (adaptation)
│   └── AGENTS.md                 roster + capability matrix
├── contracts/                 ← the connection layer (guarantees no gaps)
│   ├── envelope.schema.json      the one message shape every hop uses
│   ├── flow.graph.yaml           every edge + gate + completeness invariants I1–I14
│   ├── state-machine.md          every state + PASS / FAIL / UNCERTAIN transition
│   ├── schemas/                  payload schemas for 35 graph message types + the episode runtime record
│   └── AGENTS.md
├── oversight/                 ← the three guardian policies (safety / quality / integrity)
│   └── AGENTS.md
├── adapters/                  ← stack mappings (additive)
│   ├── generic.md · vscode-copilot.md · langgraph.md
│   └── AGENTS.md
├── tools/                     ← the structural validator + CI dependency
│   ├── validate_mesh.py · requirements.txt
│   └── AGENTS.md
├── loops/                     ← runtime: per-loop append-only ledger (the loop's source of truth)
│   └── AGENTS.md
├── experience/                ← runtime: episode records, the held-out set the Evaluator measures on
│   └── AGENTS.md
├── backpacks/   audit/        ← runtime: ratified lessons (versioned) / hash-chained decision log
│   └── AGENTS.md  (each)
├── docs/                      ← human-facing, DERIVED documentation
│   ├── ARCHITECTURE.md           rationale, diagrams, threat model, prior art
│   ├── LOOPING.md                safe loop engineering
│   ├── SELF-IMPROVEMENT.md       measured, governed Reflexion
│   ├── EXAMPLE-TRACE.md          a worked request trace
│   └── AGENTS.md
└── .github/                   ← CI workflow + issue / PR templates
    ├── workflows/validate.yml
    ├── PULL_REQUEST_TEMPLATE.md
    └── ISSUE_TEMPLATE/
```

Every durable directory carries an `AGENTS.md` ([DOX](#documentation-that-cannot-drift)) describing what it owns. The Archivist keeps them current and reachable from the root index.

---

## Model binding — one knob, no hidden tiers

All model selection lives in [`models.yaml`](models.yaml). A single `profile` flips the whole mesh; any role can be pinned in one line. IDs are explicit `provider/model` strings — no opaque tiers.

```yaml
profile: balanced            # cheap | balanced | max
profiles:
  balanced:
    worker:    openrouter/anthropic/claude-sonnet-4
    oversight: openrouter/google/gemini-2.0-flash    # different lineage than worker
roles:
  monitor:   { class: oversight }
  evaluator: { class: oversight }    # measures improvements; kept off the worker's lineage on purpose
  security:  { class: oversight, model: openrouter/openai/gpt-4o }   # one-line pin
```

Oversight (and the Evaluator) default to a **different model lineage** than workers, so a jailbreak that fools an actor doesn't automatically fool its guardian — and a flawed proposer doesn't get to grade its own idea. The validator fails if they collapse to the same model.

> Replace the example model IDs with the current slugs for your gateway before running.

---

## How "no gaps" is guaranteed — and enforced

Three mechanisms make the flow total, and one script proves it:

1. **One envelope.** Every inter-agent message is a valid [`MeshEnvelope`](contracts/envelope.schema.json), carrying `intent_ref` unchanged end-to-end.
2. **A complete flow graph.** [`flow.graph.yaml`](contracts/flow.graph.yaml) enumerates every edge and the **fourteen completeness invariants** (I1–I14, including the looping and self-improvement guarantees); senders never choose their own gates, and every gated edge defines an `on_fail`.
3. **A total state machine.** Every state defines PASS / FAIL / UNCERTAIN, defaulting to BLOCK (fail-closed).

```bash
pip install -r tools/requirements.txt
python tools/validate_mesh.py
# -> Polos validation - 13 role cards, 55 edges, 35 graph message types, 36 schemas, 342 checks
# -> PASS - every enforced completeness invariant holds.
```

The validator checks exact edge-by-edge card handoff coverage, card-vs-graph input/output consistency **in both directions**, a payload schema for **every** graph message type, envelope hardening sentinels, model-registry sanity, the capability ceilings, the constitution-is-never-written rule, final-response gating, Security control coverage, verdict audit coverage, the looping and self-improvement invariants (I12–I14), and DOX index reachability — then prints `PASS` or the exact violations. It runs in CI on every push and PR, so the mesh cannot silently drift out of integrity.

---

## Documentation that cannot drift

The repo uses **DOX**: every durable directory has an `AGENTS.md` that is a binding contract for its subtree, in a fixed section order, reachable from the root index. The Archivist maintains the tree, with a hard rule:

> **Docs describe, they do not define.** The canonical specs (`constitution/`, `roles/*`, `contracts/`, `models.yaml`) are authoritative; `AGENTS.md` files are derived. On any contradiction, the source wins and the Archivist repairs the doc.

---

## Extending it

- **Add an adapter** → drop a note in `adapters/` following `generic.md`. It must explain how the host denies tools to deciders and oversight.
- **Add or change a role** → copy `roles/_TEMPLATE.agent.md`, fill the front-matter contract, add a binding to `models.yaml`, and wire its edges in `contracts/flow.graph.yaml`. The validator enforces that the card and the graph agree.
- **Add a message type** → add `contracts/schemas/<type>.schema.json`, the edge(s), and update the affected cards.

Run `python tools/validate_mesh.py` before every PR. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Where to look

| If you want to… | Read |
|---|---|
| Understand the design rationale, threat model, and diagrams | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Understand safe looping (budgets, stop conditions, the ledger) | [`docs/LOOPING.md`](docs/LOOPING.md) |
| Understand measured self-improvement | [`docs/SELF-IMPROVEMENT.md`](docs/SELF-IMPROVEMENT.md) |
| See a request flow through the mesh with example envelopes | [`docs/EXAMPLE-TRACE.md`](docs/EXAMPLE-TRACE.md) |
| Read the immutable rules | [`constitution/core.md`](constitution/core.md) |
| See exactly how agents connect | [`contracts/flow.graph.yaml`](contracts/flow.graph.yaml) |
| Build the mesh in your stack | [`BUILD.md`](BUILD.md) + [`adapters/`](adapters/) |

---

## License & commercial use

Polos is free and open source under the **GNU AGPL-3.0** ([`LICENSE`](LICENSE)). You may use, study, modify, and share it — including inside a company.

What the AGPL is here to prevent is **quiet proprietary capture**. If you run a *modified* version of Polos as a network service, the AGPL (section 13) requires you to offer your modified source to its users. In practice Polos can power your own work freely, but it cannot be forked into a closed, repackaged commercial product without giving those improvements back to the community. That is a deliberate stance: **Polos is a public good for the agent-safety community, stewarded by [Coeus Institute](https://coeus.institute) — not a product to be privatized.**

If you want to build something on top of Polos that the AGPL would not allow, that needs a separate arrangement — contact **Coeus Institute** at <https://coeus.institute>.

> Honest note on terms: a genuine open-source license cannot ban commercial *use* outright — that is part of what "open source" means. AGPL-3.0 is the strongest open-source way to keep a project open and hard to exploit. If a hard non-commercial restriction matters more than the "open source" label, a source-available license such as PolyForm Noncommercial is the alternative.

## Status

Reference architecture, `v0.2.0` (adds safe looping + measured self-improvement). "Polos" is the project's name; forks may rename by updating `README.md`, `NOTICE`, and `CONTRIBUTING.md`.

## Credits

Polos is created and maintained by **[Coeus Institute](https://coeus.institute)** as part of its agent-safety R&D.

It draws on the reference-monitor concept, capability security / least privilege, and the "AI control" idea of a trusted weaker model supervising an untrusted stronger one; on **loop engineering** (Boris Cherny, Peter Steinberger, Addy Osmani) and the **Ralph** technique for safe loops; on **Reflexion** (Shinn et al., 2023) and its "degeneration of thought" failure mode for measured self-improvement; and on the DOX `AGENTS.md` documentation convention.
