"""Local deterministic provider used for dry-run operation."""

from __future__ import annotations

from polos.models.provider import ModelRequest, ModelResponse


class LocalProvider:
    provider_name = "local"

    def complete(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            role=request.role,
            model=request.model,
            content=f"dry-run response for {request.role}",
            provider=self.provider_name,
            dry_run=True,
            metadata={"tool_calls": []},
        )
