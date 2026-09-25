"""Decide whether an `allowed-tools` entry is read-oriented or write-capable.

Used by both /review commands and read-only skills like /deploy-check. The team's
contract: commands and skills declared as read-only must not silently grant write
or destructive capability through bare `Bash`, `Edit`, `Write`, etc.
"""

from __future__ import annotations

import re

_READ_ONLY_TOOLS = frozenset(
    {
        "Read",
        "Grep",
        "Glob",
        "WebSearch",
        "TodoWrite",
        "Task",
    }
)

# Tools that always grant write or out-of-band side effects.
_WRITE_CAPABLE_TOOLS = frozenset(
    {
        "Edit",
        "Write",
        "NotebookEdit",
        "WebFetch",
    }
)

# Sub-command prefixes that are safe as `Bash(prefix:*)`. Read-only verbs only.
_SAFE_BASH_PREFIXES = frozenset(
    {
        "git diff",
        "git log",
        "git show",
        "git status",
        "git blame",
        "git branch",
        "git ls-files",
        "git rev-parse",
        "git rev-list",
        "git remote",
        "gh pr diff",
        "gh pr view",
        "gh pr list",
        "gh pr checks",
        "gh issue view",
        "gh issue list",
        "ls",
        "cat",
        "head",
        "tail",
        "wc",
        "find",
    }
)

_BASH_SCOPED_RE = re.compile(r"^Bash\((.+?)(?::.*)?\)$")


def is_read_oriented(tool: str) -> bool:
    tool = tool.strip()
    if tool in _WRITE_CAPABLE_TOOLS:
        return False
    if tool in _READ_ONLY_TOOLS:
        return True
    if tool == "Bash":
        return False
    match = _BASH_SCOPED_RE.match(tool)
    if match:
        prefix = match.group(1).strip()
        return any(prefix == p or prefix.startswith(p + " ") for p in _SAFE_BASH_PREFIXES)
    return False


def write_capable_tools(tools: list[str]) -> list[str]:
    return [t for t in tools if not is_read_oriented(t)]
