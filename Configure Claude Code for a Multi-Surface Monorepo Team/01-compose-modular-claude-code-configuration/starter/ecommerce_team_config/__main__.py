"""Command-line entry point: validate the team config in the current repo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ecommerce_team_config.claude_md import (
    distinguishes_project_vs_user_scope,
    mentions_memory_diagnostic,
)
from ecommerce_team_config.command import (
    body_has_interacting_vs_independent_guidance,
    body_has_interview_pattern_section,
    body_has_io_examples,
    body_has_must_report_vs_skip_criteria,
    load_command,
)
from ecommerce_team_config.imports import unresolved_imports
from ecommerce_team_config.rules import load_rules
from ecommerce_team_config.skill import (
    body_has_branching_reality_note,
    body_has_check_entries,
    body_has_main_session_isolation_rationale,
    body_has_personal_customization_note,
    body_has_skill_vs_claude_md_rubric,
    load_skill,
)
from ecommerce_team_config.tool_allowlist import write_capable_tools


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ecommerce-team-config")
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="repository root containing CLAUDE.md and .claude/ (default: cwd)",
    )
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()

    problems: list[str] = []
    problems.extend(_check_claude_md(repo_root))
    problems.extend(_check_rules(repo_root))
    problems.extend(_check_review_command(repo_root))
    problems.extend(_check_deploy_check_skill(repo_root))

    if problems:
        print(f"FAIL ({len(problems)} problems):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("OK")
    return 0


def _check_claude_md(repo_root: Path) -> list[str]:
    claude_md = repo_root / "CLAUDE.md"
    if not claude_md.exists():
        return ["CLAUDE.md missing at repo root"]
    out: list[str] = []
    dangling = unresolved_imports(claude_md, repo_root=repo_root)
    if dangling:
        out.append(f"CLAUDE.md has dangling @-import targets: {dangling}")
    scope = distinguishes_project_vs_user_scope(claude_md)
    if not all((scope.mentions_user_level, scope.mentions_project_level,
                scope.states_not_version_controlled, scope.user_scope_example)):
        out.append("CLAUDE.md scope documentation block is incomplete")
    if not mentions_memory_diagnostic(claude_md):
        out.append("CLAUDE.md missing /memory diagnostic reference")
    return out


def _check_rules(repo_root: Path) -> list[str]:
    rules_dir = repo_root / ".claude" / "rules"
    if not rules_dir.exists():
        return [".claude/rules/ directory missing"]
    rules = load_rules(rules_dir)
    return [] if rules else [".claude/rules/ contains no rule files"]


def _check_review_command(repo_root: Path) -> list[str]:
    path = repo_root / ".claude" / "commands" / "review.md"
    if not path.exists():
        return [".claude/commands/review.md missing"]
    cmd = load_command(path)
    out: list[str] = []
    tools = cmd.frontmatter.get("allowed-tools", [])
    tool_list = tools if isinstance(tools, list) else [t.strip() for t in str(tools).split(",")]
    bad = write_capable_tools(tool_list)
    if bad:
        out.append(f"/review allowed-tools includes write-capable entries: {bad}")
    if not body_has_must_report_vs_skip_criteria(cmd.body):
        out.append("/review body missing must-report-vs-skip criteria")
    if not body_has_io_examples(cmd.body, minimum=2):
        out.append("/review body has fewer than 2 concrete I/O examples")
    if not body_has_interview_pattern_section(cmd.body):
        out.append("/review body missing interview-pattern subsection")
    if not body_has_interacting_vs_independent_guidance(cmd.body):
        out.append("/review body missing interacting-vs-independent guidance")
    return out


def _check_deploy_check_skill(repo_root: Path) -> list[str]:
    path = repo_root / ".claude" / "skills" / "deploy-check" / "SKILL.md"
    if not path.exists():
        return [".claude/skills/deploy-check/SKILL.md missing"]
    skill = load_skill(path)
    out: list[str] = []
    if skill.frontmatter.get("context") != "fork":
        out.append("/deploy-check frontmatter missing context: fork")
    tools = skill.frontmatter.get("allowed-tools", [])
    tool_list = tools if isinstance(tools, list) else [t.strip() for t in str(tools).split(",")]
    bad = write_capable_tools(tool_list)
    if bad:
        out.append(f"/deploy-check allowed-tools includes write-capable entries: {bad}")
    checks = body_has_check_entries(skill.body)
    if len(checks) < 3:
        out.append(f"/deploy-check body lists {len(checks)} checks; need ≥3")
    for c in checks:
        if not (c.has_detection and c.has_pass_criterion and c.has_fail_criterion):
            out.append(f"/deploy-check check {c.title!r} missing detection/pass/fail")
    if not body_has_main_session_isolation_rationale(skill.body):
        out.append("/deploy-check body missing main-session isolation rationale")
    if not body_has_branching_reality_note(skill.body):
        out.append("/deploy-check body missing Branching Reality reference")
    if not body_has_personal_customization_note(skill.body):
        out.append("/deploy-check body missing personal-customization note")
    if not body_has_skill_vs_claude_md_rubric(skill.body):
        out.append("/deploy-check body missing skill-vs-CLAUDE.md rubric")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
