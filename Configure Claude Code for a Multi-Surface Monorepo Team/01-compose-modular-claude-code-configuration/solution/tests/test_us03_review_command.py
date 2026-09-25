"""Tests for the project-scoped /review slash command."""

from pathlib import Path

import pytest

from ecommerce_team_config.command import (
    body_has_interacting_vs_independent_guidance,
    body_has_interview_pattern_section,
    body_has_io_examples,
    body_has_must_report_vs_skip_criteria,
    load_command,
)
from ecommerce_team_config.tool_allowlist import write_capable_tools


@pytest.fixture(scope="module")
def review_command_path(repo_root: Path) -> Path:
    return repo_root / ".claude" / "commands" / "review.md"


def test_ac_03_01_exists_with_valid_frontmatter(review_command_path: Path) -> None:
    assert review_command_path.exists()
    cmd = load_command(review_command_path)
    assert isinstance(cmd.frontmatter, dict) and cmd.frontmatter


def test_ac_03_02_description_and_argument_hint(review_command_path: Path) -> None:
    cmd = load_command(review_command_path)
    desc = cmd.frontmatter.get("description", "")
    assert isinstance(desc, str) and len(desc) >= 10, "description must be ≥10 chars"
    assert cmd.frontmatter.get("argument-hint"), "argument-hint frontmatter must be present"


def test_ac_03_03_allowed_tools_is_read_oriented(review_command_path: Path) -> None:
    cmd = load_command(review_command_path)
    tools = cmd.frontmatter.get("allowed-tools")
    assert tools, "allowed-tools frontmatter must be present"
    tool_list = tools if isinstance(tools, list) else [t.strip() for t in str(tools).split(",")]
    offenders = write_capable_tools(tool_list)
    assert not offenders, f"/review must not allow write-capable tools, got {offenders}"


def test_ac_03_04_must_report_vs_skip_criteria(review_command_path: Path) -> None:
    cmd = load_command(review_command_path)
    assert body_has_must_report_vs_skip_criteria(cmd.body), (
        "Body must contain explicit must-report vs skip taxonomy"
    )


def test_ac_03_05_two_concrete_io_examples(review_command_path: Path) -> None:
    cmd = load_command(review_command_path)
    assert body_has_io_examples(cmd.body, minimum=2), (
        "Body must contain at least 2 concrete input/output examples"
    )


def test_ac_03_06_is_project_scoped(review_command_path: Path, repo_root: Path) -> None:
    rel = review_command_path.relative_to(repo_root)
    assert rel.parts[:2] == (".claude", "commands"), (
        f"Command must live under .claude/commands/, found at {rel}"
    )


def test_ac_03_07_interview_pattern_subsection(review_command_path: Path) -> None:
    cmd = load_command(review_command_path)
    assert body_has_interview_pattern_section(cmd.body), (
        "Body must contain an Interview-pattern subsection"
    )


def test_ac_03_08_interacting_vs_independent_guidance(review_command_path: Path) -> None:
    cmd = load_command(review_command_path)
    assert body_has_interacting_vs_independent_guidance(cmd.body), (
        "Body must distinguish interacting issues (bundle) from independent issues (sequential)"
    )
