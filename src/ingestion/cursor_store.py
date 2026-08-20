from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class CursorStore:
    """Small local cursor store used by tests and dry runs.

    In production, the same contract can be backed by Azure Table Storage,
    Cosmos DB, or an ADF metadata table.
    """

    path: Path

    def load(self, source_name: str) -> str:
        if not self.path.exists():
            return "1970-01-01T00:00:00Z"
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return payload.get(source_name, "1970-01-01T00:00:00Z")

    def save(self, source_name: str, cursor_value: str | None = None) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {}
        if self.path.exists():
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        payload[source_name] = cursor_value or datetime.now(timezone.utc).isoformat()
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
