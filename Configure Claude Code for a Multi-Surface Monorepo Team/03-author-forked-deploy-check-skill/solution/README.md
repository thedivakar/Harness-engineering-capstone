# Solution — Exercise 3

This directory contains the project state after Exercise 3.

Compared to the starter, `.claude/skills/deploy-check/SKILL.md` is now complete:

- Frontmatter: `name: deploy-check`, `description`, `context: fork`, quoted `argument-hint`, and a read-only `allowed-tools` allowlist (`Read`, `Grep`, `Glob`, `Bash(git status:*)`, `Bash(git diff:*)`, `Bash(git log:*)`, `Bash(git rev-parse:*)`, `Bash(git ls-files:*)`, `Bash(gh pr view:*)`, `Bash(gh pr checks:*)`).
- "Why this is a skill" rubric contrasts on-demand/forked/task-specific against always-loaded/universal.
- "Why `context: fork`" rationale explicitly names main-session isolation and the Branching-Reality analogy at the skill layer.
- Three checks (uncommitted changes, migrations up-to-date, CI checks green) each with Detect / Pass / Fail.
- Personalization note pointing teammates at `~/.claude/skills/deploy-check-strict/` for personal variants.

## Verify

```bash
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py tests/test_us03_review_command.py tests/test_us04_deploy_check_skill.py && ecommerce-team-config .
```

Expected: **28 passed** + `OK`.
