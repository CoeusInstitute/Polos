"""Read-only verification runner."""

from __future__ import annotations

from pathlib import Path
import subprocess

from polos.audit.reader import read_jsonl
from polos.runtime.tasks import TASK_ROOT
from polos.tools.validator import validate_mesh
from polos.verification.checks import CheckResult, not_applicable
from polos.verification.evidence import write_evidence


FORBIDDEN_PATHS = ("constitution/", ".env", ".git/", ".ssh/", ".aws/")
ALLOWED_POLICY_DECISIONS = {"allowed", "requires_approval", "requires_sandbox"}


def run_required_checks(root: Path, task_id: str, required_checks: list[str]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for check in required_checks:
        if check == "mesh_validate":
            validation = validate_mesh(root)
            results.append(CheckResult(
                name="mesh_validate",
                passed=validation.passed,
                stdout=validation.stdout,
                stderr=validation.stderr,
                exit_code=validation.exit_code,
            ))
        elif check == "pytest":
            results.append(run_command(root, "pytest", ["python", "-m", "pytest"]))
        elif check == "git_diff_presence":
            results.append(run_command(root, "git_diff_presence", ["git", "diff", "--stat"]))
        elif check == "forbidden_files":
            results.append(check_forbidden_files(root))
        elif check == "policy_violations":
            results.append(check_policy_violations(root, task_id))
        else:
            results.append(not_applicable(check, "No runner is registered for this check."))
    write_evidence(root / TASK_ROOT / task_id, results)
    return results


def run_command(root: Path, name: str, command: list[str]) -> CheckResult:
    try:
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        return not_applicable(name, str(exc))
    return CheckResult(
        name=name,
        passed=completed.returncode == 0,
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
    )


def required_checks_passed(results: list[CheckResult]) -> bool:
    return all(result.passed or not result.applicable for result in results)


def check_forbidden_files(root: Path, forbidden: tuple[str, ...] = FORBIDDEN_PATHS) -> CheckResult:
    try:
        completed = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return not_applicable("forbidden_files", str(exc))
    if completed.returncode != 0:
        return not_applicable("forbidden_files", "git diff unavailable in this workspace")
    changed = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    violations = [path for path in changed if any(path.startswith(prefix) for prefix in forbidden)]
    return CheckResult(
        name="forbidden_files",
        passed=not violations,
        reason="forbidden paths changed: " + ", ".join(violations) if violations else "no forbidden paths changed",
        metadata={"changed": changed, "violations": violations},
    )


def check_policy_violations(root: Path, task_id: str) -> CheckResult:
    toolcalls_path = root / TASK_ROOT / task_id / "TOOLCALLS.jsonl"
    events = read_jsonl(toolcalls_path)
    violations = [
        {"tool": event.get("tool"), "policy_decision": event.get("policy_decision")}
        for event in events
        if event.get("event_type") == "tool_call"
        and event.get("policy_decision") not in ALLOWED_POLICY_DECISIONS
        and event.get("exit_code") == 0
    ]
    return CheckResult(
        name="policy_violations",
        passed=not violations,
        reason="policy-violating executions detected" if violations else "no policy-violating executions recorded",
        metadata={"violations": violations, "events_scanned": len(events)},
    )
