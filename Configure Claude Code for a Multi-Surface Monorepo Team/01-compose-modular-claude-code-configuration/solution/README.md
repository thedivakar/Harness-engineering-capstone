# Solution — Exercise 1

This directory contains the project state after Exercise 1.

Compared to the starter, the following are now complete:

- `CLAUDE.md` — scope-distinction table, `@-import` block pulling in all four standards, and the `/memory` troubleshooting line.
- `.claude/rules/api.md` — frontmatter (`paths: ["src/api/**/*"]`) plus a body of API conventions (handler signature shape, error throwing, DB access boundaries, validation, logging).
- `.claude/rules/tests.md` — frontmatter (`paths: ["**/*.test.tsx", "**/*.test.ts"]`) plus a body of testing conventions. Note the cross-cutting glob — it matches test files under `src/components/` AND under `src/api/`, so the same test file picks up both the React rule and the test rule.

## Verify

```bash
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py
```

Expected: **13 passed**.
