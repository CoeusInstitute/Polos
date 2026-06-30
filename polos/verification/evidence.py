"""Evidence report writers."""

from __future__ import annotations

from pathlib import Path
import json

from polos.verification.checks import CheckResult


def write_evidence(task_path: Path, results: list[CheckResult]) -> None:
    task_path.mkdir(parents=True, exist_ok=True)
    machine_path = task_path / "verification.json"
    machine_path.write_text(json.dumps({"checks": [result.to_dict() for result in results]}, indent=2), encoding="utf-8")
    lines = ["# Evidence", ""]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        if not result.applicable:
            status = "N/A"
        lines.append(f"## {result.name}: {status}")
        if result.reason:
            lines.append(result.reason)
        if result.stdout:
            lines.extend(["", "```text", result.stdout.rstrip(), "```"])
        if result.stderr:
            lines.extend(["", "```text", result.stderr.rstrip(), "```"])
        lines.append("")
    (task_path / "EVIDENCE.md").write_text("\n".join(lines), encoding="utf-8")
