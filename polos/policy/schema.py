"""Policy data types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class PolicyDecision(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    REQUIRES_APPROVAL = "requires_approval"
    REQUIRES_SANDBOX = "requires_sandbox"
    REQUIRES_ELEVATED_GRANT = "requires_elevated_grant"


@dataclass(slots=True)
class ToolRequest:
    task_id: str
    role: str
    tool: str
    arguments: dict[str, Any]
    root: Path
    grant_id: str | None = None


@dataclass(slots=True)
class PolicyResult:
    decision: PolicyDecision
    reason: str
    matched_rule: str | None = None
    redacted_arguments: dict[str, Any] = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        return self.decision == PolicyDecision.ALLOWED
