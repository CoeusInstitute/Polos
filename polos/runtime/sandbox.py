"""Sandbox interfaces for tool execution.

The initial local sandbox is a constrained subprocess wrapper, not an OS isolation boundary.
Adapters that can provide stronger isolation should implement the same interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
import subprocess


@dataclass(slots=True)
class SandboxRequest:
    command: str
    cwd: Path
    timeout_seconds: int = 60
    env: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class SandboxResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    isolation: str


class Sandbox(Protocol):
    def run(self, request: SandboxRequest) -> SandboxResult:
        ...


class LocalSubprocessSandbox:
    isolation = "local-subprocess-timeout-env-scrub"

    def run(self, request: SandboxRequest) -> SandboxResult:
        try:
            completed = subprocess.run(
                request.command,
                cwd=request.cwd,
                capture_output=True,
                text=True,
                shell=True,
                check=False,
                timeout=request.timeout_seconds,
                env=request.env or None,
            )
        except subprocess.TimeoutExpired as exc:
            return SandboxResult(False, 124, exc.stdout or "", exc.stderr or "timeout", self.isolation)
        return SandboxResult(completed.returncode == 0, completed.returncode, completed.stdout, completed.stderr, self.isolation)
