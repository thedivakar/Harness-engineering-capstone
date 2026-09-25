"""Parse and resolve @path import directives in CLAUDE.md files."""

from __future__ import annotations

import re
from pathlib import Path

_IMPORT_RE = re.compile(r"@([\w./-]+\.\w+)")


def find_imports(claude_md: Path) -> list[str]:
    text = claude_md.read_text(encoding="utf-8")
    return _IMPORT_RE.findall(text)


def unresolved_imports(claude_md: Path, *, repo_root: Path) -> list[str]:
    missing: list[str] = []
    base = claude_md.parent
    for raw in find_imports(claude_md):
        candidate = raw[2:] if raw.startswith("./") else raw
        path = (
            (repo_root / candidate[1:]).resolve()
            if candidate.startswith("/")
            else (base / candidate).resolve()
        )
        if not path.exists():
            missing.append(raw)
    return missing
