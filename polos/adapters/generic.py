"""Generic single-process adapter skeleton."""

from __future__ import annotations

from polos.adapters.base import AdapterCapabilities, BaseAdapter


class GenericAdapter(BaseAdapter):
    capabilities = AdapterCapabilities(
        name="generic",
        grants="Taskmaster grants are enforced by the in-process ToolGateway.",
        denial="Deciders and oversight receive no tool registry; policy denies unknown tools.",
        output_capture="ToolGateway captures stdout/stderr refs into per-task audit events.",
        approvals="Approval is represented as a policy/grant precondition.",
        secret_protection="Environment values are not serialized; secret-looking arguments are redacted.",
        role_mapping="Each Polos role maps to a deterministic local role runner stub.",
        supports_write=True,
    )
