from polos.runtime.roles import RoleInput, authorize_tool, role_runner


def test_decider_role_runner_produces_manifest_without_tools() -> None:
    runner = role_runner("taskmaster")
    output = runner.run(RoleInput(role="taskmaster", intent_ref="intent-1", payload={}))

    assert output.output_type == "manifest"
    assert output.tool_requests == []
    assert not authorize_tool("taskmaster", "shell_run")


def test_oversight_role_has_no_tool_authorization() -> None:
    assert not authorize_tool("monitor", "read_file")
    assert not authorize_tool("security", "shell_run")
