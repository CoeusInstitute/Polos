"""Base host adapter contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AdapterCapabilities:
    name: str
    grants: str
    denial: str
    output_capture: str
    approvals: str
    secret_protection: str
    role_mapping: str
    supports_write: bool = False
    supports_network: bool = False


class BaseAdapter:
    capabilities = AdapterCapabilities(
        name="base",
        grants="No tools are granted by the base adapter.",
        denial="All effectful tools are denied by default.",
        output_capture="No output capture configured.",
        approvals="No approval channel configured.",
        secret_protection="Secrets are never read or logged by the base adapter.",
        role_mapping="Polos roles are represented as runtime role ids only.",
    )

    def describe(self) -> AdapterCapabilities:
        return self.capabilities
