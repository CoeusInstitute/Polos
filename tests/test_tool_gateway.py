from pathlib import Path

from polos.runtime.approvals import ApprovalStore
from polos.runtime.grants import GrantStore
from polos.runtime.sandbox import LocalSubprocessSandbox
from polos.runtime.tasks import create_task
from polos.policy.engine import PolicyEngine
from polos.tools.gateway import ToolGateway


def test_gateway_denies_write_without_grant(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Write a task artifact")
    gateway = ToolGateway(tmp_path, GrantStore())

    result = gateway.call(
        task_id=task.task_id,
        role="execution-worker",
        tool="write_file",
        arguments={"path": ".agent/tasks/example/PLAN.md", "content": "x"},
    )

    assert not result.ok
    assert result.stderr == "active grant required"


def test_gateway_denies_when_task_contract_is_missing(tmp_path: Path) -> None:
    gateway = ToolGateway(tmp_path, GrantStore())

    result = gateway.call(
        task_id="missing",
        role="execution-worker",
        tool="read_file",
        arguments={"path": "README.md"},
    )

    assert not result.ok
    assert result.stderr == "task contract not found"


def test_gateway_allows_scoped_write_with_grant(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Write a task artifact")
    store = GrantStore()
    grant = store.issue(
        task_id=task.task_id,
        role="execution-worker",
        allowed_tools={"write_file"},
        filesystem_scope=[".agent/**"],
        command_allowlist=[],
        ttl_seconds=60,
        max_tool_calls=2,
        max_wall_clock_seconds=60,
        reason="write generated runtime artifact",
        issued_by="taskmaster",
    )
    gateway = ToolGateway(tmp_path, store)

    result = gateway.call(
        task_id=task.task_id,
        role="execution-worker",
        tool="write_file",
        arguments={"path": ".agent/tasks/example/PLAN.md", "content": "x"},
        grant_id=grant.grant_id,
    )

    assert result.ok
    assert (tmp_path / ".agent" / "tasks" / "example" / "PLAN.md").read_text(encoding="utf-8") == "x"


def test_gateway_uses_sandbox_when_policy_requires_it(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Run sandboxed command")
    store = GrantStore()
    grant = store.issue(
        task_id=task.task_id,
        role="execution-worker",
        allowed_tools={"shell_run"},
        filesystem_scope=["."],
        command_allowlist=["echo *"],
        ttl_seconds=60,
        max_tool_calls=2,
        max_wall_clock_seconds=60,
        reason="sandbox smoke",
        issued_by="taskmaster",
    )
    policy = PolicyEngine({"shell": {"default": "requires_sandbox"}, "filesystem": {"read": ["."], "write": [".agent/**"], "deny": []}})
    gateway = ToolGateway(tmp_path, store, policy_engine=policy, sandbox=LocalSubprocessSandbox())

    result = gateway.call(
        task_id=task.task_id,
        role="execution-worker",
        tool="shell_run",
        arguments={"command": "echo sandbox"},
        grant_id=grant.grant_id,
    )

    assert result.ok
    assert "sandbox" in result.stdout
    assert result.policy_decision == "requires_sandbox"


def test_gateway_blocks_approval_required_command_without_approval(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Run approval command")
    store = GrantStore()
    grant = store.issue(
        task_id=task.task_id,
        role="execution-worker",
        allowed_tools={"shell_run"},
        filesystem_scope=["."],
        command_allowlist=["echo *"],
        ttl_seconds=60,
        max_tool_calls=2,
        max_wall_clock_seconds=60,
        reason="approval smoke",
        issued_by="taskmaster",
    )
    policy = PolicyEngine({"shell": {"default": "deny", "require_approval": ["echo *"]}, "filesystem": {"read": ["."], "write": [".agent/**"], "deny": []}})
    gateway = ToolGateway(tmp_path, store, policy_engine=policy)

    result = gateway.call(task.task_id, "execution-worker", "shell_run", {"command": "echo approved"}, grant.grant_id)

    assert not result.ok
    assert result.stderr == "approval required but unavailable"


def test_gateway_runs_approval_required_command_with_active_approval(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Run approval command")
    store = GrantStore()
    grant = store.issue(
        task_id=task.task_id,
        role="execution-worker",
        allowed_tools={"shell_run"},
        filesystem_scope=["."],
        command_allowlist=["echo *"],
        ttl_seconds=60,
        max_tool_calls=2,
        max_wall_clock_seconds=60,
        reason="approval smoke",
        issued_by="taskmaster",
    )
    approvals = ApprovalStore()
    approvals.approve(task.task_id, "shell_run", "echo *", "human", "test approval")
    policy = PolicyEngine({"shell": {"default": "deny", "require_approval": ["echo *"]}, "filesystem": {"read": ["."], "write": [".agent/**"], "deny": []}})
    gateway = ToolGateway(tmp_path, store, policy_engine=policy, approval_store=approvals)

    result = gateway.call(task.task_id, "execution-worker", "shell_run", {"command": "echo approved"}, grant.grant_id)

    assert result.ok
    assert "approved" in result.stdout
    assert result.policy_decision == "requires_approval"
