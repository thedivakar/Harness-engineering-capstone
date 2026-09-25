"""Tests for path-scoped rule files in .claude/rules/ with glob frontmatter."""

from pathlib import Path

import pytest

from ecommerce_team_config.rules import (
    body_has_concrete_convention,
    load_rule,
    matching_rules,
)


@pytest.fixture(scope="module")
def rules_dir(repo_root: Path) -> Path:
    return repo_root / ".claude" / "rules"


def test_ac_02_01_react_rule_has_component_and_page_globs(rules_dir: Path) -> None:
    rule = load_rule(rules_dir / "react.md")
    assert "src/components/**/*" in rule.paths
    assert "src/pages/**/*" in rule.paths


def test_ac_02_02_api_rule_has_api_glob(rules_dir: Path) -> None:
    rule = load_rule(rules_dir / "api.md")
    assert "src/api/**/*" in rule.paths


def test_ac_02_03_tests_rule_has_test_globs(rules_dir: Path) -> None:
    rule = load_rule(rules_dir / "tests.md")
    assert "**/*.test.tsx" in rule.paths
    assert "**/*.test.ts" in rule.paths


def test_ac_02_04_react_file_matches_only_react_rule(rules_dir: Path) -> None:
    matches = {r.name for r in matching_rules(rules_dir, "src/components/Cart/Cart.tsx")}
    assert matches == {"react"}, f"Expected only react.md to match, got {matches}"


def test_ac_02_05_api_file_matches_only_api_rule(rules_dir: Path) -> None:
    matches = {r.name for r in matching_rules(rules_dir, "src/api/orders/handler.ts")}
    assert matches == {"api"}, f"Expected only api.md to match, got {matches}"


def test_ac_02_06_test_file_matches_react_and_tests(rules_dir: Path) -> None:
    matches = {r.name for r in matching_rules(rules_dir, "src/components/Cart/Cart.test.tsx")}
    assert matches == {"react", "tests"}, (
        f"Expected react.md and tests.md to both match, got {matches}"
    )


def test_ac_02_07_each_rule_has_concrete_body(rules_dir: Path) -> None:
    for name in ("react", "api", "tests"):
        rule = load_rule(rules_dir / f"{name}.md")
        assert body_has_concrete_convention(rule.body), (
            f"{name}.md body must contain at least one concrete non-trivial convention"
        )
