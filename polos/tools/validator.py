"""Wrapper around the canonical Polos structural validator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


@dataclass(slots=True)
class ValidationResult:
    exit_code: int
    stdout: str
    stderr: str
    validator_path: Path

    @property
    def passed(self) -> bool:
        return self.exit_code == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "validator_path": str(self.validator_path),
        }


def validate_mesh(root: Path) -> ValidationResult:
    validator_path = root / "tools" / "validate_mesh.py"
    if not validator_path.exists():
        return ValidationResult(
            exit_code=1,
            stdout="",
            stderr=f"validator not found: {validator_path}\n",
            validator_path=validator_path,
        )
    completed = subprocess.run(
        [sys.executable, str(validator_path)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return ValidationResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        validator_path=validator_path,
    )
