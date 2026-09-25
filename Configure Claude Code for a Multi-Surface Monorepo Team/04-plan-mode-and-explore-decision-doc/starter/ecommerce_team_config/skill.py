"""Parse `.claude/skills/<name>/SKILL.md` and check body structure."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ecommerce_team_config.frontmatter import parse_frontmatter

_DETECTION_RE = re.compile(r"^\s*(detect|how\s+to\s+(check|detect)|signal)\b", re.IGNORECASE)
_PASS_RE = re.compile(r"^\s*(pass|green|ok\b|success)\b", re.IGNORECASE)
_FAIL_RE = re.compile(r"^\s*(fail|red|block|stop)\b", re.IGNORECASE)
_MAIN_SESSION_RE = re.compile(
    r"main\s+(session|conversation|context)|out\s+of\s+the\s+main", re.IGNORECASE
)
_BRANCHING_REALITY_RE = re.compile(r"branching\s+reality", re.IGNORECASE)
_PERSONAL_CUSTOMIZATION_RE = re.compile(r"~/\.claude/skills/", re.IGNORECASE)


@dataclass(frozen=True)
class Skill:
    name: str
    frontmatter: dict[str, Any]
    body: str


@dataclass(frozen=True)
class CheckEntry:
    title: str
    has_detection: bool
    has_pass_criterion: bool
    has_fail_criterion: bool


def load_skill(path: Path) -> Skill:
    data, body = parse_frontmatter(path)
    return Skill(name=path.parent.name, frontmatter=data, body=body)


def body_has_check_entries(body: str) -> list[CheckEntry]:
    """Split the body on H3+ headings under a 'Checks' section and inspect each
    block for detection / pass / fail markers."""
    blocks = _extract_check_blocks(body)
    return [
        CheckEntry(
            title=title,
            has_detection=any(_DETECTION_RE.match(line) for line in lines),
            has_pass_criterion=any(_PASS_RE.match(line) for line in lines),
            has_fail_criterion=any(_FAIL_RE.match(line) for line in lines),
        )
        for title, lines in blocks
    ]


def _extract_check_blocks(body: str) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    in_checks_section = False
    current_title: str | None = None
    current_lines: list[str] = []
    for raw in body.splitlines():
        line = raw.rstrip()
        h2 = re.match(r"^##\s+(.+)$", line)
        h3 = re.match(r"^###\s+(.+)$", line)
        if h2:
            if current_title is not None:
                blocks.append((current_title, current_lines))
                current_title, current_lines = None, []
            in_checks_section = "check" in h2.group(1).lower()
            continue
        if h3 and in_checks_section:
            if current_title is not None:
                blocks.append((current_title, current_lines))
            current_title, current_lines = h3.group(1).strip(), []
            continue
        if current_title is not None:
            # Strip leading list/bold markers so the marker regexes can match.
            stripped = re.sub(r"^[\s\-\*\d\.]*\*{0,2}", "", line)
            current_lines.append(stripped)
    if current_title is not None:
        blocks.append((current_title, current_lines))
    return blocks


def body_has_main_session_isolation_rationale(body: str) -> bool:
    return bool(_MAIN_SESSION_RE.search(body))


def body_has_branching_reality_note(body: str) -> bool:
    return bool(_BRANCHING_REALITY_RE.search(body))


def body_has_personal_customization_note(body: str) -> bool:
    return bool(_PERSONAL_CUSTOMIZATION_RE.search(body))


def body_has_skill_vs_claude_md_rubric(body: str) -> bool:
    """Heuristic: a real decision rubric mentions both "skill" and "CLAUDE.md", and
    contrasts on-demand/forked against always-loaded/universal."""
    mentions_both = "skill" in body.lower() and "claude.md" in body.lower()
    mentions_on_demand = re.search(r"on[- ]demand|forked|task[- ]specific", body, re.IGNORECASE)
    mentions_always_loaded = re.search(
        r"always[- ]loaded|universal|every\s+session", body, re.IGNORECASE
    )
    return bool(mentions_both and mentions_on_demand and mentions_always_loaded)
