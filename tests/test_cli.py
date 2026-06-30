from pathlib import Path

from polos.cli import main
from polos.runtime.tasks import list_tasks


def write_fake_validator(root: Path, exit_code: int = 0) -> None:
    tools = root / "tools"
    tools.mkdir()
    (tools / "validate_mesh.py").write_text(
        "import sys\nprint('PASS - fake validator')\nsys.exit(%d)\n" % exit_code,
        encoding="utf-8",
    )


def test_cli_plan_creates_task(tmp_path: Path, capsys) -> None:
    exit_code = main(["--root", str(tmp_path), "plan", "test task", "--title", "Test Task"])

    assert exit_code == 0
    assert ".agent/tasks/" in capsys.readouterr().out
    tasks = list_tasks(tmp_path)
    assert len(tasks) == 1
    assert tasks[0].title == "Test Task"


def test_cli_run_dry_run_writes_evidence_and_updates_status(tmp_path: Path, capsys) -> None:
    write_fake_validator(tmp_path)
    assert main(["--root", str(tmp_path), "plan", "test task", "--title", "Test Task"]) == 0
    task = list_tasks(tmp_path)[0]

    exit_code = main(["--root", str(tmp_path), "run", "--dry-run", "--task-id", task.task_id])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "dry-run: no tools executed" in output
    assert "status: complete" in output
    assert "PASS - fake validator" in (task.path / "EVIDENCE.md").read_text(encoding="utf-8")
    assert list_tasks(tmp_path)[0].status == "complete"


def test_cli_audit_json_lists_task_and_toolcalls(tmp_path: Path, capsys) -> None:
    assert main(["--root", str(tmp_path), "plan", "test task", "--title", "Test Task"]) == 0
    exit_code = main(["--root", str(tmp_path), "audit", "--json"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert '"tasks"' in output
    assert '"toolcalls"' in output
    assert '"hash_chains"' in output
