import pytest

from polos.runtime.grants import GrantStore


def test_taskmaster_can_issue_execution_worker_grant() -> None:
    store = GrantStore()
    grant = store.issue(
        task_id="task-1",
        role="execution-worker",
        allowed_tools={"write_file"},
        filesystem_scope=[".agent/**"],
        command_allowlist=[],
        ttl_seconds=60,
        max_tool_calls=1,
        max_wall_clock_seconds=60,
        reason="write task artifact",
        issued_by="taskmaster",
    )

    assert grant.allows("write_file")
    grant.consume()
    assert not grant.allows("write_file")


def test_non_taskmaster_cannot_issue_grant() -> None:
    store = GrantStore()
    with pytest.raises(PermissionError):
        store.issue(
            task_id="task-1",
            role="execution-worker",
            allowed_tools={"write_file"},
            filesystem_scope=[".agent/**"],
            command_allowlist=[],
            ttl_seconds=60,
            max_tool_calls=1,
            max_wall_clock_seconds=60,
            reason="not allowed",
            issued_by="router",
        )


def test_security_can_revoke_grant() -> None:
    store = GrantStore()
    grant = store.issue(
        task_id="task-1",
        role="execution-worker",
        allowed_tools={"write_file"},
        filesystem_scope=[".agent/**"],
        command_allowlist=[],
        ttl_seconds=60,
        max_tool_calls=2,
        max_wall_clock_seconds=60,
        reason="write task artifact",
        issued_by="taskmaster",
    )

    store.revoke(grant.grant_id, revoked_by="security", reason="halt")
    assert not grant.allows("write_file")
