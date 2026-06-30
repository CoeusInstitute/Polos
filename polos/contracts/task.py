"""Durable task contract for Polos runtime work."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


AUTONOMY_LEVELS = {
    "L0": "answer only",
    "L1": "read-only analysis",
    "L2": "propose plan",
    "L3": "propose patch",
    "L4": "execute in sandbox with approval",
    "L5": "execute and verify autonomously within scoped grants",
    "L6": "long-running loop with checkpoints",
}

TASK_STATUSES = {"planned", "ready", "running", "blocked", "complete", "cancelled"}


@dataclass(slots=True)
class TaskContract:
    task_id: str
    title: str
    original_user_request: str
    normalized_goal: str
    intent_ref: str
    acceptance_criteria: list[str]
    risk_level: str
    autonomy_level: str
    requested_mode: str
    permissions: dict[str, Any]
    budgets: dict[str, Any]
    required_checks: list[str]
    created_at: str
    status: str
    artifacts: dict[str, str]
    path: Path = field(repr=False)

    def validate(self) -> None:
        if self.autonomy_level not in AUTONOMY_LEVELS:
            raise ValueError(f"unknown autonomy level: {self.autonomy_level}")
        if self.status not in TASK_STATUSES:
            raise ValueError(f"unknown task status: {self.status}")
        if not self.task_id.strip():
            raise ValueError("task_id is required")
        if not self.intent_ref.strip():
            raise ValueError("intent_ref is required")
        if not self.acceptance_criteria:
            raise ValueError("at least one acceptance criterion is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "original_user_request": self.original_user_request,
            "normalized_goal": self.normalized_goal,
            "intent_ref": self.intent_ref,
            "acceptance_criteria": list(self.acceptance_criteria),
            "risk_level": self.risk_level,
            "autonomy_level": self.autonomy_level,
            "autonomy_description": AUTONOMY_LEVELS[self.autonomy_level],
            "requested_mode": self.requested_mode,
            "permissions": dict(self.permissions),
            "budgets": dict(self.budgets),
            "required_checks": list(self.required_checks),
            "created_at": self.created_at,
            "status": self.status,
            "artifacts": dict(self.artifacts),
        }

    def write(self) -> None:
        self.validate()
        self.path.mkdir(parents=True, exist_ok=True)
        task_path = self.path / "TASK.yaml"
        with task_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self.to_dict(), handle, sort_keys=False)

    @classmethod
    def load(cls, path: Path) -> "TaskContract":
        with (path / "TASK.yaml").open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        contract = cls(
            task_id=data["task_id"],
            title=data["title"],
            original_user_request=data["original_user_request"],
            normalized_goal=data["normalized_goal"],
            intent_ref=data["intent_ref"],
            acceptance_criteria=list(data["acceptance_criteria"]),
            risk_level=data["risk_level"],
            autonomy_level=data["autonomy_level"],
            requested_mode=data["requested_mode"],
            permissions=dict(data["permissions"]),
            budgets=dict(data["budgets"]),
            required_checks=list(data["required_checks"]),
            created_at=data["created_at"],
            status=data["status"],
            artifacts=dict(data["artifacts"]),
            path=path,
        )
        contract.validate()
        return contract


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
