"""Tests for the CLAUDE.md hierarchy with @-import and modular standards."""

from pathlib import Path

from ecommerce_team_config.claude_md import (
    distinguishes_project_vs_user_scope,
    mentions_memory_diagnostic,
)
from ecommerce_team_config.imports import find_imports, unresolved_imports


def test_ac_01_01_root_claude_md_has_at_least_one_import(repo_root: Path) -> None:
    """Root CLAUDE.md contains ≥1 @-import referencing a file under .claude/standards/."""
    claude_md = repo_root / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md must exist at repo root"

    imports = find_imports(claude_md)
    standards_imports = [p for p in imports if ".claude/standards/" in p]
    assert standards_imports, (
        f"Expected at least one @-import under .claude/standards/, got {imports!r}"
    )


def test_ac_01_02_two_standards_files_each_imported(repo_root: Path) -> None:
    """≥2 standards files under .claude/standards/, one frontend-relevant and one
    API-relevant, each referenced by an @-import from root CLAUDE.md."""
    standards_dir = repo_root / ".claude" / "standards"
    standards_files = list(standards_dir.glob("*.md"))
    assert len(standards_files) >= 2, (
        f"Expected ≥2 standards files under .claude/standards/, found {len(standards_files)}"
    )

    imports = find_imports(repo_root / "CLAUDE.md")
    imported_names = {Path(p).name for p in imports}
    standards_names = {f.name for f in standards_files}
    assert standards_names.issubset(imported_names), (
        f"All standards files must be @-imported. Missing: {standards_names - imported_names}"
    )

    has_frontend = any(
        kw in f.stem.lower() for f in standards_files for kw in ("frontend", "react", "ui", "web")
    )
    has_api = any(
        kw in f.stem.lower() for f in standards_files for kw in ("api", "backend", "server")
    )
    assert has_frontend, "One standards file must be frontend-relevant by name"
    assert has_api, "One standards file must be API-relevant by name"


def test_ac_01_03_no_dangling_imports(repo_root: Path) -> None:
    """Every @-import path resolves to an existing file."""
    unresolved = unresolved_imports(repo_root / "CLAUDE.md", repo_root=repo_root)
    assert not unresolved, f"Dangling @-import targets: {unresolved}"


def test_ac_01_04_claude_md_under_200_lines(repo_root: Path) -> None:
    """Root CLAUDE.md is under 200 lines (modular, not monolithic)."""
    line_count = sum(1 for _ in (repo_root / "CLAUDE.md").open())
    assert line_count < 200, f"CLAUDE.md has {line_count} lines; modular target is <200"


def test_ac_01_05_documents_scope_and_user_level_not_versioned(repo_root: Path) -> None:
    """CLAUDE.md distinguishes project-level vs user-level scope, explicitly states
    user-level is not shared via version control, and gives a user-scope example."""
    result = distinguishes_project_vs_user_scope(repo_root / "CLAUDE.md")
    assert result.mentions_user_level, "Must mention user-level (~/.claude/) scope"
    assert result.mentions_project_level, "Must mention project-level scope"
    assert result.states_not_version_controlled, (
        "Must explicitly state user-level settings are not shared via version control"
    )
    assert result.user_scope_example, "Must give a concrete user-scope example"


def test_ac_01_06_references_memory_command(repo_root: Path) -> None:
    """CLAUDE.md contains a troubleshooting one-liner pointing at /memory."""
    assert mentions_memory_diagnostic(repo_root / "CLAUDE.md"), (
        "CLAUDE.md must reference /memory as the diagnostic command for hierarchy issues"
    )
