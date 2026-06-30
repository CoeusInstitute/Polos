"""Redacted runtime environment profile detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import platform
import subprocess


@dataclass(slots=True)
class EnvironmentProfile:
    host_kind: str
    os: str
    workspace_root: str
    git_remotes: list[dict[str, str]] = field(default_factory=list)
    package_scripts: dict[str, str] = field(default_factory=dict)
    provider_targets: dict[str, bool] = field(default_factory=dict)
    approval_policy: str = "fail-closed"
    secret_values_recorded: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_kind": self.host_kind,
            "os": self.os,
            "workspace_root": self.workspace_root,
            "git_remotes": list(self.git_remotes),
            "package_scripts": dict(self.package_scripts),
            "provider_targets": dict(self.provider_targets),
            "approval_policy": self.approval_policy,
            "secret_values_recorded": self.secret_values_recorded,
        }


def detect_environment(root: Path, host_kind: str = "local-cli") -> EnvironmentProfile:
    return EnvironmentProfile(
        host_kind=host_kind,
        os=platform.system().lower() or "unknown",
        workspace_root=str(root.resolve()),
        git_remotes=git_remotes(root),
        package_scripts=package_scripts(root),
        provider_targets={
            "github": bool(git_remotes(root)),
            "vercel": (root / ".vercel").exists() or (root / "vercel.json").exists(),
            "supabase": (root / "supabase" / "config.toml").exists(),
        },
    )


def write_environment_profile(root: Path, force: bool = False) -> Path:
    profile_path = root / ".agent" / "environment" / "profile.json"
    if profile_path.exists() and not force:
        return profile_path
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile = detect_environment(root)
    profile_path.write_text(json.dumps(profile.to_dict(), indent=2), encoding="utf-8")
    return profile_path


def git_remotes(root: Path) -> list[dict[str, str]]:
    try:
        completed = subprocess.run(["git", "remote", "-v"], cwd=root, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return []
    if completed.returncode != 0:
        return []
    remotes: list[dict[str, str]] = []
    for line in completed.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            remotes.append({"name": parts[0], "url": parts[1], "mode": parts[2].strip("()")})
    return remotes


def package_scripts(root: Path) -> dict[str, str]:
    package_path = root / "package.json"
    if not package_path.exists():
        return {}
    try:
        data = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    scripts = data.get("scripts")
    return dict(scripts) if isinstance(scripts, dict) else {}
