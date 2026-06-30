"""JIT execution grants for the Polos runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import uuid

from polos.audit.logger import AuditLogger, utc_now
from polos.runtime.roles import ROLE_CAPABILITIES


@dataclass(slots=True)
class Grant:
    grant_id: str
    task_id: str
    role: str
    allowed_tools: set[str]
    filesystem_scope: list[str]
    command_allowlist: list[str]
    expires_at: str
    max_tool_calls: int
    max_wall_clock_seconds: int
    reason: str
    issued_by: str
    status: str = "active"
    tool_calls_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def active(self) -> bool:
        return self.status == "active" and not self.expired() and self.tool_calls_used < self.max_tool_calls

    def expired(self) -> bool:
        return parse_time(self.expires_at) <= datetime.now(timezone.utc)

    def allows(self, tool: str) -> bool:
        return self.active() and tool in self.allowed_tools

    def consume(self) -> None:
        self.tool_calls_used += 1
        if self.tool_calls_used >= self.max_tool_calls:
            self.status = "exhausted"


class GrantStore:
    def __init__(self, audit_logger: AuditLogger | None = None) -> None:
        self._grants: dict[str, Grant] = {}
        self.audit_logger = audit_logger

    def issue(
        self,
        task_id: str,
        role: str,
        allowed_tools: set[str],
        filesystem_scope: list[str],
        command_allowlist: list[str],
        ttl_seconds: int,
        max_tool_calls: int,
        max_wall_clock_seconds: int,
        reason: str,
        issued_by: str,
    ) -> Grant:
        issuer = ROLE_CAPABILITIES.get(issued_by)
        if issuer is None or not issuer.can_issue_grants:
            raise PermissionError("only taskmaster may issue grants")
        if role != "execution-worker":
            raise PermissionError("JIT effectful grants are scoped to execution-worker")
        grant = Grant(
            grant_id=f"grant-{uuid.uuid4().hex}",
            task_id=task_id,
            role=role,
            allowed_tools=set(allowed_tools),
            filesystem_scope=list(filesystem_scope),
            command_allowlist=list(command_allowlist),
            expires_at=(datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            max_tool_calls=max_tool_calls,
            max_wall_clock_seconds=max_wall_clock_seconds,
            reason=reason,
            issued_by=issued_by,
        )
        self._grants[grant.grant_id] = grant
        self._audit("grant_issued", grant)
        return grant

    def get(self, grant_id: str | None) -> Grant | None:
        if grant_id is None:
            return None
        return self._grants.get(grant_id)

    def revoke(self, grant_id: str, revoked_by: str, reason: str) -> None:
        actor = ROLE_CAPABILITIES.get(revoked_by)
        if actor is None or not actor.can_revoke_grants:
            raise PermissionError("only security may revoke grants")
        grant = self._grants[grant_id]
        grant.status = "revoked"
        grant.metadata["revoked_by"] = revoked_by
        grant.metadata["revoke_reason"] = reason
        self._audit("grant_revoked", grant)

    def _audit(self, event_type: str, grant: Grant) -> None:
        if self.audit_logger is None:
            return
        self.audit_logger.append({
            "event_type": event_type,
            "task_id": grant.task_id,
            "role": grant.role,
            "grant_id": grant.grant_id,
            "status": grant.status,
            "expires_at": grant.expires_at,
        })


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def task_audit_logger(root: Path, task_id: str) -> AuditLogger:
    return AuditLogger(root / ".agent" / "tasks" / task_id / "TOOLCALLS.jsonl")
