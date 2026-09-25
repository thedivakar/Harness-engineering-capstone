# Exercise 2 — Author the Project-Scoped `/review` Slash Command

## What you'll build

A `.claude/commands/review.md` file that gives every teammate the same PR review experience: read-only tool allowlist, explicit must-report-vs-skip criteria, an interview pattern for ambiguous intent, interacting-vs-independent bundling guidance, and two worked I/O examples.

## What's already provided

The `starter/` directory contains everything you produced in Exercise 1 (`CLAUDE.md` + standards + rules) plus a starter `.claude/commands/review.md` with section headings, the intro paragraph, the Phase 4 output-format block, and the Notes section already filled in. Your TODOs are the frontmatter, Phase 1, Phase 2, Phase 3, and the two examples.

## How to run

```bash
cd starter/
# Reuse the venv from Exercise 1, or create a new one with pip install -e ".[dev]"
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py tests/test_us03_review_command.py
```

## Verify command

```bash
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py tests/test_us03_review_command.py
```

Expected at completion: **21 passed, 0 failed**.

The `ecommerce-team-config` CLI will still report the deploy-check skill missing — you build that in Exercise 3.
