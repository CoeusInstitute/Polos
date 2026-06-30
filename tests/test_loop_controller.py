from pathlib import Path

from polos.runtime.loop_controller import LoopBudget, LoopController
from polos.runtime.tasks import create_task


def test_loop_blocks_without_external_stop_condition(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Loop until verified")
    controller = LoopController(tmp_path)

    result = controller.run(
        task.task_id,
        LoopBudget(max_iterations=1, max_wall_clock_seconds=1, max_cost_usd=0, no_progress_patience=1),
        stop_condition="",
    )

    assert result.status == "blocked"
    assert result.iterations == 0


def test_loop_stops_on_security_halt_signal(tmp_path: Path) -> None:
    task = create_task(tmp_path, "Loop until halted")
    controller = LoopController(tmp_path)

    result = controller.run(
        task.task_id,
        LoopBudget(max_iterations=5, max_wall_clock_seconds=10, max_cost_usd=0, no_progress_patience=3),
        stop_condition="verifier confirms acceptance criteria",
        halt_signal=lambda: "integrity signal",
    )

    assert result.status == "halted"
    assert "integrity signal" in result.reason
