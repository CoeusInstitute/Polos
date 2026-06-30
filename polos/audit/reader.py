"""Audit log reading and hash-chain verification."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from polos.audit.logger import event_hash


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                events.append(json.loads(line))
    return events


def verify_hash_chain(path: Path) -> bool:
    previous_hash: str | None = None
    for event in read_jsonl(path):
        if event.get("prev_hash") != previous_hash:
            return False
        if event.get("hash") != event_hash(event):
            return False
        previous_hash = event.get("hash")
    return True
