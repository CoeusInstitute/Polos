"""Verification check models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CheckResult:
    name: str
    passed: bool
    applicable: bool = True
    reason: str = ""
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "passed": self.passed,
            "applicable": self.applicable,
            "reason": self.reason,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "metadata": dict(self.metadata),
        }


def not_applicable(name: str, reason: str) -> CheckResult:
    return CheckResult(name=name, passed=True, applicable=False, reason=reason)
