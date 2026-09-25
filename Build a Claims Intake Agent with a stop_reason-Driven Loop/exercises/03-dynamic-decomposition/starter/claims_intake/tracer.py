import json
from pathlib import Path
from typing import Any, TextIO


class Tracer:
    """Append-only JSONL tracer. One JSON object per call to `write`."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._fh: TextIO = path.open("a", encoding="utf-8")

    def write(self, event: dict[str, Any]) -> None:
        self._fh.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()

    def __enter__(self) -> "Tracer":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class NullTracer(Tracer):
    """In-memory tracer for tests; never touches the filesystem."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.path = Path("/dev/null")
        # Deliberately do not open a file handle; we override write/close.

    def write(self, event: dict[str, Any]) -> None:
        self.events.append(event)

    def close(self) -> None:
        return None
