"""Parse `.claude/rules/*.md` files and simulate which rules apply to a given file path."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from pathspec import PathSpec

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)


@dataclass(frozen=True)
class Rule:
    name: str
    paths: tuple[str, ...]
    body: str


def load_rule(path: Path) -> Rule:
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path}: no YAML frontmatter found (expected --- ... ---)")
    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    raw_paths = frontmatter.get("paths")
    if not isinstance(raw_paths, list) or not all(isinstance(p, str) for p in raw_paths):
        raise ValueError(f"{path}: frontmatter 'paths' must be a list of strings")
    return Rule(name=path.stem, paths=tuple(raw_paths), body=body)


def load_rules(rules_dir: Path) -> list[Rule]:
    return sorted((load_rule(p) for p in rules_dir.glob("*.md")), key=lambda r: r.name)


def matching_rules(rules_dir: Path, file_path: str) -> list[Rule]:
    return [r for r in load_rules(rules_dir) if _matches(r.paths, file_path)]


def _matches(patterns: tuple[str, ...], file_path: str) -> bool:
    spec = PathSpec.from_lines("gitignore", patterns)
    return spec.match_file(file_path)


def body_has_concrete_convention(body: str) -> bool:
    """Heuristic: a useful rule body is at least ~10 non-trivial lines and references
    at least one concrete code construct (a backtick-quoted identifier, a path, etc.)."""
    non_trivial = [
        line for line in body.splitlines() if line.strip() and not line.strip().startswith("#")
    ]
    has_code_ref = bool(re.search(r"`[^`]+`", body))
    return len(non_trivial) >= 10 and has_code_ref
