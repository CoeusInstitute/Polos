"""Bounded Loop Controller runtime."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Callable
import json

from polos.audit.logger import utc_now
from polos.contracts.task import TaskContract
from polos.runtime.tasks import TASK_ROOT
from polos.verification.runner import required_checks_passed, run_required_checks


@dataclass(slots=True)
class LoopBudget:
    max_iterations: int
    max_wall_clock_seconds: int
    max_cost_usd: float
    no_progress_patience: int


@dataclass(slots=True)
class LoopResult:
    status: str
    iterations: int
    reason: str


class LoopController:
    def __init__(self, root: Path, mesh_limits: dict[str, object] | None = None) -> None:
        self.root = root
        self.mesh_limits = mesh_limits or {}

    def run(
        self,
        task_id: str,
        budget: LoopBudget,
        stop_condition: str,
        halt_signal: Callable[[], str | None] | None = None,
    ) -> LoopResult:
        if not stop_condition.strip():
            return LoopResult("blocked", 0, "external verifier-checkable stop condition is required")
        budget = self._cap_budget(budget)
        task = TaskContract.load(self.root / TASK_ROOT / task_id)
        ledger_path = self.root / TASK_ROOT / task_id / "loops" / "ledger.jsonl"
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        started = monotonic()
        no_progress = 0
        previous_signature = ""
        for iteration in range(1, budget.max_iterations + 1):
            halt_reason = halt_signal() if halt_signal else None
            if halt_reason:
                return LoopResult("halted", iteration - 1, f"security halt: {halt_reason}")
            if monotonic() - started > budget.max_wall_clock_seconds:
                return LoopResult("budget_exhausted", iteration - 1, "max wall-clock reached")
            context = rebuild_context(ledger_path)
            checks = run_required_checks(self.root, task.task_id, task.required_checks)
            verified = required_checks_passed(checks)
            signature = json.dumps([result.to_dict() for result in checks], sort_keys=True)
            if signature == previous_signature:
                no_progress += 1
            else:
                no_progress = 0
            previous_signature = signature
            decision = "done" if verified else "retry"
            append_ledger(ledger_path, {
                "iteration": iteration,
                "assignment": f"Verify stop condition: {stop_condition}",
                "grant_id": None,
                "actions_attempted": [],
                "context_entries": len(context),
                "result": "verification_passed" if verified else "verification_failed",
                "verifier_result": [result.to_dict() for result in checks],
                "qc_result": "accepted" if verified else "rework",
                "decision": decision,
            })
            if verified:
                return LoopResult("done", iteration, "verified completion")
            if any(result.name == "policy_violations" and not result.passed and result.applicable for result in checks):
                return LoopResult("policy_violation", iteration, "policy violation detected during verification")
            if no_progress >= budget.no_progress_patience:
                return LoopResult("no_progress", iteration, "no-progress patience exhausted")
        return LoopResult("budget_exhausted", budget.max_iterations, "max iterations reached")

    def _cap_budget(self, budget: LoopBudget) -> LoopBudget:
        loop_limits = self.mesh_limits.get("loop", {}) if isinstance(self.mesh_limits, dict) else {}
        return LoopBudget(
            max_iterations=min(budget.max_iterations, int(loop_limits.get("max_iterations", budget.max_iterations))),
            max_wall_clock_seconds=min(budget.max_wall_clock_seconds, int(loop_limits.get("max_wall_clock_seconds", budget.max_wall_clock_seconds))),
            max_cost_usd=min(budget.max_cost_usd, float(loop_limits.get("max_cost_usd", budget.max_cost_usd))),
            no_progress_patience=min(budget.no_progress_patience, int(loop_limits.get("no_progress_patience", budget.no_progress_patience))),
        )


def append_ledger(path: Path, event: dict[str, object]) -> None:
    entry = dict(event)
    entry["recorded_at"] = utc_now()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def rebuild_context(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    entries: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                entries.append(json.loads(line))
    return entries
