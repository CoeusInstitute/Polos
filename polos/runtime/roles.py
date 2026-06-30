"""Runtime role registry and capability ceilings."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RoleId(str, Enum):
    ALPHA = "alpha"
    ROUTER = "router"
    TASKMASTER = "taskmaster"
    LOOP_CONTROLLER = "loop-controller"
    RETRIEVAL_WORKER = "retrieval-worker"
    EXECUTION_WORKER = "execution-worker"
    ARCHIVIST = "archivist"
    VERIFIER = "verifier"
    MONITOR = "monitor"
    QC = "qc"
    SECURITY = "security"
    LEARNING = "learning"
    EVALUATOR = "evaluator"
    NURSE = "nurse"


DECIDERS = {RoleId.ALPHA.value, RoleId.ROUTER.value, RoleId.TASKMASTER.value, RoleId.LOOP_CONTROLLER.value}
OVERSIGHT = {RoleId.MONITOR.value, RoleId.QC.value, RoleId.SECURITY.value, RoleId.EVALUATOR.value}
WRITE_TOOLS = {"write_file", "patch_file", "shell_run"}
READ_TOOLS = {"read_file", "list_dir", "search_text", "git_status", "git_diff"}


@dataclass(frozen=True, slots=True)
class RoleCapabilities:
    role: str
    effectful_tools: frozenset[str]
    readonly_tools: frozenset[str]
    can_issue_grants: bool = False
    can_revoke_grants: bool = False


@dataclass(slots=True)
class RoleInput:
    role: str
    intent_ref: str
    payload: dict[str, object]
    context: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class RoleOutput:
    role: str
    output_type: str
    payload: dict[str, object]
    tool_requests: list[dict[str, object]] = field(default_factory=list)


ROLE_CAPABILITIES = {
    RoleId.ALPHA.value: RoleCapabilities(RoleId.ALPHA.value, frozenset(), frozenset()),
    RoleId.ROUTER.value: RoleCapabilities(RoleId.ROUTER.value, frozenset(), frozenset()),
    RoleId.TASKMASTER.value: RoleCapabilities(RoleId.TASKMASTER.value, frozenset(), frozenset(), can_issue_grants=True),
    RoleId.LOOP_CONTROLLER.value: RoleCapabilities(RoleId.LOOP_CONTROLLER.value, frozenset(), frozenset()),
    RoleId.RETRIEVAL_WORKER.value: RoleCapabilities(RoleId.RETRIEVAL_WORKER.value, frozenset(), frozenset(READ_TOOLS)),
    RoleId.EXECUTION_WORKER.value: RoleCapabilities(RoleId.EXECUTION_WORKER.value, frozenset(WRITE_TOOLS), frozenset(READ_TOOLS)),
    RoleId.ARCHIVIST.value: RoleCapabilities(RoleId.ARCHIVIST.value, frozenset(), frozenset(READ_TOOLS)),
    RoleId.VERIFIER.value: RoleCapabilities(RoleId.VERIFIER.value, frozenset(), frozenset(READ_TOOLS)),
    RoleId.MONITOR.value: RoleCapabilities(RoleId.MONITOR.value, frozenset(), frozenset()),
    RoleId.QC.value: RoleCapabilities(RoleId.QC.value, frozenset(), frozenset()),
    RoleId.SECURITY.value: RoleCapabilities(RoleId.SECURITY.value, frozenset(), frozenset(), can_revoke_grants=True),
    RoleId.LEARNING.value: RoleCapabilities(RoleId.LEARNING.value, frozenset(), frozenset()),
    RoleId.EVALUATOR.value: RoleCapabilities(RoleId.EVALUATOR.value, frozenset(), frozenset()),
    RoleId.NURSE.value: RoleCapabilities(RoleId.NURSE.value, frozenset(), frozenset()),
}


def authorize_tool(role: str, tool: str) -> bool:
    capabilities = ROLE_CAPABILITIES.get(role)
    if capabilities is None:
        return False
    if role in DECIDERS or role in OVERSIGHT:
        return False
    return tool in capabilities.effectful_tools or tool in capabilities.readonly_tools


class DeterministicRoleRunner:
    def __init__(self, role: str) -> None:
        if role not in ROLE_CAPABILITIES:
            raise KeyError(f"unknown role: {role}")
        self.role = role

    def run(self, role_input: RoleInput) -> RoleOutput:
        if role_input.role != self.role:
            raise ValueError("role input does not match runner role")
        if self.role in DECIDERS:
            return RoleOutput(self.role, "manifest", {"intent_ref": role_input.intent_ref, "status": "planned"})
        if self.role == RoleId.EXECUTION_WORKER.value:
            return RoleOutput(self.role, "work_result", {"intent_ref": role_input.intent_ref, "status": "not_executed"})
        if self.role in OVERSIGHT:
            return RoleOutput(self.role, "verdict", {"decision": "PASS", "rationale": ["deterministic stub only"]})
        return RoleOutput(self.role, "result", {"intent_ref": role_input.intent_ref, "status": "stubbed"})


def role_runner(role: str) -> DeterministicRoleRunner:
    return DeterministicRoleRunner(role)
