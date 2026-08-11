from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .errors import XAAError


class RunLock:
    def __init__(self, path: Path, stale_after_seconds: int = 6 * 60 * 60) -> None:
        self.path = path
        self.stale_after_seconds = stale_after_seconds
        self._acquired = False

    def __enter__(self) -> "RunLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            age = time.time() - self.path.stat().st_mtime
            if age > self.stale_after_seconds:
                self.path.unlink(missing_ok=True)
        try:
            descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise XAAError(
                "XAA is already running. Wait for the previous process to finish."
            ) from exc
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(str(os.getpid()))
        self._acquired = True
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self._acquired:
            self.path.unlink(missing_ok=True)


class HistoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise XAAError(f"Could not read the history file: {exc}") from exc
        if not isinstance(data, list):
            raise XAAError("The history file has an invalid format.")
        return [entry for entry in data if isinstance(entry, dict)]

    def append(self, entry: dict[str, Any]) -> None:
        entries = self.load()
        entries.append(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(entries[-500:], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.path)

    def recent_published(self, limit: int) -> list[dict[str, Any]]:
        published = [entry for entry in self.load() if entry.get("status") == "published"]
        return published[-limit:]

    def hours_since_last_publish(self, now: datetime) -> float | None:
        entries = self.recent_published(1)
        if not entries:
            return None
        value = entries[-1].get("created_at")
        if not isinstance(value, str):
            return None
        try:
            previous = datetime.fromisoformat(value)
        except ValueError:
            return None
        if previous.tzinfo is None:
            previous = previous.replace(tzinfo=now.tzinfo)
        return max(0.0, (now - previous).total_seconds() / 3600)
