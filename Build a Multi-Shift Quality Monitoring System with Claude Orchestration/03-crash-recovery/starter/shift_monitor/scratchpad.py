"""Append-only typed scratchpad backed by JSON lines."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class ScratchpadEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    hypothesis_id: str
    evidence: str
    conclusion: str
    ts: datetime


class Scratchpad:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, entry: ScratchpadEntry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = entry.model_dump_json() + "\n"
        with open(self.path, "ab") as f:
            f.write(line.encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())

    def read(self) -> list[ScratchpadEntry]:
        if not self.path.exists():
            return []
        entries: list[ScratchpadEntry] = []
        with open(self.path, "rb") as f:
            for raw in f:
                line = raw.decode("utf-8").strip()
                if line:
                    entries.append(ScratchpadEntry.model_validate_json(line))
        return entries
