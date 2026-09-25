# Exercise 1 — Compose Modular Claude Code Configuration

## What you'll build

A working Claude Code configuration foundation for the team's monorepo: a project-level `CLAUDE.md` that imports shared standards modularly, plus path-scoped `.claude/rules/*.md` files that load conventions per file Claude is editing.

By the end of this exercise:
- `CLAUDE.md` carries an `@-import` block, a scope-distinction table (project / user / directory), and a `/memory` troubleshooting one-liner.
- `.claude/rules/api.md` and `.claude/rules/tests.md` declare YAML frontmatter with `paths:` globs that activate the right conventions for API handler files and test files. (`.claude/rules/react.md` is provided as the worked example.)

## What's already provided

The `starter/` directory contains:

- The full Python validator package (`ecommerce_team_config/`), test suite (`tests/`), and React/Node/Postgres scaffold under `src/`. You consume the validator as a black-box checker — you do not modify it.
- The four `.claude/standards/*.md` files (`frontend.md`, `api.md`, `database.md`, `testing.md`) already complete. These are the always-loaded shared standards your `@-import` block will pull in.
- `.claude/rules/react.md` already complete, as a worked example of the path-scoped rule pattern (YAML frontmatter with `paths:` globs + body conventions).
- A starter `CLAUDE.md` and stub `.claude/rules/api.md` + `.claude/rules/tests.md` with `# TODO:` comments marking each location you implement.

## How to run

```bash
cd starter/
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py
```

You should see failures while the TODOs are unfilled. As you fill them in, more tests pass. The exercise is complete when both files pass cleanly.

## Verify command

```bash
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py
```

Expected at completion: **13 passed, 0 failed**.

The validator CLI (`ecommerce-team-config`) will still report missing `.claude/commands/review.md` and `.claude/skills/deploy-check/SKILL.md` — that is expected. You will build those in Exercises 2 and 3.
