"""Codex CLI adapter skeleton."""

from __future__ import annotations

from polos.adapters.base import AdapterCapabilities, BaseAdapter


class CodexCliAdapter(BaseAdapter):
    capabilities = AdapterCapabilities(
        name="codex-cli",
        grants="Polos grants wrap Codex-style tool access before shell/file tools are exposed.",
        denial="Planner roles never receive Codex tools; effectful commands fail closed without grants.",
        output_capture="Command output is redirected into Polos audit artifacts.",
        approvals="Approval decisions are recorded as grant metadata before action.",
        secret_protection="Secret env vars are inherited only by approved subprocesses and never logged.",
        role_mapping="Codex sessions are treated as Execution Worker or read-only workers, never as oversight authority.",
        supports_write=True,
    )
