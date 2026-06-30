"""Provider interface shared by all model backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(slots=True)
class ModelRequest:
    role: str
    model: str
    messages: list[dict[str, str]]
    dry_run: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ModelResponse:
    role: str
    model: str
    content: str
    provider: str
    dry_run: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


class ModelProvider(Protocol):
    provider_name: str

    def complete(self, request: ModelRequest) -> ModelResponse:
        ...
