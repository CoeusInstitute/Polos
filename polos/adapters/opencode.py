"""OpenCode adapter skeleton."""

from __future__ import annotations

from polos.adapters.base import AdapterCapabilities, BaseAdapter


class OpenCodeAdapter(BaseAdapter):
    capabilities = AdapterCapabilities(
        name="opencode",
        grants="OpenCode tool access is scoped through Polos grants before execution.",
        denial="Unknown or ungranted tools are denied by the Polos gateway.",
        output_capture="Tool results are captured as structured audit events.",
        approvals="Approval state is external input to policy and cannot be inferred by the worker.",
        secret_protection="Secret material is redacted from arguments and omitted from logs.",
        role_mapping="OpenCode agents map to Polos workers only; decider and oversight roles remain tool-less.",
        supports_write=True,
    )
