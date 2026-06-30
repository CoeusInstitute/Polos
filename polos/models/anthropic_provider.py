"""Anthropic-compatible provider placeholder."""

from __future__ import annotations

import os

from polos.models.local_provider import LocalProvider
from polos.models.provider import ModelRequest, ModelResponse


class AnthropicProvider:
    provider_name = "anthropic"

    def complete(self, request: ModelRequest) -> ModelResponse:
        if request.dry_run or not os.environ.get("ANTHROPIC_API_KEY"):
            return LocalProvider().complete(request)
        raise NotImplementedError("Anthropic live calls are not wired in Polos v0.3 skeleton")
