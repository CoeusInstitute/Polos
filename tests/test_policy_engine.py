from pathlib import Path

from polos.policy.engine import PolicyEngine
from polos.policy.schema import PolicyDecision, ToolRequest


def request(tool: str, arguments: dict[str, object], role: str = "execution-worker") -> ToolRequest:
    return ToolRequest(task_id="task-1", role=role, tool=tool, arguments=arguments, root=Path.cwd())


def test_policy_allows_repo_read_by_default() -> None:
    result = PolicyEngine().decide(request("read_file", {"path": "README.md"}, role="retrieval-worker"))
    assert result.decision == PolicyDecision.ALLOWED


def test_policy_denies_secret_file_reads() -> None:
    result = PolicyEngine().decide(request("read_file", {"path": ".env.local"}, role="retrieval-worker"))
    assert result.decision == PolicyDecision.DENIED


def test_policy_denies_write_from_non_execution_role() -> None:
    result = PolicyEngine().decide(request("write_file", {"path": ".agent/tasks/x/PLAN.md"}, role="taskmaster"))
    assert result.decision == PolicyDecision.DENIED


def test_policy_requires_approval_for_package_install() -> None:
    result = PolicyEngine().decide(request("shell_run", {"command": "pip install something"}))
    assert result.decision == PolicyDecision.REQUIRES_APPROVAL
