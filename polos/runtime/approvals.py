"""Approval records for policy-gated actions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import uuid


@dataclass(slots=True)
class Approval:
    approval_id: str
    task_id: str
    tool: str
    matched_rule: str | None
    approved_by: str
    reason: str
    expires_at: str
    status: str = "active"

    def active(self) -> bool:
        return self.status == "active" and parse_time(self.expires_at) > datetime.now(timezone.utc)


class ApprovalStore:
    def __init__(self) -> None:
        self._approvals: dict[str, Approval] = {}

    def approve(
        self,
        task_id: str,
        tool: str,
        matched_rule: str | None,
        approved_by: str,
        reason: str,
        ttl_seconds: int = 300,
    ) -> Approval:
        if approved_by not in {"human", "security"}:
            raise PermissionError("approvals must come from human or security")
        approval = Approval(
            approval_id=f"approval-{uuid.uuid4().hex}",
            task_id=task_id,
            tool=tool,
            matched_rule=matched_rule,
            approved_by=approved_by,
            reason=reason,
            expires_at=(datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )
        self._approvals[approval.approval_id] = approval
        return approval

    def has_active_approval(self, task_id: str, tool: str, matched_rule: str | None) -> bool:
        return any(
            approval.task_id == task_id
            and approval.tool == tool
            and approval.matched_rule == matched_rule
            and approval.active()
            for approval in self._approvals.values()
        )


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
