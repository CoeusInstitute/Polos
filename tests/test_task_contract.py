from pathlib import Path
import json

from polos.contracts.task import TaskContract
from polos.runtime.tasks import create_task, init_runtime


def test_create_task_writes_contract_and_artifacts(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Implement a dry-run task", title="Dry run task")

    assert (task.path / "TASK.yaml").exists()
    assert (task.path / "PLAN.md").exists()
    assert (task.path / "LOG.md").exists()
    assert (task.path / "TOOLCALLS.jsonl").exists()
    assert (task.path / "EVIDENCE.md").exists()
    assert (task.path / "REVIEW.md").exists()

    loaded = TaskContract.load(task.path)
    assert loaded.task_id == task.task_id
    assert loaded.status == "planned"
    assert loaded.autonomy_level == "L2"
    assert loaded.required_checks == ["mesh_validate"]


def test_init_runtime_writes_redacted_environment_profile(tmp_path: Path) -> None:
    init_runtime(tmp_path)
    profile_path = tmp_path / ".agent" / "environment" / "profile.json"

    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    assert profile["host_kind"] == "local-cli"
    assert profile["secret_values_recorded"] is False
    assert "workspace_root" in profile
