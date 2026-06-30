"""Governed tool gateway for Polos runtime calls."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import fnmatch
import subprocess

from polos.audit.logger import AuditLogger, utc_now
from polos.policy.engine import PolicyEngine
from polos.policy.schema import PolicyDecision, ToolRequest
from polos.runtime.approvals import ApprovalStore
from polos.runtime.grants import GrantStore
from polos.runtime.roles import authorize_tool
from polos.runtime.sandbox import Sandbox, SandboxRequest
from polos.runtime.tasks import load_task


@dataclass(slots=True)
class ToolResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    policy_decision: str


class ToolGateway:
    def __init__(
        self,
        root: Path,
        grant_store: GrantStore,
        policy_engine: PolicyEngine | None = None,
        sandbox: Sandbox | None = None,
        approval_store: ApprovalStore | None = None,
    ) -> None:
        self.root = root
        self.grant_store = grant_store
        self.policy_engine = policy_engine or PolicyEngine()
        self.sandbox = sandbox
        self.approval_store = approval_store
        self.tools: dict[str, Callable[[dict[str, Any]], ToolResult]] = {
            "read_file": self._read_file,
            "write_file": self._write_file,
            "patch_file": self._patch_file,
            "list_dir": self._list_dir,
            "search_text": self._search_text,
            "shell_run": self._shell_run,
            "git_status": lambda arguments: self._shell_run({"command": "git status"}),
            "git_diff": lambda arguments: self._shell_run({"command": "git diff"}),
        }

    def call(self, task_id: str, role: str, tool: str, arguments: dict[str, Any], grant_id: str | None = None) -> ToolResult:
        try:
            load_task(self.root, task_id)
        except FileNotFoundError:
            return ToolResult(False, 126, "", "task contract not found", "denied")
        audit_logger = AuditLogger(self.root / ".agent" / "tasks" / task_id / "TOOLCALLS.jsonl")
        started_at = utc_now()
        request = ToolRequest(task_id=task_id, role=role, tool=tool, arguments=arguments, root=self.root, grant_id=grant_id)
        policy = self.policy_engine.decide(request)
        if not authorize_tool(role, tool):
            result = ToolResult(False, 126, "", "role is not authorized for tool", "denied")
            self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, "denied", grant_id, started_at, result)
            return result
        grant = self.grant_store.get(grant_id)
        if tool in {"write_file", "patch_file", "shell_run"} and (grant is None or not grant.allows(tool)):
            result = ToolResult(False, 126, "", "active grant required", "denied")
            self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, "denied", grant_id, started_at, result)
            return result
        if grant is not None and not grant_covers(grant.filesystem_scope, arguments.get("path") or arguments.get("file_path")):
            result = ToolResult(False, 126, "", "grant filesystem scope does not cover request", "denied")
            self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, "denied", grant_id, started_at, result)
            return result
        if grant is not None and tool == "shell_run" and not grant_allows_command(grant.command_allowlist, arguments.get("command", "")):
            result = ToolResult(False, 126, "", "grant command allowlist does not cover request", "denied")
            self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, "denied", grant_id, started_at, result)
            return result
        if policy.decision == PolicyDecision.REQUIRES_SANDBOX:
            if self.sandbox is None or tool != "shell_run":
                result = ToolResult(False, 126, "", "sandbox required but unavailable", policy.decision.value)
                self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, policy.decision.value, grant_id, started_at, result)
                return result
            result = self._shell_run(arguments, use_sandbox=True)
            if grant is not None:
                grant.consume()
            self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, policy.decision.value, grant_id, started_at, result)
            return result
        if policy.decision == PolicyDecision.REQUIRES_APPROVAL:
            if self.approval_store is None or not self.approval_store.has_active_approval(task_id, tool, policy.matched_rule):
                result = ToolResult(False, 126, "", "approval required but unavailable", policy.decision.value)
                self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, policy.decision.value, grant_id, started_at, result)
                return result
            implementation = self.tools.get(tool)
            if implementation is None:
                result = ToolResult(False, 127, "", "unknown tool", "denied")
            else:
                raw_result = implementation(arguments)
                result = ToolResult(
                    raw_result.ok,
                    raw_result.exit_code,
                    raw_result.stdout,
                    raw_result.stderr,
                    policy.decision.value,
                )
                if grant is not None:
                    grant.consume()
            self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, policy.decision.value, grant_id, started_at, result)
            return result
        if policy.decision != PolicyDecision.ALLOWED:
            result = ToolResult(False, 126, "", policy.reason, policy.decision.value)
            self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, policy.decision.value, grant_id, started_at, result)
            return result
        implementation = self.tools.get(tool)
        if implementation is None:
            result = ToolResult(False, 127, "", "unknown tool", "denied")
        else:
            result = implementation(arguments)
            if grant is not None:
                grant.consume()
        self._audit(audit_logger, task_id, role, tool, policy.redacted_arguments, policy.decision.value, grant_id, started_at, result)
        return result

    def _read_file(self, arguments: dict[str, Any]) -> ToolResult:
        path = self.root / arguments["path"]
        return ToolResult(True, 0, path.read_text(encoding="utf-8"), "", "allowed")

    def _write_file(self, arguments: dict[str, Any]) -> ToolResult:
        path = self.root / arguments["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(arguments.get("content", ""), encoding="utf-8")
        return ToolResult(True, 0, "", "", "allowed")

    def _patch_file(self, arguments: dict[str, Any]) -> ToolResult:
        path = self.root / arguments["path"]
        old_text = arguments.get("old_text")
        new_text = arguments.get("new_text")
        if not isinstance(old_text, str) or not isinstance(new_text, str):
            return ToolResult(False, 2, "", "patch_file requires old_text and new_text", "allowed")
        content = path.read_text(encoding="utf-8")
        if content.count(old_text) != 1:
            return ToolResult(False, 2, "", "old_text must occur exactly once", "allowed")
        path.write_text(content.replace(old_text, new_text), encoding="utf-8")
        return ToolResult(True, 0, "", "", "allowed")

    def _list_dir(self, arguments: dict[str, Any]) -> ToolResult:
        path = self.root / arguments.get("path", ".")
        entries = [entry.name + ("/" if entry.is_dir() else "") for entry in sorted(path.iterdir())]
        return ToolResult(True, 0, "\n".join(entries), "", "allowed")

    def _search_text(self, arguments: dict[str, Any]) -> ToolResult:
        query = arguments.get("query", "")
        path = self.root / arguments.get("path", ".")
        matches: list[str] = []
        for file_path in path.rglob("*"):
            if file_path.is_file():
                try:
                    text = file_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                if query in text:
                    matches.append(file_path.relative_to(self.root).as_posix())
        return ToolResult(True, 0, "\n".join(matches), "", "allowed")

    def _shell_run(self, arguments: dict[str, Any], use_sandbox: bool = False) -> ToolResult:
        if use_sandbox:
            assert self.sandbox is not None
            sandbox_result = self.sandbox.run(SandboxRequest(command=arguments["command"], cwd=self.root))
            return ToolResult(
                sandbox_result.ok,
                sandbox_result.exit_code,
                sandbox_result.stdout,
                sandbox_result.stderr,
                "requires_sandbox",
            )
        completed = subprocess.run(arguments["command"], cwd=self.root, capture_output=True, text=True, shell=True, check=False)
        return ToolResult(completed.returncode == 0, completed.returncode, completed.stdout, completed.stderr, "allowed")

    def _audit(
        self,
        audit_logger: AuditLogger,
        task_id: str,
        role: str,
        tool: str,
        arguments_redacted: dict[str, Any],
        policy_decision: str,
        grant_id: str | None,
        started_at: str,
        result: ToolResult,
    ) -> None:
        audit_logger.append({
            "event_type": "tool_call",
            "task_id": task_id,
            "role": role,
            "tool": tool,
            "arguments_redacted": arguments_redacted,
            "policy_decision": policy_decision,
            "grant_id": grant_id,
            "started_at": started_at,
            "ended_at": utc_now(),
            "exit_code": result.exit_code,
            "stdout_ref": None,
            "stderr_ref": None,
            "files_touched": [],
            "risk": "medium" if tool == "shell_run" else "low",
        })


def grant_covers(scope: list[str], path_value: object) -> bool:
    if not path_value:
        return True
    if not isinstance(path_value, str):
        return False
    normalized = path_value.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized or "."
    for pattern in scope:
        rule = pattern.replace("\\", "/").rstrip("/")
        if rule in {".", "**"}:
            return True
        if rule.endswith("/**"):
            base = rule[:-3].rstrip("/")
            if normalized == base or normalized.startswith(f"{base}/"):
                return True
        if fnmatch.fnmatchcase(normalized, rule):
            return True
    return False


def grant_allows_command(allowlist: list[str], command: str) -> bool:
    return any(fnmatch.fnmatchcase(command.strip(), rule) for rule in allowlist)
