"""Resolve role-to-model bindings from models.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os

import yaml

from polos.models.anthropic_provider import AnthropicProvider
from polos.models.local_provider import LocalProvider
from polos.models.openai_provider import OpenAIProvider
from polos.models.provider import ModelProvider, ModelRequest, ModelResponse


@dataclass(slots=True)
class ModelBinding:
    role: str
    role_class: str
    model: str


class ModelRouter:
    def __init__(self, root: Path, dry_run: bool = True) -> None:
        self.root = root
        self.dry_run = dry_run
        self.config = load_models(root)
        self.profile = os.environ.get("MESH_PROFILE", self.config.get("profile"))
        self.providers: dict[str, ModelProvider] = {
            "local": LocalProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "openrouter": LocalProvider(),
        }

    def binding_for(self, role: str) -> ModelBinding:
        roles = self.config.get("roles", {})
        profiles = self.config.get("profiles", {})
        if role not in roles:
            raise KeyError(f"no model binding for role: {role}")
        role_config = roles[role]
        role_class = role_config.get("class")
        model = role_config.get("model") or profiles[self.profile][role_class]
        return ModelBinding(role=role, role_class=role_class, model=model)

    def complete(self, role: str, messages: list[dict[str, str]]) -> ModelResponse:
        binding = self.binding_for(role)
        provider_key = provider_from_model(binding.model)
        provider = self.providers.get(provider_key, self.providers["local"])
        return provider.complete(ModelRequest(role=role, model=binding.model, messages=messages, dry_run=self.dry_run))

    def oversight_lineage_ok(self) -> bool:
        profiles = self.config.get("profiles", {})
        profile = profiles.get(self.profile, {})
        oversight = profile.get("oversight")
        return bool(oversight and oversight not in {profile.get("worker"), profile.get("decider")})


def load_models(root: Path) -> dict[str, Any]:
    with (root / "models.yaml").open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def provider_from_model(model: str) -> str:
    provider = model.split("/", 1)[0]
    if provider == "openrouter":
        return "openrouter"
    if provider in {"openai", "anthropic"}:
        return provider
    return "local"
