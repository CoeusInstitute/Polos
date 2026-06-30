"""Hash-chained JSONL audit logger."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json


@dataclass(slots=True)
class AuditLogger:
    path: Path

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        previous_hash = self.last_hash()
        entry = dict(event)
        entry["timestamp"] = utc_now()
        entry["prev_hash"] = previous_hash
        entry["hash"] = event_hash(entry)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry

    def last_hash(self) -> str | None:
        if not self.path.exists():
            return None
        last_line = ""
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    last_line = line
        if not last_line:
            return None
        return json.loads(last_line).get("hash")


def event_hash(event: dict[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
