from pathlib import Path
import json

from polos.runtime.tasks import TASK_ROOT, create_task
from polos.verification.runner import (
    check_forbidden_files,
    check_policy_violations,
    required_checks_passed,
    run_required_checks,
)


def write_toolcalls(task_path: Path, events: list[dict]) -> None:
    toolcalls = task_path / "TOOLCALLS.jsonl"
    toolcalls.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")


def test_policy_violations_passes_on_clean_log(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Clean policy log")
    write_toolcalls(
        task.path,
        [{"event_type": "tool_call", "tool": "read_file", "policy_decision": "allowed", "exit_code": 0}],
    )

    result = check_policy_violations(tmp_path, task.task_id)

    assert result.passed
    assert result.metadata["violations"] == []


def test_policy_violations_flags_denied_execution(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Tampered policy log")
    write_toolcalls(
        task.path,
        [{"event_type": "tool_call", "tool": "shell_run", "policy_decision": "denied", "exit_code": 0}],
    )

    result = check_policy_violations(tmp_path, task.task_id)

    assert not result.passed
    assert result.metadata["violations"]


def test_forbidden_files_check_degrades_gracefully_without_git(tmp_path: Path) -> None:
    result = check_forbidden_files(tmp_path)

    # No git repository in the temp dir, so the check is not applicable rather than a hard failure.
    assert not result.applicable
    assert required_checks_passed([result])


def test_run_required_checks_writes_evidence_for_registered_checks(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Evidence for policy check")
    write_toolcalls(
        task.path,
        [{"event_type": "tool_call", "tool": "read_file", "policy_decision": "allowed", "exit_code": 0}],
    )

    results = run_required_checks(tmp_path, task.task_id, ["policy_violations"])

    evidence = (tmp_path / TASK_ROOT / task.task_id / "verification.json").read_text(encoding="utf-8")
    assert results[0].name == "policy_violations"
    assert '"policy_violations"' in evidence
