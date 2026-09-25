# Solution — Exercise 2

This directory contains the project state after Exercise 2.

Compared to the starter, `.claude/commands/review.md` is now complete:

- Frontmatter declares `description`, `argument-hint`, and an `allowed-tools` list of granular read-only entries (`Read`, `Grep`, `Glob`, `Bash(git diff:*)`, `Bash(git log:*)`, `Bash(git show:*)`, `Bash(git status:*)`, `Bash(gh pr diff:*)`, `Bash(gh pr view:*)`, `Bash(gh pr checks:*)`).
- Phase 1 names four interview triggers (dependency changes, public-API/DB-column changes, refactors without test changes, multi-surface diffs).
- Phase 2 lists the must-report taxonomy (bugs, security, convention violations the rules catch, breaking changes, migration safety) and the skip list (formatting, naming bikeshed, untracked-style preferences, TODO-with-ticket).
- Phase 3 gives the interacting-vs-independent heuristic with a one-line test.
- Two worked examples: one with two independent convention findings on `src/api/orders/get.ts`, one with three interacting bugs on `src/api/orders/refund.ts`.

## Verify

```bash
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py tests/test_us03_review_command.py
```

Expected: **21 passed**.
