"""Claude Code adapter skeleton."""

from __future__ import annotations

from polos.adapters.base import AdapterCapabilities, BaseAdapter


class ClaudeCodeAdapter(BaseAdapter):
    capabilities = AdapterCapabilities(
        name="claude-code",
        grants="Polos grants are the authority layer; Claude Code permissions are treated as host capabilities.",
        denial="Deciders and oversight are represented without tool access regardless of host defaults.",
        output_capture="Host transcript/output is referenced from Polos audit events when available.",
        approvals="Host approvals can satisfy Polos approval requirements only when tied to a grant id.",
        secret_protection="Secrets remain in host-managed stores and are never copied into task artifacts.",
        role_mapping="Claude Code can implement worker calls, but Polos Monitor/QC/Security remain separate roles.",
        supports_write=True,
    )
