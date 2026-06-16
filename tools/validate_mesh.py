#!/usr/bin/env python3
"""
validate_mesh.py - structural integrity checker for Polos (the governed agent mesh).

Proves the "no gaps" property mechanically. Run before going live and in CI:

    pip install -r tools/requirements.txt
    python tools/validate_mesh.py

Exit code 0 = all invariants hold; 1 = one or more violations (printed).
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUBSTRATE_NODES = {"human", "audit", "backpacks", "loops"}
CONTROL_TYPES = {"halt", "quarantine"}
GATE_ROLES = {"monitor", "qc", "security"}
OVERSIGHT_ROLES = {"monitor", "qc", "security"}
READONLY_ALLOWED = {
    "retrieval-worker",
    "execution-worker",
    "archivist",
    "learning",
    "verifier",
    "evaluator",
}
ALLOWED_OFF_GRAPH_SCHEMAS = {"episode"}


def rel(path):
    return os.path.relpath(path, ROOT)


def load_yaml(path):
    import yaml
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def front_matter(path):
    import yaml
    text = read_text(path)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError(f"{rel(path)}: missing YAML front-matter")
    return yaml.safe_load(match.group(1))


def is_truthy_list(value):
    return bool(value or [])


def resolved_model(models, active_profile, role):
    role_cfg = models.get("roles", {}).get(role, {})
    if "model" in role_cfg:
        return role_cfg["model"]
    role_class = role_cfg.get("class")
    return models.get("profiles", {}).get(active_profile, {}).get(role_class)


def main():
    problems, checks = [], 0

    def fail(message):
        problems.append(message)

    # ---- 1. JSON + YAML well-formedness -----------------------------------
    for path in glob.glob(os.path.join(ROOT, "**", "*.json"), recursive=True):
        checks += 1
        try:
            load_json(path)
        except Exception as exc:
            fail(f"[json] {rel(path)}: {exc}")

    yaml_paths = glob.glob(os.path.join(ROOT, "*.yaml")) + glob.glob(
        os.path.join(ROOT, "**", "*.yaml"), recursive=True
    )
    for path in yaml_paths:
        checks += 1
        try:
            load_yaml(path)
        except Exception as exc:
            fail(f"[yaml] {rel(path)}: {exc}")

    # ---- 2. Load canonical graph, cards, models, config --------------------
    graph = load_yaml(os.path.join(ROOT, "contracts", "flow.graph.yaml"))
    edges = graph.get("edges", [])
    edge_set = set()
    all_types = set()
    from_types, to_types = {}, {}
    edges_from = {}

    for edge in edges:
        checks += 1
        for key in ("from", "to", "type", "gates"):
            if key not in edge:
                fail(f"[graph] edge missing '{key}': {edge}")
        if not all(key in edge for key in ("from", "to", "type", "gates")):
            continue

        source, target, msg_type = edge["from"], edge["to"], edge["type"]
        edge_tuple = (source, target, msg_type)
        if edge_tuple in edge_set:
            fail(f"[graph] duplicate edge {source}->{target} ({msg_type})")
        edge_set.add(edge_tuple)
        all_types.add(msg_type)
        from_types.setdefault(source, set()).add(msg_type)
        edges_from.setdefault(source, []).append(edge)
        if msg_type not in CONTROL_TYPES:
            to_types.setdefault(target, set()).add(msg_type)

        gates = edge.get("gates") or []
        if gates and "on_fail" not in edge:
            fail(f"[I4] edge {source}->{target} ({msg_type}) has gates but no on_fail")
        if not gates and "on_fail" in edge:
            fail(f"[I4] edge {source}->{target} ({msg_type}) has on_fail but no gates")
        for gate in gates:
            if gate not in GATE_ROLES:
                fail(f"[graph] edge {source}->{target} ({msg_type}) uses unknown gate '{gate}'")
        if edge.get("on_fail") not in (None, "refuse", "block"):
            fail(f"[graph] edge {source}->{target} ({msg_type}) has unknown on_fail '{edge.get('on_fail')}'")

    cards = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "roles", "*.agent.md"))):
        if path.endswith("_TEMPLATE.agent.md"):
            continue
        fm = front_matter(path)
        role = fm.get("role")
        if role in cards:
            fail(f"[card] duplicate role '{role}'")
        cards[role] = fm

    role_ids = set(cards)
    models = load_yaml(os.path.join(ROOT, "models.yaml"))
    cfg = load_yaml(os.path.join(ROOT, "mesh.config.yaml")) or {}
    limits = cfg.get("limits", {})

    # ---- 3. Node, schema, and model registry sanity ------------------------
    for edge in edges:
        checks += 1
        source, target = edge.get("from"), edge.get("to")
        if source not in role_ids and source not in SUBSTRATE_NODES:
            fail(f"[graph] edge source '{source}' is neither a role nor a substrate node")
        if target not in role_ids and target not in SUBSTRATE_NODES:
            fail(f"[graph] edge target '{target}' is neither a role nor a substrate node")

    schema_dir = os.path.join(ROOT, "contracts", "schemas")
    schema_files = {
        os.path.basename(path).replace(".schema.json", "")
        for path in glob.glob(os.path.join(schema_dir, "*.schema.json"))
    }
    for msg_type in sorted(all_types):
        checks += 1
        if msg_type not in schema_files:
            fail(f"[schema] message type '{msg_type}' has no contracts/schemas/{msg_type}.schema.json")
    for schema_name in sorted(schema_files - all_types - ALLOWED_OFF_GRAPH_SCHEMAS):
        checks += 1
        fail(f"[schema] contracts/schemas/{schema_name}.schema.json is not used by the graph or an allowed runtime store")

    model_roles = set(models.get("roles", {}).keys())
    for role in sorted(role_ids - model_roles):
        checks += 1
        fail(f"[models] role card '{role}' has no models.yaml binding")
    for role in sorted(model_roles - role_ids):
        checks += 1
        fail(f"[models] models.yaml binding '{role}' has no role card")

    active = os.environ.get("MESH_PROFILE", models.get("profile"))
    if active not in models.get("profiles", {}):
        fail(f"[models] active profile '{active}' not defined in profiles")
    else:
        profile = models["profiles"][active]
        if profile.get("worker") == profile.get("oversight"):
            fail(f"[models] profile '{active}': oversight shares the worker model")
        if resolved_model(models, active, "learning") == resolved_model(models, active, "evaluator"):
            fail("[I13] evaluator resolves to the same model as learning")

    for role, role_cfg in sorted(models.get("roles", {}).items()):
        checks += 1
        role_class = role_cfg.get("class")
        if role_class not in {"worker", "oversight"}:
            fail(f"[models] {role}: class must be worker or oversight")
        if role in OVERSIGHT_ROLES | {"evaluator"} and role_class != "oversight":
            fail(f"[models] {role}: must bind to oversight class")
        if role == "learning" and role_class != "worker":
            fail("[models] learning: must bind to worker class")

    # ---- 4. Agent cards vs graph (exact handoffs, types, gates, ceilings) --
    for role, fm in sorted(cards.items()):
        checks += 1
        inputs = set(fm.get("inputs") or [])
        outputs = set(fm.get("outputs") or [])
        handoffs = {(role, item["to"], item["type"]) for item in (fm.get("handoffs") or [])}
        graph_handoffs = {(edge["from"], edge["to"], edge["type"]) for edge in edges_from.get(role, [])}
        graph_outputs = from_types.get(role, set())
        graph_inputs = to_types.get(role, set())

        if fm.get("model_ref") not in model_roles:
            fail(f"[card] {role}: model_ref '{fm.get('model_ref')}' not in models.yaml")
        for handoff in sorted(handoffs - edge_set):
            fail(f"[card] {role}: handoff to {handoff[1]} ({handoff[2]}) has no edge in flow graph")
        for handoff in sorted(graph_handoffs - handoffs):
            fail(f"[card] {role}: graph edge to {handoff[1]} ({handoff[2]}) missing from handoffs")

        for msg_type in sorted(graph_outputs - outputs):
            fail(f"[I1] {role}: graph sends '{msg_type}' but card.outputs omits it")
        for msg_type in sorted(outputs - graph_outputs):
            fail(f"[I1] {role}: card.outputs '{msg_type}' has no outbound edge")
        for msg_type in sorted(graph_inputs - inputs):
            fail(f"[I2] {role}: graph delivers '{msg_type}' but card.inputs omits it")
        for msg_type in sorted(inputs - graph_inputs):
            fail(f"[I2] {role}: card.inputs '{msg_type}' has no inbound edge")

        cap = fm.get("capabilities", {})
        if is_truthy_list(cap.get("effectful_tools")) and role != "execution-worker":
            fail(f"[I6] {role}: holds effectful_tools but is not execution-worker")
        if is_truthy_list(cap.get("readonly_tools")) and role not in READONLY_ALLOWED:
            fail(f"[ceiling] {role}: holds readonly_tools but is not an allowed read-only role")
        if is_truthy_list(cap.get("write_scope")) and role != "archivist":
            fail(f"[ceiling] {role}: has a standing write_scope but is not archivist")
        if cap.get("issue_credentials") and role != "taskmaster":
            fail(f"[ceiling] {role}: issues credentials but is not taskmaster")
        if cap.get("veto") not in (None, "none") and role not in OVERSIGHT_ROLES:
            fail(f"[ceiling] {role}: has veto '{cap.get('veto')}' but is not an oversight role")

        expected_trust = "trusted-diverse" if role in OVERSIGHT_ROLES | {"evaluator"} else "worker"
        if fm.get("trust_class") != expected_trust:
            fail(f"[card] {role}: trust_class must be {expected_trust}")

        for edge in edges_from.get(role, []):
            gates = set(edge.get("gates") or [])
            if gates and not gates.issubset(set(fm.get("gates_out") or [])):
                fail(f"[gates] {role}: gates_out omits {sorted(gates)} for {edge['type']} to {edge['to']}")
            target_card = cards.get(edge["to"])
            if gates and target_card and not gates.issubset(set(target_card.get("gates_in") or [])):
                fail(f"[gates] {edge['to']}: gates_in omits {sorted(gates)} for {role}->{edge['to']} ({edge['type']})")

    # ---- 5. Constitution and core graph invariants -------------------------
    for edge in edges:
        checks += 1
        if edge["to"].startswith("constitution"):
            fail(f"[I7] edge writes to constitution: {edge}")
    for role, fm in cards.items():
        for write_scope in fm.get("capabilities", {}).get("write_scope") or []:
            checks += 1
            if "constitution" in write_scope:
                fail(f"[I7] {role}: write_scope includes constitution path '{write_scope}'")

    required_edges = {
        ("execution-worker", "monitor", "work_result"),
        ("monitor", "qc", "work_result"),
        ("archivist", "monitor", "doc_change"),
        ("monitor", "qc", "doc_change"),
        ("alpha", "monitor", "response"),
        ("monitor", "human", "response"),
        ("qc", "taskmaster", "doc_committed"),
        ("security", "human", "escalation"),
        ("monitor", "security", "verdict"),
        ("qc", "security", "verdict"),
        ("monitor", "audit", "verdict"),
        ("qc", "audit", "verdict"),
        ("security", "audit", "verdict"),
    }
    for edge_tuple in sorted(required_edges):
        checks += 1
        if edge_tuple not in edge_set:
            fail(f"[graph] missing required edge {edge_tuple[0]}->{edge_tuple[1]}:{edge_tuple[2]}")
    for forbidden in (("execution-worker", "qc", "work_result"), ("execution-worker", "taskmaster", "work_result"), ("alpha", "human", "response")):
        checks += 1
        if forbidden in edge_set:
            fail(f"[graph] forbidden bypass edge {forbidden[0]}->{forbidden[1]}:{forbidden[2]}")

    for role, fm in sorted(cards.items()):
        if role == "security":
            continue
        checks += 1
        expected_control = "quarantine" if fm.get("plane") in {"execution", "adaptation"} else "halt"
        if ("security", role, expected_control) not in edge_set:
            fail(f"[I8] security lacks {expected_control} edge to {role}")

    # ---- 6. Looping + self-improvement invariants -------------------------
    roles_enabled = cfg.get("roles_enabled", {})
    for required in ("monitor", "qc", "security"):
        checks += 1
        if roles_enabled.get(required) is not True:
            fail(f"[config] roles_enabled.{required} must be true")
    if roles_enabled.get("learning") is True and roles_enabled.get("evaluator") is not True:
        fail("[config] roles_enabled.evaluator must be true when learning is true")

    loopcfg = limits.get("loop", {})
    for key in ("max_iterations", "max_wall_clock_seconds", "max_cost_usd", "no_progress_patience"):
        checks += 1
        if key not in loopcfg:
            fail(f"[I12] mesh.config limits.loop missing budget '{key}'")
    if loopcfg.get("require_external_stop_condition") is not True:
        fail("[I12] mesh.config limits.loop.require_external_stop_condition must be true")
    for edge_tuple, message in {
        ("qc", "loop-controller", "iteration_result"): "stop evidence must arrive via QC",
        ("verifier", "qc", "verify_result"): "stop condition must be Verifier-checked",
        ("loop-controller", "alpha", "loop_complete"): "loop completion path missing",
    }.items():
        checks += 1
        if edge_tuple not in edge_set:
            fail(f"[I12] missing {edge_tuple[0]}->{edge_tuple[1]}:{edge_tuple[2]} ({message})")
    if ("execution-worker", "loop-controller", "iteration_result") in edge_set:
        fail("[I12] execution-worker must not self-report iteration_result to loop-controller")

    if ("learning", "evaluator", "proposed_improvement") not in edge_set:
        fail("[I13] missing learning->evaluator:proposed_improvement")
    if ("evaluator", "monitor", "measured_improvement") not in edge_set:
        fail("[I13] missing evaluator->monitor:measured_improvement")
    for edge in edges:
        if edge["type"] == "proposed_improvement":
            checks += 1
            if edge["to"] != "evaluator":
                fail(f"[I13] proposed_improvement must go only to the Evaluator, not {edge['to']}")
            if edge["from"] != "learning":
                fail(f"[I13] proposed_improvement must originate only from Learning, not {edge['from']}")
        if edge["type"] == "measured_improvement":
            checks += 1
            if edge["from"] != "evaluator":
                fail(f"[I13] measured_improvement must originate only from the Evaluator, not {edge['from']}")
            if edge["to"] != "monitor":
                fail(f"[I13] measured_improvement must go only to the Monitor, not {edge['to']}")

    impcfg = limits.get("improvement", {})
    if impcfg.get("commits_append_only") is not True:
        fail("[I14] mesh.config limits.improvement.commits_append_only must be true")
    for edge in edges:
        if edge["type"] == "backpack_commit" and edge["from"] not in {"security", "human"}:
            fail(f"[I14] backpack_commit originates from {edge['from']} (only security or human may commit)")

    # ---- 7. Schema hardening sentinels ------------------------------------
    envelope = load_json(os.path.join(ROOT, "contracts", "envelope.schema.json"))
    required_envelope = set(envelope.get("required", []))
    for field in ("credentials", "gates_required", "consequence_class"):
        checks += 1
        if field not in required_envelope:
            fail(f"[schema] MeshEnvelope must require '{field}'")
    if not envelope.get("allOf"):
        fail("[schema] MeshEnvelope must condition credentials on assignment vs non-assignment messages")

    schema_expectations = {
        "assignment": {"assignment_id", "goal", "definition_of_done", "consequence_class"},
        "work_result": {"assignment_ref", "status", "outputs", "evidence"},
        "accepted_result": {"assignment_ref", "result"},
        "rework_request": {"assignment_ref", "failed_checks"},
        "doc_assignment": {"doc_assignment_id", "targets", "reason"},
        "doc_committed": {"doc_assignment_ref", "path"},
        "verify_spec": {"verify_id", "target_ref", "check"},
        "verify_result": {"verify_ref", "check", "passed", "evidence"},
        "aggregate_result": {"result_refs", "results"},
        "measured_improvement": {"target_failure", "hypothesis", "kind", "target_role", "delta", "evidence_trace_ids", "measured_benefit", "regressions", "evaluation_evidence"},
        "iteration_assignment": {"iteration_n", "ledger_ref", "goal", "fresh_context"},
        "iteration_result": {"iteration", "passed", "verified_evidence"},
        "loop_complete": {"loop_id", "status", "ledger_ref"},
    }
    for schema_name, required_fields in sorted(schema_expectations.items()):
        checks += 1
        schema = load_json(os.path.join(schema_dir, f"{schema_name}.schema.json"))
        missing = required_fields - set(schema.get("required", []))
        if missing:
            fail(f"[schema] {schema_name}.schema.json required fields missing {sorted(missing)}")
    for schema_name in ("backpack_commit", "proposed_improvement"):
        checks += 1
        schema = load_json(os.path.join(schema_dir, f"{schema_name}.schema.json"))
        if not schema.get("allOf"):
            fail(f"[schema] {schema_name}.schema.json must encode conditional requirements")
    for schema_name in ("backpack_commit", "proposed_improvement", "measured_improvement"):
        checks += 1
        schema = load_json(os.path.join(schema_dir, f"{schema_name}.schema.json"))
        kind_enum = schema.get("properties", {}).get("kind", {}).get("enum")
        if kind_enum != ["lesson", "playbook"]:
            fail(f"[I14] {schema_name}.schema.json kind must be restricted to ['lesson','playbook'], got {kind_enum}")

    # ---- 8. DOX reachability ----------------------------------------------
    agents_dirs = {
        os.path.dirname(rel(path))
        for path in glob.glob(os.path.join(ROOT, "**", "AGENTS.md"), recursive=True)
    }
    all_docs_text = "\n".join(
        read_text(path) for path in glob.glob(os.path.join(ROOT, "**", "AGENTS.md"), recursive=True)
    )
    for directory in sorted(agents_dirs):
        if directory == "":
            continue
        checks += 1
        if f"{directory}/AGENTS.md" not in all_docs_text:
            fail(f"[DOX] {directory}/AGENTS.md is not referenced by any Child DOX Index")

    # ---- report ------------------------------------------------------------
    print(
        f"Polos validation - {len(cards)} role cards, {len(edges)} edges, "
        f"{len(all_types)} graph message types, {len(schema_files)} schemas, {checks} checks"
    )
    if problems:
        print(f"\nFAIL - {len(problems)} violation(s):")
        for problem in problems:
            print("  -", problem)
        return 1
    print("\nPASS - every enforced completeness invariant holds.")
    return 0


if __name__ == "__main__":
    try:
        import yaml  # noqa: F401
    except ImportError:
        print("This validator needs pyyaml: pip install -r tools/requirements.txt", file=sys.stderr)
        sys.exit(2)
    sys.exit(main())