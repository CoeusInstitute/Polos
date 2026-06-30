"""Fail-closed policy evaluation for Polos tool requests."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any
import fnmatch
import shlex

import yaml

from polos.policy.schema import PolicyDecision, PolicyResult, ToolRequest


WRITE_TOOLS = {"write_file", "patch_file", "shell_run"}
SHELL_TOOLS = {"shell_run"}
READ_FILE_TOOLS = {"read_file", "list_dir", "search_text"}
SECRET_KEYS = {"password", "token", "secret", "key", "credential", "authorization"}


class PolicyEngine:
    def __init__(self, policy: dict[str, Any] | None = None) -> None:
        self.policy = policy or load_default_policy()

    def decide(self, request: ToolRequest) -> PolicyResult:
        redacted = redact_arguments(request.arguments)
        if request.role != "execution-worker" and request.tool in WRITE_TOOLS:
            return PolicyResult(
                PolicyDecision.DENIED,
                "only execution-worker may request write or shell tools",
                redacted_arguments=redacted,
            )
        if request.tool in READ_FILE_TOOLS | {"write_file", "patch_file"}:
            path_value = request.arguments.get("path") or request.arguments.get("file_path")
            if not isinstance(path_value, str) or not path_value:
                return PolicyResult(PolicyDecision.DENIED, "file tool missing path", redacted_arguments=redacted)
            return self._decide_filesystem(request, path_value, redacted)
        if request.tool in SHELL_TOOLS:
            command = request.arguments.get("command")
            if not isinstance(command, str) or not command.strip():
                return PolicyResult(PolicyDecision.DENIED, "shell command missing", redacted_arguments=redacted)
            return self._decide_shell(command, redacted)
        if request.tool in {"git_status", "git_diff"}:
            return PolicyResult(PolicyDecision.ALLOWED, "git read-only tool allowed", redacted_arguments=redacted)
        return PolicyResult(PolicyDecision.DENIED, "unknown tool blocked by default", redacted_arguments=redacted)

    def _decide_filesystem(self, request: ToolRequest, path_value: str, redacted: dict[str, Any]) -> PolicyResult:
        relative = normalize_relative_path(request.root, path_value)
        filesystem = self.policy.get("filesystem", {})
        for pattern in filesystem.get("deny", []) or []:
            if match_path(relative, pattern):
                return PolicyResult(PolicyDecision.DENIED, "path denied by policy", pattern, redacted)
        rules = filesystem.get("write" if request.tool in {"write_file", "patch_file"} else "read", []) or []
        for pattern in rules:
            if match_path(relative, pattern):
                return PolicyResult(PolicyDecision.ALLOWED, "filesystem rule allowed", pattern, redacted)
        return PolicyResult(PolicyDecision.DENIED, "no filesystem allow rule matched", redacted_arguments=redacted)

    def _decide_shell(self, command: str, redacted: dict[str, Any]) -> PolicyResult:
        normalized = normalize_command(command)
        shell = self.policy.get("shell", {})
        for pattern in shell.get("deny", []) or []:
            if fnmatch.fnmatchcase(normalized, pattern):
                return PolicyResult(PolicyDecision.DENIED, "shell command denied by policy", pattern, redacted)
        for pattern in shell.get("require_approval", []) or []:
            if fnmatch.fnmatchcase(normalized, pattern):
                return PolicyResult(PolicyDecision.REQUIRES_APPROVAL, "shell command requires approval", pattern, redacted)
        for pattern in shell.get("allow", []) or []:
            if fnmatch.fnmatchcase(normalized, pattern):
                return PolicyResult(PolicyDecision.ALLOWED, "shell command allowed", pattern, redacted)
        default = shell.get("default", "deny")
        if default == "requires_sandbox":
            return PolicyResult(PolicyDecision.REQUIRES_SANDBOX, "shell default requires sandbox", redacted_arguments=redacted)
        return PolicyResult(PolicyDecision.DENIED, "shell default deny", redacted_arguments=redacted)


def load_default_policy() -> dict[str, Any]:
    resource = files("polos.policy").joinpath("defaults.yaml")
    return yaml.safe_load(resource.read_text(encoding="utf-8")) or {}


def normalize_relative_path(root: Path, path_value: str) -> str:
    path = Path(path_value)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return "../outside-root"
    posix = path.as_posix()
    if posix.startswith("./"):
        posix = posix[2:]
    return posix or "."


def match_path(relative: str, pattern: str) -> bool:
    normalized_pattern = pattern.rstrip("/")
    if normalized_pattern in {".", "**"}:
        return not relative.startswith("../")
    if normalized_pattern.endswith("/**"):
        base = normalized_pattern[:-3].rstrip("/")
        return relative == base or relative.startswith(f"{base}/")
    return fnmatch.fnmatchcase(relative, normalized_pattern)


def normalize_command(command: str) -> str:
    try:
        return " ".join(shlex.split(command, posix=False))
    except ValueError:
        return command.strip()


def redact_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in arguments.items():
        lowered = key.lower()
        if any(secret_key in lowered for secret_key in SECRET_KEYS):
            redacted[key] = "<redacted>"
        else:
            redacted[key] = value
    return redacted
