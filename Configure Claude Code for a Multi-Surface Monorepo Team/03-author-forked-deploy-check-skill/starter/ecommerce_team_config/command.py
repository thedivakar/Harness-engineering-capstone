"""Parse `.claude/commands/*.md` and check body structure."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ecommerce_team_config.frontmatter import parse_frontmatter

_MUST_REPORT_RE = re.compile(r"\bmust[- ]report\b|\bmust\s+(flag|raise)\b", re.IGNORECASE)
_SKIP_RE = re.compile(r"\bskip\b|\bdo\s+not\s+report\b|\bignore\b", re.IGNORECASE)
_INTERVIEW_HEADING_RE = re.compile(r"^\s*#+\s+.*interview\s+pattern", re.IGNORECASE | re.MULTILINE)
_INTERACTING_RE = re.compile(r"\binteracting\b", re.IGNORECASE)
_INDEPENDENT_RE = re.compile(r"\bindependent\b", re.IGNORECASE)
_BUNDLE_RE = re.compile(
    r"\bbundle\b|\bsingle\s+(message|report)\b|\ball\s+together\b", re.IGNORECASE
)
_SEQUENTIAL_RE = re.compile(
    r"\bsequential\b|\bone\s+at\s+a\s+time\b|\bseparate(ly)?\b", re.IGNORECASE
)


@dataclass(frozen=True)
class Command:
    name: str
    frontmatter: dict[str, Any]
    body: str


def load_command(path: Path) -> Command:
    data, body = parse_frontmatter(path)
    return Command(name=path.stem, frontmatter=data, body=body)


def body_has_must_report_vs_skip_criteria(body: str) -> bool:
    return bool(_MUST_REPORT_RE.search(body)) and bool(_SKIP_RE.search(body))


def body_has_io_examples(body: str, *, minimum: int = 2) -> bool:
    """A concrete I/O example has a labeled input and a labeled output near each other.
    We require at least `minimum` such pairs, each within a 40-line window.
    """
    input_positions = [
        m.start()
        for m in re.finditer(r"^\s*(?:#+\s*|\*\*)?Input\b", body, re.MULTILINE)
    ]
    output_positions = [
        m.start()
        for m in re.finditer(r"^\s*(?:#+\s*|\*\*)?Output\b", body, re.MULTILINE)
    ]
    pairs = 0
    for i_pos in input_positions:
        nearby = [o for o in output_positions if 0 < o - i_pos < 4000]
        if nearby:
            pairs += 1
    return pairs >= minimum


def body_has_interview_pattern_section(body: str) -> bool:
    return bool(_INTERVIEW_HEADING_RE.search(body))


def body_has_interacting_vs_independent_guidance(body: str) -> bool:
    return (
        bool(_INTERACTING_RE.search(body))
        and bool(_INDEPENDENT_RE.search(body))
        and bool(_BUNDLE_RE.search(body))
        and bool(_SEQUENTIAL_RE.search(body))
    )
