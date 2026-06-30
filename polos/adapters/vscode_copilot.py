"""VS Code Copilot adapter skeleton."""

from __future__ import annotations

from polos.adapters.base import AdapterCapabilities, BaseAdapter


class VSCodeCopilotAdapter(BaseAdapter):
    capabilities = AdapterCapabilities(
        name="vscode-copilot",
        grants="Human-visible tool grants remain mediated by the runtime gateway when Polos is the executor.",
        denial="Prompt roles are not trusted as enforcement; runtime role and policy checks deny tools.",
        output_capture="CLI and file-operation output is summarized into task evidence and audit logs.",
        approvals="VS Code approval prompts can satisfy policy approval gates when exposed to the runtime.",
        secret_protection="Secrets stay in local env/provider stores and are not requested in chat.",
        role_mapping="Role cards map to system prompts or local runner stubs depending on host capability.",
        supports_write=True,
    )
