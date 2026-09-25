"""Structural checks on root CLAUDE.md beyond import resolution."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_USER_LEVEL_RE = re.compile(r"~/\.claude/|user[- ]level|user[- ]scope", re.IGNORECASE)
_PROJECT_LEVEL_RE = re.compile(r"project[- ]level|project[- ]scope|\.claude/CLAUDE\.md")
_NOT_VERSIONED_RE = re.compile(
    r"not\s+(shared|committed|tracked|checked[- ]in|version[- ]controlled)"
    r"|outside\s+(version|git)\s+control"
    r"|stays\s+local|never\s+(committed|shared)",
    re.IGNORECASE,
)
_USER_EXAMPLE_RE = re.compile(
    r"(commit\s+message|editor\s+preference|personal|alias|prompt|theme|nickname)",
    re.IGNORECASE,
)
_MEMORY_RE = re.compile(r"/memory\b")


@dataclass(frozen=True)
class ScopeDocCheck:
    mentions_user_level: bool
    mentions_project_level: bool
    states_not_version_controlled: bool
    user_scope_example: bool


def distinguishes_project_vs_user_scope(claude_md: Path) -> ScopeDocCheck:
    text = claude_md.read_text(encoding="utf-8")
    return ScopeDocCheck(
        mentions_user_level=bool(_USER_LEVEL_RE.search(text)),
        mentions_project_level=bool(_PROJECT_LEVEL_RE.search(text)),
        states_not_version_controlled=bool(_NOT_VERSIONED_RE.search(text)),
        user_scope_example=bool(_USER_EXAMPLE_RE.search(text)),
    )


def mentions_memory_diagnostic(claude_md: Path) -> bool:
    return bool(_MEMORY_RE.search(claude_md.read_text(encoding="utf-8")))
